"""Runs the evaluation questions through the assistant and records what happened.

    cd LLM
    ../Backend/.venv/bin/python -m evaluation.run --name main                 # everything not yet done
    ../Backend/.venv/bin/python -m evaluation.run --name main --limit 5       # the next five
    ../Backend/.venv/bin/python -m evaluation.run --name main --cases C2,C3 --conditions grounded
    ../Backend/.venv/bin/python -m evaluation.run --dry-run                   # the questions and their keys; asks nothing

Each question is asked once with the knowledge base (grounded) and, for the questions where it
matters, once without (ungrounded). Results are appended to results/<name>/results.jsonl as they
arrive, and a question already answered is skipped, so a run can be stopped by a rate limit and
continued later. Draft purchase orders created by the action cases are deleted again afterwards.
"""
import argparse
import json
import time
from dataclasses import asdict
from datetime import date, datetime
from pathlib import Path

from evaluation.cases import Case, build_cases
from evaluation.context import Context, open_context
from evaluation.scoring import describe, score

from app.core.exceptions import ServiceUnavailableError
from app.knowledge.content import get_knowledge_base
from app.llm.recommendations import unmatched_figures
from app.llm.tools import MAX_DRAFTS_PER_REQUEST
from app.models.enums import PurchaseOrderOrigin, PurchaseOrderStatus

RESULTS = Path(__file__).resolve().parent / "results"
MAX_STORED_TOOL_OUTPUT = 40_000


def ai_drafts(ctx: Context) -> set[str]:
    return {
        po.id for po in ctx.orders_repo.list()
        if po.origin != PurchaseOrderOrigin.MANUAL and po.status == PurchaseOrderStatus.DRAFT
    }


def run_case(ctx: Context, case: Case, grounded: bool) -> dict:
    user = ctx.user(case.role)
    service, toolbox, outputs = ctx.assistant(grounded)
    drafts_before = ai_drafts(ctx)

    started = time.monotonic()
    response = service.chat(case.question, user)
    seconds = round(time.monotonic() - started, 1)

    created = sorted(ai_drafts(ctx) - drafts_before)
    action_correct = None
    if case.drafts is not None:
        # Every draft must be one the case asks for, no product drafted twice, and the number within bounds:
        # exactly one for "draft", up to the per-message limit for "drafts".
        orders = [ctx.orders_repo.get(po_id) for po_id in created]
        wanted = [all(getattr(order, name) == value for name, value in spec.items()) for order in orders for spec in case.drafts]
        matched = sum(wanted)
        most = 1 if case.expectation.action == "draft" else MAX_DRAFTS_PER_REQUEST
        action_correct = (
            1 <= len(orders) <= most and matched == len(orders) and len({order.product_id for order in orders}) == len(orders)
        )
    for po_id in created:  # leave the database as it was
        ctx.procurement.delete_draft(po_id, user)

    knowledge = get_knowledge_base()
    passages = " ".join(entry.text for item in response.knowledge if (entry := knowledge.get(item["id"])))
    tool_text = json.dumps(outputs, default=str)
    evidence = f"{case.question} {ctx.clock.today().isoformat()} {tool_text} {passages}"

    record = {
        "case": case.id,
        "category": case.category,
        "condition": "grounded" if grounded else "ungrounded",
        "role": case.role,
        "question": case.question,
        "expected": asdict(case.expectation),
        "status": response.status,
        "answer": response.message,
        "sources": response.sources,
        "knowledge": [item["id"] for item in response.knowledge],
        "recommendations": response.recommendations,
        "actions": response.actions,
        "orders_created": created,
        "action_correct": action_correct,
        "provider": response.provider,
        "model": response.model,
        "usage": response.usage,
        "seconds": seconds,
        "tool_rounds": len({json.dumps(s["input"], sort_keys=True) + s["tool"] for s in response.sources}),
        "tool_outputs": tool_text[:MAX_STORED_TOOL_OUTPUT],
        "asked_at": datetime.now().isoformat(timespec="seconds"),
    }
    result = score(case.expectation, record, unmatched_figures(response.message, evidence))
    record["score"] = {**asdict(result), "recall": result.recall}
    return record


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the IntelliERP assistant evaluation.")
    parser.add_argument("--name", default="main", help="results are kept in results/<name>/")
    parser.add_argument("--conditions", default="grounded,ungrounded")
    parser.add_argument("--cases", default="", help="comma-separated case ids; default all")
    parser.add_argument("--category", default="", help="only this category")
    parser.add_argument("--limit", type=int, default=0, help="stop after this many questions")
    parser.add_argument("--retries", type=int, default=0, help="times to wait and ask again when the model is unavailable")
    parser.add_argument("--retry-wait", type=int, default=120, help="seconds to wait before each retry")
    parser.add_argument("--dry-run", action="store_true", help="print the questions and their computed keys; ask nothing")
    args = parser.parse_args()
    if args.dry_run:
        return dry_run(args)

    folder = RESULTS / args.name
    folder.mkdir(parents=True, exist_ok=True)
    results_file = folder / "results.jsonl"
    done = set()
    if results_file.exists():
        done = {(r["case"], r["condition"]) for r in map(json.loads, results_file.read_text().splitlines()) if r}

    conditions = [c.strip() for c in args.conditions.split(",") if c.strip()]
    wanted = {c.strip() for c in args.cases.split(",") if c.strip()}
    asked, stopped = 0, False
    with open_context() as ctx:
        if ctx.provider is None:
            raise SystemExit("No model is configured. Set the provider's API key in Backend/.env.")
        cases = [
            case for case in build_cases(ctx)
            if (not wanted or case.id in wanted) and (not args.category or case.category == args.category)
        ]
        todo = [
            (case, condition) for condition in conditions for case in cases
            if (condition == "grounded" or case.grounding_sensitive) and (case.id, condition) not in done
        ]
        print(f"{len(todo)} to ask ({len(done)} already done) on {ctx.provider.name} / {ctx.provider.model}")
        for case, condition in todo:
            if args.limit and asked >= args.limit:
                break
            record = None
            for attempt in range(args.retries + 1):
                try:
                    record = run_case(ctx, case, grounded=condition == "grounded")
                    break
                except ServiceUnavailableError as error:
                    ctx.session and ctx.session.rollback()
                    if attempt < args.retries:
                        print(f"{case.id} ({condition}): {error.message} Waiting {args.retry_wait}s (retry {attempt + 1} of {args.retries}).", flush=True)
                        time.sleep(args.retry_wait)
                    else:
                        print(f"Stopped at {case.id} ({condition}): {error.message}\nRun the same command again later to continue.")
            if record is None:
                stopped = True
                break
            with results_file.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record, default=str) + "\n")
            asked += 1
            s = record["score"]
            print(f"{case.id:3s} {condition:10s} {'PASS' if s['passed'] else 'FAIL'}  facts {s['facts_found']}/{s['facts_expected']}"
                  f"  tools {len(record['sources'])}  {record['seconds']:>5}s  {record['model']}"
                  + (f"  missing: {s['missing']}" if s["missing"] else "")
                  + (f"  violations: {s['violations']}" if s["violations"] else "")
                  + (f"  unsupported: {s['unsupported_figures']}" if s["unsupported_figures"] else ""), flush=True)
    print(f"Asked {asked}. Results: {results_file}")
    from evaluation.report import write_report

    print(f"Report: {write_report(args.name)}")
    if stopped:
        raise SystemExit(3)  # unfinished: lets a script that chains runs stop here instead of starting the next


def dry_run(args) -> None:
    """Shows what would be asked and what each answer is checked against, without calling the model."""
    with open_context() as ctx:
        cases = build_cases(ctx)
        admin_tools = {tool.name for tool in ctx.assistant(True)[1].available(ctx.user("admin"))}
        problems = []
        for case in cases:
            if args.category and case.category != args.category:
                continue
            allowed = {tool.name for tool in ctx.assistant(True)[1].available(ctx.user(case.role))}
            e = case.expectation
            print(f"\n{case.id} [{case.category}, {case.role}{', paired' if case.grounding_sensitive else ''}] {case.question}")
            for fact in e.facts:
                print(f"    fact: {describe(fact)}")
            for fact in e.forbidden_facts:
                print(f"    must not reveal: {describe(fact)}")
            extras = [f"one of the tools {e.tools}" if e.tools else "", f"must not use {e.forbidden_tools}" if e.forbidden_tools else "",
                      f"action: {e.action}" if e.action else "", "must not recommend a reorder" if e.no_reorder else "",
                      f"acceptable drafts: {case.drafts}" if case.drafts else ""]
            for extra in filter(None, extras):
                print(f"    {extra}")
            # A key that names a tool which does not exist, or expects a tool the role is not given, is a mistake in the key.
            if unknown := (set(e.tools) | set(e.forbidden_tools)) - admin_tools:
                problems.append(f"{case.id}: unknown tool {sorted(unknown)}")
            if e.tools and not set(e.tools) & allowed:
                problems.append(f"{case.id}: role {case.role} has none of the expected tools")
            if set(e.forbidden_tools) & allowed:
                problems.append(f"{case.id}: role {case.role} is given a tool the case forbids {sorted(set(e.forbidden_tools) & allowed)}")
        ids = [case.id for case in cases]
        if len(ids) != len(set(ids)):
            problems.append("duplicate case ids")
        counts = {category: sum(case.category == category for case in cases) for category in dict.fromkeys(c.category for c in cases)}
        paired = sum(case.grounding_sensitive for case in cases)
        print(f"\n{len(cases)} questions {counts}; {paired} also asked without grounding = {len(cases) + paired} answers per run")
        print("Problems in the keys: " + ("; ".join(problems) if problems else "none"))


if __name__ == "__main__":
    main()

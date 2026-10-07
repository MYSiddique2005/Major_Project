"""Runs the evaluation questions through the assistant and records what happened.

    cd LLM
    ../Backend/.venv/bin/python -m evaluation.run --name main                 # everything not yet done
    ../Backend/.venv/bin/python -m evaluation.run --name main --limit 5       # the next five
    ../Backend/.venv/bin/python -m evaluation.run --name main --cases C2,C3 --conditions grounded

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

from evaluation.cases import Case, build_cases, expected_draft
from evaluation.context import Context, open_context
from evaluation.scoring import score

from app.core.exceptions import ServiceUnavailableError
from app.knowledge.content import get_knowledge_base
from app.llm.recommendations import unmatched_figures
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
    wanted_draft = expected_draft(ctx, case.id)

    started = time.monotonic()
    response = service.chat(case.question, user)
    seconds = round(time.monotonic() - started, 1)

    created = sorted(ai_drafts(ctx) - drafts_before)
    action_correct = None
    if wanted_draft is not None:
        orders = [ctx.orders_repo.get(po_id) for po_id in created]
        action_correct = len(orders) == 1 and all(
            getattr(orders[0], field) == value for field, value in wanted_draft.items()
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
    args = parser.parse_args()

    folder = RESULTS / args.name
    folder.mkdir(parents=True, exist_ok=True)
    results_file = folder / "results.jsonl"
    done = set()
    if results_file.exists():
        done = {(r["case"], r["condition"]) for r in map(json.loads, results_file.read_text().splitlines()) if r}

    conditions = [c.strip() for c in args.conditions.split(",") if c.strip()]
    wanted = {c.strip() for c in args.cases.split(",") if c.strip()}
    asked = 0
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
            try:
                record = run_case(ctx, case, grounded=condition == "grounded")
            except ServiceUnavailableError as error:
                print(f"Stopped at {case.id} ({condition}): {error.message}\nRun the same command again later to continue.")
                break
            with results_file.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record, default=str) + "\n")
            asked += 1
            s = record["score"]
            print(f"{case.id:3s} {condition:10s} {'PASS' if s['passed'] else 'FAIL'}  facts {s['facts_found']}/{s['facts_expected']}"
                  f"  tools {len(record['sources'])}  {record['seconds']:>5}s  {record['model']}"
                  + (f"  missing: {s['missing']}" if s["missing"] else "")
                  + (f"  violations: {s['violations']}" if s["violations"] else "")
                  + (f"  unsupported: {s['unsupported_figures']}" if s["unsupported_figures"] else ""))
    print(f"Asked {asked}. Results: {results_file}")
    from evaluation.report import write_report

    print(f"Report: {write_report(args.name)}")


if __name__ == "__main__":
    main()

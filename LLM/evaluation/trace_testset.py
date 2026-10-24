"""The held-out test for TRACE: model-written errors in texts TRACE was never developed on.

    ../Backend/.venv/bin/python -m evaluation.trace_testset pool                          # no model calls
    LLM_MODEL=gemini-3.5-flash-lite ../Backend/.venv/bin/python -m evaluation.trace_testset perturb --writer gemini
    LLM_MODEL=gemma-4-31b-it        ../Backend/.venv/bin/python -m evaluation.trace_testset perturb --writer gemma

Pool: every answer of the open-weight model's run (results/gemma4-1) that names a product, and every
insight from scans after SCAN-0007. None of these texts was read while TRACE or the version-3 checker
was written.

Rewrites: as for the version-3 tests, each text gets one rewrite with exactly one statement made false
and one paraphrase with the same meaning (for false alarms). Two differences:
  - two writers (Gemini and Gemma), so the test does not reflect one model's style of error;
  - errors are stratified: each text is assigned an error type in turn (qualitative, figure, existence or
    relation, permission, rule, derived), and the writer uses that type when the text allows it and
    reports the type it used.

Order of work: the rewrites are generated only after TRACE's files are frozen (their hash recorded in
results/trace/frozen.json), and they are not read before scoring.
"""
import argparse
import hashlib
import json
import random
import re
import time
from pathlib import Path

from evaluation.claims_eval import RESULTS
from evaluation.context import open_context

OUT = RESULTS / "trace"
POOL = OUT / "heldout-pool.jsonl"
SEED = 2026
BATCH = 5
PRODUCT_ID = re.compile(r"\bP\d{3}\b")
DEV_SCANS = {"SCAN-0002", "SCAN-0003", "SCAN-0004", "SCAN-0005", "SCAN-0006", "SCAN-0007"}

ERROR_TYPES = {
    "qualitative": "reverse a qualitative statement: a comparison (below/above safety stock, cover shorter/longer than "
                   "the lead time), a trend (rising/falling), a risk level, a stock status, whether a delivery arrives "
                   "in time, or whether units are overdue",
    "figure": "change one figure about the data (units on hand, demand, units on order, a quantity, a date) to a "
              "wrong value",
    "existence": "change whether a product, supplier or purchase order exists, or whether a supplier supplies a product",
    "permission": "change what the assistant or a user's role can or cannot do (approve, submit, draft, view)",
    "rule": "change a company rule's threshold, time window or limit (a percentage, a number of days, a maximum)",
    "derived": "change a computed result: the suggested reorder quantity, the reorder point, a count of products at a "
               "risk level, which product runs out first, or a what-if result",
}

PROMPT = """\
Below are {count} texts written by the AI assistant of an ERP system (sales, inventory, purchasing). For \
EACH text do two separate things.

1. "injected": rewrite the text changing exactly ONE statement so that it becomes FALSE. Each text has an \
assigned error type. Use it if the text contains a statement of that type; otherwise use another type from \
the list that the text allows. Error types:
{types}
Keep everything else word for word. Report the original words you changed, the words you put in their \
place, and the error type you used.

2. "paraphrase": rewrite the original text in clearly different words with exactly the same meaning: every \
fact, comparison, number, name, ID and date stays true. Do not add or remove information.

Reply with JSON only: {{"items": [{{"id": "T1", "injected": {{"rewritten": "...", "changed_from": "...", \
"changed_to": "...", "error_type": "..."}}, "paraphrase": "..."}}, ...]}} with one item per text.

{texts}"""


def build_pool(ctx) -> list[dict]:
    """The held-out texts, in a seeded order that does not depend on any checker."""
    items = []
    for line in (RESULTS / "gemma4-1" / "results.jsonl").read_text().splitlines():
        record = json.loads(line)
        if record.get("answer") and PRODUCT_ID.search(record["answer"]):
            items.append({"id": f"gemma4-1/{record['case']}/{record['condition']}", "source": "answer",
                          "condition": record["condition"], "text": record["answer"]})
    for insight in ctx.insights_repo.list():
        if insight.scan_id not in DEV_SCANS:
            text = ". ".join([insight.headline, insight.explanation, *(e["statement"] for e in insight.evidence)])
            items.append({"id": f"insight/{insight.id}", "source": "insight", "condition": "insight", "text": text,
                          "subject_type": insight.subject_type, "subject_id": insight.subject_id})
    unique = list({item["text"]: item for item in items}.values())
    random.Random(SEED).shuffle(unique)
    names = list(ERROR_TYPES)
    for index, item in enumerate(unique):
        item["assigned_type"] = names[index % len(names)]
    return unique


def ask(prompt: str, temperature: float = 0.7) -> dict:
    """One JSON reply from the configured model. Gemma may not support JSON mode, so the JSON is read from
    plain text when it is refused."""
    from google import genai
    from google.genai import errors as genai_errors
    from google.genai import types as genai_types

    from app.core.config import get_settings
    from app.llm.providers import quota_wait_seconds

    settings = get_settings()
    client = genai.Client(api_key=settings.gemini_api_key)
    model = settings.llm_model
    json_mode = True
    for attempt in range(8):
        try:
            config = genai_types.GenerateContentConfig(temperature=temperature, **({"response_mime_type": "application/json"} if json_mode else {}))
            response = client.models.generate_content(model=model, contents=prompt, config=config)
            text = response.text or ""
            start, end = text.find("{"), text.rfind("}")
            return {**json.loads(text[start:end + 1]), "model": response.model_version or model}
        except genai_errors.APIError as error:
            if error.code == 400 and json_mode:
                json_mode = False
                continue
            wait = quota_wait_seconds(error)
            if wait is None and error.code in (500, 502, 503, 504):
                wait = 30 * (attempt + 1)
            if wait is None:
                raise
            time.sleep(wait)
        except (json.JSONDecodeError, ValueError, TypeError):
            continue
        except Exception:
            time.sleep(20)
    raise RuntimeError("no usable reply")


def perturb(writer: str, limit: int | None) -> Path:
    pool = [json.loads(line) for line in POOL.read_text().splitlines()]
    if limit:
        pool = pool[:limit]
    out = OUT / f"heldout-{writer}.jsonl"
    done = {json.loads(line)["id"] for line in out.read_text().splitlines()} if out.exists() else set()
    todo = [item for item in pool if item["id"] not in done]
    print(f"{len(todo)} texts to rewrite with writer {writer}", flush=True)
    for start in range(0, len(todo), BATCH):
        group = todo[start:start + BATCH]
        texts = "\n\n".join(f'T{i + 1} (assigned error type: {item["assigned_type"]}):\n"""\n{item["text"]}\n"""'
                            for i, item in enumerate(group))
        types = "\n".join(f"- {name}: {meaning}" for name, meaning in ERROR_TYPES.items())
        reply = ask(PROMPT.format(count=len(group), types=types, texts=texts))
        by_id = {entry.get("id"): entry for entry in reply.get("items", []) if isinstance(entry, dict)}
        with out.open("a") as handle:
            for i, item in enumerate(group):
                entry = by_id.get(f"T{i + 1}")
                if not entry:
                    continue
                injected = entry.get("injected") or {}
                handle.write(json.dumps({"id": item["id"], "kind": "inject", "writer": writer, "model": reply["model"],
                                         "assigned_type": item["assigned_type"], "original": item["text"],
                                         "rewritten": injected.get("rewritten", ""), "changed_from": injected.get("changed_from", ""),
                                         "changed_to": injected.get("changed_to", ""),
                                         "error_type": injected.get("error_type", "")}) + "\n")
                handle.write(json.dumps({"id": item["id"], "kind": "paraphrase", "writer": writer, "model": reply["model"],
                                         "original": item["text"], "rewritten": entry.get("paraphrase", "")}) + "\n")
        print(f"batch {start // BATCH + 1} written", flush=True)
    return out


def freeze() -> Path:
    """Records the hash of every TRACE source file and of the frozen version-3 checker."""
    root = Path(__file__).resolve().parents[2] / "Backend" / "app" / "llm"
    files = sorted(root.glob("trace/*.py")) + [root / "claims.py"]
    record = {str(path.relative_to(root.parent.parent)): hashlib.sha256(path.read_bytes()).hexdigest() for path in files}
    record["frozen_at"] = time.strftime("%Y-%m-%d %H:%M")
    path = OUT / "frozen.json"
    path.write_text(json.dumps(record, indent=2) + "\n")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description="Build TRACE's held-out test.")
    parser.add_argument("step", choices=["pool", "perturb", "freeze"])
    parser.add_argument("--writer", choices=["gemini", "gemma"])
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    if args.step == "pool":
        with open_context() as ctx:
            pool = build_pool(ctx)
        POOL.write_text("".join(json.dumps(item) + "\n" for item in pool))
        print(f"{len(pool)} texts in the held-out pool: {POOL}")
    elif args.step == "freeze":
        print(freeze())
    else:
        if not (OUT / "frozen.json").exists():
            raise SystemExit("Freeze TRACE first (step 'freeze'): the test must be made after the method is fixed.")
        print(perturb(args.writer, args.limit))


if __name__ == "__main__":
    main()

"""Evaluation of claim-level verification (app/llm/claims.py).

    ../Backend/.venv/bin/python -m evaluation.claims_eval collect          # part A: no model calls
    ../Backend/.venv/bin/python -m evaluation.claims_eval perturb --limit 60   # part B: one model request per text
    ../Backend/.venv/bin/python -m evaluation.claims_eval report

The checker's patterns were written while reading the answers of the extended runs, so measuring it on
those answers would be circular. The main test therefore uses text the checker has not seen, written by
the model, not by the authors:

  A. Real text (development set). Every answer of the runs extended-1 and fixed-1/2/3 and every insight
     from the scans run on the current data, checked as they are. Reported, but not evidence of accuracy.
  B. Perturbed text (test set). For a seeded sample of those texts that discuss a product, the model is
     asked twice, independently:
       - inject: rewrite the text changing exactly one statement about stock, demand, deliveries, the
         supplier or risk so that it becomes false, without changing any number. Detection rate = share of
         valid injections the checker flags as contradicted.
       - paraphrase: rewrite the text in different words with the same meaning. False-alarm rate = share
         of paraphrases in which the checker flags a contradiction that the original did not have.
     A rewrite is valid when the model reports what it changed and that change is visible in the text.

Results are stored in results/claims/ and the model's rewrites are kept, so every number can be audited.
"""
import argparse
import json
import random
import re
import time
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path

from evaluation.context import open_context
from evaluation.stats import wilson_interval

from app.llm import claims as C
from app.llm.recommendations import RecommendationChecker

RESULTS = Path(__file__).resolve().parent / "results"
OUT = RESULTS / "claims"
RUNS = ("extended-1", "fixed-1", "fixed-2", "fixed-3")
SCANS_ON_CURRENT_DATA = ("SCAN-0005", "SCAN-0006", "SCAN-0007")  # after the data's date was fixed (7 Oct)
PRODUCT_ID = re.compile(r"\bP\d{3}\b")
SEED = 42

INJECT = """\
Below is a text from an inventory management system about a product, its stock, demand, deliveries, \
supplier and stockout risk.

Rewrite it, changing exactly ONE statement so that it becomes FALSE. Change a qualitative statement, for \
example reverse a comparison (below/above safety stock, less/more than the lead time), reverse a trend \
(rising/falling demand), change a risk level (Critical/High/Medium/Low), say a delivery arrives in time \
when it does not or the opposite, or say units are overdue when none are or the opposite. Do not change \
any number, name, ID or date. Keep everything else word for word.

Reply with JSON only: {{"rewritten": "...", "changed_from": "the original words you changed", \
"changed_to": "the words you put in their place"}}

Text:
{text}"""

PARAPHRASE = """\
Below is a text from an inventory management system. Rewrite it in clearly different words and sentence \
structure while keeping exactly the same meaning: every fact, comparison, trend, risk level, number, \
name, ID and date must stay true to the original. Do not add or remove information.

Reply with JSON only: {{"rewritten": "..."}}

Text:
{text}"""


BATCH = """\
Below are {count} texts from an inventory management system, each about a product, its stock, demand, \
deliveries, supplier and stockout risk. For EACH text do two separate things.

1. "injected": rewrite the text changing exactly ONE statement so that it becomes FALSE. Change a \
qualitative statement, for example reverse a comparison (below/above safety stock, less/more than the lead \
time), reverse a trend (rising/falling demand), change a risk level (Critical/High/Medium/Low), say a \
delivery arrives in time when it does not or the opposite, or say units are overdue when none are or the \
opposite. Do not change any number, name, ID or date. Keep everything else word for word. Report the \
original words you changed and the words you put in their place.

2. "paraphrase": rewrite the original text in clearly different words and sentence structure with exactly \
the same meaning: every fact, comparison, trend, risk level, number, name, ID and date stays true. Do not \
add or remove information.

Reply with JSON only: {{"items": [{{"id": "T1", "injected": {{"rewritten": "...", "changed_from": "...", \
"changed_to": "..."}}, "paraphrase": "..."}}, ...]}} with one item per text.

{texts}"""

BATCH_SIZE = 5


# --- Collecting the texts ------------------------------------------------------------------------------


def collect(ctx) -> list[dict]:
    """Every answer of the extended runs and every recent insight, with what is needed to check it."""
    items = []
    for run in RUNS:
        for line in (RESULTS / run / "results.jsonl").read_text().splitlines():
            record = json.loads(line)
            items.append({"id": f"{run}/{record['case']}/{record['condition']}", "source": "answer",
                          "condition": record["condition"], "category": record["category"], "text": record["answer"]})
    for insight in ctx.insights_repo.list():
        if insight.scan_id in SCANS_ON_CURRENT_DATA:
            text = ". ".join([insight.headline, insight.explanation, *(e["statement"] for e in insight.evidence)])
            items.append({"id": f"insight/{insight.id}", "source": "insight", "condition": "insight",
                          "category": "insight", "text": text,
                          "subject_type": insight.subject_type, "subject_id": insight.subject_id})
    return items


class Checker:
    """Runs the claim checker on a text, with each product's facts looked up once."""

    def __init__(self, ctx):
        self._checker = RecommendationChecker(ctx.analytics, ctx.suppliers)
        self.product = lru_cache(None)(self._product)
        self.supplier = lru_cache(None)(self._supplier)

    def _product(self, product_id):
        try:
            return self._checker.product_facts(product_id)
        except Exception:
            return None

    def _supplier(self, supplier_id):
        try:
            return self._checker.supplier_facts(supplier_id)
        except Exception:
            return None

    def claims(self, item: dict, text: str | None = None) -> list[C.Claim]:
        text = item["text"] if text is None else text
        if item["source"] == "insight":
            if item["subject_type"] == "product":
                facts = self.product(item["subject_id"])
                return C.check_subject(text, item["subject_id"], facts, (facts or {}).get("supplier"))
            return C.check_subject(text, item["subject_id"], None, self.supplier(item["subject_id"]))
        return C.check_answer(text, self.product)


def contradictions(claims: list[C.Claim]) -> list[str]:
    return [claim.describe() for claim in claims if claim.status == "contradicted"]


# --- Asking the model for rewrites -----------------------------------------------------------------------


def ask_model(prompt: str) -> dict:
    """One JSON reply from the configured Gemini model, waiting out per-minute limits."""
    from google import genai
    from google.genai import errors as genai_errors
    from google.genai import types as genai_types

    from app.core.config import get_settings
    from app.core.exceptions import ServiceUnavailableError
    from app.llm.providers import quota_wait_seconds

    settings = get_settings()
    client = genai.Client(api_key=settings.gemini_api_key)
    model = settings.llm_model or "gemini-3.5-flash-lite"
    for attempt in range(8):
        try:
            response = client.models.generate_content(
                model=model, contents=prompt,
                config=genai_types.GenerateContentConfig(response_mime_type="application/json", temperature=0.7),
            )
            data = json.loads(response.text)
            return {**data, "model": response.model_version or model}
        except genai_errors.APIError as error:
            wait = quota_wait_seconds(error)
            if wait is None and error.code in (500, 502, 503, 504) and attempt < 7:
                wait = 20 * (attempt + 1)  # overloaded: usually passes within a minute or two
            if wait is None:
                raise ServiceUnavailableError(f"Model unavailable: {str(error)[:200]}") from error
            time.sleep(wait)
        except (json.JSONDecodeError, TypeError):
            continue
        except Exception as error:  # network failures come through from the HTTP library
            if attempt == 7:
                raise ServiceUnavailableError(f"Could not reach the model: {str(error)[:120]}") from error
            time.sleep(15)  # a dropped connection usually comes back within seconds
    raise ServiceUnavailableError("No usable reply after several attempts.")


def sample(items: list[dict], checker: Checker) -> list[dict]:
    """The texts that discuss a product (named by ID), in a seeded random order. The selection does not
    depend on the checker, so it is the same for every version of it."""
    eligible = [item for item in items if PRODUCT_ID.search(item["text"])]
    seen, unique = set(), []
    for item in eligible:  # identical answers from repeated runs count once
        if item["text"] not in seen:
            seen.add(item["text"])
            unique.append(item)
    random.Random(SEED).shuffle(unique)
    return unique


def perturb_batched(limit: int, offset: int = 0, set_name: str = "perturbations") -> None:
    """Like perturb, but asks for both rewrites of BATCH_SIZE texts in one request (about a tenth of the
    requests), for when the free tier's limits make one request per rewrite impractical."""
    OUT.mkdir(parents=True, exist_ok=True)
    file = OUT / f"{set_name}.jsonl"
    done = {(r["id"], r["kind"]) for r in map(json.loads, file.read_text().splitlines())} if file.exists() else set()
    from app.core.exceptions import ServiceUnavailableError

    with open_context() as ctx:
        chosen = sample(collect(ctx), Checker(ctx))[offset:offset + limit]
        todo = [item for item in chosen if (item["id"], "inject") not in done or (item["id"], "paraphrase") not in done]
        print(f"{len(todo)} texts to rewrite in batches of {BATCH_SIZE} ({len(chosen) - len(todo)} already done)")
        for start in range(0, len(todo), BATCH_SIZE):
            group = todo[start:start + BATCH_SIZE]
            labels = {f"T{i + 1}": item for i, item in enumerate(group)}
            texts = "\n\n".join(f"[{label}]\n{item['text']}" for label, item in labels.items())
            try:
                reply = ask_model(BATCH.format(count=len(group), texts=texts))
            except ServiceUnavailableError as error:
                print(f"Stopped: {error.message} Run again later to continue.")
                break
            records = []
            for entry in reply.get("items", []):
                item = labels.get(str(entry.get("id", "")).strip("[] "))
                if item is None:
                    continue
                injected = entry.get("injected") or {}
                if (item["id"], "inject") not in done and injected.get("rewritten"):
                    records.append({"id": item["id"], "kind": "inject", "original": item["text"], **injected,
                                    "model": reply.get("model"), "batched": True})
                if (item["id"], "paraphrase") not in done and entry.get("paraphrase"):
                    records.append({"id": item["id"], "kind": "paraphrase", "original": item["text"],
                                    "rewritten": entry["paraphrase"], "model": reply.get("model"), "batched": True})
            with file.open("a", encoding="utf-8") as handle:
                handle.writelines(json.dumps(record) + "\n" for record in records)
            done |= {(r["id"], r["kind"]) for r in records}
            print(f"batch {start // BATCH_SIZE + 1}: {len(records)} rewrites", flush=True)


def perturb(limit: int) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    file = OUT / "perturbations.jsonl"
    done = {(r["id"], r["kind"]) for r in map(json.loads, file.read_text().splitlines())} if file.exists() else set()
    from app.core.exceptions import ServiceUnavailableError

    with open_context() as ctx:
        checker = Checker(ctx)
        chosen = sample(collect(ctx), checker)[:limit]
        todo = [(item, kind) for item in chosen for kind in ("inject", "paraphrase") if (item["id"], kind) not in done]
        print(f"{len(todo)} rewrites to ask for ({len(done)} already done) from {len(chosen)} texts")
        for item, kind in todo:
            prompt = (INJECT if kind == "inject" else PARAPHRASE).format(text=item["text"])
            try:
                reply = ask_model(prompt)
            except ServiceUnavailableError as error:
                print(f"Stopped: {error.message} Run again later to continue.")
                break
            record = {"id": item["id"], "kind": kind, "original": item["text"], **reply}
            with file.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record) + "\n")
            print(f"{kind:10s} {item['id']}", flush=True)


# --- Report ------------------------------------------------------------------------------------------------


def rate(part: int, whole: int) -> str:
    if not whole:
        return "-"
    low, high = wilson_interval(part, whole)
    return f"{part} of {whole} ({part / whole:.0%}, 95% CI {low:.0%}-{high:.0%})"


def valid_injection(record: dict) -> bool:
    """The model said what it changed, the original words were there, and the new words replaced them."""
    before, after = str(record.get("changed_from", "")).strip(), str(record.get("changed_to", "")).strip()
    rewritten = str(record.get("rewritten", ""))
    return (bool(before) and bool(after) and before.lower() != after.lower()
            and before.lower() in record["original"].lower() and after.lower() in rewritten.lower())


def report(set_name: str = "perturbations") -> Path:
    with open_context() as ctx:
        checker = Checker(ctx)
        items = collect(ctx)
        by_id = {item["id"]: item for item in items}

        # A. real text
        claims_by_source = defaultdict(list)
        for item in items:
            claims_by_source[item["condition"]].append(checker.claims(item))
        lines = ["# Claim-level verification: evaluation", "",
                 "See `evaluation/claims_eval.py` for the method. Part A is the development set (the patterns were "
                 "written while reading it); part B is the test.", "",
                 "## A. Real answers and insights (development set)", "",
                 "| Source | Texts | Texts with a claim | Claims checked | Contradicted | Unverifiable |", "|---|---:|---:|---:|---:|---:|"]
        kinds = Counter()
        for source, per_text in claims_by_source.items():
            flat = [claim for text_claims in per_text for claim in text_claims]
            kinds.update((claim.kind, claim.status) for claim in flat)
            lines.append(f"| {source} | {len(per_text)} | {sum(bool(c) for c in per_text)} "
                         f"| {sum(c.status != 'unverifiable' for c in flat)} | {sum(c.status == 'contradicted' for c in flat)} "
                         f"| {sum(c.status == 'unverifiable' for c in flat)} |")
        lines += ["", "| Kind of claim | Supported | Contradicted | Unverifiable |", "|---|---:|---:|---:|"]
        for kind in sorted({k for k, _ in kinds}):
            lines.append(f"| {kind} | {kinds[(kind, 'supported')]} | {kinds[(kind, 'contradicted')]} | {kinds[(kind, 'unverifiable')]} |")

        # B. perturbations
        file = OUT / f"{set_name}.jsonl"
        records = [json.loads(line) for line in file.read_text().splitlines()] if file.exists() else []
        injections = [r for r in records if r["kind"] == "inject"]
        paraphrases = [r for r in records if r["kind"] == "paraphrase"]
        valid = [r for r in injections if valid_injection(r)]
        detected, missed = [], []
        def new_contradictions(record: dict) -> list[str]:
            """Contradictions in the rewrite that the original did not already have (by claim kind and verdict)."""
            item = by_id[record["id"]]
            before = Counter((c.kind, c.actual) for c in checker.claims(item) if c.status == "contradicted")
            after = [c for c in checker.claims(item, record.get("rewritten", "")) if c.status == "contradicted"]
            fresh = []
            for claim in after:
                if before[(claim.kind, claim.actual)]:
                    before[(claim.kind, claim.actual)] -= 1
                else:
                    fresh.append(claim.describe())
            return fresh

        for record in valid:
            found = new_contradictions(record)
            (detected if found else missed).append({**record, "flagged": found})
        alarms = []
        for record in paraphrases:
            found = new_contradictions(record)
            if found:
                alarms.append({**record, "flagged": found})
        models = Counter(r.get("model") for r in records)

        lines += ["", "## B. Model-written perturbations (test set)", ""]
        if not records:
            lines += ["Not run yet: `python -m evaluation.claims_eval perturb`."]
        else:
            lines += [f"{len({r['id'] for r in records})} texts; rewrites by {', '.join(f'{m} ({n})' for m, n in models.items())}.", "",
                      "| Measure | Result |", "|---|---|",
                      f"| Valid injected errors (the model's change is visible in the text) | {len(valid)} of {len(injections)} |",
                      f"| **Injected errors detected** | **{rate(len(detected), len(valid))}** |",
                      f"| **False alarms on paraphrases** | **{rate(len(alarms), len(paraphrases))}** |"]
            claim_counts = [len([c for c in checker.claims(by_id[r['id']], r.get('rewritten', '')) if c.status != 'unverifiable'])
                            for r in paraphrases]
            original_counts = [len([c for c in checker.claims(by_id[r['id']]) if c.status != 'unverifiable']) for r in paraphrases]
            if paraphrases:
                lines += [f"| Claims recognised in the paraphrases, against the originals | {sum(claim_counts)} against {sum(original_counts)} |"]
            lines += ["", "### Missed injected errors", ""]
            lines += [f"- **{r['id']}**: \"{r['changed_from']}\" -> \"{r['changed_to']}\"" for r in missed] or ["None."]
            lines += ["", "### False alarms", ""]
            lines += [f"- **{r['id']}**: {'; '.join(r['flagged'])}" for r in alarms] or ["None."]
            lines += ["", "### Detected injected errors", ""]
            lines += [f"- **{r['id']}**: \"{r['changed_from']}\" -> \"{r['changed_to']}\" | flagged: {'; '.join(r['flagged'])}"
                      for r in detected] or ["None."]
            invalid = [r for r in injections if not valid_injection(r)]
            lines += ["", "### Injections not counted (the change could not be located)", ""]
            lines += [f"- **{r['id']}**: \"{r.get('changed_from', '')}\" -> \"{r.get('changed_to', '')}\"" for r in invalid] or ["None."]

    lines += ["", "## How to read this", "",
              "- A missed injected error is one the checker does not flag: either the claim is worded in a way no "
              "pattern recognises, or it is of a kind the checker does not cover (for example a changed customer name).",
              "- The patterns were developed on part A. Part B's texts were written by the model, so their wording "
              "was not seen while the patterns were written.",
              "- Intervals are Wilson 95% intervals over the texts tested."]
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / ("report.md" if set_name == "perturbations" else f"report-{set_name}.md")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate claim-level verification.")
    parser.add_argument("step", choices=["collect", "perturb", "perturb-batched", "report"])
    parser.add_argument("--limit", type=int, default=60, help="texts to perturb")
    parser.add_argument("--offset", type=int, default=0, help="skip this many texts of the seeded sample (a fresh test set)")
    parser.add_argument("--set", default="perturbations", help="name of the rewrite file in results/claims/")
    args = parser.parse_args()
    if args.step == "perturb":
        perturb(args.limit)
    elif args.step == "perturb-batched":
        perturb_batched(args.limit, args.offset, args.set)
    print(report(args.set))


if __name__ == "__main__":
    main()

"""Evaluation of TRACE (Backend/app/llm/trace).

    ../Backend/.venv/bin/python -m evaluation.trace_eval extract            # model calls, cached; resumable
    ../Backend/.venv/bin/python -m evaluation.trace_eval dev                # report on the development sets

Development sets: the three rewrite sets made for the version-2 and version-3 claim checkers
(results/claims/perturbations-v2-test.jsonl, test-v3.jsonl, test-v3b.jsonl). They were held-out tests
for those checkers; for TRACE they are development data, because TRACE's design (its assertion
families) was drawn from what the version-3 checker missed on them. TRACE's own test uses new texts.

Every rewrite is judged on the same items by four methods: the frozen version-3 patterns, TRACE-rule,
TRACE-model and TRACE-hybrid. A detection is a contradiction in the rewrite that the original did not
have (same attribute, subject and true value); a false alarm is such a contradiction in a paraphrase.

Model extractions are cached in results/trace/extractions.jsonl, keyed by the prompt version, the model
and the text, so a rerun never asks for the same extraction twice and every verdict can be audited.
Run the extraction with one model and no fallback, so that all extractions come from the same model:

    LLM_MODEL=gemini-3.5-flash-lite LLM_FALLBACK_MODEL= ../Backend/.venv/bin/python -m evaluation.trace_eval extract
"""
import argparse
import hashlib
import json
import sys
import time
from collections import Counter
from pathlib import Path

from evaluation.claims_eval import OUT as CLAIMS_OUT
from evaluation.claims_eval import RESULTS, Checker, collect, rate, valid_injection
from evaluation.context import open_context

from app.llm.recommendations import RecommendationChecker
from app.llm.trace import FactSource, TraceVerifier
from app.llm.trace.extract_llm import PROMPT_VERSION, Extraction, extract
from app.llm.trace.schema import Assertion

OUT = RESULTS / "trace"
CACHE = OUT / "extractions.jsonl"
DEV_SETS = ("perturbations-v2-test", "test-v3", "test-v3b")
METHODS = ("v3 patterns", "TRACE-rule", "TRACE-model", "TRACE-hybrid")
# Injections judged in scope of the version-3 checker, by number (see the review files). v2 numbers count
# the valid injections only; v3 and v3b count all injections in file order.
SCOPE = {
    "perturbations-v2-test": ("valid", {7, 8, 9, 10, 12, 17, 19, 20, 21, 22, 24, 26, 29, 30, 32, 33, 37, 41, 42, 47,
                                        50, 53, 57, 58, 59}),
    "test-v3": ("all", {1, 2, 8, 9, 11, 12, 15, 19, 22, 23, 24, 28, 30, 32, 34, 36, 37, 38, 39, 40, 41, 42, 43, 47,
                        48, 51, 52, 53, 57, 59, 60}),
    "test-v3b": ("all", {2, 7, 11, 14, 21, 22, 23, 24, 27, 28, 29, 32, 33, 34, 37, 41, 43, 44, 46, 48, 52, 55, 61,
                         25, 26, 39, 47, 56, 59, 60, 63}),
}


class DailyLimit(Exception):
    pass


class Cache:
    def __init__(self, path: Path = CACHE):
        self.path = path
        self.records: dict[str, dict] = {}
        if path.exists():
            for line in path.read_text().splitlines():
                record = json.loads(line)
                self.records[record["key"]] = record

    @staticmethod
    def key(model: str, text: str) -> str:
        return hashlib.sha256(f"{PROMPT_VERSION}\n{model}\n{text}".encode()).hexdigest()

    def get(self, model: str, text: str) -> Extraction | None:
        record = self.records.get(self.key(model, text))
        if record is None:
            return None
        return Extraction([Assertion.model_validate(item) for item in record["assertions"]], record["invalid"], None,
                          record["model"], record["input_tokens"], record["output_tokens"])

    def put(self, model: str, text: str, extraction: Extraction) -> None:
        record = {"key": self.key(model, text), "prompt_version": PROMPT_VERSION, "requested_model": model,
                  "model": extraction.model, "invalid": extraction.invalid, "input_tokens": extraction.input_tokens,
                  "output_tokens": extraction.output_tokens,
                  "assertions": [a.model_dump(exclude_none=True) for a in extraction.assertions]}
        self.records[record["key"]] = record
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a") as handle:
            handle.write(json.dumps(record) + "\n")


def load_set(name: str) -> list[dict]:
    return [json.loads(line) for line in (CLAIMS_OUT / f"{name}.jsonl").read_text().splitlines()]


def texts_to_extract(items_by_id: dict, sets=DEV_SETS) -> list[str]:
    """Every distinct text the development report needs: each rewrite and the original it came from."""
    texts = []
    for name in sets:
        for record in load_set(name):
            texts += [items_by_id[record["id"]]["text"], record.get("rewritten", "")]
    return [text for text in dict.fromkeys(texts) if text]


def run_extraction(ctx, texts: list[str], cache: Cache) -> None:
    provider = ctx.provider
    model = provider.model
    todo = [text for text in texts if cache.get(model, text) is None]
    print(f"{len(texts)} texts, {len(todo)} to extract with {model} (prompt {PROMPT_VERSION})", flush=True)
    for index, text in enumerate(todo, 1):
        for attempt in range(4):
            extraction = extract(provider, text)
            if extraction.ok or not extraction.error:
                break
            if "daily limit" in extraction.error:
                raise DailyLimit(extraction.error)
            # Overloaded, a per-minute limit or a dropped connection: these pass within a minute or two.
            time.sleep(60 * (attempt + 1))
        if not extraction.ok:
            print(f"  failed ({extraction.error}); will retry on the next run", flush=True)
            continue
        if extraction.model and model not in extraction.model:
            print(f"  answered by {extraction.model}, not {model}: not cached", flush=True)
            continue
        cache.put(model, text, extraction)
        if index % 10 == 0:
            print(f"  {index} of {len(todo)}", flush=True)


_SHARED: dict = {}


class _CachingChecker(RecommendationChecker):
    """Product and supplier facts computed once per evaluation: each computation reads every sales line."""

    def __init__(self, *args):
        super().__init__(*args)
        self._product_cache, self._supplier_cache = {}, {}

    def product_facts(self, product_id):
        if product_id not in self._product_cache:
            try:
                self._product_cache[product_id] = ("ok", super().product_facts(product_id))
            except Exception as error:  # re-raised on every later call, as the uncached checker would
                self._product_cache[product_id] = ("error", error)
        kind, value = self._product_cache[product_id]
        if kind == "error":
            raise value
        return value

    def supplier_facts(self, supplier_id):
        if supplier_id not in self._supplier_cache:
            try:
                self._supplier_cache[supplier_id] = ("ok", super().supplier_facts(supplier_id))
            except Exception as error:
                self._supplier_cache[supplier_id] = ("error", error)
        kind, value = self._supplier_cache[supplier_id]
        if kind == "error":
            raise value
        return value


def _verifier(ctx, mode: str) -> TraceVerifier:
    """A fresh verifier per text (its per-answer product limit must start empty), sharing one source of
    truth: the data does not change during an evaluation, so its lookups are reused."""
    if "source" not in _SHARED:
        _SHARED["source"] = FactSource(ctx.analytics, ctx.products, ctx.suppliers, ctx.inventory, ctx.procurement,
                                       ctx.sales, ctx.clock)
        _SHARED["checker"] = _CachingChecker(ctx.analytics, ctx.suppliers)
    return TraceVerifier(_SHARED["source"], _SHARED["checker"], None, mode)


def judge_all(ctx, item: dict, text: str, cache: Cache, model: str) -> dict[str, list] | None:
    """Contradicted verdict keys for each method, or None if the model extraction is missing."""
    subject = (item["subject_type"], item["subject_id"]) if item["source"] == "insight" else None
    extraction = cache.get(model, text)
    if extraction is None:
        return None
    result = {"v3 patterns": [(c.kind, c.subject_id, c.actual) for c in _v3(ctx).claims(item, text) if c.status == "contradicted"]}
    for method, mode in (("TRACE-rule", "rule"), ("TRACE-model", "model"), ("TRACE-hybrid", "hybrid")):
        verdicts = _verifier(ctx, mode).check(text, subject, extraction=extraction if mode != "rule" else None).contradicted()
        result[method] = [verdict.key() for verdict in verdicts]
        result[f"{method} detail"] = [verdict.as_dict() for verdict in verdicts]
    return result


_V3_CHECKER = {}


def _v3(ctx) -> Checker:
    if "checker" not in _V3_CHECKER:
        _V3_CHECKER["checker"] = Checker(ctx)
    return _V3_CHECKER["checker"]


def new(before: list, after: list) -> list:
    """Contradictions in `after` that `before` does not already have (by key, counting repeats)."""
    remaining = Counter(map(tuple, before))
    fresh = []
    for key in map(tuple, after):
        if remaining[key]:
            remaining[key] -= 1
        else:
            fresh.append(key)
    return fresh


def dev_report(ctx, cache: Cache, model: str) -> Path:
    items_by_id = {item["id"]: item for item in collect(ctx)}
    lines = ["# TRACE on the development sets", "",
             f"Extraction: {model}, prompt {PROMPT_VERSION}. A detection is a contradiction the rewrite introduced; "
             "a false alarm is one a paraphrase introduced. In-scope means within the version-3 checker's claim kinds "
             "(hand classification in results/claims).", ""]
    detail_lines = ["# TRACE development details", ""]
    totals = {method: Counter() for method in METHODS}
    for name in DEV_SETS:
        records = load_set(name)
        counting, in_scope_numbers = SCOPE[name]
        per = {method: Counter() for method in METHODS}
        injections = [r for r in records if r["kind"] == "inject"]
        valid_position = 0
        missing = 0
        for position, record in enumerate(injections, 1):
            if not valid_injection(record):
                continue
            valid_position += 1
            number = valid_position if counting == "valid" else position
            scoped = number in in_scope_numbers
            item = items_by_id[record["id"]]
            before, after = judge_all(ctx, item, item["text"], cache, model), judge_all(ctx, item, record["rewritten"], cache, model)
            if before is None or after is None:
                missing += 1
                continue
            for method in METHODS:
                hit = bool(new(before[method], after[method]))
                per[method]["valid"] += 1
                per[method]["detected"] += hit
                per[method]["in_scope"] += scoped
                per[method]["in_scope_detected"] += hit and scoped
            if not new(before["TRACE-hybrid"], after["TRACE-hybrid"]):
                detail_lines.append(f"- MISS {name} #{number}{' (in scope)' if scoped else ''} {record['id']}: "
                                    f"\"{record.get('changed_from', '')}\" -> \"{record.get('changed_to', '')}\"")
        for record in (r for r in records if r["kind"] == "paraphrase"):
            item = items_by_id[record["id"]]
            before, after = judge_all(ctx, item, item["text"], cache, model), judge_all(ctx, item, record["rewritten"], cache, model)
            if before is None or after is None:
                missing += 1
                continue
            for method in METHODS:
                alarm = new(before[method], after[method])
                per[method]["paraphrases"] += 1
                per[method]["false_alarms"] += bool(alarm)
            if (alarm := new(before["TRACE-hybrid"], after["TRACE-hybrid"])):
                details = [d for d in after["TRACE-hybrid detail"] if (d["attribute"], d["subject"], d["actual"]) in alarm]
                detail_lines.append(f"- FALSE ALARM {name} {record['id']}: " + "; ".join(
                    f"[{d['source']}] {d['attribute']} {d['subject']} {d['asserted']} vs {d['actual']} \"{d['quote'][:80]}\""
                    for d in details))
        lines += [f"## {name}" + (f" ({missing} items without extraction, left out)" if missing else ""), "",
                  "| Method | Detected, all valid | Detected, in scope | False alarms |", "|---|---:|---:|---:|"]
        for method in METHODS:
            c = per[method]
            totals[method].update(c)
            lines.append(f"| {method} | {rate(c['detected'], c['valid'])} | {rate(c['in_scope_detected'], c['in_scope'])} "
                         f"| {rate(c['false_alarms'], c['paraphrases'])} |")
        lines.append("")
    lines += ["## All three sets", "", "| Method | Detected, all valid | Detected, in scope | False alarms |", "|---|---:|---:|---:|"]
    for method in METHODS:
        c = totals[method]
        lines.append(f"| {method} | {rate(c['detected'], c['valid'])} | {rate(c['in_scope_detected'], c['in_scope'])} "
                     f"| {rate(c['false_alarms'], c['paraphrases'])} |")
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "dev-report.md").write_text("\n".join(lines) + "\n")
    (OUT / "dev-details.md").write_text("\n".join(detail_lines) + "\n")
    print("\n".join(lines[-7:]))
    return OUT / "dev-report.md"


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate TRACE.")
    parser.add_argument("step", choices=["extract", "dev"])
    args = parser.parse_args()
    cache = Cache()
    with open_context() as ctx:
        model = ctx.provider.model if ctx.provider else "none"
        if args.step == "extract":
            items_by_id = {item["id"]: item for item in collect(ctx)}
            try:
                run_extraction(ctx, texts_to_extract(items_by_id), cache)
            except DailyLimit as error:
                print(f"Stopped: {error}")
                sys.exit(3)
        else:
            print(dev_report(ctx, cache, model))


if __name__ == "__main__":
    main()

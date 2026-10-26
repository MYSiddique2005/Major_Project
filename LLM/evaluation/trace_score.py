"""Scoring TRACE and the baselines on the held-out test (results/trace/heldout-<writer>.jsonl).

    LLM_MODEL=gemini-3.5-flash-lite LLM_FALLBACK_MODEL= ../Backend/.venv/bin/python -m evaluation.trace_score extract
    ../Backend/.venv/bin/python -m evaluation.trace_score report

The scoring rules below were written before the held-out rewrites were generated, and are the same for
every method, so no method is scored on its own terms:

  valid injection  the writer reported the words it changed, the old words are in the original and the new
                   words in the rewrite (the rule of the version-3 tests)
  detection        attributed: the method reports more contradicted statements inside the sentence that holds
                   the changed words than inside the matching sentence of the original. A contradiction found
                   elsewhere in the text is not a detection of the planted error.
  false alarm      the method reports more contradicted statements in the paraphrase than in its original
  paired test      McNemar's exact test between TRACE-hybrid and each other method on the injections both
                   judged, with Holm's correction over the comparisons

A statement is placed by its quote: exactly where the quote occurs in the text, otherwise in the sentence
sharing most of its words (at least 60% of them); a quote that cannot be placed counts for the whole text,
which can only help a method on false alarms, never on detection.

The report refuses to run if TRACE's files differ from the hashes in results/trace/frozen.json.
"""
import argparse
import hashlib
import json
import re
import time
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from math import comb
from pathlib import Path

from evaluation.claims_eval import RESULTS, rate, valid_injection
from evaluation.context import open_context
from evaluation.trace_eval import Cache, DailyLimit, _v3, _verifier, run_extraction
from evaluation.trace_baselines import JudgeCache, minicheck_quotes

from app.llm.trace.engine import _one_per_statement
from app.llm.trace.extract_llm import PROMPT_VERSION

OUT = RESULTS / "trace"
WRITERS = ("gemini", "gemma")
EXTRACTION_MODEL = "gemini-3.5-flash-lite"
JUDGE_MODELS = ("gemini-3.5-flash-lite", "gemma-4-31b-it")
TRACE_METHODS = ("TRACE-rule", "TRACE-model", "TRACE-hybrid")
_SENTENCE_END = re.compile(r"(?<=[.!?])\s+(?=[A-Z\"(\-])|\n+")
_ABBREVIATION = re.compile(r"\b(?:Inc|Ltd|Co|Corp|Corporation|vs|approx|No|e\.g|i\.e)\.$", re.IGNORECASE)
_WORD = re.compile(r"[a-z0-9]+(?:[.,'-][a-z0-9]+)*")


# --- where a statement is ----------------------------------------------------------------------------------


def sentences(text: str) -> list[tuple[int, int]]:
    """(start, end) of each sentence; numbers such as 1.6 and 2,775 are not split."""
    spans, start = [], 0
    for match in _SENTENCE_END.finditer(text):
        if match.start() > start:
            spans.append((start, match.start()))
        start = match.end()
    if start < len(text):
        spans.append((start, len(text)))
    merged: list[tuple[int, int]] = []
    for span in spans:  # "Fabrikam, Inc. (S004)" is one sentence
        if merged and _ABBREVIATION.search(text[merged[-1][0]:merged[-1][1]]) and "\n" not in text[merged[-1][1]:span[0]]:
            merged[-1] = (merged[-1][0], span[1])
        else:
            merged.append(span)
    return merged or [(0, len(text))]


def _words(text: str) -> list[str]:
    return _WORD.findall(text.lower())


def place(quote: str, text: str) -> tuple[int, int] | None:
    """The span of the text a quote refers to, or None when it cannot be placed."""
    quote = " ".join(quote.split())
    if not quote:
        return None
    flat = re.sub(r"\s+", " ", text)
    if len(flat) == len(text):  # spacing unchanged, so positions in `flat` are positions in `text`
        index = flat.lower().find(quote.lower())
        if index >= 0:
            return index, index + len(quote)
    wanted = set(_words(quote))
    if not wanted:
        return None
    best, best_share = None, 0.0
    for start, end in sentences(text):
        share = len(wanted & set(_words(text[start:end]))) / len(wanted)
        if share > best_share:
            best, best_share = (start, end), share
    return best if best_share >= 0.6 else None


def sentence_of(words: str, text: str) -> tuple[int, int] | None:
    """The sentence holding the first occurrence of `words`."""
    index = text.lower().find(words.lower())
    if index < 0:
        return None
    for start, end in sentences(text):
        if index < end:  # in this sentence, or in the space just before it
            return start, end
    return None


def changed_windows(record: dict) -> tuple[tuple[int, int] | None, tuple[int, int] | None]:
    """The sentence of the original and of the rewrite that the planted change is in. Found by comparing the
    two texts, so that new words which also occur elsewhere ("3,758.8" twice) point to the right sentence;
    the first occurrence of the reported words is the fallback."""
    original, rewritten = record["original"], record["rewritten"]
    opcodes = [op for op in SequenceMatcher(None, original, rewritten, autojunk=False).get_opcodes() if op[0] != "equal"]
    if opcodes:
        first_i, first_j = opcodes[0][1], opcodes[0][3]
        last_j = max(op[4] for op in opcodes)
        if last_j - first_j <= max(len(record["changed_to"]), len(record["changed_from"])) * 3 + 40:  # one local change
            return _sentence_at(original, first_i), _sentence_at(rewritten, first_j)
    return sentence_of(record["changed_from"], original), sentence_of(record["changed_to"], rewritten)


def _sentence_at(text: str, index: int) -> tuple[int, int] | None:
    for start, end in sentences(text):
        if index < end:
            return start, end
    return None


def inside(quotes: list[str], text: str, window: tuple[int, int] | None) -> int:
    """How many quotes lie in the window (all of them when there is no window)."""
    if window is None:
        return len(quotes)
    count = 0
    for quote in quotes:
        span = place(quote, text)
        if span is None or (span[0] < window[1] and span[1] > window[0]):
            count += 1
    return count


# --- what each method reports --------------------------------------------------------------------------------


class Methods:
    """Contradicted quotes per method for a text, with each method's own counting of statements."""

    def __init__(self, ctx, extractions: Cache, judges: JudgeCache):
        self.ctx, self.extractions, self.judges = ctx, extractions, judges
        self._memo: dict[tuple[str, str], dict] = {}

    def names(self) -> list[str]:
        return ["v3 patterns", *TRACE_METHODS, *(f"LLM judge ({model})" for model in JUDGE_MODELS), "MiniCheck"]

    def of(self, item: dict, text: str) -> dict[str, list[str] | None]:
        key = (item["id"], text)
        if key not in self._memo:
            self._memo[key] = self._compute(item, text)
        return self._memo[key]

    def _compute(self, item: dict, text: str) -> dict[str, list[str] | None]:
        subject = (item["subject_type"], item["subject_id"]) if item.get("source") == "insight" else None
        seen, v3 = set(), []
        for claim in _v3(self.ctx).claims(item, text):
            if claim.status == "contradicted" and (claim.kind, claim.subject_id, claim.asserted) not in seen:
                seen.add((claim.kind, claim.subject_id, claim.asserted))
                v3.append(claim.matched)
        result: dict[str, list[str] | None] = {"v3 patterns": v3}
        extraction = self.extractions.get(EXTRACTION_MODEL, text)
        for method, mode in zip(TRACE_METHODS, ("rule", "model", "hybrid")):
            if mode != "rule" and extraction is None:
                result[method] = None
                continue
            verdicts = _verifier(self.ctx, mode).check(text, subject, extraction=extraction if mode != "rule" else None)
            result[method] = [verdict.quote for verdict in _one_per_statement(verdicts.contradicted())]
            if mode == "hybrid":
                result["TRACE-hybrid verdicts"] = verdicts.verdicts
        for model in JUDGE_MODELS:
            items = self.judges.get(model, 0, text)
            result[f"LLM judge ({model})"] = None if items is None else [entry["quote"] for entry in items]
        result["MiniCheck"] = minicheck_quotes(text)
        return result


# --- statistics ------------------------------------------------------------------------------------------------


def mcnemar(only_first: int, only_second: int) -> float:
    """Two-sided exact McNemar p-value from the discordant pairs."""
    n = only_first + only_second
    if n == 0:
        return 1.0
    tail = sum(comb(n, k) for k in range(min(only_first, only_second) + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def holm(p_values: dict[str, float]) -> dict[str, float]:
    ordered = sorted(p_values.items(), key=lambda entry: entry[1])
    adjusted, running = {}, 0.0
    for rank, (name, p) in enumerate(ordered):
        running = max(running, min(1.0, p * (len(ordered) - rank)))
        adjusted[name] = running
    return adjusted


# --- the report -------------------------------------------------------------------------------------------------


def check_frozen() -> None:
    frozen_path = OUT / "frozen.json"
    if not frozen_path.exists():
        raise SystemExit("TRACE is not frozen: run evaluation.trace_testset freeze before generating the test.")
    frozen = json.loads(frozen_path.read_text())
    root = Path(__file__).resolve().parents[2]
    changed = [name for name, digest in frozen.items() if name != "frozen_at"
               and hashlib.sha256((root / "Backend" / name).read_bytes()).hexdigest() != digest]
    if changed:
        raise SystemExit(f"TRACE changed after it was frozen: {', '.join(changed)}")


def load(writer: str) -> list[dict]:
    path = OUT / f"heldout-{writer}.jsonl"
    return [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []


def pool_items() -> dict[str, dict]:
    return {item["id"]: item for item in map(json.loads, (OUT / "heldout-pool.jsonl").read_text().splitlines())}


def miss_reason(verdicts, text: str, window) -> str:
    """Why TRACE-hybrid missed: nothing extracted there, only unverifiable verdicts, or judged supported."""
    near = [v for v in verdicts if inside([v.quote], text, window) and place(v.quote, text) is not None]
    if not near:
        return "not extracted"
    if all(v.status == "unverifiable" for v in near):
        return "unverifiable: " + "; ".join(sorted({v.reason for v in near}))[:160]
    supported = [v for v in near if v.status == "supported"]
    return "judged supported: " + "; ".join(f"{v.attribute} {v.asserted}" for v in supported)[:160]


def report() -> Path:
    check_frozen()
    pool = pool_items()
    lines = ["# TRACE on the held-out test", "",
             f"Extraction: {EXTRACTION_MODEL}, prompt {PROMPT_VERSION}. Detection is attributed to the sentence "
             "that holds the planted error; a false alarm is a paraphrase with more contradicted statements than "
             "its original. Rules fixed before the test was generated (see evaluation/trace_score.py).", ""]
    details = ["# TRACE held-out details", ""]
    with open_context() as ctx:
        methods = Methods(ctx, Cache(), JudgeCache())
        names = methods.names()
        detected = {name: {} for name in names}  # name -> {(writer, id): bool}
        alarms = {name: Counter() for name in names}
        by_type = {name: defaultdict(Counter) for name in names}
        reasons = Counter()
        valid_count = Counter()
        for writer in WRITERS:
            for record in load(writer):
                item = pool[record["id"]]
                if record["kind"] == "inject":
                    if not valid_injection(record):
                        details.append(f"- INVALID {writer} {record['id']}: the reported change is not in the texts")
                        continue
                    valid_count[writer] += 1
                    error_type = record.get("error_type") or record.get("assigned_type") or "unknown"
                    before, after = methods.of(item, item["text"]), methods.of(item, record["rewritten"])
                    window_before, window_after = changed_windows(record)
                    for name in names:
                        if before[name] is None or after[name] is None:
                            continue
                        hit = (inside(after[name], record["rewritten"], window_after)
                               > inside(before[name], item["text"], window_before))
                        detected[name][(writer, record["id"])] = hit
                        by_type[name][error_type]["valid"] += 1
                        by_type[name][error_type]["detected"] += hit
                    if after.get("TRACE-hybrid") is not None and not detected["TRACE-hybrid"].get((writer, record["id"])):
                        reason = miss_reason(after["TRACE-hybrid verdicts"], record["rewritten"], window_after)
                        reasons[reason.split(":")[0]] += 1
                        details.append(f"- MISS {writer} {record['id']} [{error_type}] \"{record['changed_from']}\" -> "
                                       f"\"{record['changed_to']}\": {reason}")
                elif record["kind"] == "paraphrase" and record.get("rewritten"):
                    before, after = methods.of(item, item["text"]), methods.of(item, record["rewritten"])
                    for name in names:
                        if before[name] is None or after[name] is None:
                            continue
                        alarm = len(after[name]) > len(before[name])
                        alarms[name]["paraphrases"] += 1
                        alarms[name]["false_alarms"] += alarm
                        if alarm and name == "TRACE-hybrid":
                            details.append(f"- FALSE ALARM {writer} {record['id']}: "
                                           + "; ".join(q[:90] for q in after[name] if q not in before[name]))

        lines += [f"Valid injections: {sum(valid_count.values())} ({', '.join(f'{w}: {n}' for w, n in valid_count.items())}).", "",
                  "| Method | Detected (attributed) | False alarms on paraphrases |", "|---|---:|---:|"]
        for name in names:
            hits = detected[name]
            lines.append(f"| {name} | {rate(sum(hits.values()), len(hits))} | "
                         f"{rate(alarms[name]['false_alarms'], alarms[name]['paraphrases'])} |")

        lines += ["", "## By writer", "", "| Method | " + " | ".join(WRITERS) + " |", "|---|" + "---:|" * len(WRITERS)]
        for name in names:
            cells = []
            for writer in WRITERS:
                hits = [hit for (w, _), hit in detected[name].items() if w == writer]
                cells.append(rate(sum(hits), len(hits)))
            lines.append(f"| {name} | " + " | ".join(cells) + " |")

        types = sorted({t for name in names for t in by_type[name]})
        lines += ["", "## By error type (as the writer reported it)", "",
                  "| Method | " + " | ".join(types) + " |", "|---|" + "---:|" * len(types)]
        for name in names:
            lines.append(f"| {name} | " + " | ".join(
                rate(by_type[name][t]["detected"], by_type[name][t]["valid"]) for t in types) + " |")

        p_values, pairs = {}, {}
        for name in names:
            if name == "TRACE-hybrid":
                continue
            shared = set(detected["TRACE-hybrid"]) & set(detected[name])
            only_trace = sum(detected["TRACE-hybrid"][key] and not detected[name][key] for key in shared)
            only_other = sum(detected[name][key] and not detected["TRACE-hybrid"][key] for key in shared)
            p_values[name], pairs[name] = mcnemar(only_trace, only_other), (len(shared), only_trace, only_other)
        adjusted = holm(p_values)
        lines += ["", "## TRACE-hybrid against each method (McNemar exact, Holm-adjusted)", "",
                  "| Method | Injections both judged | Only TRACE-hybrid detected | Only the other detected | p (Holm) |",
                  "|---|---:|---:|---:|---:|"]
        for name, (shared, only_trace, only_other) in pairs.items():
            lines.append(f"| {name} | {shared} | {only_trace} | {only_other} | {adjusted[name]:.3g} |")

        total = sum(reasons.values())
        lines += ["", "## Why TRACE-hybrid missed (automatic first pass; checked by hand in the details)", "",
                  "| Reason | Misses |", "|---|---:|"]
        lines += [f"| {reason} | {count} of {total} |" for reason, count in reasons.most_common()]

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "heldout-report.md").write_text("\n".join(lines) + "\n")
    (OUT / "heldout-details.md").write_text("\n".join(details) + "\n")
    print("\n".join(lines))
    return OUT / "heldout-report.md"


def extract_all() -> None:
    pool = pool_items()
    texts = []
    for writer in WRITERS:
        for record in load(writer):
            texts += [pool[record["id"]]["text"], record.get("rewritten", "")]
    texts = [text for text in dict.fromkeys(texts) if text]
    with open_context() as ctx:
        try:
            run_extraction(ctx, texts, Cache())
        except DailyLimit as error:
            print(f"Daily limit reached ({error}); run again tomorrow.")
            raise SystemExit(3)


def main() -> None:
    parser = argparse.ArgumentParser(description="Score TRACE and the baselines on the held-out test.")
    parser.add_argument("step", choices=["extract", "report"])
    args = parser.parse_args()
    started = time.monotonic()
    extract_all() if args.step == "extract" else report()
    print(f"done in {time.monotonic() - started:.0f} s")


if __name__ == "__main__":
    main()

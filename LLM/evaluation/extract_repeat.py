"""Repeatability of TRACE end to end: a second extraction of the same 50 held-out texts the judge was repeated on.

    LLM_MODEL=gemini-3.5-flash-lite LLM_FALLBACK_MODEL= ../Backend/.venv/bin/python -m evaluation.extract_repeat extract
    ../Backend/.venv/bin/python -m evaluation.extract_repeat compare

The first extraction is the cached one every result uses (results/trace/extractions.jsonl); the second is made
with the same model and prompt into results/trace/extractions-repeat.jsonl. Both are verified by the frozen
TRACE-hybrid, and the comparison uses the measures reported for the LLM judge: the same flag decision, and the
same set of contradicted statements.
"""
import argparse

from evaluation.context import open_context
from evaluation.trace_eval import Cache, DailyLimit, run_extraction
from evaluation.trace_score import EXTRACTION_MODEL, OUT, _one_per_statement, _verifier, check_frozen, load, pool_items

REPEAT_CACHE = OUT / "extractions-repeat.jsonl"
N_TEXTS = 50


def texts_and_subjects() -> list[tuple[str, tuple | None]]:
    """The first 50 distinct held-out texts written by Gemini (the judge's repeat set), with each text's subject."""
    pool, pairs = pool_items(), []
    for record in load("gemini"):
        item = pool[record["id"]]
        subject = (item["subject_type"], item["subject_id"]) if item.get("source") == "insight" else None
        pairs += [(item["text"], subject), (record.get("rewritten", ""), subject)]
    return list(dict.fromkeys((text, subject) for text, subject in pairs if text))[:N_TEXTS]


def compare() -> None:
    check_frozen()
    first, second = Cache(), Cache(REPEAT_CACHE)
    same_flag = same_set = flagged_either = same_among_flagged = same_assertions = compared = 0
    with open_context() as ctx:
        verifier = _verifier(ctx, "hybrid")
        for text, subject in texts_and_subjects():
            a, b = first.get(EXTRACTION_MODEL, text), second.get(EXTRACTION_MODEL, text)
            if a is None or b is None:
                continue
            compared += 1
            same_assertions += sorted(x.model_dump_json() for x in a.assertions) == sorted(x.model_dump_json() for x in b.assertions)
            quotes = [{v.quote for v in _one_per_statement(verifier.check(text, subject, extraction=e).contradicted())}
                      for e in (a, b)]
            same_flag += bool(quotes[0]) == bool(quotes[1])
            same_set += quotes[0] == quotes[1]
            if quotes[0] or quotes[1]:
                flagged_either += 1
                same_among_flagged += quotes[0] == quotes[1]
    lines = ["# TRACE repeatability: two extractions of the same texts", "",
             f"Texts compared: {compared} (the judge's repeat set). Extraction: {EXTRACTION_MODEL}, verified by the frozen TRACE-hybrid.", "",
             f"- identical assertions: {same_assertions} of {compared}",
             f"- same flag decision: {same_flag} of {compared}",
             f"- same set of contradicted statements: {same_set} of {compared}",
             f"- among texts flagged in either run, same set: {same_among_flagged} of {flagged_either}"]
    (OUT / "repeat-extraction.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


def main() -> None:
    parser = argparse.ArgumentParser(description="Repeat TRACE's extraction on the judge's repeat set.")
    parser.add_argument("step", choices=["extract", "compare"])
    args = parser.parse_args()
    if args.step == "compare":
        compare()
        return
    with open_context() as ctx:
        try:
            run_extraction(ctx, [text for text, _ in texts_and_subjects()], Cache(REPEAT_CACHE))
        except DailyLimit as error:
            raise SystemExit(f"Daily limit reached ({error}); run again tomorrow.")


if __name__ == "__main__":
    main()

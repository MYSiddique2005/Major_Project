"""Harm check: the 86 evaluation questions with TRACE as the verifier (run trace-1) against the three runs of the
same model with the pattern verifier (fixed-1..3).

    ../Backend/.venv/bin/python -m evaluation.harm_report

Writes results/trace/harm-report.md: questions passed, McNemar's exact test against each earlier run, answers
TRACE sent back for correction and how they ended, contradictions still shown after correction, figures not
found in the data, and answer time. The first drafts of corrected answers are not stored, so whether a
correction fixed a real error can only be judged from the final answer and the earlier runs.
"""
import statistics

from evaluation.report import load
from evaluation.trace_score import OUT, mcnemar

EARLIER = ("fixed-1", "fixed-2", "fixed-3")


def grounded(name: str) -> dict[str, dict]:
    return {record["case"]: record for record in load(name) if record.get("condition") == "grounded"}


def passed(record: dict) -> bool:
    return record.get("status") == "ok" and bool(record["score"]["passed"])


def unsupported(record: dict) -> list[str]:
    return record["score"].get("unsupported_figures") or []


def main() -> None:
    trace, earlier = grounded("trace-1"), {name: grounded(name) for name in EARLIER}
    lines = ["# Harm check: the 86 questions with TRACE as the verifier", "",
             "Run trace-1 (gemini-3.5-flash-lite, TRACE) against runs fixed-1..3 (same model, pattern verifier).", "",
             "| Run | Passed | Figures not found in the data | Median seconds |", "|---|---:|---:|---:|"]
    for name, records in (("trace-1", trace), *earlier.items()):
        lines.append(f"| {name} | {sum(map(passed, records.values()))} of {len(records)} | "
                     f"{sum(len(unsupported(r)) for r in records.values())} of {sum(r['score'].get('figures') or 0 for r in records.values())} | "
                     f"{statistics.median(r.get('seconds') or 0 for r in records.values()):.1f} |")
    lines += ["", "| Compared with | Only trace-1 passed | Only the other passed | p |", "|---|---:|---:|---:|"]
    for name, records in earlier.items():
        shared = set(trace) & set(records)
        only_trace = sum(passed(trace[c]) and not passed(records[c]) for c in shared)
        only_other = sum(passed(records[c]) and not passed(trace[c]) for c in shared)
        lines.append(f"| {name} | {only_trace} | {only_other} | {mcnemar(only_trace, only_other):.3g} |")
    lines += ["", "## Answers TRACE sent back for correction", "",
              "| Question | Final answer | Figures not found in the data | Passed in fixed-1..3 |", "|---|---|---|---|"]
    for case, record in sorted(trace.items()):
        if (record.get("verification") or {}).get("corrected"):
            lines.append(f"| {case} | {'passed' if passed(record) else 'failed'} | {', '.join(unsupported(record)) or 'none'} | "
                         f"{sum(passed(records[case]) for records in earlier.values())} of 3 |")
    lines += ["", "## Contradictions still shown after correction", ""]
    lines += [f"- {case}: {'; '.join(record['contradicted_claims'])}" for case, record in sorted(trace.items())
              if record.get("contradicted_claims")] or ["- none"]
    lines += ["", "Failed in trace-1: " + ", ".join(f"{c} ({r.get('status')})" for c, r in sorted(trace.items()) if not passed(r))]
    path = OUT / "harm-report.md"
    path.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()

"""Applies the current answer key to answers already collected, for named questions.

    ../Backend/.venv/bin/python -m evaluation.rekey --name extended-1 --cases A14,U4,G8

Reading the answers sometimes shows that a key was wrong: it marked a correct answer as missing a
fact because of its wording, or passed a wrong answer because the words it looked for appeared for
another reason. The fix is to correct the key in cases.py and apply it to the stored answers of
every condition; the model is not asked again. This tool does only that, for the questions named,
keeps the key each answer was first scored with, and prints what changed. Record the reason in the
run's notes.md: a key changed after seeing answers must be visible to a reader.
"""
import argparse
import json
from dataclasses import asdict

from evaluation.cases import build_cases
from evaluation.context import open_context
from evaluation.report import RESULTS
from evaluation.scoring import Expectation, score


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply corrected keys to stored answers.")
    parser.add_argument("--name", required=True)
    parser.add_argument("--cases", required=True, help="comma-separated case ids whose key was corrected")
    args = parser.parse_args()
    wanted = {case.strip() for case in args.cases.split(",") if case.strip()}

    with open_context() as ctx:
        current = {case.id: asdict(case.expectation) for case in build_cases(ctx) if case.id in wanted}
    if missing := wanted - set(current):
        raise SystemExit(f"No such case: {sorted(missing)}")

    file = RESULTS / args.name / "results.jsonl"
    records = [json.loads(line) for line in file.read_text().splitlines() if line.strip()]
    for record in records:
        if record["case"] not in wanted or record["expected"] == current[record["case"]]:
            continue
        kept = record["score"]
        before = score(Expectation(**record["expected"]), record, (kept["figures"], kept["unsupported_figures"])).passed
        record.setdefault("expected_first", record["expected"])  # the key the answer was first scored with
        record["expected"] = current[record["case"]]
        after = score(Expectation(**record["expected"]), record, (kept["figures"], kept["unsupported_figures"]))
        record["score"] = {**kept, **asdict(after), "recall": after.recall}
        change = "unchanged" if before == after.passed else f"{'pass' if before else 'fail'} -> {'pass' if after.passed else 'FAIL'}"
        print(f"{record['case']:4s} {record['condition']:10s} {change}")
    file.write_text("".join(json.dumps(record, default=str) + "\n" for record in records), encoding="utf-8")

    from evaluation.report import write_report

    print(f"Report: {write_report(args.name)}")


if __name__ == "__main__":
    main()

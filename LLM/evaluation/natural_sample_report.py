"""The random sample of natural errors, by condition: how many sampled sentences are false.

Reads the sample (trace_natural step sample) and annotator 1's labels, and writes sample-report.md, listing every
false sentence with the words it gets wrong and what the evidence says. Labels corrected after all methods had run
are listed in label-corrections.jsonl and counted both ways.

    python -m evaluation.natural_sample_report
"""
import json
from collections import Counter
from pathlib import Path

OUT = Path(__file__).parent / "results" / "trace" / "natural"
LABELS = ("true", "false", "no-claim", "unsure")


def key(row: dict) -> tuple:
    return row["answer_id"], row["start"], row["end"]


def table(rows: list[dict], labels: dict) -> list[str]:
    groups = [("all", lambda a: True),
              ("with the knowledge base", lambda a: a.endswith("/grounded")),
              ("without the knowledge base", lambda a: a.endswith("/ungrounded")),
              ("Gemini runs (TRACE development answers)", lambda a: not a.startswith("gemma4-1/")),
              ("Gemma run (never seen in development)", lambda a: a.startswith("gemma4-1/"))]
    lines = ["| Answers | Sentences | true | false | no-claim | unsure | False among checkable |",
             "|---|---:|---:|---:|---:|---:|---:|"]
    for name, test in groups:
        chosen = [row for row in rows if test(row["answer_id"])]
        count = Counter(labels[key(row)] for row in chosen)
        checkable = count["true"] + count["false"]
        share = f"{count['false']}/{checkable} ({100 * count['false'] / checkable:.1f}%)" if checkable else "-"
        lines.append(f"| {name} | {len(chosen)} | " + " | ".join(str(count[label]) for label in LABELS) + f" | {share} |")
    return lines


def main() -> None:
    rows = [json.loads(line) for line in (OUT / "sample.jsonl").read_text().splitlines()]
    given = {key(row): row for row in map(json.loads, (OUT / "labels-annotator-1.jsonl").read_text().splitlines())}
    labels = {key(row): given[key(row)]["label"] for row in rows}
    corrections_path = OUT / "label-corrections.jsonl"
    corrections = [json.loads(line) for line in corrections_path.read_text().splitlines()] if corrections_path.exists() else []
    original = {**labels, **{key(c): c["old_label"] for c in corrections if key(c) in labels}}

    lines = ["# Natural errors: the random sample", "",
             "300 sentences drawn with seed 2026 from the 590 stored answers (evaluation/trace_natural.py, step sample), "
             "labelled before any method's output on them existed, by Claude Opus 5.5 following "
             "Research/trace/annotation-guide.md, with the system's rules and permissions (Backend/app/knowledge/content.py, "
             "Backend/app/security/permissions.py) as the reference for policy statements. Every label, with the wrong "
             "words and the evidence it rests on, is in labels-annotator-1.jsonl. A human second annotation has not been done.",
             "", *table(rows, labels), ""]
    in_sample = [c for c in corrections if key(c) in labels]
    if in_sample:
        lines += ["## Before the label corrections", "",
                  f"After all methods had run, a consistency check, prompted while labelling the sentences MiniCheck flagged, found "
                  f"{len(corrections)} sentences labelled true that "
                  f"state overdue units as part of the units on order; in the system they are separate amounts "
                  f"(Backend/app/analytics/stock_risk.py, inbound_units: ordered, not delivered, not overdue). They were "
                  f"relabelled false ({len(in_sample)} of them in this sample; see label-corrections.jsonl). With the "
                  f"original labels:", "", *table(rows, original), ""]
    lines += ["## The false sentences", ""]
    for row in sorted(rows, key=key):
        label = given[key(row)]
        if label["label"] == "false":
            lines.append(f"- {row['answer_id']}: \"{label['wrong_words']}\" — {label['what_the_evidence_says']}")
    (OUT / "sample-report.md").write_text("\n".join(lines) + "\n")
    print("\n".join(table(rows, labels)))


if __name__ == "__main__":
    main()

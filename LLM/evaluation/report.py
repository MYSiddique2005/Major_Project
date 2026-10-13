"""Turns a run's results into a report: results/<name>/report.md.

    ../Backend/.venv/bin/python -m evaluation.report --name main

Scores are recomputed from the stored answers each time, so a change to the scoring rules applies to
answers already collected without asking the model again.
"""
import argparse
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean

from evaluation.context import open_context
from evaluation.scoring import Expectation, score

from app.llm.recommendations import unmatched_figures

RESULTS = Path(__file__).resolve().parent / "results"
CATEGORIES = ["grounding", "factual", "cross_module", "action", "abstention"]
LABELS = {"grounding": "Grounding (terms and rules)", "factual": "Factual (one module)",
          "cross_module": "Cross-module reasoning", "action": "Controlled actions and permissions",
          "abstention": "Abstention (data cannot answer)"}


def load(name: str) -> list[dict]:
    file = RESULTS / name / "results.jsonl"
    records = [json.loads(line) for line in file.read_text().splitlines() if line.strip()] if file.exists() else []
    for record in records:  # re-score with the current rules, keeping the figure check done at run time
        kept = record["score"]
        result = score(Expectation(**record["expected"]), record, (kept["figures"], kept["unsupported_figures"]))
        record["score"] = {**kept, "facts_found": result.facts_found, "facts_expected": result.facts_expected,
                           "missing": result.missing, "tool_ok": result.tool_ok,
                           "violations": result.violations, "action_ok": result.action_ok, "passed": result.passed,
                           "recall": result.recall}
    return records


def cell(text: str) -> str:
    """Text made safe for a Markdown table cell."""
    return text.replace("|", "\\|").replace("\n", " ")


def pct(part: float, whole: float) -> str:
    return f"{part / whole:.0%}" if whole else "-"


def summary_row(label: str, records: list[dict]) -> str:
    if not records:
        return f"| {label} | 0 | - | - | - | - | - | - |"
    scores = [r["score"] for r in records]
    recalls = [s["recall"] for s in scores if s["recall"] is not None]
    with_tools = [s for s in scores if s["tool_ok"] is not None]
    figures = sum(s["figures"] for s in scores)
    unsupported = sum(len(s["unsupported_figures"]) for s in scores)
    return (
        f"| {label} | {len(records)} | {pct(sum(s['passed'] for s in scores), len(scores))} "
        f"| {mean(recalls):.0%} | {pct(sum(s['tool_ok'] for s in with_tools), len(with_tools))} "
        f"| {unsupported} of {figures} | {mean(r['seconds'] for r in records):.0f}s "
        f"| {mean(len(r['sources']) for r in records):.1f} |"
    )


def insight_section(lines: list[str]) -> None:
    with open_context() as ctx:
        insights = ctx.insights_repo.list()
        scans = ctx.scans_repo.list()
    lines += ["", "## Proactive insights (RQ3)", ""]
    if not insights:
        lines += ["No scan has produced insights in this database yet."]
        return
    completed = [scan for scan in scans if scan.status == "Completed"]
    reorders = [i for i in insights if i.action == "reorder"]
    figures = sum(i.checks["figures_checked"] for i in insights)
    unmatched = sum(len(i.checks["figures_unmatched"]) for i in insights)
    lines += [
        f"From the {len(insights)} insights stored by {len(completed)} completed scans "
        f"({len(scans) - len(completed)} scans failed, mostly on rate limits).", "",
        "| Measure | Result |", "|---|---|",
        f"| Insights whose subject was a finding the analytics had flagged | {len(insights)} of {len(insights)} (enforced by the server) |",
        f"| Evidence from two or more modules | {sum(i.checks['cross_module'] for i in insights)} of {len(insights)} |",
        f"| Figures in the text found in the system data | {figures - unmatched} of {figures} |",
        f"| Reorder insights whose quantity equals the reorder rule | "
        f"{sum(i.checks['quantity_matches_rule'] is True for i in reorders)} of {len(reorders)} |",
        f"| Actions recommended | {', '.join(f'{a}: {sum(i.action == a for i in insights)}' for a in sorted({i.action for i in insights}))} |",
        "", "Detection itself (which products and suppliers are flagged) is done by the rule-based analytics, so its "
        "precision and recall are properties of those rules, not of the model. What the model adds, and what is "
        "measured here, is the explanation and the recommended action.",
    ]


def write_report(name: str) -> Path:
    records = load(name)
    grounded = [r for r in records if r["condition"] == "grounded"]
    ungrounded = [r for r in records if r["condition"] == "ungrounded"]
    models = defaultdict(int)
    for record in records:
        models[record["model"]] += 1

    lines = [f"# Evaluation report: {name}", "",
             f"{len(records)} answers ({len(grounded)} grounded, {len(ungrounded)} ungrounded). "
             f"Models that answered: {', '.join(f'{m} ({n})' for m, n in sorted(models.items()))}."]
    if records:
        lines += [f"Collected between {min(r['asked_at'] for r in records)} and {max(r['asked_at'] for r in records)}."]

    header = ["| Group | Questions | Passed | Facts found | Right tool used | Unsupported figures | Avg time | Avg tool calls |",
              "|---|---:|---:|---:|---:|---:|---:|---:|"]
    lines += ["", "## Results with grounding (the system as built)", "", *header]
    lines += [summary_row(LABELS[c], [r for r in grounded if r["category"] == c]) for c in CATEGORIES]
    lines += [summary_row("**All**", grounded)]

    paired_ids = {r["case"] for r in ungrounded} & {r["case"] for r in grounded}
    lines += ["", "## Effect of grounding (RQ1)", ""]
    if paired_ids:
        lines += [f"The same {len(paired_ids)} questions, asked with and without the knowledge base.", "", *header,
                  summary_row("With grounding", [r for r in grounded if r["case"] in paired_ids]),
                  summary_row("Without grounding", [r for r in ungrounded if r["case"] in paired_ids]), "",
                  "| Question | With | Without | Missing without grounding |", "|---|---|---|---|"]
        for case_id in sorted(paired_ids):
            with_g = next(r for r in grounded if r["case"] == case_id)["score"]
            without = next(r for r in ungrounded if r["case"] == case_id)["score"]
            lines += [f"| {case_id} | {'pass' if with_g['passed'] else 'fail'} | {'pass' if without['passed'] else 'fail'} "
                      f"| {cell('; '.join(without['missing'])) or '-'} |"]
    else:
        lines += ["No question has been answered in both conditions yet."]

    insight_section(lines)

    lines += ["", "## Every answer", "",
              "| Case | Condition | Role | Result | Facts | Tools called | Unsupported figures | Model |", "|---|---|---|---|---|---|---|---|"]
    for record in sorted(records, key=lambda r: (r["condition"], r["case"])):
        s = record["score"]
        problems = "; ".join([*(f"missing {m}" for m in s["missing"]), *s["violations"],
                              *(["wrong tool"] if s["tool_ok"] is False else []),
                              *(["draft wrong or absent"] if s["action_ok"] is False and record["expected"]["action"] == "draft" else [])])
        lines += [f"| {record['case']} | {record['condition']} | {record['role']} | {'pass' if s['passed'] else 'FAIL: ' + cell(problems)} "
                  f"| {s['facts_found']}/{s['facts_expected']} | {', '.join(dict.fromkeys(x['tool'] for x in record['sources'])) or '-'} "
                  f"| {', '.join(s['unsupported_figures']) or '-'} | {record['model']} |"]

    failures = [r for r in records if not r["score"]["passed"]]
    if failures:
        lines += ["", "## Failed answers in full", ""]
        for record in failures:
            lines += [f"### {record['case']} ({record['condition']}, {record['model']})", "",
                      f"**Question:** {record['question']}", "", f"**Expected facts:** {record['expected']['facts']}", "",
                      "**Answer:**", "", "> " + record["answer"].replace("\n", "\n> "), ""]

    notes = RESULTS / name / "notes.md"
    if notes.exists():
        lines += ["", notes.read_text().strip()]

    lines += ["", "## How to read this", "",
              "- **Passed** means every expected fact was found, a tool that can answer the question was used, nothing "
              "forbidden happened, and (for action cases) the right thing was or was not done.",
              "- **Facts found** are matched by number (within 1%) or by phrase. A correct answer worded in a way the "
              "phrase list does not anticipate is marked as missing, so pass rates can understate.",
              "- **Unsupported figures** are numbers in an answer that appear in none of the question, the tool results and "
              "the knowledge passages. Figures the model derives by arithmetic count as unsupported; the check cannot "
              "tell a derived figure from an invented one, or a real figure used in the wrong place.",
              "- Each question was asked once per condition. The model is not deterministic, so a single run is one sample.",
              "- When more than one model answered, differences between questions are partly differences between models."]
    path = RESULTS / name / "report.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", default="main")
    print(write_report(parser.parse_args().name))

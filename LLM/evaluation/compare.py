"""Summarises several runs of the same questions: results/<out>-summary.md.

    ../Backend/.venv/bin/python -m evaluation.compare --names extended-1,extended-2,extended-3 --out extended

A single run asks each question once, and the model is not deterministic. Repeating the run shows
which results are stable. The summary gives, per run, the pass rate with a 95% confidence interval
and the paired test of grounding; and across runs, how each question fared every time it was asked.
"""
import argparse
from collections import defaultdict
from pathlib import Path
from statistics import mean

from evaluation.report import CATEGORIES, LABELS, RESULTS, cell, load
from evaluation.stats import sign_test, wilson_interval


def rate(records: list[dict]) -> str:
    """'81 of 86 (94%, 95% CI 87-98%)'"""
    if not records:
        return "-"
    passed = sum(r["score"]["passed"] for r in records)
    low, high = wilson_interval(passed, len(records))
    return f"{passed} of {len(records)} ({passed / len(records):.0%}, 95% CI {low:.0%}-{high:.0%})"


def short(records: list[dict]) -> str:
    return f"{sum(r['score']['passed'] for r in records)}/{len(records)}" if records else "-"


def figures(records: list[dict]) -> str:
    return f"{sum(len(r['score']['unsupported_figures']) for r in records)} of {sum(r['score']['figures'] for r in records)}"


def recall(records: list[dict]) -> str:
    values = [r["score"]["recall"] for r in records if r["score"]["recall"] is not None]
    return f"{mean(values):.0%}" if values else "-"


def p_value(p: float) -> str:
    return "< 0.0001" if p < 0.0001 else f"{p:.4f}"


def write_summary(names: list[str], out: str) -> Path:
    runs = {name: load(name) for name in names}
    lines = [f"# Evaluation summary: {', '.join(names)}", "",
             "Each run asks every question once with the knowledge base, and the grounding-sensitive questions once "
             "more without it. The runs repeat the same questions on the same system, so differences between them "
             "show how much one run can be trusted."]

    lines += ["", "## Each run", "",
              "| Run | Answers | Models | Passed with grounding | Facts found | Unsupported figures | Asked |",
              "|---|---:|---|---|---:|---:|---|"]
    for name, records in runs.items():
        grounded = [r for r in records if r["condition"] == "grounded"]
        models = defaultdict(int)
        for record in records:
            models[record["model"]] += 1
        asked = f"{min(r['asked_at'] for r in records)[:10]} to {max(r['asked_at'] for r in records)[:10]}" if records else "-"
        lines += [f"| {name} | {len(records)} | {', '.join(f'{m} ({n})' for m, n in sorted(models.items()))} "
                  f"| {rate(grounded)} | {recall(grounded)} | {figures(grounded)} | {asked} |"]

    lines += ["", "## Passed with grounding, by group", "", f"| Group | {' | '.join(names)} |", f"|---|{'---:|' * len(names)}"]
    for category in CATEGORIES:
        lines += [f"| {LABELS[category]} | " + " | ".join(
            short([r for r in records if r["condition"] == "grounded" and r["category"] == category]) for records in runs.values()
        ) + " |"]
    lines += ["| **All** | " + " | ".join(short([r for r in records if r["condition"] == "grounded"]) for records in runs.values()) + " |"]

    lines += ["", "## Effect of grounding (RQ1)", "",
              "The same questions asked with and without the knowledge base, compared question by question. The test is "
              "the exact sign test on the questions where the two conditions disagree (the exact form of McNemar's test).", "",
              "| Run | Pairs | Passed with | Passed without | Only with | Only without | p (two-sided) | Unsupported figures with / without |",
              "|---|---:|---:|---:|---:|---:|---:|---|"]
    for name, records in runs.items():
        with_g = {r["case"]: r for r in records if r["condition"] == "grounded"}
        without = {r["case"]: r for r in records if r["condition"] == "ungrounded"}
        pairs = sorted(set(with_g) & set(without))
        if not pairs:
            lines += [f"| {name} | 0 | - | - | - | - | - | - |"]
            continue
        only_with = sum(with_g[c]["score"]["passed"] and not without[c]["score"]["passed"] for c in pairs)
        only_without = sum(without[c]["score"]["passed"] and not with_g[c]["score"]["passed"] for c in pairs)
        lines += [f"| {name} | {len(pairs)} | {short([with_g[c] for c in pairs])} | {short([without[c] for c in pairs])} "
                  f"| {only_with} | {only_without} | {p_value(sign_test(only_with, only_without))} "
                  f"| {figures([with_g[c] for c in pairs])} / {figures([without[c] for c in pairs])} |"]

    # --- consistency: how each question fared across the runs that asked it -----------------------
    outcomes: dict[tuple[str, str], dict[str, dict]] = defaultdict(dict)
    for name, records in runs.items():
        for record in records:
            outcomes[(record["condition"], record["case"])][name] = record
    # A run stopped by a rate limit has answered only part of the questions; compare what the started runs share.
    names = [name for name in names if runs[name]]
    complete = {key: by_run for key, by_run in outcomes.items() if len(by_run) == len(names)}
    lines += ["", "## Consistency across runs", ""]
    if len(names) < 2 or not complete:
        lines += ["Needs at least two runs that have answered the same questions."]
    else:
        lines += [f"Counting only the {len(complete)} answers present in all {len(names)} runs that have started "
                  f"({', '.join(names)}).", "",
                  "| Condition | Questions | Passed every time | Failed every time | Mixed |", "|---|---:|---:|---:|---:|"]
        unstable = []
        for condition in ("grounded", "ungrounded"):
            keys = [key for key in complete if key[0] == condition]
            passes = {key: sum(r["score"]["passed"] for r in complete[key].values()) for key in keys}
            always = sum(count == len(names) for count in passes.values())
            never = sum(count == 0 for count in passes.values())
            lines += [f"| {condition} | {len(keys)} | {always} | {never} | {len(keys) - always - never} |"]
            unstable += [key for key in keys if passes[key] < len(names) and condition == "grounded"]
        if unstable:
            lines += ["", "Questions that did not pass every time with grounding:", "",
                      f"| Question | {' | '.join(names)} | What was missing or wrong |", f"|---|{'---|' * len(names)}---|"]
            for key in sorted(unstable, key=lambda k: (k[1][0], int(k[1][1:]))):
                by_run = complete[key]
                problems = []
                for name in names:
                    s = by_run[name]["score"]
                    problems += [*(f"missing {m}" for m in s["missing"]), *s["violations"],
                                 *(["wrong tool"] if s["tool_ok"] is False else []),
                                 *(["draft wrong or absent"] if s["action_ok"] is False and not s["violations"] else [])]
                lines += [f"| {key[1]} | " + " | ".join("pass" if by_run[n]["score"]["passed"] else "FAIL" for n in names)
                          + f" | {cell('; '.join(dict.fromkeys(problems)))} |"]
        else:
            lines += ["", "Every question passed with grounding in every run."]

    lines += ["", "## How to read this", "",
              "- A 95% confidence interval says how far the true pass rate on questions like these could plausibly be "
              "from the measured one, given how few questions there are. It does not cover the questions being "
              "unrepresentative: they were written by the system's builders.",
              "- The sign test asks whether grounding helped on more questions than it hurt by more than chance. A small "
              "p-value supports a real effect on these questions.",
              "- Runs on the same questions are not independent samples, so they are reported side by side, not pooled.",
              "- Scoring is by number and phrase matching; see each run's report for every answer and the scoring rules."]
    path = RESULTS / f"{out}-summary.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Summarise several evaluation runs.")
    parser.add_argument("--names", required=True, help="comma-separated run names")
    parser.add_argument("--out", default="runs", help="the summary is written to results/<out>-summary.md")
    args = parser.parse_args()
    print(write_summary([name.strip() for name in args.names.split(",") if name.strip()], args.out))

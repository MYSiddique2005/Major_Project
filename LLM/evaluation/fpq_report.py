"""False-premise questions with the verifier off, with patterns and with TRACE, on both models.

    ../Backend/.venv/bin/python -m evaluation.fpq_report

Reads results/fpq-<model>-<setting>/results.jsonl (written by evaluation.run --suite fpq) and writes
results/fpq-report.md: the share of answers that rebut the premise (the run's own keyword and number scoring,
in which verification plays no part), by premise family, how often the verifier sent an answer back for
correction, and McNemar's exact test between each setting and the verifier off on the questions both answered.
"""
from pathlib import Path

from evaluation.claims_eval import rate
from evaluation.report import load as load_run
from evaluation.trace_score import mcnemar

RESULTS = Path(__file__).resolve().parent / "results"
MODELS = {"gemini": "gemini-3.5-flash-lite", "gemma": "gemma-4-31b-it"}
SETTINGS = ("off", "patterns", "trace")
FAMILIES = ("state", "policy", "derived")


def load(model: str, setting: str) -> dict[str, dict]:
    """Answered questions of one run, re-scored with the current rules (as evaluation.report does)."""
    if not (RESULTS / f"fpq-{model}-{setting}" / "results.jsonl").exists():
        return {}
    return {record["case"]: record for record in load_run(f"fpq-{model}-{setting}")
            if record.get("status") == "ok" and record.get("answer")}


def passed(record: dict) -> bool:
    return bool(record["score"]["passed"])


def main() -> None:
    lines = ["# False-premise questions", "",
             "An answer passes when it states the true fact that rebuts the premise (keyword and number scoring, the "
             "same rules as the main evaluation). Verification plays no part in scoring.", ""]
    for model, model_id in MODELS.items():
        runs = {setting: load(model, setting) for setting in SETTINGS}
        lines += [f"## {model_id}", "",
                  "| Setting | Answers | Passed | " + " | ".join(f"Passed ({family})" for family in FAMILIES)
                  + " | Sent back for correction | Mean seconds |",
                  "|---|---:|---:|" + "---:|" * len(FAMILIES) + "---:|---:|"]
        for setting, records in runs.items():
            if not records:
                lines.append(f"| {setting} | 0 | - |" + " - |" * len(FAMILIES) + " - | - |")
                continue
            values = list(records.values())
            by_family = [rate(sum(passed(r) for r in values if r["category"] == family),
                              sum(1 for r in values if r["category"] == family)) for family in FAMILIES]
            corrected = sum(1 for r in values if (r.get("verification") or {}).get("corrected"))
            seconds = sum(r.get("seconds") or 0 for r in values) / len(values)
            lines.append(f"| {setting} | {len(values)} | {rate(sum(passed(r) for r in values), len(values))} | "
                         + " | ".join(by_family) + f" | {corrected} | {seconds:.0f} |")
        lines += ["", "| Compared with off | Questions both answered | Only this setting passed | Only off passed | p |",
                  "|---|---:|---:|---:|---:|"]
        for setting in SETTINGS[1:]:
            shared = sorted(set(runs["off"]) & set(runs[setting]))
            if not shared:
                continue
            only_this = sum(passed(runs[setting][c]) and not passed(runs["off"][c]) for c in shared)
            only_off = sum(passed(runs["off"][c]) and not passed(runs[setting][c]) for c in shared)
            lines.append(f"| {setting} | {len(shared)} | {only_this} | {only_off} | {mcnemar(only_this, only_off):.3g} |")
        failed = {setting: sorted(c for c, r in records.items() if not passed(r)) for setting, records in runs.items()}
        lines += ["", "Questions failed: " + "; ".join(f"{s}: {', '.join(c) or 'none'}" for s, c in failed.items()), ""]
    path = RESULTS / "fpq-report.md"
    path.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()

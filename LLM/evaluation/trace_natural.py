"""Natural errors: the assistant's own false statements in its 590 stored answers, found by pooling.

    ../Backend/.venv/bin/python -m evaluation.trace_natural sample                 # no model calls
    LLM_MODEL=gemini-3.5-flash-lite LLM_FALLBACK_MODEL= ../Backend/.venv/bin/python -m evaluation.trace_natural extract
    LLM_MODEL=gemini-3.5-flash-lite ../Backend/.venv/bin/python -m evaluation.trace_natural judge
    LLM_MODEL=gemma-4-31b-it        ../Backend/.venv/bin/python -m evaluation.trace_natural judge
    ../Backend/.venv/bin/python -m evaluation.trace_natural minicheck-prep         # then evaluation/minicheck_run.py
    ../Backend/.venv/bin/python -m evaluation.trace_natural sheets                 # annotation sheets
    ../Backend/.venv/bin/python -m evaluation.trace_natural score                  # after annotation

Every step after sample takes --scope sampled: only the answers that hold a sampled sentence (211 of 590),
which is what recall on the random sample needs, at a third of the model calls.

Answers: the five runs of 118 answers (gemini-3.5-flash-lite: extended-1, fixed-1, fixed-2, fixed-3; gemma-4-31b-it:
gemma4-1), 430 with the knowledge base and 160 without. The unit of annotation is the sentence.

Pooling, as in information-retrieval evaluation: every sentence any method flags is annotated, plus a seeded
random sample of sentences (SAMPLE_SIZE) annotated whatever the methods say, which estimates how many false
statements all methods miss. Annotators see the question, the answer, the sentence and the evidence (the tool
results the assistant was given and the current facts), never which method flagged it. A second annotator
labels a seeded 20% of the rows blind, for Cohen's kappa.

Labels already given are kept in labels-annotator-1.jsonl (by answer and sentence span) and filled into
annotator 1's sheet when it is written, so the random sample can be labelled before any method has run.

The answers of the four Gemini runs include the originals of TRACE's development sets, so results are reported
separately for answers TRACE was developed on and for the Gemma answers it never saw.
"""
import argparse
import csv
import json
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

from evaluation.claims_eval import RESULTS, rate
from evaluation.context import open_context
from evaluation.trace_eval import DEV_SETS, Cache, DailyLimit, load_set, run_extraction
from evaluation.trace_baselines import JudgeCache, judge_texts, minicheck_prep
from evaluation.trace_score import Methods, check_frozen, place, sentences

from app.llm.recommendations import RecommendationChecker

OUT = RESULTS / "trace" / "natural"
RUNS = ("extended-1", "fixed-1", "fixed-2", "fixed-3", "gemma4-1")
SEED = 2026
SAMPLE_SIZE = 300
SECOND_SHARE = 0.2
LABELS = ("false", "true", "no-claim", "unsure")
_SKIP = re.compile(r"^(would you like|do you want|shall i|let me know|if you (?:want|need|would like))", re.IGNORECASE)


def answers() -> list[dict]:
    dev_texts = {record["original"] for name in DEV_SETS for record in load_set(name)}
    items = []
    for run in RUNS:
        for line in (RESULTS / run / "results.jsonl").read_text().splitlines():
            record = json.loads(line)
            if record.get("answer"):
                items.append({"id": f"{run}/{record['case']}/{record['condition']}", "source": "answer", "run": run,
                              "condition": record["condition"], "role": record.get("role", ""),
                              "question": record.get("question", ""), "text": record["answer"],
                              "tool_outputs": record.get("tool_outputs") or [],
                              "development": record["answer"] in dev_texts})
    return items


def checkable_sentences(text: str) -> list[tuple[int, int]]:
    """Sentences that can hold a statement: at least four words, not a question or an offer."""
    spans = []
    for start, end in sentences(text):
        sentence = text[start:end].strip()
        if len(sentence.split()) >= 4 and not sentence.endswith("?") and not _SKIP.match(sentence.lstrip("-* ")):
            spans.append((start, end))
    return spans


def sample(items: list[dict]) -> list[dict]:
    population = [(item["id"], start, end) for item in items for start, end in checkable_sentences(item["text"])]
    chosen = random.Random(SEED).sample(population, min(SAMPLE_SIZE, len(population)))
    by_id = {item["id"]: item for item in items}
    return [{"answer_id": answer_id, "start": start, "end": end, "sentence": by_id[answer_id]["text"][start:end].strip()}
            for answer_id, start, end in sorted(chosen)]


def flags(ctx, items: list[dict]) -> list[dict]:
    """Every sentence each method flags (a contradicted statement placed in it), per answer."""
    methods = Methods(ctx, Cache(), JudgeCache())
    rows = []
    for item in items:
        result = methods.of(item, item["text"])
        for name in methods.names():
            if result[name] is None:
                rows.append({"answer_id": item["id"], "method": name, "missing": True})
                continue
            for quote in result[name]:
                span = place(quote, item["text"])
                sentence = next(((s, e) for s, e in sentences(item["text"]) if span and s < span[1] and e > span[0]), None)
                rows.append({"answer_id": item["id"], "method": name, "quote": quote,
                             "start": sentence[0] if sentence else None, "end": sentence[1] if sentence else None})
    return rows


def evidence_text(item: dict, checker: RecommendationChecker) -> str:
    """What the annotator checks against: the tool results the assistant saw, and the current facts of every
    product and supplier the answer names."""
    parts = [f"## {item['id']}", "", f"Question ({item['role']}): {item['question']}", "", "Answer:", "", item["text"], ""]
    outputs = item["tool_outputs"]
    if isinstance(outputs, str):
        try:
            outputs = json.loads(outputs)
        except json.JSONDecodeError:
            outputs = [outputs]
    for output in outputs:
        parts += ["Tool result:", "", "```json", json.dumps(output, indent=1, default=str)[:6000], "```", ""]
    for product_id in dict.fromkeys(re.findall(r"\bP\d{3}\b", item["text"])):
        try:
            facts = checker.product_facts(product_id)
            parts += [f"Current facts of {product_id}:", "", "```json", json.dumps(facts, indent=1, default=str), "```", ""]
        except Exception:
            parts += [f"{product_id}: not in the system", ""]
    for supplier_id in dict.fromkeys(re.findall(r"\bS\d{3}\b", item["text"])):
        try:
            facts = checker.supplier_facts(supplier_id)
            parts += [f"Current facts of {supplier_id}:", "", "```json", json.dumps(facts, indent=1, default=str), "```", ""]
        except Exception:
            parts += [f"{supplier_id}: not in the system", ""]
    return "\n".join(parts)


SHEET_COLUMNS = ("row", "answer_id", "question", "sentence", "label", "wrong_words", "what_the_evidence_says", "note")
LABEL_FIELDS = SHEET_COLUMNS[4:]
GIVEN = OUT / "labels-annotator-1.jsonl"


def write_sheets(ctx, items: list[dict]) -> None:
    by_id = {item["id"]: item for item in items}
    chosen = [json.loads(line) for line in (OUT / "sample.jsonl").read_text().splitlines()]
    flagged = [row for row in map(json.loads, (OUT / "flags.jsonl").read_text().splitlines())
               if not row.get("missing") and row.get("start") is not None]
    units = {(row["answer_id"], row["start"], row["end"]) for row in flagged}
    units |= {(row["answer_id"], row["start"], row["end"]) for row in chosen}
    units = sorted(units)
    random.Random(SEED + 1).shuffle(units)
    rows = [{"row": index, "answer_id": answer_id, "question": by_id[answer_id]["question"],
             "sentence": by_id[answer_id]["text"][start:end].strip(), "start": start, "end": end}
            for index, (answer_id, start, end) in enumerate(units, 1)]
    (OUT / "units.jsonl").write_text("".join(json.dumps(row) + "\n" for row in rows))

    given = {(row["answer_id"], row["start"], row["end"]): row
             for row in map(json.loads, GIVEN.read_text().splitlines())} if GIVEN.exists() else {}

    def write(path: Path, selected: list[dict], labelled: dict) -> None:
        with path.open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=SHEET_COLUMNS, extrasaction="ignore")
            writer.writeheader()
            for row in selected:
                known = labelled.get((row["answer_id"], row["start"], row["end"]), {})
                writer.writerow({**row, **{field: known.get(field, "") for field in LABEL_FIELDS}})

    write(OUT / "sheet-annotator-1.csv", rows, given)
    second = sorted(random.Random(SEED + 2).sample(rows, round(len(rows) * SECOND_SHARE)), key=lambda row: row["row"])
    write(OUT / "sheet-annotator-2.csv", second, {})
    checker = RecommendationChecker(ctx.analytics, ctx.suppliers)
    needed = dict.fromkeys(row["answer_id"] for row in rows)
    (OUT / "evidence.md").write_text("# Evidence for annotation\n\n" + "\n".join(evidence_text(by_id[a], checker) for a in needed))
    print(f"{len(rows)} sentences to annotate ({len(second)} for the second annotator); "
          f"{len(needed)} answers in evidence.md")


def read_labels(path: Path) -> dict[int, str]:
    if not path.exists():
        return {}
    with path.open() as handle:
        return {int(row["row"]): row["label"].strip().lower() for row in csv.DictReader(handle)
                if row["label"].strip().lower() in LABELS}


def kappa(first: dict[int, str], second: dict[int, str]) -> tuple[float | None, int]:
    shared = sorted(set(first) & set(second))
    if not shared:
        return None, 0
    observed = sum(first[row] == second[row] for row in shared) / len(shared)
    a, b = Counter(first[row] for row in shared), Counter(second[row] for row in shared)
    expected = sum(a[label] * b[label] for label in LABELS) / len(shared) ** 2
    return (1.0 if expected == 1 else (observed - expected) / (1 - expected)), len(shared)


def score(items: list[dict]) -> Path:
    by_id = {item["id"]: item for item in items}
    units = {row["row"]: row for row in map(json.loads, (OUT / "units.jsonl").read_text().splitlines())}
    labels = read_labels(OUT / "sheet-annotator-1.csv")
    second = read_labels(OUT / "sheet-annotator-2.csv")
    flagged = defaultdict(set)  # method -> {(answer_id, sentence start)}
    missing = defaultdict(set)  # method -> answers it could not judge (no extraction or judge reply)
    methods: list[str] = []
    for row in map(json.loads, (OUT / "flags.jsonl").read_text().splitlines()):
        if row["method"] not in methods:
            methods.append(row["method"])
        if row.get("missing"):
            missing[row["method"]].add(row["answer_id"])
        elif row.get("start") is not None:
            flagged[row["method"]].add((row["answer_id"], row["start"]))
    sampled = {(row["answer_id"], row["start"]) for row in map(json.loads, (OUT / "sample.jsonl").read_text().splitlines())}

    lines = ["# Natural errors in the stored answers", "",
             f"{len(labels)} of {len(units)} pooled sentences labelled by annotator 1; "
             f"{len(second)} by annotator 2."]
    value, shared = kappa(labels, second)
    if value is not None:
        lines.append(f"Agreement on {shared} sentences labelled by both: Cohen's kappa {value:.2f}.")
    for group, keep in (("all answers", lambda item: True), ("answers TRACE was developed on", lambda item: item["development"]),
                        ("answers TRACE never saw (Gemma run)", lambda item: item["run"] == "gemma4-1")):
        lines += ["", f"## {group}", "",
                  "| Method | Precision of flags | Recall on the random sample |", "|---|---:|---:|"]
        in_group = {row_id for row_id, unit in units.items() if keep(by_id[unit["answer_id"]])}
        false_in_sample = [row_id for row_id in in_group if labels.get(row_id) == "false"
                           and (units[row_id]["answer_id"], units[row_id]["start"]) in sampled]
        for name in methods:
            mine = [row_id for row_id in in_group if (units[row_id]["answer_id"], units[row_id]["start"]) in flagged[name]
                    and labels.get(row_id) in ("false", "true", "no-claim")]
            correct = sum(labels[row_id] == "false" for row_id in mine)
            judged_sample = [row_id for row_id in false_in_sample if units[row_id]["answer_id"] not in missing[name]]
            found = sum((units[row_id]["answer_id"], units[row_id]["start"]) in flagged[name] for row_id in judged_sample)
            lines.append(f"| {name} | {rate(correct, len(mine))} | {rate(found, len(judged_sample))} |")
        labelled_sample = [row_id for row_id in in_group if (units[row_id]["answer_id"], units[row_id]["start"]) in sampled
                           and labels.get(row_id) in LABELS]
        lines.append("")
        lines.append(f"False sentences in the random sample: {rate(len(false_in_sample), len(labelled_sample))}.")
    path = OUT / "report.md"
    path.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description="Natural errors in the stored answers.")
    parser.add_argument("step", choices=["sample", "extract", "judge", "minicheck-prep", "flags", "sheets", "score"])
    parser.add_argument("--scope", choices=["all", "sampled"], default="all")
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    items = answers()
    if args.scope == "sampled" and args.step != "sample":
        sampled = {json.loads(line)["answer_id"] for line in (OUT / "sample.jsonl").read_text().splitlines()}
        items = [item for item in items if item["id"] in sampled]
    if args.step == "sample":
        chosen = sample(items)
        (OUT / "sample.jsonl").write_text("".join(json.dumps(row) + "\n" for row in chosen))
        print(f"{len(items)} answers ({sum(item['development'] for item in items)} development originals); "
              f"{len(chosen)} sentences sampled")
    elif args.step == "extract":
        with open_context() as ctx:
            try:
                run_extraction(ctx, [item["text"] for item in items], Cache())
            except DailyLimit as error:
                print(f"Daily limit reached ({error}); run again tomorrow.")
                raise SystemExit(3)
    elif args.step == "judge":
        judge_texts([item["text"] for item in items])
    elif args.step == "minicheck-prep":
        minicheck_prep([item["text"] for item in items])
    elif args.step == "flags":
        check_frozen()
        with open_context() as ctx:
            rows = flags(ctx, items)
        (OUT / "flags.jsonl").write_text("".join(json.dumps(row) + "\n" for row in rows))
        print(f"{sum(1 for row in rows if not row.get('missing'))} flags written")
    elif args.step == "sheets":
        with open_context() as ctx:
            write_sheets(ctx, items)
    else:
        score(items)


if __name__ == "__main__":
    main()

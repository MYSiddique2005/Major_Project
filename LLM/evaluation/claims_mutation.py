"""Mutation test of claim-level verification: insert errors by swapping words for their opposites.

    ../Backend/.venv/bin/python -m evaluation.claims_mutation          # writes results/claims/mutation.md

Needs no model. Each text from the development set that discusses a product is copied with exactly one word or phrase replaced by its opposite (below/above,
rising/falling, High/Low, in time/too late, ...). The swap list is domain vocabulary written for this
test, not the verifier's patterns. A mutant is detected when the verifier flags a contradiction in the
sentence that was changed.

Not every swap makes a false statement about the data: a swapped word can sit in a description of a rule
("Medium risk applies if ... less than the lead time"), a heading or a hypothetical. Those are not errors
the verifier should flag. The undetected mutants are therefore listed, and a seeded sample of them is
classified by hand in mutation-review.md; the corrected detection rate counts only real errors.
"""
import json
import random
import re
from collections import Counter, defaultdict

from evaluation.claims_eval import OUT, PRODUCT_ID, SEED, Checker, collect, contradictions, rate

from app.llm import claims as C

# (pattern, replacement). Each is applied at one place at a time.
SWAPS = [
    (r"\bbelow\b", "above"), (r"\babove\b", "below"),
    (r"\bless than\b", "more than"), (r"\bmore than\b", "less than"), (r"\bfewer than\b", "more than"),
    (r"\bshorter than\b", "longer than"), (r"\blonger than\b", "shorter than"),
    (r"\brising\b", "falling"), (r"\bfalling\b", "rising"),
    (r"\bincreasing\b", "decreasing"), (r"\bdecreasing\b", "increasing"),
    (r"\bincreased\b", "decreased"), (r"\bdecreased\b", "increased"),
    (r"\bup (?=\d)", "down "), (r"\bdown (?=\d)", "up "),
    (r"\bin time\b", "too late"), (r"\btoo late\b", "in time"),
    (r"\bbefore (?=(?:the )?(?:stock|it|projected stockout))", "after "),
    (r"\bout of stock\b", "in stock"),
    (r"\boverdue\b", "on time"),
    (r"\bCritical\b(?! Stock)", "Low"), (r"\bHigh\b(?! Stock)", "Low"), (r"\bMedium\b", "Critical"), (r"\bLow\b(?! Stock)", "High"),
    (r"\bworsening\b", "improving"), (r"\bimproving\b", "worsening"),
]
_SWAPS = [(re.compile(pattern), replacement) for pattern, replacement in SWAPS]
MUTANTS_PER_TEXT = 3
REVIEW_SAMPLE = 40


def mutants(text: str, rng: random.Random) -> list[dict]:
    sites = []
    for pattern, replacement in _SWAPS:
        for match in pattern.finditer(text):
            sites.append((match.start(), match.end(), match.group(0), replacement))
    rng.shuffle(sites)
    result = []
    for start, end, before, after in sites[:MUTANTS_PER_TEXT]:
        mutated = text[:start] + after + text[end:]
        sentence = next((s for s in C.sentences(mutated) if after in s and s.replace(after, before, 1) in text), None)
        result.append({"before": before, "after": after, "text": mutated, "sentence": sentence})
    return result


def main() -> None:
    from evaluation.context import open_context

    rng = random.Random(SEED)
    rows = []
    with open_context() as ctx:
        checker = Checker(ctx)
        seen = set()
        for item in collect(ctx):
            if not PRODUCT_ID.search(item["text"]) or item["text"] in seen:
                continue
            already = {c.sentence for c in checker.claims(item) if c.status == "contradicted"}
            seen.add(item["text"])
            for mutant in mutants(item["text"], rng):
                flagged = [c for c in checker.claims(item, mutant["text"]) if c.status == "contradicted"]
                # Only a flag in the changed sentence counts, and not one that sentence already had.
                in_sentence = [c for c in flagged if mutant["sentence"] and c.sentence == mutant["sentence"]
                               and c.sentence not in already]
                rows.append({"id": item["id"], "source": item["source"], **mutant,
                             "detected": bool(in_sentence), "flagged": [c.describe() for c in flagged]})

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "mutants.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    detected = [r for r in rows if r["detected"]]
    missed = [r for r in rows if not r["detected"]]
    by_swap = defaultdict(Counter)
    for r in rows:
        by_swap[f"{r['before']} -> {r['after']}"][r["detected"]] += 1

    review = random.Random(SEED).sample(missed, min(REVIEW_SAMPLE, len(missed)))
    lines = ["# Claim verification: mutation test", "",
             "See `evaluation/claims_mutation.py`. No model is used.", "",
             f"{len({r['id'] for r in rows})} texts, {len(rows)} mutants (at most {MUTANTS_PER_TEXT} per text).", "",
             "| Measure | Result |", "|---|---|",
             f"| Mutants detected (all swaps, including ones that do not make a false data statement) | {rate(len(detected), len(rows))} |",
             "", "| Swap | Detected | Not detected |", "|---|---:|---:|"]
    for swap, counts in sorted(by_swap.items(), key=lambda kv: -sum(kv[1].values())):
        lines.append(f"| {swap} | {counts[True]} | {counts[False]} |")
    lines += ["", f"## Sample of {len(review)} undetected mutants for review", "",
              "Classify each in mutation-review.md as a real miss (a false statement about the product or supplier "
              "that went unflagged) or not an error (rule text, hypothetical, heading, or a word that is not a claim).", ""]
    for index, r in enumerate(review, 1):
        lines.append(f"{index}. **{r['id']}** \"{r['before']}\" -> \"{r['after']}\": {(r['sentence'] or '(sentence not located)')[:300]}")
    (OUT / "mutation.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(OUT / "mutation.md")


if __name__ == "__main__":
    main()

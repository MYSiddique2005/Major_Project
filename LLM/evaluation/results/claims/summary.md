# Claim-level verification: summary of the evaluation

The verifier (`Backend/app/llm/claims.py`) checks qualitative statements in the assistant's answers and
insights against the system's data. It was developed in three versions; each held-out test used texts
whose wording had not been seen while that version was written, and the verifier's file was frozen
(sha256 recorded) before each test was scored.

## Results

| Version (sha256 prefix) | Test | In-scope errors detected | False alarms on paraphrases |
|---|---|---:|---:|
| v1 (3f0e59d6) | Mutation test, word swaps in 108 development texts, 271 mutants, manual review of 40 misses | about 48% of real errors (estimate) | - |
| v2 (cb172ddc) | **Held-out**: model-written rewrites of 60 texts (`perturbations-v2-test.jsonl`) | **15 of 25 (60%, 95% CI 41-77%)** | **1 of 60 (2%, 0-9%)** |
| v3 (36154591) | **Held-out**: model-written rewrites of 60 different texts (`test-v3.jsonl`) | **25 of 31 (81%, 95% CI 64-91%)** | **2 of 60 (3%, 1-11%)** |
| v3 (36154591) | **Held-out, second set**: 64 more texts never used before (`test-v3b.jsonl`, `test-v3b-review.md`) | **23 of 31 (74%, 95% CI 57-86%)** | **0 of 64 (0%, 0-6%)** |
| v3, both sets | | **48 of 62 (77%, 95% CI 66-86%)** | **2 of 124 (2%, 0-6%)** |

All injected errors, in scope or not: v2 16 of 59 (27%), v3 25 of 60 (42%) and 23 of 64 (36%). "In scope" means a statement
about a product's or supplier's current state of one of the verifier's 12 claim kinds; the others are
permissions, whether something exists, comparisons between products, past events, periods and scenario
premises, process statements, statements about groups of products, and changed numbers (the figure check's
job). The classification of every injection is listed in `test-v2-review.md` and below.

On the development texts (every answer of the four extended runs and 18 insights, 558 claims for v3) the
final version flags only four statements, in two answers, and all four are genuine model errors that the
keyword evaluation had passed: in runs fixed-2 and fixed-3, question U11, the assistant said product P032
(125 units, reorder level 92, status In Stock) had status "Low Stock" because "125 units are below the
reorder level of 92".

## How the test sets were made

For each text, Gemini (`gemini-3.5-flash-lite`, five texts per request) was asked for two rewrites in one
reply: one with exactly one qualitative statement made false without changing any number, and one
paraphrase with the same meaning. A rewrite counts when the model's stated change is visible in the text.
Detection counts only contradictions the rewrite introduced, not ones the original already had. The texts
are a seeded random sample of answers and insights that name a product; the selection does not depend on
the verifier, so v2 and v3 were tested on the first and the second 60 texts of the same order, and v3 again,
unchanged, on the remaining 64 texts (positions 120-183, the whole rest of the pool).

## Version 3 test: classification and misses

In scope (31): 1, 2, 8, 9, 11, 12, 15, 19, 22, 23, 24, 28, 30, 32, 34, 36, 37, 38, 39, 40, 41, 42, 43, 47,
48, 51, 52, 53, 57, 59, 60 (numbers as listed by the injection listing in order of `test-v3.jsonl`).

Missed in scope (6): "no units ... on hand" (1); "currently completely in stock" (38); "Total available stock
(0 on hand + 720 on order = 720) is above the reorder point" (40); "days of cover are significantly higher
than the supplier's lead time" (51); "82 units arriving on time" (52); "Demand for <product>, P045 is falling
sharply", where the product ID and a comma sit between "demand" and "falling" (53).

False alarms (2): a six-word list heading, "Four items are at High Risk:", attributed to the product named
before it; and a negation the verifier does not know, "stopping the item from hitting Critical risk status".

These were left unfixed so that the test stays a test. A version 4 would need another fresh test.

## Limits

- The injected errors were written by a model told to change one qualitative statement, so their style
  may differ from errors a model makes on its own. The development texts contained only two such natural
  errors (both caught), too few to measure detection of natural errors.
- 25 and 31 in-scope errors per test give wide intervals; pooling the two v3 tests (62) narrows it to 66-86%.
- Scope was decided by hand, by the authors.
- The verifier is pattern-based and English-only; a claim worded unlike any pattern is not checked.

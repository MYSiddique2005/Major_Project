# Evaluation summary: gemma4-1

Each run asks every question once with the knowledge base, and the grounding-sensitive questions once more without it. The runs repeat the same questions on the same system, so differences between them show how much one run can be trusted.

## Each run

| Run | Answers | Models | Passed with grounding | Facts found | Unsupported figures | Asked |
|---|---:|---|---|---:|---:|---|
| gemma4-1 | 118 | gemma-4-31b-it (118) | 86 of 86 (100%, 95% CI 96%-100%) | 100% | 1 of 251 | 2026-10-17 to 2026-10-18 |

## Passed with grounding, by group

| Group | gemma4-1 |
|---|---:|
| Grounding (terms and rules) | 25/25 |
| Factual (one module) | 17/17 |
| Cross-module reasoning | 17/17 |
| Controlled actions and permissions | 15/15 |
| Abstention (data cannot answer) | 12/12 |
| **All** | 86/86 |

## Effect of grounding (RQ1)

The same questions asked with and without the knowledge base, compared question by question. The test is the exact sign test on the questions where the two conditions disagree (the exact form of McNemar's test).

| Run | Pairs | Passed with | Passed without | Only with | Only without | p (two-sided) | Unsupported figures with / without |
|---|---:|---:|---:|---:|---:|---:|---|
| gemma4-1 | 32 | 32/32 | 6/32 | 26 | 0 | < 0.0001 | 0 of 70 / 0 of 47 |

## Consistency across runs

Needs at least two runs that have answered the same questions.

## How to read this

- A 95% confidence interval says how far the true pass rate on questions like these could plausibly be from the measured one, given how few questions there are. It does not cover the questions being unrepresentative: they were written by the system's builders.
- The sign test asks whether grounding helped on more questions than it hurt by more than chance. A small p-value supports a real effect on these questions.
- Runs on the same questions are not independent samples, so they are reported side by side, not pooled.
- Scoring is by number and phrase matching; see each run's report for every answer and the scoring rules.

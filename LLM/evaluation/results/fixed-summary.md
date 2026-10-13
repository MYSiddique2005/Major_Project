# Evaluation summary: fixed-1, fixed-2, fixed-3

Each run asks every question once with the knowledge base, and the grounding-sensitive questions once more without it. The runs repeat the same questions on the same system, so differences between them show how much one run can be trusted.

## Each run

| Run | Answers | Models | Passed with grounding | Facts found | Unsupported figures | Asked |
|---|---:|---|---|---:|---:|---|
| fixed-1 | 118 | gemini-3.5-flash-lite (118) | 84 of 86 (98%, 95% CI 92%-99%) | 98% | 1 of 310 | 2026-10-10 to 2026-10-10 |
| fixed-2 | 118 | gemini-3.5-flash-lite (118) | 86 of 86 (100%, 95% CI 96%-100%) | 100% | 3 of 342 | 2026-10-10 to 2026-10-13 |
| fixed-3 | 118 | gemini-3.5-flash-lite (118) | 86 of 86 (100%, 95% CI 96%-100%) | 100% | 2 of 332 | 2026-10-13 to 2026-10-13 |

## Passed with grounding, by group

| Group | fixed-1 | fixed-2 | fixed-3 |
|---|---:|---:|---:|
| Grounding (terms and rules) | 25/25 | 25/25 | 25/25 |
| Factual (one module) | 17/17 | 17/17 | 17/17 |
| Cross-module reasoning | 16/17 | 17/17 | 17/17 |
| Controlled actions and permissions | 15/15 | 15/15 | 15/15 |
| Abstention (data cannot answer) | 11/12 | 12/12 | 12/12 |
| **All** | 84/86 | 86/86 | 86/86 |

## Effect of grounding (RQ1)

The same questions asked with and without the knowledge base, compared question by question. The test is the exact sign test on the questions where the two conditions disagree (the exact form of McNemar's test).

| Run | Pairs | Passed with | Passed without | Only with | Only without | p (two-sided) | Unsupported figures with / without |
|---|---:|---:|---:|---:|---:|---:|---|
| fixed-1 | 32 | 32/32 | 8/32 | 24 | 0 | < 0.0001 | 0 of 105 / 3 of 103 |
| fixed-2 | 32 | 32/32 | 9/32 | 23 | 0 | < 0.0001 | 1 of 105 / 3 of 112 |
| fixed-3 | 32 | 32/32 | 9/32 | 23 | 0 | < 0.0001 | 0 of 85 / 3 of 94 |

## Consistency across runs

Counting only the 118 answers present in all 3 runs that have started (fixed-1, fixed-2, fixed-3).

| Condition | Questions | Passed every time | Failed every time | Mixed |
|---|---:|---:|---:|---:|
| grounded | 86 | 84 | 0 | 2 |
| ungrounded | 32 | 7 | 22 | 3 |

Questions that did not pass every time with grounding:

| Question | fixed-1 | fixed-2 | fixed-3 | What was missing or wrong |
|---|---|---|---|---|
| C11 | FAIL | pass | pass | missing P059; missing P071; missing P075; missing P062; missing P058; missing P065; missing P060 |
| U1 | FAIL | pass | pass | missing not found / no product / does not exist / doesn't exist / could not find / couldn't find / unable to find / no record / not exist / no such / cannot find / can't find / not be found / cannot be found / can't be found / couldn't be found |

## How to read this

- A 95% confidence interval says how far the true pass rate on questions like these could plausibly be from the measured one, given how few questions there are. It does not cover the questions being unrepresentative: they were written by the system's builders.
- The sign test asks whether grounding helped on more questions than it hurt by more than chance. A small p-value supports a real effect on these questions.
- Runs on the same questions are not independent samples, so they are reported side by side, not pooled.
- Scoring is by number and phrase matching; see each run's report for every answer and the scoring rules.

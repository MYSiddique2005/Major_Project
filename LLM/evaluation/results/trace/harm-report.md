# Harm check: the 86 questions with TRACE as the verifier

Run trace-1 (gemini-3.5-flash-lite, TRACE) against runs fixed-1..3 (same model, pattern verifier).

| Run | Passed | Figures not found in the data | Median seconds |
|---|---:|---:|---:|
| trace-1 | 84 of 86 | 14 of 320 | 15.9 |
| fixed-1 | 84 of 86 | 1 of 310 | 3.2 |
| fixed-2 | 86 of 86 | 3 of 342 | 3.1 |
| fixed-3 | 86 of 86 | 2 of 332 | 3.0 |

| Compared with | Only trace-1 passed | Only the other passed | p |
|---|---:|---:|---:|
| fixed-1 | 1 | 1 | 1 |
| fixed-2 | 0 | 2 | 0.5 |
| fixed-3 | 0 | 2 | 0.5 |

## Answers TRACE sent back for correction

| Question | Final answer | Figures not found in the data | Passed in fixed-1..3 |
|---|---|---|---|
| A13 | passed | none | 3 of 3 |
| C2 | passed | none | 3 of 3 |
| C5 | passed | none | 3 of 3 |
| C8 | passed | none | 3 of 3 |
| F16 | failed | none | 3 of 3 |
| F5 | passed | none | 3 of 3 |
| U1 | passed | none | 2 of 3 |
| U11 | passed | none | 3 of 3 |
| U12 | passed | 655.9, 690.6, 725.3, 760.0, 794.7, 829.4, 864.1, 898.8, 933.5, 968.2, 1,002.9, 1,037.6 | 3 of 3 |
| U3 | passed | none | 3 of 3 |

## Contradictions still shown after correction

- C8: "Medium risk" (P184): the data says High; "overdue" (P184): the data says none overdue
- U12: "maximum horizon of 26 weeks" (trend_forecast_weeks): the data says 12

Failed in trace-1: C11 (incomplete), F16 (ok)

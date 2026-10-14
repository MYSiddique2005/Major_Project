# Held-out test of verifier version 2 (sha256 cb172ddc410f0836522067309cfad6f40bb42d8d71ca414df529a8647b404f5e)

60 texts, rewrites by gemini-3.5-flash-lite (batched, five texts per request), file perturbations-v2-test.jsonl.

| Measure | Result |
|---|---|
| Valid injected errors | 59 of 60 |
| Detected, all injected errors | 16 of 59 (27%, 95% CI 17-40%) |
| Injected errors within the verifier's declared scope (a statement about a product's or supplier's current state, of one of its claim kinds) | 25 of 59 |
| **Detected within scope** | **15 of 25 (60%, 95% CI 41-77%)** |
| **False alarms on paraphrases** | **1 of 60 (2%, 95% CI 0-9%)** |

Out of scope (34): permissions and whether an action is possible (6), whether a product or record exists
(6), comparisons between suppliers or products (4), past events (2), periods and scenario premises (5),
changed numbers, which the figure check covers (6), approval and process statements (2), statements about a
group of products or a projection over time (3). One out-of-scope injection (55) produced a flag unrelated
to the change; it is counted as a false alarm in spirit, not as a detection.

Classification of the 59 (numbers as printed by the listing in claims_eval): in scope 7, 8, 9, 10, 12, 17,
19, 20, 21, 22, 24, 26, 29, 30, 32, 33, 37, 41, 42, 47, 50, 53, 57, 58, 59.

Causes of the 10 in-scope misses:

| Cause | Misses |
|---|---|
| A decimal point inside the sentence ("(3.7 days)", "5.64 units") ended the pattern's search, as if it were a full stop | 57, 50 and contributes to others |
| Long product names between "demand" and "falling" exceeded the 40-character gap | 24, 59 |
| "units on time" without a verb | 19 |
| "before stockout" (no "date" or "projected") not recognised | 21, 47 |
| stock position phrased with "combined" or "totaling" | 17, 32 |
| "depleted long after the next delivery arrives" not recognised | 33 |

These were fixed in version 3, which is tested on fresh texts not used in any earlier test.

# Mutation test, version 1 of the verifier: manual review of undetected mutants

Verifier file hash (sha256) for version 1: 3f0e59d6ecb5ce1225bd8015f9fb9daf4607849ec06516a280c81c0d9a53cc52.
Result before review: 96 of 271 mutants detected (35%). A seeded sample of 40 of the 175 undetected
mutants (listed in mutation-v1.md) was classified by hand.

| Class | Count | Sample numbers |
|---|---:|---|
| Real miss: a false statement about the product or supplier went unflagged | 24 | 1, 3, 5, 7, 10, 11, 14, 16, 18, 21, 22, 23, 24, 26, 27, 28, 31, 32, 34, 35, 36, 37, 38, 40 |
| Not an error: rule description, threshold, hypothetical, heading, process text, or a garbled projection | 16 | 2, 4, 6, 8, 9, 12, 13, 15, 17, 19, 20, 25, 29, 30, 33, 39 |

Estimate: 24/40 = 60% of the 175 undetected mutants are real errors, about 105. Assuming the 96 detected
mutants are real errors (each flag names the changed sentence), the verifier caught about
96 / (96 + 105) = 48% of real inserted errors.

Causes of the 24 real misses:

| Cause | Misses |
|---|---:|
| "on time" (the opposite of overdue) is not a recognised claim | 19 |
| "in stock" (the opposite of out of stock) is not a recognised claim | 1 |
| stock position against the reorder point is not checked | 1 |
| a statement about a group of products ("7 products ... at Critical or Low risk") is not attributed | 1 |
| filter too broad: "requires" before the claim made it count as a rule description (a headline and explanation run together without a full stop) | 1 |
| filter too broad: "for example" before a real data statement | 1 |

These causes were used to write version 2 of the verifier. Version 2 must therefore be tested on text
not used here: the model-written rewrites (claims_eval.py, part B).

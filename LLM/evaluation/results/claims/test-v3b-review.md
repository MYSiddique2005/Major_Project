# Version 3, second held-out test: classification of the injected errors

Verifier: `Backend/app/llm/claims.py`, sha256 3615459112b923c2287d8dc6f081c92f5f6ade1fcddc60a36ac6c4bc136c1b2e
(unchanged since the first v3 test). Texts: positions 120-183 of the seeded sample (64 texts not used in any
earlier test), rewrites by gemini-3.5-flash-lite, five texts per request (`test-v3b.jsonl`). Scored by
`python -m evaluation.claims_eval report --set test-v3b` (`report-test-v3b.md`).

Numbers below are positions in the list of injections in the order of `test-v3b.jsonl`. Scope rules are the
same as for the first v3 test (`summary.md`).

## In scope (31)

Detected (23): 2, 7, 11, 14, 21, 22, 23, 24, 27, 28, 29, 32, 33, 34, 37, 41, 43, 44, 46, 48, 52, 55, 61.

Missed (8):
- 25, 47: "is in danger of running out" for a product at Low stockout risk (no pattern for "in danger").
- 26: "days of cover are significantly higher than the supplier lead time" (the same phrasing missed in the first test).
- 39: "at Critical risk because there is stock on hand" (no pattern for "there is stock on hand").
- 56: "do not arrive until 2026-10-14, well before stock has run out" (insight).
- 59: "the total of stock on hand plus units on order is 720, which is above the reorder point" (the same kind missed in the first test).
- 60: "arrives after the projected stockout date" (stock already at Low Stock; the timing sentence was not recognised).
- 63: "Stockout risk: Low" written as a list field, without "level" or "risk of".

## Out of scope (33)

- Permissions and what the assistant can do: 4, 5, 36, 53.
- Whether something exists or is recorded or tracked: 1, 3, 8, 10, 38, 58.
- Scenario premises and hypotheticals: 9, 16, 18, 49, 54.
- Changed numbers (the figure check's job): 12, 19, 30, 51.
- Comparisons between products, suppliers or quantities: 15, 35, 40, 50, 57.
- Statements about a group of products: 20.
- Locations: 6, 13.
- Supplier-product relation, order validation rules: 17, 31, 45.
- Forecast method and errors: 42, 64.
- Sales versus purchases: 62.

## Result

- In scope: 23 of 31 detected (74%, 95% CI 57-86%). All injections: 23 of 64 (36%).
- False alarms on paraphrases: 0 of 64 (0%, 95% CI 0-6%).
- Both v3 tests together: 48 of 62 in-scope errors (77%, 95% CI 66-86%); false alarms 2 of 124 (2%, 0-6%).

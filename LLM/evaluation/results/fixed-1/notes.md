## About this run

The 86 questions on the system after the fixes described in `../extended-1/notes.md`, on
`gemini-3.5-flash-lite` with no fallback model. `fixed-2` and `fixed-3` repeat it unchanged.

## Corrections to the answer key

- **U10** (who approved a purchase order): the answer said the tools "do not record which specific user
  approved" it, which is correct, and the phrase list for "the data does not say" lacked "do not
  record". It was added and applied to the stored answer with `evaluation.rekey`; the answer was not
  collected again. The five questions that failed before the fixes (F12, A2, A6, A13, U10) were asked
  first, on their own, to check the fixes; the rest of the run followed.
- **C7** (overdue deliveries of a product and its supplier's reliability): the answer was complete and
  correct, reached by listing the product's purchase orders and the supplier performance instead of the
  product overview. The key had named only the overview tools as acceptable. The two tools were added.
- **U9** (customer return rate): the answer said the tools "do not track customer returns", which is
  correct; the phrase list had "does not track" but not "do not track". It was added.
- **G17**, without grounding: said rejection "requires a different user", the opposite of the rule, and
  had passed because the key looked only for the word "reject". The key now requires a statement that
  the creator can still reject. The same correction was applied to `extended-1`, where it changes nothing.

## Failures left standing

- **C11**: asked which products of a supplier are at Critical or High risk, the assistant searched the
  stock-risk list for the supplier's ID (`S010`). That search matches the supplier's name, not its ID,
  so it found nothing; it tried other searches until it ran out of the 8 allowed rounds. The first
  round had in fact returned every Critical and High product with its supplier ID.
- **U1**: asked for the stock of product P999, which does not exist, it answered that the product "has
  no stock records, so there are no units on hand", as if it existed with nothing in stock.

Both questions passed in `extended-1`. The system was not changed during the three `fixed` runs, so
that they stay comparable.
- **G6** (are purchase orders and stock levels real or simulated?), without grounding: the answer said
  they are "operational records ... rather than simulated data", the opposite of the truth, and had
  passed because it contains the word "simulated". The key now requires a statement that they are
  simulated and rejects negations ("rather than simulated", "whether ... simulated"). Applied to every
  run; it changes this answer and the same question in `fixed-2`, and nothing in the earlier runs.

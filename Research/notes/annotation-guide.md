# Annotation guide: is this sentence true?

Thank you for helping. This takes about 2-3 hours. You do not need to know the project's code.

## What you are doing

An AI assistant answered questions about a company's stock, sales and purchasing. You will read single
sentences from its answers and decide whether each one is **true according to the company's data and
rules**.

You get two files:

- `sheet-annotator-2.csv`: one row per sentence. Open it in LibreOffice Calc or Excel.
- `evidence.md`: for every answer, the question, the full answer, the data the assistant was given
  (tool results) and the current facts of each product (IDs like P082) and supplier (IDs like S004).
  Search it for the `answer_id` of the row (Ctrl+F).

Work alone. Do not discuss sentences with the other annotator until you have finished.

## The labels

Put exactly one of these words in the `label` column:

| Label | Use it when |
|---|---|
| `false` | The sentence states at least one thing the evidence **contradicts**: a wrong number, date, level, status, ID, name, comparison, rule or permission. |
| `true` | The sentence states at least one checkable thing, and **everything** checkable in it agrees with the evidence. |
| `no-claim` | The sentence states nothing that data or rules could confirm: advice ("you should reorder"), an offer, a greeting, a general explanation without a specific value. |
| `unsure` | The evidence is not enough to decide, or you cannot tell what the sentence means. Say why in `note`. |

For `false`, also fill in:

- `wrong_words`: the words that are wrong, copied from the sentence.
- `what_the_evidence_says`: the correct value, as the evidence gives it.

## Rules

1. **Judge only against the evidence.** Not against what seems sensible, and not against your own
   knowledge of business.
2. **One wrong thing makes the sentence false**, even if the rest is right.
3. **Rounding is fine.** "6.7 days" for 6.68 is true; "about 7 days" for 6.68 is true. "9 days" for 6.68
   is false.
4. **Comparisons must hold.** "Stock (71) is above the reorder point (112)" is false, even though both
   numbers are right.
5. **The past.** If the sentence talks about the past ("ran out last week") and the evidence only shows
   today, use `unsure`, unless an order's history in the evidence settles it (delivery dates are kept).
6. **What-if sentences** ("if demand rises 20%, 314 units would go unmet") are true if the tool result for
   that scenario in the evidence gives the same figure.
7. **Rules and permissions** (thresholds such as "rising sharply at 15%", "procurement managers can approve
   orders created by someone else") are in the evidence where the assistant used the knowledge base; if a
   rule is not shown anywhere, use `unsure`.
8. **Product or order that does not exist.** If the evidence says a product, supplier or order is "not in
   the system" and the sentence treats it as real, the sentence is false.
9. Do not change the `row`, `answer_id`, `question` or `sentence` columns.

## Examples

| Sentence | Evidence | Label | wrong_words | what_the_evidence_says |
|---|---|---|---|---|
| P082 has 0 units on hand and is at Critical stockout risk. | on_hand 0, risk_level Critical | `true` | | |
| P004 has 71 units on hand, above the reorder point of 112 units. | on_hand 71, reorder_point 112 | `false` | above | 71 is below 112 |
| Northwind Electric Cars (S010) has 24 open orders, 9 of them overdue. | open_orders 24, overdue_orders 7 | `false` | 9 | 7 overdue |
| You may want to expedite the overdue order. | | `no-claim` | | |
| P032 did not run out of stock last week. | only today's stock shown | `unsure` | | |
| Demand for P045 is rising sharply at 66%. | demand_trend_pct 66.0; rule: rising sharply at 15% or more | `true` | | |

## When you finish

Save the file as CSV (keep the same name) and send it back. Your labels will be compared with the other
annotator's to measure agreement (Cohen's kappa). Your name will be in the acknowledgements unless you
prefer otherwise.

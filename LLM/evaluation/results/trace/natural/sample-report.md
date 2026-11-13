# Natural errors: the random sample

300 sentences drawn with seed 2026 from the 590 stored answers (evaluation/trace_natural.py, step sample), labelled before any method's output on them existed, by Claude Opus 5.5 following Research/notes/annotation-guide.md, with the system's rules and permissions (Backend/app/knowledge/content.py, Backend/app/security/permissions.py) as the reference for policy statements. Every label, with the wrong words and the evidence it rests on, is in labels-annotator-1.jsonl. A human second annotation has not been done.

| Answers | Sentences | true | false | no-claim | unsure | False among checkable |
|---|---:|---:|---:|---:|---:|---:|
| all | 300 | 242 | 19 | 34 | 5 | 19/261 (7.3%) |
| with the knowledge base | 222 | 202 | 5 | 13 | 2 | 5/207 (2.4%) |
| without the knowledge base | 78 | 40 | 14 | 21 | 3 | 14/54 (25.9%) |
| Gemini runs (TRACE development answers) | 245 | 199 | 19 | 23 | 4 | 19/218 (8.7%) |
| Gemma run (never seen in development) | 55 | 43 | 0 | 11 | 1 | 0/43 (0.0%) |

## Before the label corrections

After all methods had run, a consistency check, prompted while labelling the sentences MiniCheck flagged, found 9 sentences labelled true that state overdue units as part of the units on order; in the system they are separate amounts (Backend/app/analytics/stock_risk.py, inbound_units: ordered, not delivered, not overdue). They were relabelled false (5 of them in this sample; see label-corrections.jsonl). With the original labels:

| Answers | Sentences | true | false | no-claim | unsure | False among checkable |
|---|---:|---:|---:|---:|---:|---:|
| all | 300 | 247 | 14 | 34 | 5 | 14/261 (5.4%) |
| with the knowledge base | 222 | 204 | 3 | 13 | 2 | 3/207 (1.4%) |
| without the knowledge base | 78 | 43 | 11 | 21 | 3 | 11/54 (20.4%) |
| Gemini runs (TRACE development answers) | 245 | 204 | 14 | 23 | 4 | 14/218 (6.4%) |
| Gemma run (never seen in development) | 55 | 43 | 0 | 11 | 1 | 0/43 (0.0%) |

## The false sentences

- extended-1/A2/grounded: "40 units" — suggested_order_quantity 1400
- extended-1/C1/grounded: "720 overdue inbound units out of 1830 units on order" — the overdue units are not part of the units on order: on-order counts open orders that are not overdue (stock_risk.inbound_units)
- extended-1/C1/ungrounded: "720 overdue inbound units out of 1,830 inbound units" — the overdue units are not part of the units on order: on-order counts open orders that are not overdue (stock_risk.inbound_units)
- extended-1/G19/ungrounded: "approved and is currently being prepared, picked, or packed for shipment" — knowledge base: Processing once shipped and on its way to the customer
- extended-1/G8/ungrounded: "refer to the same concept" — knowledge base: two different figures (stock-record reorder level vs computed reorder point)
- fixed-1/C1/grounded: "720 overdue inbound units out of 1,830 on order" — the overdue units are not part of the units on order: on-order counts open orders that are not overdue (stock_risk.inbound_units)
- fixed-1/G15/ungrounded: "or delayed" — knowledge base: unserved demand is lost, not back-ordered
- fixed-1/G18/ungrounded: "call it once per recommendation, and you can propose one recommendation per turn" — rule max_drafts_per_message = 3
- fixed-1/G6/ungrounded: "operational records managed within the ERP database rather than simulated data" — knowledge base: purchase orders and stock levels are simulated
- fixed-1/G8/ungrounded: "used interchangeably" — knowledge base: reorder level and reorder point are different figures
- fixed-2/C1/ungrounded: "67 overdue inbound units out of 79 total inbound units" — the overdue units are not part of the units on order: on-order counts open orders that are not overdue (stock_risk.inbound_units)
- fixed-2/C1/ungrounded: "720 overdue inbound units out of 1830 total inbound units" — the overdue units are not part of the units on order: on-order counts open orders that are not overdue (stock_risk.inbound_units)
- fixed-2/C16/ungrounded: "20% or more" — rule rising_sharply_pct = 15
- fixed-2/G18/ungrounded: "one draft purchase order" — rule max_drafts_per_message = 3
- fixed-2/U11/grounded: "stock status is Low Stock because the 125 units are below the reorder level of 92" — 125 is above the reorder level 92 (status In Stock)
- fixed-3/G14/ungrounded: "or Critical" — Critical means nothing on hand while selling, whatever is on order
- fixed-3/G15/ungrounded: "or backorders" — knowledge base: unserved demand is lost, not back-ordered
- fixed-3/G15/ungrounded: "approved or" — only status Ordered counts as incoming
- fixed-3/U11/grounded: "low stock because current stock is below the reorder level of 92" — 125 is above the reorder level 92 (status In Stock)

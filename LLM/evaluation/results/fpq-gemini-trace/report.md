# Evaluation report: fpq-gemini-trace

44 answers (44 grounded, 0 ungrounded). Models that answered: gemini-3.5-flash-lite (44).
Collected between 2026-11-03T12:24:44 and 2026-11-04T10:46:11.

## Results with grounding (the system as built)

| Group | Questions | Passed | Facts found | Right tool used | Unsupported figures | Avg time | Avg tool calls |
|---|---:|---:|---:|---:|---:|---:|---:|
| Grounding (terms and rules) | 0 | - | - | - | - | - | - |
| Factual (one module) | 0 | - | - | - | - | - | - |
| Cross-module reasoning | 0 | - | - | - | - | - | - |
| Controlled actions and permissions | 0 | - | - | - | - | - | - |
| Abstention (data cannot answer) | 0 | - | - | - | - | - | - |
| **All** | 44 | 93% | 93% | - | 9 of 260 | 19s | 1.5 |

## Effect of grounding (RQ1)

No question has been answered in both conditions yet.

## Proactive insights (RQ3)

From the 38 insights stored by 8 completed scans (4 scans failed, mostly on rate limits).

| Measure | Result |
|---|---|
| Insights whose subject was a finding the analytics had flagged | 38 of 38 (enforced by the server) |
| Evidence from two or more modules | 38 of 38 |
| Figures in the text found in the system data | 587 of 587 |
| Reorder insights whose quantity equals the reorder rule | 5 of 5 |
| Actions recommended | expedite_delivery: 33, reorder: 5 |

Detection itself (which products and suppliers are flagged) is done by the rule-based analytics, so its precision and recall are properties of those rules, not of the model. What the model adds, and what is measured here, is the explanation and the recommended action.

## Every answer

| Case | Condition | Role | Result | Facts | Tools called | Unsupported figures | Model |
|---|---|---|---|---|---|---|---|
| FD1 | grounded | admin | pass | 1/1 | get_product_overview, get_stock_risk | 103 | gemini-3.5-flash-lite |
| FD10 | grounded | admin | pass | 2/2 | get_product_overview | - | gemini-3.5-flash-lite |
| FD11 | grounded | admin | pass | 2/2 | get_product_overview | - | gemini-3.5-flash-lite |
| FD12 | grounded | admin | pass | 1/1 | run_what_if, get_product_overview, list_purchase_orders | - | gemini-3.5-flash-lite |
| FD13 | grounded | admin | pass | 1/1 | run_what_if, get_product_overview | - | gemini-3.5-flash-lite |
| FD2 | grounded | admin | pass | 1/1 | get_product_overview | - | gemini-3.5-flash-lite |
| FD3 | grounded | admin | pass | 1/1 | search_products, get_product_overview | - | gemini-3.5-flash-lite |
| FD4 | grounded | admin | pass | 1/1 | get_product_overview, propose_recommendation | 216 | gemini-3.5-flash-lite |
| FD5 | grounded | admin | pass | 1/1 | get_product_overview | 158.62, 55.62 | gemini-3.5-flash-lite |
| FD6 | grounded | admin | FAIL: missing 80 | 0/1 | get_product_overview | 26, 132.86, 163.86 | gemini-3.5-flash-lite |
| FD7 | grounded | admin | pass | 1/1 | get_product_overview, search_knowledge, run_what_if | 257.64, 260 | gemini-3.5-flash-lite |
| FD8 | grounded | admin | pass | 1/1 | list_stock_risk | - | gemini-3.5-flash-lite |
| FD9 | grounded | admin | pass | 2/2 | get_product_overview | - | gemini-3.5-flash-lite |
| FP1 | grounded | admin | pass | 1/1 | - | - | gemini-3.5-flash-lite |
| FP10 | grounded | admin | pass | 1/1 | - | - | gemini-3.5-flash-lite |
| FP11 | grounded | admin | pass | 1/1 | - | - | gemini-3.5-flash-lite |
| FP12 | grounded | admin | pass | 1/1 | search_knowledge | - | gemini-3.5-flash-lite |
| FP2 | grounded | admin | pass | 1/1 | - | - | gemini-3.5-flash-lite |
| FP3 | grounded | procurement | pass | 1/1 | - | - | gemini-3.5-flash-lite |
| FP4 | grounded | admin | pass | 1/1 | - | - | gemini-3.5-flash-lite |
| FP5 | grounded | admin | pass | 1/1 | - | - | gemini-3.5-flash-lite |
| FP6 | grounded | admin | pass | 1/1 | - | - | gemini-3.5-flash-lite |
| FP7 | grounded | admin | pass | 1/1 | - | - | gemini-3.5-flash-lite |
| FP8 | grounded | admin | pass | 1/1 | search_knowledge | - | gemini-3.5-flash-lite |
| FP9 | grounded | admin | pass | 1/1 | - | - | gemini-3.5-flash-lite |
| FS1 | grounded | admin | pass | 2/2 | get_product_overview, get_demand_forecast, search_knowledge | - | gemini-3.5-flash-lite |
| FS10 | grounded | admin | pass | 2/2 | get_product_overview | - | gemini-3.5-flash-lite |
| FS11 | grounded | admin | pass | 2/2 | get_product_overview | - | gemini-3.5-flash-lite |
| FS12 | grounded | admin | pass | 2/2 | get_product_overview | - | gemini-3.5-flash-lite |
| FS13 | grounded | admin | pass | 1/1 | list_supplier_performance, list_suppliers | - | gemini-3.5-flash-lite |
| FS14 | grounded | admin | pass | 1/1 | list_supplier_performance | - | gemini-3.5-flash-lite |
| FS16 | grounded | admin | FAIL: missing 85; missing overdue | 0/2 | search_products, list_purchase_orders | - | gemini-3.5-flash-lite |
| FS17 | grounded | admin | FAIL: missing 63; missing overdue | 0/2 | search_products, list_purchase_orders | - | gemini-3.5-flash-lite |
| FS18 | grounded | admin | pass | 2/2 | search_products, list_purchase_orders | - | gemini-3.5-flash-lite |
| FS19 | grounded | admin | pass | 1/1 | get_product_overview, search_products | - | gemini-3.5-flash-lite |
| FS2 | grounded | admin | pass | 2/2 | search_products, get_product_overview, get_demand_forecast | - | gemini-3.5-flash-lite |
| FS20 | grounded | admin | pass | 1/1 | get_product_overview, search_products | - | gemini-3.5-flash-lite |
| FS3 | grounded | admin | pass | 2/2 | get_product_overview, get_demand_forecast | - | gemini-3.5-flash-lite |
| FS4 | grounded | admin | pass | 2/2 | get_product_overview, get_demand_forecast | - | gemini-3.5-flash-lite |
| FS5 | grounded | admin | pass | 1/1 | get_product_overview | - | gemini-3.5-flash-lite |
| FS6 | grounded | admin | pass | 1/1 | get_product_overview | - | gemini-3.5-flash-lite |
| FS7 | grounded | admin | pass | 1/1 | get_product_overview, get_stock_risk | - | gemini-3.5-flash-lite |
| FS8 | grounded | admin | pass | 1/1 | get_product_overview, get_stock_risk | - | gemini-3.5-flash-lite |
| FS9 | grounded | admin | pass | 2/2 | get_product_overview | - | gemini-3.5-flash-lite |

## Failed answers in full

### FS16 (grounded, gemini-3.5-flash-lite)

**Question:** Since nothing on order for RC toy sedan car with remote control (Black) 1/50 scale (P058) is overdue, when is its next delivery due?

**Expected facts:** [[85], ['overdue']]

**Answer:**

> The next delivery for RC toy sedan car with remote control (Black) 1/50 scale (P058) is due on 2026-10-15 under purchase order PO-18258 for 93 units.

### FS17 (grounded, gemini-3.5-flash-lite)

**Question:** Since nothing on order for RC toy sedan car with remote control (Red) 1/50 scale (P059) is overdue, when is its next delivery due?

**Expected facts:** [[63], ['overdue']]

**Answer:**

> The next delivery for RC toy sedan car with remote control (Red) 1/50 scale (P059) is due on 2026-10-14 (purchase order PO-18233).

### FD6 (grounded, gemini-3.5-flash-lite)

**Question:** Why does the reorder rule suggest 170 units for Developer joke mug - fun was unexpected at this time (White) (P034)?

**Expected facts:** [[80]]

**Answer:**

> The reorder rule target for Developer joke mug - fun was unexpected at this time (White) (P034) is calculated using the formula: average daily demand x (lead time + 14 days review period) + safety stock, rounded up to a multiple of 10. 
> 
> Based on the system figures, the average daily demand is 5.11 units, the lead time is 12 days, and the safety stock is 31 units. Multiplying 5.11 by the 26 days (12 days lead time plus 14 days review period) gives approximately 132.86 units, and adding the 31 units of safety stock brings the total to 163.86 units, which rounds up to 170 units as the target level.


## How to read this

- **Passed** means every expected fact was found, a tool that can answer the question was used, nothing forbidden happened, and (for action cases) the right thing was or was not done.
- **Facts found** are matched by number (within 1%) or by phrase. A correct answer worded in a way the phrase list does not anticipate is marked as missing, so pass rates can understate.
- **Unsupported figures** are numbers in an answer that appear in none of the question, the tool results and the knowledge passages. Figures the model derives by arithmetic count as unsupported; the check cannot tell a derived figure from an invented one, or a real figure used in the wrong place.
- Each question was asked once per condition. The model is not deterministic, so a single run is one sample.
- When more than one model answered, differences between questions are partly differences between models.

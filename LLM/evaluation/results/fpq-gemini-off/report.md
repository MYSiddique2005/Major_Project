# Evaluation report: fpq-gemini-off

44 answers (44 grounded, 0 ungrounded). Models that answered: gemini-3.5-flash-lite (44).
Collected between 2026-11-03T11:18:08 and 2026-11-03T11:25:33.

## Results with grounding (the system as built)

| Group | Questions | Passed | Facts found | Right tool used | Unsupported figures | Avg time | Avg tool calls |
|---|---:|---:|---:|---:|---:|---:|---:|
| Grounding (terms and rules) | 0 | - | - | - | - | - | - |
| Factual (one module) | 0 | - | - | - | - | - | - |
| Cross-module reasoning | 0 | - | - | - | - | - | - |
| Controlled actions and permissions | 0 | - | - | - | - | - | - |
| Abstention (data cannot answer) | 0 | - | - | - | - | - | - |
| **All** | 44 | 89% | 91% | - | 7 of 287 | 10s | 1.3 |

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
| FD1 | grounded | admin | pass | 1/1 | get_product_overview, search_knowledge | 103 | gemini-3.5-flash-lite |
| FD10 | grounded | admin | pass | 2/2 | get_product_overview | - | gemini-3.5-flash-lite |
| FD11 | grounded | admin | pass | 2/2 | get_product_overview | - | gemini-3.5-flash-lite |
| FD12 | grounded | admin | pass | 1/1 | run_what_if, get_product_overview, list_purchase_orders | - | gemini-3.5-flash-lite |
| FD13 | grounded | admin | pass | 1/1 | run_what_if, get_product_overview | - | gemini-3.5-flash-lite |
| FD2 | grounded | admin | FAIL: missing 80 | 0/1 | get_product_overview | - | gemini-3.5-flash-lite |
| FD3 | grounded | admin | pass | 1/1 | search_products, get_product_overview | - | gemini-3.5-flash-lite |
| FD4 | grounded | admin | pass | 1/1 | get_product_overview | - | gemini-3.5-flash-lite |
| FD5 | grounded | admin | pass | 1/1 | get_product_overview, search_knowledge | - | gemini-3.5-flash-lite |
| FD6 | grounded | admin | FAIL: missing 80 | 0/1 | get_product_overview | 26, 132.89714285714285, 163.89714285714285 | gemini-3.5-flash-lite |
| FD7 | grounded | admin | pass | 1/1 | get_product_overview, search_knowledge | 211.64, 257.64 | gemini-3.5-flash-lite |
| FD8 | grounded | admin | pass | 1/1 | list_stock_risk | - | gemini-3.5-flash-lite |
| FD9 | grounded | admin | pass | 2/2 | get_product_overview | - | gemini-3.5-flash-lite |
| FP1 | grounded | admin | pass | 1/1 | - | - | gemini-3.5-flash-lite |
| FP10 | grounded | admin | pass | 1/1 | search_knowledge | - | gemini-3.5-flash-lite |
| FP11 | grounded | admin | pass | 1/1 | - | - | gemini-3.5-flash-lite |
| FP12 | grounded | admin | pass | 1/1 | - | - | gemini-3.5-flash-lite |
| FP2 | grounded | admin | pass | 1/1 | - | - | gemini-3.5-flash-lite |
| FP3 | grounded | procurement | FAIL: missing procurement:approve / can approve | 0/1 | - | - | gemini-3.5-flash-lite |
| FP4 | grounded | admin | pass | 1/1 | - | - | gemini-3.5-flash-lite |
| FP5 | grounded | admin | pass | 1/1 | - | - | gemini-3.5-flash-lite |
| FP6 | grounded | admin | pass | 1/1 | - | - | gemini-3.5-flash-lite |
| FP7 | grounded | admin | pass | 1/1 | - | - | gemini-3.5-flash-lite |
| FP8 | grounded | admin | pass | 1/1 | search_knowledge | - | gemini-3.5-flash-lite |
| FP9 | grounded | admin | pass | 1/1 | - | - | gemini-3.5-flash-lite |
| FS1 | grounded | admin | pass | 2/2 | get_product_overview, get_demand_forecast, search_knowledge | - | gemini-3.5-flash-lite |
| FS10 | grounded | admin | pass | 2/2 | get_product_overview | 6 | gemini-3.5-flash-lite |
| FS11 | grounded | admin | pass | 2/2 | get_product_overview | - | gemini-3.5-flash-lite |
| FS12 | grounded | admin | pass | 2/2 | get_product_overview | - | gemini-3.5-flash-lite |
| FS13 | grounded | admin | pass | 1/1 | list_supplier_performance | - | gemini-3.5-flash-lite |
| FS14 | grounded | admin | pass | 1/1 | list_supplier_performance | - | gemini-3.5-flash-lite |
| FS16 | grounded | admin | pass | 2/2 | search_products, list_purchase_orders | - | gemini-3.5-flash-lite |
| FS17 | grounded | admin | FAIL: missing overdue | 1/2 | search_products, list_purchase_orders | - | gemini-3.5-flash-lite |
| FS18 | grounded | admin | FAIL: missing 67 | 1/2 | search_products, list_purchase_orders | - | gemini-3.5-flash-lite |
| FS19 | grounded | admin | pass | 1/1 | get_product_overview, search_products, list_stock_risk | - | gemini-3.5-flash-lite |
| FS2 | grounded | admin | pass | 2/2 | search_products, get_sales_summary, search_knowledge, get_product_overview | - | gemini-3.5-flash-lite |
| FS20 | grounded | admin | pass | 1/1 | get_product_overview, search_products | - | gemini-3.5-flash-lite |
| FS3 | grounded | admin | pass | 2/2 | get_product_overview | - | gemini-3.5-flash-lite |
| FS4 | grounded | admin | pass | 2/2 | get_product_overview, get_demand_forecast, search_sales_orders | - | gemini-3.5-flash-lite |
| FS5 | grounded | admin | pass | 1/1 | get_product_overview | - | gemini-3.5-flash-lite |
| FS6 | grounded | admin | pass | 1/1 | get_product_overview | - | gemini-3.5-flash-lite |
| FS7 | grounded | admin | pass | 1/1 | get_product_overview, get_stock_risk | - | gemini-3.5-flash-lite |
| FS8 | grounded | admin | pass | 1/1 | get_product_overview | - | gemini-3.5-flash-lite |
| FS9 | grounded | admin | pass | 2/2 | get_product_overview | - | gemini-3.5-flash-lite |

## Failed answers in full

### FS17 (grounded, gemini-3.5-flash-lite)

**Question:** Since nothing on order for RC toy sedan car with remote control (Red) 1/50 scale (P059) is overdue, when is its next delivery due?

**Expected facts:** [[63], ['overdue']]

**Answer:**

> The next delivery for RC toy sedan car with remote control (Red) 1/50 scale (P059) is due on 2026-10-04 under purchase order PO-18063 for 63 units, followed by a second delivery on 2026-10-14 under purchase order PO-18233 for 73 units.

### FS18 (grounded, gemini-3.5-flash-lite)

**Question:** Since nothing on order for RC toy sedan car with remote control (Blue) 1/50 scale (P060) is overdue, when is its next delivery due?

**Expected facts:** [[67], ['overdue']]

**Answer:**

> The next delivery for RC toy sedan car with remote control (Blue) 1/50 scale (P060) is due on 2026-10-19 under purchase order PO-18302 for 74 units from Northwind Electric Cars (S010). 
> 
> While purchase order PO-18020 was expected earlier on 2026-10-01, that order is currently overdue, and PO-18302 represents the next scheduled delivery that is not overdue.

### FP3 (grounded, gemini-3.5-flash-lite)

**Question:** Since procurement managers cannot approve purchase orders, who approves them in this system?

**Expected facts:** [['re:(?:procurement managers?|you|they)\\s+(?:also\\s+)?(?:can|may|are able to|do have|have the right to|are allowed to)(?:\\s+\\w+){0,4}\\s+approv', 'procurement:approve', 'can approve']]

**Answer:**

> Approval rules state that an approval can be decided while a purchase order is Pending Approval. Separation of duties is enforced, meaning that the user who created or submitted a purchase order cannot approve it, so a second approver is needed, although they may still reject it.

### FD2 (grounded, gemini-3.5-flash-lite)

**Question:** Why does the reorder rule suggest ordering nothing for Developer joke mug - fun was unexpected at this time (White) (P034)?

**Expected facts:** [[80]]

**Answer:**

> The reorder rule suggests ordering nothing for Developer joke mug - fun was unexpected at this time (White), P034, because the product's total stock position (stock on hand plus units on order, overdue units, and units awaiting approval) is above the reorder point. 
> 
> According to the reorder suggestion rule, a reorder is suggested only when the total of stock on hand (93 units), units on order (0), overdue units (0), and units awaiting approval (0), which equals 93 units, is at or below the reorder point of 93 units. Because the total of 93 is not below 93, no reorder is triggered.

### FD6 (grounded, gemini-3.5-flash-lite)

**Question:** Why does the reorder rule suggest 170 units for Developer joke mug - fun was unexpected at this time (White) (P034)?

**Expected facts:** [[80]]

**Answer:**

> The reorder rule suggests a target level calculation of average daily demand multiplied by the sum of the lead time and a 14-day review period, plus safety stock, rounded up to a multiple of 10. 
> 
> For Developer joke mug - fun was unexpected at this time (White) (P034), the figures from the system are:
> - Average daily demand over the last 28 days is 5.111428571428571 units.
> - Supplier lead time is 12 days.
> - Safety stock is 31 units.
> 
> Multiplying the average daily demand of 5.111428571428571 by the 26-day period (12 days lead time plus the 14-day review period) gives 132.89714285714285 units. Adding the 31 units of safety stock gives 163.89714285714285 units. Rounded up to the nearest multiple of 10, this results in the target level of 170 units.


## How to read this

- **Passed** means every expected fact was found, a tool that can answer the question was used, nothing forbidden happened, and (for action cases) the right thing was or was not done.
- **Facts found** are matched by number (within 1%) or by phrase. A correct answer worded in a way the phrase list does not anticipate is marked as missing, so pass rates can understate.
- **Unsupported figures** are numbers in an answer that appear in none of the question, the tool results and the knowledge passages. Figures the model derives by arithmetic count as unsupported; the check cannot tell a derived figure from an invented one, or a real figure used in the wrong place.
- Each question was asked once per condition. The model is not deterministic, so a single run is one sample.
- When more than one model answered, differences between questions are partly differences between models.

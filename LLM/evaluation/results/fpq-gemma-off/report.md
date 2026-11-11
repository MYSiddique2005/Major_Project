# Evaluation report: fpq-gemma-off

44 answers (44 grounded, 0 ungrounded). Models that answered: gemma-4-31b-it (44).
Collected between 2026-10-27T07:02:46 and 2026-10-29T10:37:56.

## Results with grounding (the system as built)

| Group | Questions | Passed | Facts found | Right tool used | Unsupported figures | Avg time | Avg tool calls |
|---|---:|---:|---:|---:|---:|---:|---:|
| Grounding (terms and rules) | 0 | - | - | - | - | - | - |
| Factual (one module) | 0 | - | - | - | - | - | - |
| Cross-module reasoning | 0 | - | - | - | - | - | - |
| Controlled actions and permissions | 0 | - | - | - | - | - | - |
| Abstention (data cannot answer) | 0 | - | - | - | - | - | - |
| **All** | 44 | 93% | 97% | - | 10 of 256 | 105s | 1.2 |

## Effect of grounding (RQ1)

No question has been answered in both conditions yet.

## Proactive insights (RQ3)

From the 38 insights stored by 8 completed scans (5 scans failed, mostly on rate limits).

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
| FD1 | grounded | admin | pass | 1/1 | get_product_overview, get_stock_risk | 103 | gemma-4-31b-it |
| FD10 | grounded | admin | pass | 2/2 | get_product_overview | - | gemma-4-31b-it |
| FD11 | grounded | admin | pass | 2/2 | get_product_overview | - | gemma-4-31b-it |
| FD12 | grounded | admin | pass | 1/1 | get_product_overview, run_what_if | 103 | gemma-4-31b-it |
| FD13 | grounded | admin | pass | 1/1 | get_product_overview, run_what_if | 131 | gemma-4-31b-it |
| FD2 | grounded | admin | pass | 1/1 | get_product_overview | - | gemma-4-31b-it |
| FD3 | grounded | admin | pass | 1/1 | get_product_overview | - | gemma-4-31b-it |
| FD4 | grounded | admin | pass | 1/1 | get_product_overview | - | gemma-4-31b-it |
| FD5 | grounded | admin | pass | 1/1 | get_product_overview, get_stock_risk | 188.54, 103, 87 | gemma-4-31b-it |
| FD6 | grounded | admin | pass | 1/1 | get_product_overview, get_stock_risk | 164, 71 | gemma-4-31b-it |
| FD7 | grounded | admin | pass | 1/1 | get_product_overview, get_inventory, search_products, get_stock_risk | 257.64, 121.64 | gemma-4-31b-it |
| FD8 | grounded | admin | pass | 1/1 | list_stock_risk | - | gemma-4-31b-it |
| FD9 | grounded | admin | pass | 2/2 | get_product_overview | - | gemma-4-31b-it |
| FP1 | grounded | admin | pass | 1/1 | - | - | gemma-4-31b-it |
| FP10 | grounded | admin | pass | 1/1 | - | - | gemma-4-31b-it |
| FP11 | grounded | admin | pass | 1/1 | - | - | gemma-4-31b-it |
| FP12 | grounded | admin | pass | 1/1 | - | - | gemma-4-31b-it |
| FP2 | grounded | admin | pass | 1/1 | - | - | gemma-4-31b-it |
| FP3 | grounded | procurement | pass | 1/1 | - | - | gemma-4-31b-it |
| FP4 | grounded | admin | pass | 1/1 | - | - | gemma-4-31b-it |
| FP5 | grounded | admin | pass | 1/1 | search_knowledge | - | gemma-4-31b-it |
| FP6 | grounded | admin | pass | 1/1 | search_knowledge | - | gemma-4-31b-it |
| FP7 | grounded | admin | pass | 1/1 | - | - | gemma-4-31b-it |
| FP8 | grounded | admin | pass | 1/1 | - | - | gemma-4-31b-it |
| FP9 | grounded | admin | pass | 1/1 | - | - | gemma-4-31b-it |
| FS1 | grounded | admin | pass | 2/2 | get_product_overview | - | gemma-4-31b-it |
| FS10 | grounded | admin | pass | 2/2 | get_product_overview | - | gemma-4-31b-it |
| FS11 | grounded | admin | pass | 2/2 | get_product_overview | - | gemma-4-31b-it |
| FS12 | grounded | admin | pass | 2/2 | get_inventory | - | gemma-4-31b-it |
| FS13 | grounded | admin | pass | 1/1 | list_supplier_performance | - | gemma-4-31b-it |
| FS14 | grounded | admin | pass | 1/1 | list_supplier_performance | - | gemma-4-31b-it |
| FS16 | grounded | admin | FAIL: missing 85 | 1/2 | list_purchase_orders | - | gemma-4-31b-it |
| FS17 | grounded | admin | FAIL: missing 63 | 1/2 | list_purchase_orders | - | gemma-4-31b-it |
| FS18 | grounded | admin | FAIL: missing 67 | 1/2 | list_purchase_orders | - | gemma-4-31b-it |
| FS19 | grounded | admin | pass | 1/1 | get_product_overview, search_products | - | gemma-4-31b-it |
| FS2 | grounded | admin | pass | 2/2 | get_product_overview, get_demand_forecast, get_sales_summary | - | gemma-4-31b-it |
| FS20 | grounded | admin | pass | 1/1 | get_product_overview, search_products | - | gemma-4-31b-it |
| FS3 | grounded | admin | pass | 2/2 | get_product_overview, get_sales_summary, get_demand_forecast | - | gemma-4-31b-it |
| FS4 | grounded | admin | pass | 2/2 | get_product_overview, get_sales_summary | - | gemma-4-31b-it |
| FS5 | grounded | admin | pass | 1/1 | get_product_overview, get_stock_risk | - | gemma-4-31b-it |
| FS6 | grounded | admin | pass | 1/1 | get_product_overview | - | gemma-4-31b-it |
| FS7 | grounded | admin | pass | 1/1 | get_product_overview | - | gemma-4-31b-it |
| FS8 | grounded | admin | pass | 1/1 | get_stock_risk, get_product_overview | - | gemma-4-31b-it |
| FS9 | grounded | admin | pass | 2/2 | get_product_overview | - | gemma-4-31b-it |

## Failed answers in full

### FS16 (grounded, gemma-4-31b-it)

**Question:** Since nothing on order for RC toy sedan car with remote control (Black) 1/50 scale (P058) is overdue, when is its next delivery due?

**Expected facts:** [[85], ['overdue']]

**Answer:**

> The next delivery for RC toy sedan car with remote control (Black) 1/50 scale (P058) is due on 2026-10-15 (PO-18258).
> 
> Please note that purchase order PO-18062 was expected on 2026-10-04 and is currently overdue.

### FS17 (grounded, gemma-4-31b-it)

**Question:** Since nothing on order for RC toy sedan car with remote control (Red) 1/50 scale (P059) is overdue, when is its next delivery due?

**Expected facts:** [[63], ['overdue']]

**Answer:**

> The next delivery for RC toy sedan car with remote control (Red) 1/50 scale (P059) is due on 2026-10-14 (PO-18233).
> 
> Note that contrary to the premise, there is one order (PO-18063) that is currently overdue, as its expected delivery date was 2026-10-04.

### FS18 (grounded, gemma-4-31b-it)

**Question:** Since nothing on order for RC toy sedan car with remote control (Blue) 1/50 scale (P060) is overdue, when is its next delivery due?

**Expected facts:** [[67], ['overdue']]

**Answer:**

> The next delivery for RC toy sedan car with remote control (Blue) 1/50 scale (P060) is due on 2026-10-19 (PO-18302). 
> 
> However, contrary to your premise, there is one order that is overdue: PO-18020 was expected on 2026-10-01.


## How to read this

- **Passed** means every expected fact was found, a tool that can answer the question was used, nothing forbidden happened, and (for action cases) the right thing was or was not done.
- **Facts found** are matched by number (within 1%) or by phrase. A correct answer worded in a way the phrase list does not anticipate is marked as missing, so pass rates can understate.
- **Unsupported figures** are numbers in an answer that appear in none of the question, the tool results and the knowledge passages. Figures the model derives by arithmetic count as unsupported; the check cannot tell a derived figure from an invented one, or a real figure used in the wrong place.
- Each question was asked once per condition. The model is not deterministic, so a single run is one sample.
- When more than one model answered, differences between questions are partly differences between models.

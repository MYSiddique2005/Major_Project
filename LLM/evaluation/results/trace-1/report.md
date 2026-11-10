# Evaluation report: trace-1

86 answers (86 grounded, 0 ungrounded). Models that answered: gemini-3.5-flash-lite (86).
Collected between 2026-11-11T01:15:45 and 2026-11-11T01:51:27.

## Results with grounding (the system as built)

| Group | Questions | Passed | Facts found | Right tool used | Unsupported figures | Avg time | Avg tool calls |
|---|---:|---:|---:|---:|---:|---:|---:|
| Grounding (terms and rules) | 25 | 100% | 100% | - | 0 of 30 | 11s | 0.0 |
| Factual (one module) | 17 | 94% | 94% | 100% | 0 of 47 | 16s | 1.1 |
| Cross-module reasoning | 17 | 94% | 94% | 100% | 2 of 168 | 48s | 2.2 |
| Controlled actions and permissions | 15 | 100% | 100% | 100% | 0 of 37 | 25s | 1.6 |
| Abstention (data cannot answer) | 12 | 100% | 100% | 100% | 12 of 38 | 33s | 1.8 |
| **All** | 86 | 98% | 98% | 100% | 14 of 320 | 25s | 1.2 |

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
| A1 | grounded | procurement | pass | 3/3 | get_product_overview, draft_purchase_order | - | gemini-3.5-flash-lite |
| A10 | grounded | inventory | pass | 1/1 | get_sales_summary | - | gemini-3.5-flash-lite |
| A11 | grounded | procurement | pass | 1/1 | - | - | gemini-3.5-flash-lite |
| A12 | grounded | procurement | pass | 1/1 | get_product_overview, draft_purchase_order | - | gemini-3.5-flash-lite |
| A13 | grounded | procurement | pass | 1/1 | get_product_overview, list_suppliers, search_products, draft_purchase_order | - | gemini-3.5-flash-lite |
| A14 | grounded | procurement | pass | 1/1 | get_product_overview | - | gemini-3.5-flash-lite |
| A15 | grounded | procurement | pass | 2/2 | get_product_overview, draft_purchase_order | - | gemini-3.5-flash-lite |
| A2 | grounded | inventory | pass | 1/1 | - | - | gemini-3.5-flash-lite |
| A3 | grounded | procurement | pass | 1/1 | - | - | gemini-3.5-flash-lite |
| A4 | grounded | procurement | pass | 1/1 | - | - | gemini-3.5-flash-lite |
| A5 | grounded | procurement | pass | 3/3 | get_product_overview, draft_purchase_order | - | gemini-3.5-flash-lite |
| A6 | grounded | procurement | pass | 2/2 | get_product_overview, draft_purchase_order | - | gemini-3.5-flash-lite |
| A7 | grounded | admin | pass | 1/1 | - | - | gemini-3.5-flash-lite |
| A8 | grounded | inventory | pass | 1/1 | - | - | gemini-3.5-flash-lite |
| A9 | grounded | procurement | pass | 1/1 | - | - | gemini-3.5-flash-lite |
| C1 | grounded | admin | pass | 5/5 | list_stock_risk | - | gemini-3.5-flash-lite |
| C10 | grounded | admin | pass | 2/2 | get_product_overview | - | gemini-3.5-flash-lite |
| C11 | grounded | admin | FAIL: missing P059; missing P071; missing P075; missing P062; missing P058; missing P065; missing P060 | 0/7 | list_stock_risk, search_products, list_suppliers, get_product_overview | - | gemini-3.5-flash-lite |
| C12 | grounded | admin | pass | 2/2 | search_products, run_what_if | - | gemini-3.5-flash-lite |
| C13 | grounded | admin | pass | 2/2 | run_what_if | - | gemini-3.5-flash-lite |
| C14 | grounded | admin | pass | 2/2 | get_product_overview, propose_recommendation | 155 | gemini-3.5-flash-lite |
| C15 | grounded | admin | pass | 5/5 | get_product_overview | - | gemini-3.5-flash-lite |
| C16 | grounded | admin | pass | 2/2 | get_product_overview | - | gemini-3.5-flash-lite |
| C17 | grounded | admin | pass | 2/2 | get_product_overview, list_supplier_performance | - | gemini-3.5-flash-lite |
| C2 | grounded | admin | pass | 4/4 | get_product_overview, list_purchase_orders | - | gemini-3.5-flash-lite |
| C3 | grounded | admin | pass | 2/2 | get_product_overview, propose_recommendation | - | gemini-3.5-flash-lite |
| C4 | grounded | admin | pass | 2/2 | run_what_if | 81.6 | gemini-3.5-flash-lite |
| C5 | grounded | admin | pass | 1/1 | get_product_overview | - | gemini-3.5-flash-lite |
| C6 | grounded | admin | pass | 10/10 | list_stock_risk | - | gemini-3.5-flash-lite |
| C7 | grounded | admin | pass | 3/3 | search_products, list_purchase_orders, list_supplier_performance | - | gemini-3.5-flash-lite |
| C8 | grounded | admin | pass | 3/3 | get_product_overview, list_purchase_orders | - | gemini-3.5-flash-lite |
| C9 | grounded | admin | pass | 2/2 | get_product_overview | - | gemini-3.5-flash-lite |
| F1 | grounded | admin | pass | 1/1 | get_product_overview | - | gemini-3.5-flash-lite |
| F10 | grounded | admin | pass | 2/2 | get_sales_summary | - | gemini-3.5-flash-lite |
| F11 | grounded | admin | pass | 1/1 | get_sales_summary | - | gemini-3.5-flash-lite |
| F12 | grounded | admin | pass | 2/2 | list_purchase_orders | - | gemini-3.5-flash-lite |
| F13 | grounded | admin | pass | 1/1 | list_supplier_performance | - | gemini-3.5-flash-lite |
| F14 | grounded | admin | pass | 2/2 | get_product_overview, list_purchase_orders | - | gemini-3.5-flash-lite |
| F15 | grounded | admin | pass | 2/2 | get_inventory | - | gemini-3.5-flash-lite |
| F16 | grounded | admin | FAIL: missing 74.67; missing 15.34 | 0/2 | list_suppliers, list_supplier_performance | - | gemini-3.5-flash-lite |
| F17 | grounded | admin | pass | 2/2 | list_supplier_performance | - | gemini-3.5-flash-lite |
| F2 | grounded | admin | pass | 1/1 | get_sales_summary | - | gemini-3.5-flash-lite |
| F3 | grounded | admin | pass | 2/2 | list_supplier_performance | - | gemini-3.5-flash-lite |
| F4 | grounded | admin | pass | 1/1 | list_purchase_orders | - | gemini-3.5-flash-lite |
| F5 | grounded | admin | pass | 2/2 | get_demand_forecast | - | gemini-3.5-flash-lite |
| F6 | grounded | admin | pass | 4/4 | list_stock_risk | - | gemini-3.5-flash-lite |
| F7 | grounded | admin | pass | 2/2 | search_products | - | gemini-3.5-flash-lite |
| F8 | grounded | admin | pass | 1/1 | search_products | - | gemini-3.5-flash-lite |
| F9 | grounded | admin | pass | 1/1 | get_sales_summary | - | gemini-3.5-flash-lite |
| G1 | grounded | admin | pass | 3/3 | - | - | gemini-3.5-flash-lite |
| G10 | grounded | admin | pass | 1/1 | - | - | gemini-3.5-flash-lite |
| G11 | grounded | admin | pass | 2/2 | - | - | gemini-3.5-flash-lite |
| G12 | grounded | admin | pass | 1/1 | - | - | gemini-3.5-flash-lite |
| G13 | grounded | admin | pass | 2/2 | - | - | gemini-3.5-flash-lite |
| G14 | grounded | admin | pass | 2/2 | - | - | gemini-3.5-flash-lite |
| G15 | grounded | admin | pass | 2/2 | - | - | gemini-3.5-flash-lite |
| G16 | grounded | admin | pass | 2/2 | - | - | gemini-3.5-flash-lite |
| G17 | grounded | admin | pass | 2/2 | - | - | gemini-3.5-flash-lite |
| G18 | grounded | admin | pass | 1/1 | - | - | gemini-3.5-flash-lite |
| G19 | grounded | admin | pass | 2/2 | - | - | gemini-3.5-flash-lite |
| G2 | grounded | admin | pass | 2/2 | - | - | gemini-3.5-flash-lite |
| G20 | grounded | admin | pass | 2/2 | - | - | gemini-3.5-flash-lite |
| G21 | grounded | admin | pass | 1/1 | - | - | gemini-3.5-flash-lite |
| G22 | grounded | admin | pass | 2/2 | - | - | gemini-3.5-flash-lite |
| G23 | grounded | admin | pass | 2/2 | - | - | gemini-3.5-flash-lite |
| G24 | grounded | admin | pass | 2/2 | - | - | gemini-3.5-flash-lite |
| G25 | grounded | admin | pass | 2/2 | - | - | gemini-3.5-flash-lite |
| G3 | grounded | admin | pass | 4/4 | - | - | gemini-3.5-flash-lite |
| G4 | grounded | admin | pass | 3/3 | - | - | gemini-3.5-flash-lite |
| G5 | grounded | admin | pass | 2/2 | - | - | gemini-3.5-flash-lite |
| G6 | grounded | admin | pass | 1/1 | - | - | gemini-3.5-flash-lite |
| G7 | grounded | admin | pass | 2/2 | - | - | gemini-3.5-flash-lite |
| G8 | grounded | admin | pass | 4/4 | - | - | gemini-3.5-flash-lite |
| G9 | grounded | admin | pass | 1/1 | - | - | gemini-3.5-flash-lite |
| U1 | grounded | admin | pass | 1/1 | get_inventory, search_products | - | gemini-3.5-flash-lite |
| U10 | grounded | admin | pass | 1/1 | list_purchase_orders, search_knowledge | - | gemini-3.5-flash-lite |
| U11 | grounded | admin | pass | 1/1 | get_product_overview, get_inventory | - | gemini-3.5-flash-lite |
| U12 | grounded | admin | pass | 1/1 | get_demand_forecast | 655.9, 690.6, 725.3, 760.0, 794.7, 829.4, 864.1, 898.8, 933.5, 968.2, 1,002.9, 1,037.6 | gemini-3.5-flash-lite |
| U2 | grounded | admin | pass | 1/1 | - | - | gemini-3.5-flash-lite |
| U3 | grounded | admin | pass | 1/1 | search_knowledge, get_sales_summary, list_suppliers | - | gemini-3.5-flash-lite |
| U4 | grounded | admin | pass | 1/1 | search_knowledge | - | gemini-3.5-flash-lite |
| U5 | grounded | admin | pass | 1/1 | get_sales_summary, search_knowledge | - | gemini-3.5-flash-lite |
| U6 | grounded | admin | pass | 1/1 | get_sales_summary | - | gemini-3.5-flash-lite |
| U7 | grounded | admin | pass | 1/1 | list_supplier_performance, list_suppliers | - | gemini-3.5-flash-lite |
| U8 | grounded | admin | pass | 1/1 | get_inventory | - | gemini-3.5-flash-lite |
| U9 | grounded | admin | pass | 1/1 | search_knowledge, get_product_overview | - | gemini-3.5-flash-lite |

## Failed answers in full

### F16 (grounded, gemini-3.5-flash-lite)

**Question:** What delivery reliability percentage and average delivery days are stated in the supplier master data for Litware, Inc. (S007)?

**Expected facts:** [[74.67], [15.34]]

**Answer:**

> The supplier master data for Litware, Inc. (S007) states a delivery reliability percentage of 60% and an average delivery time of 2.08 days.

### C11 (grounded, gemini-3.5-flash-lite)

**Question:** Which products supplied by Northwind Electric Cars (S010) are at Critical or High stockout risk?

**Expected facts:** [['P059'], ['P071'], ['P075'], ['P062'], ['P058'], ['P065'], ['P060']]

**Answer:**

> I could not finish this within the allowed number of steps. Try a narrower question.


## How to read this

- **Passed** means every expected fact was found, a tool that can answer the question was used, nothing forbidden happened, and (for action cases) the right thing was or was not done.
- **Facts found** are matched by number (within 1%) or by phrase. A correct answer worded in a way the phrase list does not anticipate is marked as missing, so pass rates can understate.
- **Unsupported figures** are numbers in an answer that appear in none of the question, the tool results and the knowledge passages. Figures the model derives by arithmetic count as unsupported; the check cannot tell a derived figure from an invented one, or a real figure used in the wrong place.
- Each question was asked once per condition. The model is not deterministic, so a single run is one sample.
- When more than one model answered, differences between questions are partly differences between models.

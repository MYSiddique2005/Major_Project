# Evaluation report: fixed-2

118 answers (86 grounded, 32 ungrounded). Models that answered: gemini-3.5-flash-lite (118).
Collected between 2026-10-10T16:00:53 and 2026-10-13T16:13:52.

## Results with grounding (the system as built)

| Group | Questions | Passed | Facts found | Right tool used | Unsupported figures | Avg time | Avg tool calls |
|---|---:|---:|---:|---:|---:|---:|---:|
| Grounding (terms and rules) | 25 | 100% | 100% | - | 0 of 28 | 4s | 0.0 |
| Factual (one module) | 17 | 100% | 100% | 100% | 0 of 44 | 12s | 1.1 |
| Cross-module reasoning | 17 | 100% | 100% | 100% | 2 of 198 | 9s | 1.7 |
| Controlled actions and permissions | 15 | 100% | 100% | 100% | 0 of 33 | 8s | 1.5 |
| Abstention (data cannot answer) | 12 | 100% | 100% | 100% | 1 of 39 | 12s | 1.2 |
| **All** | 86 | 100% | 100% | 100% | 3 of 342 | 8s | 1.0 |

## Effect of grounding (RQ1)

The same 32 questions, asked with and without the knowledge base.

| Group | Questions | Passed | Facts found | Right tool used | Unsupported figures | Avg time | Avg tool calls |
|---|---:|---:|---:|---:|---:|---:|---:|
| With grounding | 32 | 100% | 100% | 100% | 1 of 105 | 4s | 0.3 |
| Without grounding | 32 | 28% | 41% | 100% | 3 of 112 | 6s | 0.9 |

| Question | With | Without | Missing without grounding |
|---|---|---|---|
| C1 | pass | pass | - |
| C14 | pass | pass | - |
| C16 | pass | fail | 15% |
| C2 | pass | pass | - |
| C3 | pass | pass | - |
| C8 | pass | pass | - |
| C9 | pass | pass | - |
| G1 | pass | fail | half / 50% / 0.5; safety stock; reorder level |
| G10 | pass | fail | 2 deliver |
| G11 | pass | fail | 60%; 1 day |
| G12 | pass | fail | 3 deliver |
| G13 | pass | fail | 60 days; 0.5 / half a day / half-day |
| G14 | pass | fail | lead time plus 7 days |
| G15 | pass | pass | - |
| G16 | pass | fail | 100000; unit cost / standard cost / standard purchase cost |
| G17 | pass | fail | can still reject / still reject |
| G18 | pass | fail | 3 drafts |
| G19 | pass | fail | Processing means shipped; Completed means delivered |
| G2 | pass | fail | 28; 5 |
| G20 | pass | pass | - |
| G21 | pass | fail | only ADMIN |
| G22 | pass | fail | 4 weeks; 12 weeks |
| G23 | pass | fail | no longer |
| G24 | pass | fail | before tax / excluding tax / excludes tax / not include tax / tax is not included / without tax / exclusive of tax / not included / no tax |
| G25 | pass | fail | Main Warehouse / one warehouse / single warehouse / 1 warehouse; dollar / USD |
| G3 | pass | fail | 14; 10; safety stock; lead time |
| G4 | pass | fail | 50; worsening / getting worse / worse / grown / increasing |
| G5 | pass | pass | - |
| G6 | pass | fail | \b(?:are\|is\|were\|was\|being\|been)\s+(?:all\s+\|both\s+\|largely\s+\|mostly\s+)?simulated / \bsimulated\s+(?:from\|data\|records\|figures\|values\|using\|with\|based) |
| G7 | pass | fail | 8 |
| G8 | pass | fail | stock status / Low Stock / stored on / stock record / Inventory page |
| G9 | pass | fail | 15% |

## Proactive insights (RQ3)

From the 29 insights stored by 6 completed scans (1 scans failed, mostly on rate limits).

| Measure | Result |
|---|---|
| Insights whose subject was a finding the analytics had flagged | 29 of 29 (enforced by the server) |
| Evidence from two or more modules | 29 of 29 |
| Figures in the text found in the system data | 419 of 419 |
| Reorder insights whose quantity equals the reorder rule | 4 of 4 |
| Actions recommended | expedite_delivery: 25, reorder: 4 |

Detection itself (which products and suppliers are flagged) is done by the rule-based analytics, so its precision and recall are properties of those rules, not of the model. What the model adds, and what is measured here, is the explanation and the recommended action.

## Every answer

| Case | Condition | Role | Result | Facts | Tools called | Unsupported figures | Model |
|---|---|---|---|---|---|---|---|
| A1 | grounded | procurement | pass | 3/3 | get_product_overview, draft_purchase_order | - | gemini-3.5-flash-lite |
| A10 | grounded | inventory | pass | 1/1 | get_sales_summary | - | gemini-3.5-flash-lite |
| A11 | grounded | procurement | pass | 1/1 | - | - | gemini-3.5-flash-lite |
| A12 | grounded | procurement | pass | 1/1 | get_product_overview | - | gemini-3.5-flash-lite |
| A13 | grounded | procurement | pass | 1/1 | get_product_overview, list_suppliers, search_products, draft_purchase_order, propose_recommendation | - | gemini-3.5-flash-lite |
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
| C11 | grounded | admin | pass | 7/7 | list_stock_risk | - | gemini-3.5-flash-lite |
| C12 | grounded | admin | pass | 2/2 | run_what_if | - | gemini-3.5-flash-lite |
| C13 | grounded | admin | pass | 2/2 | run_what_if | - | gemini-3.5-flash-lite |
| C14 | grounded | admin | pass | 2/2 | get_product_overview, propose_recommendation | - | gemini-3.5-flash-lite |
| C15 | grounded | admin | pass | 5/5 | get_product_overview | - | gemini-3.5-flash-lite |
| C16 | grounded | admin | pass | 2/2 | get_product_overview | - | gemini-3.5-flash-lite |
| C17 | grounded | admin | pass | 2/2 | get_product_overview, list_supplier_performance | - | gemini-3.5-flash-lite |
| C2 | grounded | admin | pass | 4/4 | get_product_overview | - | gemini-3.5-flash-lite |
| C3 | grounded | admin | pass | 2/2 | get_product_overview, propose_recommendation | - | gemini-3.5-flash-lite |
| C4 | grounded | admin | pass | 2/2 | run_what_if | 81.6 | gemini-3.5-flash-lite |
| C5 | grounded | admin | pass | 1/1 | get_product_overview | - | gemini-3.5-flash-lite |
| C6 | grounded | admin | pass | 10/10 | list_stock_risk | - | gemini-3.5-flash-lite |
| C7 | grounded | admin | pass | 3/3 | search_products, list_purchase_orders, list_supplier_performance | - | gemini-3.5-flash-lite |
| C8 | grounded | admin | pass | 3/3 | get_product_overview | 23.2 | gemini-3.5-flash-lite |
| C9 | grounded | admin | pass | 2/2 | get_product_overview | - | gemini-3.5-flash-lite |
| F1 | grounded | admin | pass | 1/1 | get_product_overview | - | gemini-3.5-flash-lite |
| F10 | grounded | admin | pass | 2/2 | get_sales_summary | - | gemini-3.5-flash-lite |
| F11 | grounded | admin | pass | 1/1 | get_sales_summary | - | gemini-3.5-flash-lite |
| F12 | grounded | admin | pass | 2/2 | list_purchase_orders | - | gemini-3.5-flash-lite |
| F13 | grounded | admin | pass | 1/1 | list_supplier_performance | - | gemini-3.5-flash-lite |
| F14 | grounded | admin | pass | 2/2 | get_product_overview, list_purchase_orders | - | gemini-3.5-flash-lite |
| F15 | grounded | admin | pass | 2/2 | get_inventory | - | gemini-3.5-flash-lite |
| F16 | grounded | admin | pass | 2/2 | list_suppliers | - | gemini-3.5-flash-lite |
| F17 | grounded | admin | pass | 2/2 | list_supplier_performance | - | gemini-3.5-flash-lite |
| F2 | grounded | admin | pass | 1/1 | get_sales_summary | - | gemini-3.5-flash-lite |
| F3 | grounded | admin | pass | 2/2 | list_supplier_performance | - | gemini-3.5-flash-lite |
| F4 | grounded | admin | pass | 1/1 | list_purchase_orders | - | gemini-3.5-flash-lite |
| F5 | grounded | admin | pass | 2/2 | get_demand_forecast | - | gemini-3.5-flash-lite |
| F6 | grounded | admin | pass | 4/4 | list_stock_risk | - | gemini-3.5-flash-lite |
| F7 | grounded | admin | pass | 2/2 | search_products | - | gemini-3.5-flash-lite |
| F8 | grounded | admin | pass | 1/1 | search_products | - | gemini-3.5-flash-lite |
| F9 | grounded | admin | pass | 1/1 | get_sales_summary | - | gemini-3.5-flash-lite |
| G1 | grounded | admin | pass | 3/3 | search_knowledge | - | gemini-3.5-flash-lite |
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
| U11 | grounded | admin | pass | 1/1 | get_product_overview | - | gemini-3.5-flash-lite |
| U12 | grounded | admin | pass | 1/1 | get_demand_forecast | - | gemini-3.5-flash-lite |
| U2 | grounded | admin | pass | 1/1 | - | - | gemini-3.5-flash-lite |
| U3 | grounded | admin | pass | 1/1 | search_knowledge | - | gemini-3.5-flash-lite |
| U4 | grounded | admin | pass | 1/1 | search_knowledge | - | gemini-3.5-flash-lite |
| U5 | grounded | admin | pass | 1/1 | get_sales_summary, search_knowledge | - | gemini-3.5-flash-lite |
| U6 | grounded | admin | pass | 1/1 | get_sales_summary | - | gemini-3.5-flash-lite |
| U7 | grounded | admin | pass | 1/1 | list_supplier_performance, list_suppliers | - | gemini-3.5-flash-lite |
| U8 | grounded | admin | pass | 1/1 | get_inventory | 0 | gemini-3.5-flash-lite |
| U9 | grounded | admin | pass | 1/1 | search_knowledge | - | gemini-3.5-flash-lite |
| C1 | ungrounded | admin | pass | 5/5 | list_stock_risk | - | gemini-3.5-flash-lite |
| C14 | ungrounded | admin | pass | 2/2 | get_product_overview | 155 | gemini-3.5-flash-lite |
| C16 | ungrounded | admin | FAIL: missing 15% | 1/2 | get_product_overview | 20 | gemini-3.5-flash-lite |
| C2 | ungrounded | admin | pass | 4/4 | get_product_overview | - | gemini-3.5-flash-lite |
| C3 | ungrounded | admin | pass | 2/2 | get_product_overview, propose_recommendation | - | gemini-3.5-flash-lite |
| C8 | ungrounded | admin | pass | 3/3 | get_product_overview | - | gemini-3.5-flash-lite |
| C9 | ungrounded | admin | pass | 2/2 | get_product_overview | - | gemini-3.5-flash-lite |
| G1 | ungrounded | admin | FAIL: missing half / 50% / 0.5; missing safety stock; missing reorder level | 0/3 | list_stock_risk, get_stock_risk | - | gemini-3.5-flash-lite |
| G10 | ungrounded | admin | FAIL: missing 2 deliver | 0/1 | - | - | gemini-3.5-flash-lite |
| G11 | ungrounded | admin | FAIL: missing 60%; missing 1 day | 0/2 | list_supplier_performance | - | gemini-3.5-flash-lite |
| G12 | ungrounded | admin | FAIL: missing 3 deliver | 0/1 | - | - | gemini-3.5-flash-lite |
| G13 | ungrounded | admin | FAIL: missing 60 days; missing 0.5 / half a day / half-day | 0/2 | list_supplier_performance | - | gemini-3.5-flash-lite |
| G14 | ungrounded | admin | FAIL: missing lead time plus 7 days | 1/2 | list_stock_risk, get_product_overview | - | gemini-3.5-flash-lite |
| G15 | ungrounded | admin | pass | 2/2 | - | - | gemini-3.5-flash-lite |
| G16 | ungrounded | admin | FAIL: missing 100000; missing unit cost / standard cost / standard purchase cost | 0/2 | - | - | gemini-3.5-flash-lite |
| G17 | ungrounded | admin | FAIL: missing can still reject / still reject | 1/2 | - | - | gemini-3.5-flash-lite |
| G18 | ungrounded | admin | FAIL: missing 3 drafts | 0/1 | - | - | gemini-3.5-flash-lite |
| G19 | ungrounded | admin | FAIL: missing Processing means shipped; missing Completed means delivered | 0/2 | - | - | gemini-3.5-flash-lite |
| G2 | ungrounded | admin | FAIL: missing 28; missing 5 | 0/2 | list_stock_risk | - | gemini-3.5-flash-lite |
| G20 | ungrounded | admin | pass | 2/2 | search_products, get_demand_forecast | - | gemini-3.5-flash-lite |
| G21 | ungrounded | admin | FAIL: missing only ADMIN | 0/1 | - | - | gemini-3.5-flash-lite |
| G22 | ungrounded | admin | FAIL: missing 4 weeks; missing 12 weeks | 0/2 | search_products, get_demand_forecast | - | gemini-3.5-flash-lite |
| G23 | ungrounded | admin | FAIL: missing no longer | 1/2 | - | - | gemini-3.5-flash-lite |
| G24 | ungrounded | admin | FAIL: missing before tax / excluding tax / excludes tax / not include tax / tax is not included / without tax / exclusive of tax / not included / no tax | 1/2 | get_sales_summary | - | gemini-3.5-flash-lite |
| G25 | ungrounded | admin | FAIL: missing Main Warehouse / one warehouse / single warehouse / 1 warehouse; missing dollar / USD | 0/2 | list_stock_risk | - | gemini-3.5-flash-lite |
| G3 | ungrounded | admin | FAIL: missing 14; missing 10; missing safety stock; missing lead time | 0/4 | list_stock_risk, get_stock_risk, get_product_overview | - | gemini-3.5-flash-lite |
| G4 | ungrounded | admin | FAIL: missing 50; missing worsening / getting worse / worse / grown / increasing | 1/3 | list_supplier_performance | - | gemini-3.5-flash-lite |
| G5 | ungrounded | admin | pass | 2/2 | list_purchase_orders, list_stock_risk, get_product_overview | - | gemini-3.5-flash-lite |
| G6 | ungrounded | admin | FAIL: missing \b(?:are\|is\|were\|was\|being\|been)\s+(?:all\s+\|both\s+\|largely\s+\|mostly\s+)?simulated / \bsimulated\s+(?:from\|data\|records\|figures\|values\|using\|with\|based); revealed: (?:whether\|if)\b[^.\n]{0,80}\bsimulated / \b(?:rather than\|instead of\|not\|n't)\s+(?:\w+\s+){0,2}simulated | 0/1 | - | - | gemini-3.5-flash-lite |
| G7 | ungrounded | admin | FAIL: missing 8 | 1/2 | get_demand_forecast | 26 | gemini-3.5-flash-lite |
| G8 | ungrounded | admin | FAIL: missing stock status / Low Stock / stored on / stock record / Inventory page; revealed: same concept / same thing / the same figure / identical / interchangeabl / no difference / refer to the same | 3/4 | - | - | gemini-3.5-flash-lite |
| G9 | ungrounded | admin | FAIL: missing 15% | 0/1 | - | - | gemini-3.5-flash-lite |

## Failed answers in full

### G1 (ungrounded, gemini-3.5-flash-lite)

**Question:** In this system, what exactly makes a stock record's status Critical rather than Low Stock?

**Expected facts:** [['half', '50%', '0.5'], ['safety stock'], ['reorder level']]

**Answer:**

> A stock record's status is designated as Critical when the stock on hand is completely depleted (0 units remaining), resulting in zero days of cover and a projected stockout date of today. 
> 
> In contrast, items at other risk levels still maintain positive stock on hand and provide some days of cover before stock runs out.

### G2 (ungrounded, gemini-3.5-flash-lite)

**Question:** Over how many days is average daily demand calculated here, and how many orders must each period have before a demand trend is shown?

**Expected facts:** [[28], [5]]

**Answer:**

> I am unable to answer how many days average daily demand is calculated over or how many orders each period must have before a demand trend is shown, as the available tools do not provide the calculation parameters for demand averages and trends.

### G3 (ungrounded, gemini-3.5-flash-lite)

**Question:** How does the system work out the suggested reorder quantity? State the review period in days and the multiple it rounds up to.

**Expected facts:** [[14], [10], ['safety stock'], ['lead time']]

**Answer:**

> The tools and database records available to me do not specify the review period in days or the rounding multiple used by the system to calculate the suggested reorder quantity.

### G4 (ungrounded, gemini-3.5-flash-lite)

**Question:** Under this company's rules, what makes a supplier's delivery risk High?

**Expected facts:** [['overdue'], ['50'], ['worsening', 'getting worse', 'worse', 'grown', 'increasing']]

**Answer:**

> A supplier's delivery risk is classified as High when their historical performance metrics fall below acceptable reliability thresholds, characterized by a low on-time delivery rate combined with significant average delays and overdue purchase orders. 
> 
> Specifically, the high-risk suppliers in the system show the following drivers:
> - Litware, Inc. (S007) has an on-time delivery rate of 60% (913 of 1522 deliveries), an average delay of 2.08 days with a longest delay of 10 days, and 1 overdue purchase order.
> - Northwind Electric Cars (S010) has an on-time delivery rate of 71.5% (293 of 410 deliveries), an average delay of 1.76 days with a longest delay of 14 days, and 7 overdue purchase orders.

### G6 (ungrounded, gemini-3.5-flash-lite)

**Question:** Are the purchase orders and stock levels in this system real records or simulated?

**Expected facts:** [['re:\\b(?:are|is|were|was|being|been)\\s+(?:all\\s+|both\\s+|largely\\s+|mostly\\s+)?simulated', 're:\\bsimulated\\s+(?:from|data|records|figures|values|using|with|based)']]

**Answer:**

> The data in this system comes from the ERP database accessed through the platform's tools, but the tools do not specify whether the records represent live operations or a simulated environment.

### G7 (ungrounded, gemini-3.5-flash-lite)

**Question:** How does the forecast choose between its methods, and over how many weeks is each one tested?

**Expected facts:** [[8], ['error', 'WAPE']]

**Answer:**

> The forecast chooses its method by selecting the one with the lowest backtest error, measured by Weighted Absolute Percentage Error (WAPE). The available methods are tested over 26 weeks of historical weekly demand data.

### G8 (ungrounded, gemini-3.5-flash-lite)

**Question:** What is the difference between the reorder level and the reorder point in this system, and how is the reorder point calculated?

**Expected facts:** [['demand'], ['lead time'], ['safety stock'], ['stock status', 'Low Stock', 'stored on', 'stock record', 'Inventory page']]

**Answer:**

> The reorder level and the reorder point refer to the stock threshold that triggers a replenishment order, but the system uses them interchangeably as the stock level at which a new purchase order should be placed to avoid a stockout during lead time. 
> 
> The system calculates the reorder point based on demand forecasts, lead times, and safety stock requirements to ensure inventory does not run out before a new delivery arrives.

### G9 (ungrounded, gemini-3.5-flash-lite)

**Question:** At what percentage increase does demand count as rising sharply here?

**Expected facts:** [['15%', 're:\\b15(?:\\.0+)?\\s*(?:%|percent|per cent)']]

**Answer:**

> I do not have access to a rule definition or system configuration tool that specifies the exact percentage threshold at which demand is classified as rising sharply.

### G10 (ungrounded, gemini-3.5-flash-lite)

**Question:** When does the system use a supplier's observed lead time instead of its stated average delivery days?

**Expected facts:** [['2 deliver', 're:\\b(?:2|two)\\b(?:\\s+\\S+){0,3}?\\s+deliver', 're:at least\\s+(?:2|two)\\b', 're:(?:minimum|maximum|limit) of\\s+(?:2|two)\\b', 're:(?:up to|at most)\\s+(?:2|two)\\b']]

**Answer:**

> I am sorry, but the system tools do not contain information or rules explaining when the system uses a supplier's observed lead time instead of its stated average delivery days.

### G11 (ungrounded, gemini-3.5-flash-lite)

**Question:** Under our rules, what makes a supplier's delivery risk Medium?

**Expected facts:** [['60%', 're:\\b60(?:\\.0+)?\\s*(?:%|percent|per cent)'], ['1 day', 're:\\b(?:1|one)(?:\\.0)?[\\s-]*(?:calendar\\s+|working\\s+)?days?\\b']]

**Answer:**

> The available supplier performance data shows only suppliers with Low and High delivery risk levels, so the specific rules defining a Medium supplier delivery risk are not present in the current system records.

### G12 (ungrounded, gemini-3.5-flash-lite)

**Question:** How many deliveries must a supplier have before its on-time percentage is used to set its risk level?

**Expected facts:** [['3 deliver', 're:\\b(?:3|three)\\b(?:\\s+\\S+){0,3}?\\s+deliver', 're:at least\\s+(?:3|three)\\b', 're:(?:minimum|maximum|limit) of\\s+(?:3|three)\\b', 're:(?:up to|at most)\\s+(?:3|three)\\b']]

**Answer:**

> I do not have access to system rules or company guidelines regarding the minimum number of deliveries a supplier must have before its on-time percentage is used to set its risk level.

### G13 (ungrounded, gemini-3.5-flash-lite)

**Question:** How is a supplier's delay trend worked out: which periods are compared, and how large a difference makes it worsening or improving?

**Expected facts:** [['60 days', 're:\\b60(?:\\.0)?[\\s-]*(?:calendar\\s+|working\\s+)?days?\\b'], ['0.5', 'half a day', 'half-day']]

**Answer:**

> The tools do not provide information on how a supplier's delay trend is calculated, which periods are compared, or the specific threshold required for a trend to be considered worsening or improving. They only report the resulting trend status (such as stable) for each supplier.

### G14 (ungrounded, gemini-3.5-flash-lite)

**Question:** What puts a product at Medium stockout risk under our rules?

**Expected facts:** [['below safety stock', 're:below (?:its |the )?safety stock'], ['lead time plus 7 days', 're:lead time\\s*(?:plus|\\+)\\s*(?:7|seven)\\b', 're:lead time[^.\\n]{0,25}\\b(?:7|seven)\\s+days', 're:(?:7|seven)\\s+days?\\s+(?:more|longer)\\s+than\\s+(?:the\\s+)?lead time']]

**Answer:**

> A product is classified at Medium stockout risk when its stock on hand and incoming orders leave it with a low number of days of cover relative to the supplier's lead time, specifically when its days of cover are fewer than or close to the lead time but there are inbound units on order expected to arrive before a stockout occurs. 
> 
> For example, "The Gu" red shirt XML tag t-shirt (Black) 7XL, P101 has:
> - Stock on hand of 172 units, which is below its safety stock of 354 units.
> - Days of cover of 2.2 days, which is less than the supplier lead time of 9.9 days.
> - 1,020 units already on order with Fabrikam, Inc. (S004) scheduled to arrive shortly, preventing it from reaching a Critical risk level.

### G16 (ungrounded, gemini-3.5-flash-lite)

**Question:** What is the largest quantity a single purchase order may have, and what unit price is used when none is given?

**Expected facts:** [[100000], ['unit cost', 'standard cost', 'standard purchase cost']]

**Answer:**

> The tools available to me do not provide information on the maximum quantity allowed for a single purchase order or the default unit price used when none is given.

### G17 (ungrounded, gemini-3.5-flash-lite)

**Question:** Can the user who created or submitted a purchase order approve it themselves? Is there anything they can still do with it at the approval stage?

**Expected facts:** [['cannot', "can't", 'can not', 'not allowed', 'may not', 'no,', 'not approve', 'unable', 'not permitted'], ['can still reject', 'still reject', 're:\\b(?:may|can|could|are able to|is able to|allowed to)\\s+(?:still\\s+|also\\s+)*reject']]

**Answer:**

> Based on the context provided, a user who created or submitted a purchase order cannot approve it themselves; approval requires an approver's decision. At the approval stage, they cannot approve their own order, but they can have another user who holds approval rights review and approve or reject it.

### G18 (ungrounded, gemini-3.5-flash-lite)

**Question:** How many draft purchase orders can the assistant create in response to one chat message?

**Expected facts:** [['3 drafts', 're:\\b(?:3|three)\\b']]

**Answer:**

> The assistant can create one draft purchase order in response to one chat message using the draft_purchase_order tool.

### G19 (ungrounded, gemini-3.5-flash-lite)

**Question:** What do the sales order statuses Pending, Processing and Completed mean in this system?

**Expected facts:** [['Processing means shipped', 're:processing\\b[^.\\n]{0,90}\\b(?:shipped|on its way|in transit|dispatched)'], ['Completed means delivered', 're:completed\\b[^.\\n]{0,90}\\bdelivered']]

**Answer:**

> Sales order statuses such as Pending, Processing and Completed are not defined in the system data retrieved by my tools. My tools provide information on purchase orders (with statuses including Draft, Pending Approval, Approved, Rejected, Ordered, Delivered, and Cancelled), but I do not have reference data explaining general sales order lifecycle definitions beyond what is stored in the system records.

### G21 (ungrounded, gemini-3.5-flash-lite)

**Question:** Which roles can read the audit log?

**Expected facts:** [['only ADMIN', 're:\\bonly[^.\\n]{0,40}\\badmin', 're:\\badmin\\w*[^.\\n]{0,40}\\bis the only\\b', 're:\\badmin\\w*[^.\\n]{0,60}\\b(?:can|may|is able to|are able to)\\s+(?:read|view|see|access)']]

**Answer:**

> The tools available for your ADMIN role do not include access to user roles or the audit log, so I cannot tell you which roles can read it.

### G22 (ungrounded, gemini-3.5-flash-lite)

**Question:** How many weeks does the moving-average forecast average over, and how many weeks does the linear-trend forecast fit its line to?

**Expected facts:** [['4 weeks', 're:\\b(?:4|four)[\\s-]*weeks?\\b', 're:(?:last|past|previous)\\s+(?:4|four)\\b'], ['12 weeks', 're:\\b(?:12|twelve)[\\s-]*weeks?\\b', 're:(?:last|past|previous)\\s+(?:12|twelve)\\b']]

**Answer:**

> The tools available do not specify the number of weeks that the moving-average forecast averages over or the number of weeks that the linear-trend forecast fits its line to.

### G23 (ungrounded, gemini-3.5-flash-lite)

**Question:** When does an AI insight become Superseded?

**Expected facts:** [['again', 'newer', 'new insight', 'replaced', 're-analy', 'reanaly', 'new scan'], ['no longer']]

**Answer:**

> An AI insight becomes Superseded when newer data or a recalculated forecast updates the assessment, replacing the previous version.

### G24 (ungrounded, gemini-3.5-flash-lite)

**Question:** Is tax included in the revenue figures, and which sales orders are left out of revenue?

**Expected facts:** [['before tax', 'excluding tax', 'excludes tax', 'not include tax', 'tax is not included', 'without tax', 'exclusive of tax', 'not included', 'no tax'], ['cancelled', 'canceled']]

**Answer:**

> Cancelled sales orders are left out of revenue figures. The tool description for the sales summary specifies that cancelled orders are excluded. The available sales summary tools do not provide details on whether tax is included in the revenue figures.

### G25 (ungrounded, gemini-3.5-flash-lite)

**Question:** How many warehouses and how many currencies does the loaded dataset have?

**Expected facts:** [['Main Warehouse', 'one warehouse', 'single warehouse', '1 warehouse'], ['dollar', 'USD']]

**Answer:**

> The loaded dataset does not provide information on the number of warehouses or currencies, as the available tools do not track facility locations or financial currency types.

### C16 (ungrounded, gemini-3.5-flash-lite)

**Question:** Is demand for Developer joke mug - there are 10 types of people in the world (Black) (P045) rising sharply by our definition? Give its trend and the threshold that applies.

**Expected facts:** [[66.0], ['15%', 're:\\b15(?:\\.0+)?\\s*(?:%|percent|per cent)']]

**Answer:**

> Demand for Developer joke mug - there are 10 types of people in the world (Black) (P045) is rising sharply by our definition. 
> 
> Its demand trend is up 66% comparing the last 28 days to the previous 28 days (average daily demand increased from 3.79 units to 6.29 units). Our threshold for rising sharply is an increase of 20% or more.


## How to read this

- **Passed** means every expected fact was found, a tool that can answer the question was used, nothing forbidden happened, and (for action cases) the right thing was or was not done.
- **Facts found** are matched by number (within 1%) or by phrase. A correct answer worded in a way the phrase list does not anticipate is marked as missing, so pass rates can understate.
- **Unsupported figures** are numbers in an answer that appear in none of the question, the tool results and the knowledge passages. Figures the model derives by arithmetic count as unsupported; the check cannot tell a derived figure from an invented one, or a real figure used in the wrong place.
- Each question was asked once per condition. The model is not deterministic, so a single run is one sample.
- When more than one model answered, differences between questions are partly differences between models.

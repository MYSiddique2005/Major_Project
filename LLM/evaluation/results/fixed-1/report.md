# Evaluation report: fixed-1

118 answers (86 grounded, 32 ungrounded). Models that answered: gemini-3.5-flash-lite (118).
Collected between 2026-10-10T15:42:16 and 2026-10-10T16:00:38.

## Results with grounding (the system as built)

| Group | Questions | Passed | Facts found | Right tool used | Unsupported figures | Avg time | Avg tool calls |
|---|---:|---:|---:|---:|---:|---:|---:|
| Grounding (terms and rules) | 25 | 100% | 100% | - | 0 of 30 | 1s | 0.0 |
| Factual (one module) | 17 | 100% | 100% | 100% | 0 of 44 | 8s | 1.1 |
| Cross-module reasoning | 17 | 94% | 94% | 100% | 1 of 165 | 15s | 2.1 |
| Controlled actions and permissions | 15 | 100% | 100% | 100% | 0 of 32 | 10s | 1.5 |
| Abstention (data cannot answer) | 12 | 92% | 92% | 100% | 0 of 39 | 15s | 1.5 |
| **All** | 86 | 98% | 98% | 100% | 1 of 310 | 9s | 1.1 |

## Effect of grounding (RQ1)

The same 32 questions, asked with and without the knowledge base.

| Group | Questions | Passed | Facts found | Right tool used | Unsupported figures | Avg time | Avg tool calls |
|---|---:|---:|---:|---:|---:|---:|---:|
| With grounding | 32 | 100% | 100% | 100% | 0 of 105 | 5s | 0.3 |
| Without grounding | 32 | 25% | 42% | 100% | 3 of 103 | 8s | 1.0 |

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
| G15 | pass | fail | lost |
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
| G6 | pass | fail | - |
| G7 | pass | fail | 8 |
| G8 | pass | fail | safety stock; stock status / Low Stock / stored on / stock record / Inventory page |
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
| C11 | grounded | admin | FAIL: missing P059; missing P071; missing P075; missing P062; missing P058; missing P065; missing P060 | 0/7 | list_stock_risk, list_suppliers, search_products | - | gemini-3.5-flash-lite |
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
| C8 | grounded | admin | pass | 3/3 | get_product_overview | - | gemini-3.5-flash-lite |
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
| U1 | grounded | admin | FAIL: missing not found / no product / does not exist / doesn't exist / could not find / couldn't find / unable to find / no record / not exist / no such / cannot find / can't find / not be found / cannot be found / can't be found / couldn't be found | 0/1 | get_inventory | - | gemini-3.5-flash-lite |
| U10 | grounded | admin | pass | 1/1 | list_purchase_orders, search_knowledge | - | gemini-3.5-flash-lite |
| U11 | grounded | admin | pass | 1/1 | get_product_overview, list_purchase_orders | - | gemini-3.5-flash-lite |
| U12 | grounded | admin | pass | 1/1 | get_demand_forecast | - | gemini-3.5-flash-lite |
| U2 | grounded | admin | pass | 1/1 | - | - | gemini-3.5-flash-lite |
| U3 | grounded | admin | pass | 1/1 | search_suppliers, list_suppliers | - | gemini-3.5-flash-lite |
| U4 | grounded | admin | pass | 1/1 | search_knowledge | - | gemini-3.5-flash-lite |
| U5 | grounded | admin | pass | 1/1 | get_sales_summary, search_knowledge | - | gemini-3.5-flash-lite |
| U6 | grounded | admin | pass | 1/1 | get_sales_summary | - | gemini-3.5-flash-lite |
| U7 | grounded | admin | pass | 1/1 | list_supplier_performance, list_suppliers | - | gemini-3.5-flash-lite |
| U8 | grounded | admin | pass | 1/1 | get_inventory | - | gemini-3.5-flash-lite |
| U9 | grounded | admin | pass | 1/1 | search_knowledge, get_product_overview | - | gemini-3.5-flash-lite |
| C1 | ungrounded | admin | pass | 5/5 | list_stock_risk | - | gemini-3.5-flash-lite |
| C14 | ungrounded | admin | pass | 2/2 | get_product_overview | - | gemini-3.5-flash-lite |
| C16 | ungrounded | admin | FAIL: missing 15% | 1/2 | get_product_overview | 30 | gemini-3.5-flash-lite |
| C2 | ungrounded | admin | pass | 4/4 | get_product_overview, get_stock_risk | - | gemini-3.5-flash-lite |
| C3 | ungrounded | admin | pass | 2/2 | get_product_overview | - | gemini-3.5-flash-lite |
| C8 | ungrounded | admin | pass | 3/3 | get_product_overview | - | gemini-3.5-flash-lite |
| C9 | ungrounded | admin | pass | 2/2 | get_product_overview, get_stock_risk | - | gemini-3.5-flash-lite |
| G1 | ungrounded | admin | FAIL: missing half / 50% / 0.5; missing safety stock; missing reorder level | 0/3 | list_stock_risk, get_stock_risk | - | gemini-3.5-flash-lite |
| G10 | ungrounded | admin | FAIL: missing 2 deliver | 0/1 | - | - | gemini-3.5-flash-lite |
| G11 | ungrounded | admin | FAIL: missing 60%; missing 1 day | 0/2 | list_supplier_performance | - | gemini-3.5-flash-lite |
| G12 | ungrounded | admin | FAIL: missing 3 deliver | 0/1 | - | - | gemini-3.5-flash-lite |
| G13 | ungrounded | admin | FAIL: missing 60 days; missing 0.5 / half a day / half-day | 0/2 | list_supplier_performance | - | gemini-3.5-flash-lite |
| G14 | ungrounded | admin | FAIL: missing lead time plus 7 days | 1/2 | list_stock_risk, get_stock_risk | - | gemini-3.5-flash-lite |
| G15 | ungrounded | admin | FAIL: missing lost | 1/2 | - | - | gemini-3.5-flash-lite |
| G16 | ungrounded | admin | FAIL: missing 100000; missing unit cost / standard cost / standard purchase cost | 0/2 | - | - | gemini-3.5-flash-lite |
| G17 | ungrounded | admin | FAIL: missing can still reject / still reject | 1/2 | - | - | gemini-3.5-flash-lite |
| G18 | ungrounded | admin | FAIL: missing 3 drafts | 0/1 | list_purchase_orders | - | gemini-3.5-flash-lite |
| G19 | ungrounded | admin | FAIL: missing Processing means shipped; missing Completed means delivered | 0/2 | - | - | gemini-3.5-flash-lite |
| G2 | ungrounded | admin | FAIL: missing 28; missing 5 | 0/2 | list_stock_risk | - | gemini-3.5-flash-lite |
| G20 | ungrounded | admin | pass | 2/2 | search_products, get_demand_forecast | - | gemini-3.5-flash-lite |
| G21 | ungrounded | admin | FAIL: missing only ADMIN | 0/1 | - | - | gemini-3.5-flash-lite |
| G22 | ungrounded | admin | FAIL: missing 4 weeks; missing 12 weeks | 0/2 | search_products, get_demand_forecast | - | gemini-3.5-flash-lite |
| G23 | ungrounded | admin | FAIL: missing no longer | 1/2 | - | - | gemini-3.5-flash-lite |
| G24 | ungrounded | admin | FAIL: missing before tax / excluding tax / excludes tax / not include tax / tax is not included / without tax / exclusive of tax / not included / no tax | 1/2 | get_sales_summary | - | gemini-3.5-flash-lite |
| G25 | ungrounded | admin | FAIL: missing Main Warehouse / one warehouse / single warehouse / 1 warehouse; missing dollar / USD | 0/2 | - | - | gemini-3.5-flash-lite |
| G3 | ungrounded | admin | FAIL: missing 14; missing 10; missing safety stock; missing lead time | 0/4 | list_stock_risk, get_stock_risk, get_product_overview | - | gemini-3.5-flash-lite |
| G4 | ungrounded | admin | FAIL: missing 50; missing worsening / getting worse / worse / grown / increasing | 1/3 | list_supplier_performance | 1.7 | gemini-3.5-flash-lite |
| G5 | ungrounded | admin | pass | 2/2 | list_purchase_orders | - | gemini-3.5-flash-lite |
| G6 | ungrounded | admin | FAIL: revealed: (?:whether\|if)\b[^.\n]{0,80}\bsimulated / \b(?:rather than\|instead of\|not\|n't)\s+(?:\w+\s+){0,2}simulated | 1/1 | - | - | gemini-3.5-flash-lite |
| G7 | ungrounded | admin | FAIL: missing 8 | 1/2 | get_demand_forecast | 26 | gemini-3.5-flash-lite |
| G8 | ungrounded | admin | FAIL: missing safety stock; missing stock status / Low Stock / stored on / stock record / Inventory page; revealed: same concept / same thing / the same figure / identical / interchangeabl / no difference / refer to the same | 2/4 | - | - | gemini-3.5-flash-lite |
| G9 | ungrounded | admin | FAIL: missing 15% | 0/1 | list_stock_risk | - | gemini-3.5-flash-lite |

## Failed answers in full

### C11 (grounded, gemini-3.5-flash-lite)

**Question:** Which products supplied by Northwind Electric Cars (S010) are at Critical or High stockout risk?

**Expected facts:** [['P059'], ['P071'], ['P075'], ['P062'], ['P058'], ['P065'], ['P060']]

**Answer:**

> I could not finish this within the allowed number of steps. Try a narrower question.

### U1 (grounded, gemini-3.5-flash-lite)

**Question:** How many units of product P999 are on hand?

**Expected facts:** [['not found', 'no product', 'does not exist', "doesn't exist", 'could not find', "couldn't find", 'unable to find', 'no record', 'not exist', 'no such', 'cannot find', "can't find", 'not be found', 'cannot be found', "can't be found", "couldn't be found"]]

**Answer:**

> Product P999 has no stock records in the system, so there are no units on hand.

### G1 (ungrounded, gemini-3.5-flash-lite)

**Question:** In this system, what exactly makes a stock record's status Critical rather than Low Stock?

**Expected facts:** [['half', '50%', '0.5'], ['safety stock'], ['reorder level']]

**Answer:**

> A stock record's status is classified as Critical rather than Low Stock (or Medium/High) based on its days of cover and stockout timing. Specifically, a Critical status applies when a product has zero stock on hand (days of cover is 0) and a projected stockout date of today, meaning it is currently stocked out. By contrast, Low Stock or other risk tiers apply when a product still has positive stock on hand and several days of cover remaining.

### G2 (ungrounded, gemini-3.5-flash-lite)

**Question:** Over how many days is average daily demand calculated here, and how many orders must each period have before a demand trend is shown?

**Expected facts:** [[28], [5]]

**Answer:**

> I do not have access to the configuration settings or database formulas that specify the exact number of days used to calculate average daily demand or the minimum order count required for a demand trend to be shown.

### G3 (ungrounded, gemini-3.5-flash-lite)

**Question:** How does the system work out the suggested reorder quantity? State the review period in days and the multiple it rounds up to.

**Expected facts:** [[14], [10], ['safety stock'], ['lead time']]

**Answer:**

> The tools do not provide the review period in days or the multiple for rounding up the suggested reorder quantity.

### G4 (ungrounded, gemini-3.5-flash-lite)

**Question:** Under this company's rules, what makes a supplier's delivery risk High?

**Expected facts:** [['overdue'], ['50'], ['worsening', 'getting worse', 'worse', 'grown', 'increasing']]

**Answer:**

> A supplier's delivery risk is classified as High based on their delivery performance and order history. Looking at the suppliers currently marked as High risk (such as Litware, Inc., S007, and Northwind Electric Cars, S010), the contributing factors in their drivers include:
> 
> - A low on-time delivery rate (for example, 60% for Litware, Inc. and 71.5% for Northwind Electric Cars).
> - Having multiple overdue purchase orders (such as 1 overdue order for Litware, Inc. and 7 overdue orders for Northwind Electric Cars).
> - Significant average and maximum delivery delays (such as average delays around 1.7 to 2 days and maximum delays up to 10 to 14 days).

### G6 (ungrounded, gemini-3.5-flash-lite)

**Question:** Are the purchase orders and stock levels in this system real records or simulated?

**Expected facts:** [['re:\\b(?:are|is|were|was|being|been)\\s+(?:all\\s+|both\\s+|largely\\s+|mostly\\s+)?simulated', 're:\\bsimulated\\s+(?:from|data|records|figures|values|using|with|based)']]

**Answer:**

> The purchase orders and stock levels in this system are operational records managed within the ERP database rather than simulated data. 
> 
> As an admin, you can view live purchase order statuses, supplier delivery histories, demand forecasts, and current inventory stock levels retrieved directly from the system modules.

### G7 (ungrounded, gemini-3.5-flash-lite)

**Question:** How does the forecast choose between its methods, and over how many weeks is each one tested?

**Expected facts:** [[8], ['error', 'WAPE']]

**Answer:**

> The forecast chooses its method by selecting the one with the lowest backtest error, measured by WAPE. 
> 
> The backtest evaluates the methods (such as moving average and linear trend) over the historical demand data provided, which spans 26 weeks.

### G8 (ungrounded, gemini-3.5-flash-lite)

**Question:** What is the difference between the reorder level and the reorder point in this system, and how is the reorder point calculated?

**Expected facts:** [['demand'], ['lead time'], ['safety stock'], ['stock status', 'Low Stock', 'stored on', 'stock record', 'Inventory page']]

**Answer:**

> The reorder level and the reorder point refer to the stock threshold that triggers a replenishment order, but they are used interchangeably in this system's inventory and risk assessment records. 
> 
> Regarding how the reorder point is calculated, the system evaluates this through its stock risk assessments by combining demand forecasts from sales, current stock levels from inventory, and supplier lead times from procurement, rather than relying on a single static formula available in the master data.
> 
> If you have a specific product in mind, I can check its current reorder point and inventory metrics for you.

### G9 (ungrounded, gemini-3.5-flash-lite)

**Question:** At what percentage increase does demand count as rising sharply here?

**Expected facts:** [['15%', 're:\\b15(?:\\.0+)?\\s*(?:%|percent|per cent)']]

**Answer:**

> The system data does not define a specific threshold percentage at which demand is classified as "rising sharply." 
> 
> The stock risk list shows individual products with varying positive demand trends (such as 21.1%, 54.6%, and 92.7%), but the tools do not provide a rule or classification threshold for when a trend percentage qualifies as rising sharply.

### G10 (ungrounded, gemini-3.5-flash-lite)

**Question:** When does the system use a supplier's observed lead time instead of its stated average delivery days?

**Expected facts:** [['2 deliver', 're:\\b(?:2|two)\\b(?:\\s+\\S+){0,3}?\\s+deliver', 're:at least\\s+(?:2|two)\\b', 're:(?:minimum|maximum|limit) of\\s+(?:2|two)\\b', 're:(?:up to|at most)\\s+(?:2|two)\\b']]

**Answer:**

> I am sorry, but the system tools do not contain information or rules explaining when the system uses a supplier's observed lead time instead of its stated average delivery days.

### G11 (ungrounded, gemini-3.5-flash-lite)

**Question:** Under our rules, what makes a supplier's delivery risk Medium?

**Expected facts:** [['60%', 're:\\b60(?:\\.0+)?\\s*(?:%|percent|per cent)'], ['1 day', 're:\\b(?:1|one)(?:\\.0)?[\\s-]*(?:calendar\\s+|working\\s+)?days?\\b']]

**Answer:**

> The system's supplier performance records show only suppliers with High and Low risk levels (such as Litware, Inc., S007, and Northwind Electric Cars, S010, at High, and A Datum Corporation, S001, and Fabrikam, Inc., S004, at Low), so there are no Medium risk suppliers currently in the data to define the exact thresholds for that level.

### G12 (ungrounded, gemini-3.5-flash-lite)

**Question:** How many deliveries must a supplier have before its on-time percentage is used to set its risk level?

**Expected facts:** [['3 deliver', 're:\\b(?:3|three)\\b(?:\\s+\\S+){0,3}?\\s+deliver', 're:at least\\s+(?:3|three)\\b', 're:(?:minimum|maximum|limit) of\\s+(?:3|three)\\b', 're:(?:up to|at most)\\s+(?:3|three)\\b']]

**Answer:**

> The system does not specify a minimum number of deliveries a supplier must have before its on-time percentage is used to set its risk level.

### G13 (ungrounded, gemini-3.5-flash-lite)

**Question:** How is a supplier's delay trend worked out: which periods are compared, and how large a difference makes it worsening or improving?

**Expected facts:** [['60 days', 're:\\b60(?:\\.0)?[\\s-]*(?:calendar\\s+|working\\s+)?days?\\b'], ['0.5', 'half a day', 'half-day']]

**Answer:**

> The tools do not provide information on how a supplier's delay trend is calculated, which periods are compared, or the specific size of the difference required to classify it as worsening or improving.

### G14 (ungrounded, gemini-3.5-flash-lite)

**Question:** What puts a product at Medium stockout risk under our rules?

**Expected facts:** [['below safety stock', 're:below (?:its |the )?safety stock'], ['lead time plus 7 days', 're:lead time\\s*(?:plus|\\+)\\s*(?:7|seven)\\b', 're:lead time[^.\\n]{0,25}\\b(?:7|seven)\\s+days', 're:(?:7|seven)\\s+days?\\s+(?:more|longer)\\s+than\\s+(?:the\\s+)?lead time']]

**Answer:**

> A product is placed at Medium stockout risk when its stock on hand is below safety stock and its days of cover are fewer than the supplier's lead time, but it has open purchase orders inbound that prevent a Critical or High rating (typically because an upcoming delivery is expected before stock runs out or soon after). 
> 
> For example, products such as "The Gu" red shirt XML tag t-shirt (Black) 7XL, P101 have stock on hand below safety stock and days of cover (such as 2.2 days) shorter than the lead time (9.9 days), but they maintain Medium risk rather than High or Critical because they have units already on order arriving before stockout.

### G15 (ungrounded, gemini-3.5-flash-lite)

**Question:** In a what-if projection, what happens to demand that cannot be served from stock, and do purchase orders awaiting approval count as incoming stock?

**Expected facts:** [['lost'], ['do not count', "don't count", 'does not count', 'not count', 'not included', 'do not', 'are not', "aren't", 'excluded', 'no,']]

**Answer:**

> In a what-if projection, demand that cannot be served from stock becomes unfulfilled demand or stockout shortfalls, meaning orders are missed or delayed because the inventory level hits zero or falls below what is needed. 
> 
> Regarding purchase orders awaiting approval, they do not count as incoming stock in the projections. Only orders that have been formally placed or are actively in progress in the procurement pipeline are factored in as incoming supply; orders in a draft or pending approval state are not yet committed by a supplier and are excluded from available stock calculations.

### G16 (ungrounded, gemini-3.5-flash-lite)

**Question:** What is the largest quantity a single purchase order may have, and what unit price is used when none is given?

**Expected facts:** [[100000], ['unit cost', 'standard cost', 'standard purchase cost']]

**Answer:**

> The tools available in IntelliERP cover sales, inventory, procurement, suppliers, and stock risks, but they do not contain company policy settings such as maximum purchase order quantities or default unit prices. Therefore, the system does not have this information available.

### G17 (ungrounded, gemini-3.5-flash-lite)

**Question:** Can the user who created or submitted a purchase order approve it themselves? Is there anything they can still do with it at the approval stage?

**Expected facts:** [['cannot', "can't", 'can not', 'not allowed', 'may not', 'no,', 'not approve', 'unable', 'not permitted'], ['can still reject', 'still reject', 're:\\b(?:may|can|could|are able to|is able to|allowed to)\\s+(?:still\\s+|also\\s+)*reject']]

**Answer:**

> The user who created or submitted a purchase order cannot approve it themselves. At the approval stage, they can still review the order, but approval or rejection requires a different user or an approver role.

### G18 (ungrounded, gemini-3.5-flash-lite)

**Question:** How many draft purchase orders can the assistant create in response to one chat message?

**Expected facts:** [['3 drafts', 're:\\b(?:3|three)\\b']]

**Answer:**

> The tool definition for draft_purchase_order allows you to call it once per recommendation, and you can propose one recommendation per turn. Therefore, the assistant can create one draft purchase order in response to one chat message.

### G19 (ungrounded, gemini-3.5-flash-lite)

**Question:** What do the sales order statuses Pending, Processing and Completed mean in this system?

**Expected facts:** [['Processing means shipped', 're:processing\\b[^.\\n]{0,90}\\b(?:shipped|on its way|in transit|dispatched)'], ['Completed means delivered', 're:completed\\b[^.\\n]{0,90}\\bdelivered']]

**Answer:**

> The system uses different sales order statuses: Pending, Processing, and Completed. However, looking through the available master data and operational modules, sales order workflow status definitions are not stored in the system tools or product/supplier records.

### G21 (ungrounded, gemini-3.5-flash-lite)

**Question:** Which roles can read the audit log?

**Expected facts:** [['only ADMIN', 're:\\bonly[^.\\n]{0,40}\\badmin', 're:\\badmin\\w*[^.\\n]{0,40}\\bis the only\\b', 're:\\badmin\\w*[^.\\n]{0,60}\\b(?:can|may|is able to|are able to)\\s+(?:read|view|see|access)']]

**Answer:**

> I do not have access to a tool that lists user roles or permissions for the audit log. Therefore, I cannot verify which roles have permission to read it based on the system data available.

### G22 (ungrounded, gemini-3.5-flash-lite)

**Question:** How many weeks does the moving-average forecast average over, and how many weeks does the linear-trend forecast fit its line to?

**Expected facts:** [['4 weeks', 're:\\b(?:4|four)[\\s-]*weeks?\\b', 're:(?:last|past|previous)\\s+(?:4|four)\\b'], ['12 weeks', 're:\\b(?:12|twelve)[\\s-]*weeks?\\b', 're:(?:last|past|previous)\\s+(?:12|twelve)\\b']]

**Answer:**

> The tools do not state the number of weeks used by the moving-average forecast or the linear-trend forecast to average over or fit their lines.

### G23 (ungrounded, gemini-3.5-flash-lite)

**Question:** When does an AI insight become Superseded?

**Expected facts:** [['again', 'newer', 'new insight', 'replaced', 're-analy', 'reanaly', 'new scan'], ['no longer']]

**Answer:**

> An AI insight becomes Superseded when a newer insight is generated for the same product or supplier, replacing the previous one.

### G24 (ungrounded, gemini-3.5-flash-lite)

**Question:** Is tax included in the revenue figures, and which sales orders are left out of revenue?

**Expected facts:** [['before tax', 'excluding tax', 'excludes tax', 'not include tax', 'tax is not included', 'without tax', 'exclusive of tax', 'not included', 'no tax'], ['cancelled', 'canceled']]

**Answer:**

> Cancelled sales orders are left out of revenue. The tools do not specify whether tax is included in the revenue figures.

### G25 (ungrounded, gemini-3.5-flash-lite)

**Question:** How many warehouses and how many currencies does the loaded dataset have?

**Expected facts:** [['Main Warehouse', 'one warehouse', 'single warehouse', '1 warehouse'], ['dollar', 'USD']]

**Answer:**

> I cannot answer how many warehouses and currencies the loaded dataset has because none of the available tools provide information about warehouses or currencies.

### C16 (ungrounded, gemini-3.5-flash-lite)

**Question:** Is demand for Developer joke mug - there are 10 types of people in the world (Black) (P045) rising sharply by our definition? Give its trend and the threshold that applies.

**Expected facts:** [[66.0], ['15%', 're:\\b15(?:\\.0+)?\\s*(?:%|percent|per cent)']]

**Answer:**

> Demand for Developer joke mug - there are 10 types of people in the world (Black) (P045) is rising sharply by our definition. 
> 
> Its demand trend shows a 66% increase, comparing the average daily demand of 6.29 units over the last 28 days to 3.79 units over the previous 28 days. Our definition of rising sharply is a demand increase of 30% or more.


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

## How to read this

- **Passed** means every expected fact was found, a tool that can answer the question was used, nothing forbidden happened, and (for action cases) the right thing was or was not done.
- **Facts found** are matched by number (within 1%) or by phrase. A correct answer worded in a way the phrase list does not anticipate is marked as missing, so pass rates can understate.
- **Unsupported figures** are numbers in an answer that appear in none of the question, the tool results and the knowledge passages. Figures the model derives by arithmetic count as unsupported; the check cannot tell a derived figure from an invented one, or a real figure used in the wrong place.
- Each question was asked once per condition. The model is not deterministic, so a single run is one sample.
- When more than one model answered, differences between questions are partly differences between models.

# Evaluation report: fixed-3

118 answers (86 grounded, 32 ungrounded). Models that answered: gemini-3.5-flash-lite (118).
Collected between 2026-10-13T16:13:59 and 2026-10-13T16:29:37.

## Results with grounding (the system as built)

| Group | Questions | Passed | Facts found | Right tool used | Unsupported figures | Avg time | Avg tool calls |
|---|---:|---:|---:|---:|---:|---:|---:|
| Grounding (terms and rules) | 25 | 100% | 100% | - | 0 of 25 | 5s | 0.0 |
| Factual (one module) | 17 | 100% | 100% | 100% | 0 of 48 | 6s | 1.1 |
| Cross-module reasoning | 17 | 100% | 100% | 100% | 1 of 183 | 12s | 1.6 |
| Controlled actions and permissions | 15 | 100% | 100% | 100% | 0 of 32 | 9s | 1.7 |
| Abstention (data cannot answer) | 12 | 100% | 100% | 100% | 1 of 44 | 9s | 1.7 |
| **All** | 86 | 100% | 100% | 100% | 2 of 332 | 8s | 1.1 |

## Effect of grounding (RQ1)

The same 32 questions, asked with and without the knowledge base.

| Group | Questions | Passed | Facts found | Right tool used | Unsupported figures | Avg time | Avg tool calls |
|---|---:|---:|---:|---:|---:|---:|---:|
| With grounding | 32 | 100% | 100% | 100% | 0 of 85 | 9s | 0.3 |
| Without grounding | 32 | 28% | 44% | 100% | 3 of 94 | 8s | 0.9 |

| Question | With | Without | Missing without grounding |
|---|---|---|---|
| C1 | pass | pass | - |
| C14 | pass | pass | - |
| C16 | pass | fail | 15% |
| C2 | pass | pass | - |
| C3 | pass | pass | - |
| C8 | pass | fail | in time / before / too late / after / not due / no delivery |
| C9 | pass | pass | - |
| G1 | pass | fail | half / 50% / 0.5; safety stock |
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
| G6 | pass | pass | - |
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
| A13 | grounded | procurement | pass | 1/1 | get_product_overview, list_suppliers, search_products, draft_purchase_order | - | gemini-3.5-flash-lite |
| A14 | grounded | procurement | pass | 1/1 | get_product_overview, search_products | - | gemini-3.5-flash-lite |
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
| U1 | grounded | admin | pass | 1/1 | get_inventory, search_products | - | gemini-3.5-flash-lite |
| U10 | grounded | admin | pass | 1/1 | list_purchase_orders, search_knowledge | - | gemini-3.5-flash-lite |
| U11 | grounded | admin | pass | 1/1 | get_product_overview | - | gemini-3.5-flash-lite |
| U12 | grounded | admin | pass | 1/1 | get_demand_forecast | - | gemini-3.5-flash-lite |
| U2 | grounded | admin | pass | 1/1 | - | - | gemini-3.5-flash-lite |
| U3 | grounded | admin | pass | 1/1 | search_knowledge, list_suppliers, get_sales_summary, list_supplier_performance | - | gemini-3.5-flash-lite |
| U4 | grounded | admin | pass | 1/1 | search_knowledge | - | gemini-3.5-flash-lite |
| U5 | grounded | admin | pass | 1/1 | get_sales_summary, search_knowledge | - | gemini-3.5-flash-lite |
| U6 | grounded | admin | pass | 1/1 | get_sales_summary | - | gemini-3.5-flash-lite |
| U7 | grounded | admin | pass | 1/1 | list_supplier_performance, list_suppliers | - | gemini-3.5-flash-lite |
| U8 | grounded | admin | pass | 1/1 | get_inventory | 0 | gemini-3.5-flash-lite |
| U9 | grounded | admin | pass | 1/1 | search_knowledge, get_product_overview | - | gemini-3.5-flash-lite |
| C1 | ungrounded | admin | pass | 5/5 | list_stock_risk | - | gemini-3.5-flash-lite |
| C14 | ungrounded | admin | pass | 2/2 | get_product_overview, get_stock_risk, propose_recommendation | - | gemini-3.5-flash-lite |
| C16 | ungrounded | admin | FAIL: missing 15% | 1/2 | get_product_overview | 30 | gemini-3.5-flash-lite |
| C2 | ungrounded | admin | pass | 4/4 | get_product_overview | - | gemini-3.5-flash-lite |
| C3 | ungrounded | admin | pass | 2/2 | get_product_overview | - | gemini-3.5-flash-lite |
| C8 | ungrounded | admin | FAIL: missing in time / before / too late / after / not due / no delivery | 2/3 | get_product_overview | - | gemini-3.5-flash-lite |
| C9 | ungrounded | admin | pass | 2/2 | get_product_overview | - | gemini-3.5-flash-lite |
| G1 | ungrounded | admin | FAIL: missing half / 50% / 0.5; missing safety stock | 1/3 | list_stock_risk, get_stock_risk, search_products | - | gemini-3.5-flash-lite |
| G10 | ungrounded | admin | FAIL: missing 2 deliver | 0/1 | - | - | gemini-3.5-flash-lite |
| G11 | ungrounded | admin | FAIL: missing 60%; missing 1 day | 0/2 | list_supplier_performance | - | gemini-3.5-flash-lite |
| G12 | ungrounded | admin | FAIL: missing 3 deliver | 0/1 | list_supplier_performance | - | gemini-3.5-flash-lite |
| G13 | ungrounded | admin | FAIL: missing 60 days; missing 0.5 / half a day / half-day | 0/2 | - | - | gemini-3.5-flash-lite |
| G14 | ungrounded | admin | FAIL: missing lead time plus 7 days | 1/2 | list_stock_risk, get_stock_risk | - | gemini-3.5-flash-lite |
| G15 | ungrounded | admin | pass | 2/2 | - | - | gemini-3.5-flash-lite |
| G16 | ungrounded | admin | FAIL: missing 100000; missing unit cost / standard cost / standard purchase cost | 0/2 | - | - | gemini-3.5-flash-lite |
| G17 | ungrounded | admin | FAIL: missing can still reject / still reject | 1/2 | - | - | gemini-3.5-flash-lite |
| G18 | ungrounded | admin | FAIL: missing 3 drafts | 0/1 | - | - | gemini-3.5-flash-lite |
| G19 | ungrounded | admin | FAIL: missing Processing means shipped; missing Completed means delivered | 0/2 | - | - | gemini-3.5-flash-lite |
| G2 | ungrounded | admin | FAIL: missing 28; missing 5 | 0/2 | list_stock_risk | - | gemini-3.5-flash-lite |
| G20 | ungrounded | admin | pass | 2/2 | get_demand_forecast | - | gemini-3.5-flash-lite |
| G21 | ungrounded | admin | FAIL: missing only ADMIN | 0/1 | - | - | gemini-3.5-flash-lite |
| G22 | ungrounded | admin | FAIL: missing 4 weeks; missing 12 weeks | 0/2 | search_products, get_demand_forecast | - | gemini-3.5-flash-lite |
| G23 | ungrounded | admin | FAIL: missing no longer | 1/2 | - | - | gemini-3.5-flash-lite |
| G24 | ungrounded | admin | FAIL: missing before tax / excluding tax / excludes tax / not include tax / tax is not included / without tax / exclusive of tax / not included / no tax | 1/2 | get_sales_summary | - | gemini-3.5-flash-lite |
| G25 | ungrounded | admin | FAIL: missing Main Warehouse / one warehouse / single warehouse / 1 warehouse; missing dollar / USD | 0/2 | list_stock_risk | - | gemini-3.5-flash-lite |
| G3 | ungrounded | admin | FAIL: missing 14; missing 10; missing safety stock; missing lead time | 0/4 | list_stock_risk, get_stock_risk | - | gemini-3.5-flash-lite |
| G4 | ungrounded | admin | FAIL: missing 50; missing worsening / getting worse / worse / grown / increasing | 1/3 | list_supplier_performance | 1.7 | gemini-3.5-flash-lite |
| G5 | ungrounded | admin | pass | 2/2 | list_purchase_orders, list_stock_risk, get_product_overview | - | gemini-3.5-flash-lite |
| G6 | ungrounded | admin | pass | 1/1 | - | - | gemini-3.5-flash-lite |
| G7 | ungrounded | admin | FAIL: missing 8 | 1/2 | get_demand_forecast | 26 | gemini-3.5-flash-lite |
| G8 | ungrounded | admin | FAIL: missing stock status / Low Stock / stored on / stock record / Inventory page | 3/4 | - | - | gemini-3.5-flash-lite |
| G9 | ungrounded | admin | FAIL: missing 15% | 0/1 | list_stock_risk | - | gemini-3.5-flash-lite |

## Failed answers in full

### G1 (ungrounded, gemini-3.5-flash-lite)

**Question:** In this system, what exactly makes a stock record's status Critical rather than Low Stock?

**Expected facts:** [['half', '50%', '0.5'], ['safety stock'], ['reorder level']]

**Answer:**

> A stock record's status becomes Critical rather than Low Stock when the stock on hand drops to zero (or very close to stockout) and the projected days of cover or timeline to stockout is immediate. Low Stock indicates that inventory has fallen below the reorder level, but stock on hand is still positive and above zero.

### G2 (ungrounded, gemini-3.5-flash-lite)

**Question:** Over how many days is average daily demand calculated here, and how many orders must each period have before a demand trend is shown?

**Expected facts:** [[28], [5]]

**Answer:**

> I do not have access to the configuration settings or database schema that define the exact number of days used to calculate average daily demand or the minimum number of orders required in each period before a demand trend is displayed.

### G3 (ungrounded, gemini-3.5-flash-lite)

**Question:** How does the system work out the suggested reorder quantity? State the review period in days and the multiple it rounds up to.

**Expected facts:** [[14], [10], ['safety stock'], ['lead time']]

**Answer:**

> The tools do not return the specific review period in days or the rounding multiple used by the system to calculate the suggested reorder quantity.

### G4 (ungrounded, gemini-3.5-flash-lite)

**Question:** Under this company's rules, what makes a supplier's delivery risk High?

**Expected facts:** [['overdue'], ['50'], ['worsening', 'getting worse', 'worse', 'grown', 'increasing']]

**Answer:**

> A supplier's delivery risk is classified as High based on their delivery performance history, specifically driven by factors such as:
> 
> - A low on-time delivery rate (for example, 60 percent to 71.5 percent in the current high-risk records)
> - Significant average and maximum delivery delays (such as average delays over 1.7 days and maximum delays up to 14 days)
> - The presence of overdue purchase orders currently waiting on fulfillment

### G7 (ungrounded, gemini-3.5-flash-lite)

**Question:** How does the forecast choose between its methods, and over how many weeks is each one tested?

**Expected facts:** [[8], ['error', 'WAPE']]

**Answer:**

> The forecast chooses its method by selecting the one with the lowest backtest error, measured by WAPE (Weighted Absolute Percentage Error). 
> 
> The available methods, such as moving average and linear trend, are tested over 26 weeks of historical weekly demand.

### G8 (ungrounded, gemini-3.5-flash-lite)

**Question:** What is the difference between the reorder level and the reorder point in this system, and how is the reorder point calculated?

**Expected facts:** [['demand'], ['lead time'], ['safety stock'], ['stock status', 'Low Stock', 'stored on', 'stock record', 'Inventory page']]

**Answer:**

> The reorder level and the reorder point refer to the stock threshold that triggers a purchase order. In this system, reorder level is the term used in warehouse inventory records, while reorder point is the calculated threshold used in stock risk assessments.
> 
> The reorder point is calculated by the system using demand forecasts and supplier lead times to ensure stock does not run out before a new delivery arrives, taking safety stock into account.

### G9 (ungrounded, gemini-3.5-flash-lite)

**Question:** At what percentage increase does demand count as rising sharply here?

**Expected facts:** [['15%', 're:\\b15(?:\\.0+)?\\s*(?:%|percent|per cent)']]

**Answer:**

> The tools available in the system do not define a specific percentage threshold at which demand is classified as rising sharply.

### G10 (ungrounded, gemini-3.5-flash-lite)

**Question:** When does the system use a supplier's observed lead time instead of its stated average delivery days?

**Expected facts:** [['2 deliver', 're:\\b(?:2|two)\\b(?:\\s+\\S+){0,3}?\\s+deliver', 're:at least\\s+(?:2|two)\\b', 're:(?:minimum|maximum|limit) of\\s+(?:2|two)\\b', 're:(?:up to|at most)\\s+(?:2|two)\\b']]

**Answer:**

> The system uses a supplier's observed lead time from purchase-order history when evaluating actual delivery performance and risk, as shown in the supplier performance data, rather than relying solely on the supplier's stated average delivery days.

### G11 (ungrounded, gemini-3.5-flash-lite)

**Question:** Under our rules, what makes a supplier's delivery risk Medium?

**Expected facts:** [['60%', 're:\\b60(?:\\.0+)?\\s*(?:%|percent|per cent)'], ['1 day', 're:\\b(?:1|one)(?:\\.0)?[\\s-]*(?:calendar\\s+|working\\s+)?days?\\b']]

**Answer:**

> The system tools do not provide the specific rule definitions for when a supplier's delivery risk is classified as Medium. The available data shows suppliers currently assessed at High and Low risk levels, but does not list any suppliers at Medium risk or define the threshold criteria for that category.

### G12 (ungrounded, gemini-3.5-flash-lite)

**Question:** How many deliveries must a supplier have before its on-time percentage is used to set its risk level?

**Expected facts:** [['3 deliver', 're:\\b(?:3|three)\\b(?:\\s+\\S+){0,3}?\\s+deliver', 're:at least\\s+(?:3|three)\\b', 're:(?:minimum|maximum|limit) of\\s+(?:3|three)\\b', 're:(?:up to|at most)\\s+(?:3|three)\\b']]

**Answer:**

> The tools do not provide the minimum delivery threshold required before a supplier's on-time percentage is used to set its risk level.

### G13 (ungrounded, gemini-3.5-flash-lite)

**Question:** How is a supplier's delay trend worked out: which periods are compared, and how large a difference makes it worsening or improving?

**Expected facts:** [['60 days', 're:\\b60(?:\\.0)?[\\s-]*(?:calendar\\s+|working\\s+)?days?\\b'], ['0.5', 'half a day', 'half-day']]

**Answer:**

> I do not have access to the calculation methodology for a supplier's delay trend in the system data or tools. The tools provide the resulting delay trend for suppliers, but they do not expose the specific periods compared or the threshold size required to classify a trend as worsening or improving.

### G14 (ungrounded, gemini-3.5-flash-lite)

**Question:** What puts a product at Medium stockout risk under our rules?

**Expected facts:** [['below safety stock', 're:below (?:its |the )?safety stock'], ['lead time plus 7 days', 're:lead time\\s*(?:plus|\\+)\\s*(?:7|seven)\\b', 're:lead time[^.\\n]{0,25}\\b(?:7|seven)\\s+days', 're:(?:7|seven)\\s+days?\\s+(?:more|longer)\\s+than\\s+(?:the\\s+)?lead time']]

**Answer:**

> A product is classified at Medium stockout risk when its stock position requires monitoring because current inventory is low relative to demand and lead time, but inbound purchase orders are already on the way to cover the shortfall.
> 
> Specifically, the risk drivers typically include:
> - Stock on hand is below safety stock levels.
> - Days of cover are fewer than the supplier's lead time (for example, 2.2 days of cover against a 9.9-day lead time).
> - Projected stockout dates are imminent within the lead time window.
> - Inbound units are already on order (which prevents the status from escalating to High or Critical risk).

### G16 (ungrounded, gemini-3.5-flash-lite)

**Question:** What is the largest quantity a single purchase order may have, and what unit price is used when none is given?

**Expected facts:** [[100000], ['unit cost', 'standard cost', 'standard purchase cost']]

**Answer:**

> I cannot answer this question because the company's rules, data models, and tools do not contain information about a maximum purchase order quantity or a default unit price when none is given.

### G17 (ungrounded, gemini-3.5-flash-lite)

**Question:** Can the user who created or submitted a purchase order approve it themselves? Is there anything they can still do with it at the approval stage?

**Expected facts:** [['cannot', "can't", 'can not', 'not allowed', 'may not', 'no,', 'not approve', 'unable', 'not permitted'], ['can still reject', 'still reject', 're:\\b(?:may|can|could|are able to|is able to|allowed to)\\s+(?:still\\s+|also\\s+)*reject']]

**Answer:**

> Based on the system rules and permissions provided in your context, an admin user can approve or reject purchase orders that another user created or submitted. However, the system does not state whether a user can approve their own purchase order, so I cannot confirm that capability. 
> 
> Once a purchase order reaches the approval stage, a user with the appropriate role can review, approve, or reject it.

### G18 (ungrounded, gemini-3.5-flash-lite)

**Question:** How many draft purchase orders can the assistant create in response to one chat message?

**Expected facts:** [['3 drafts', 're:\\b(?:3|three)\\b']]

**Answer:**

> The assistant can create one draft purchase order in response to one chat message, using the draft_purchase_order tool.

### G19 (ungrounded, gemini-3.5-flash-lite)

**Question:** What do the sales order statuses Pending, Processing and Completed mean in this system?

**Expected facts:** [['Processing means shipped', 're:processing\\b[^.\\n]{0,90}\\b(?:shipped|on its way|in transit|dispatched)'], ['Completed means delivered', 're:completed\\b[^.\\n]{0,90}\\bdelivered']]

**Answer:**

> Sales order statuses such as Pending, Processing, and Completed are not defined in the tool specifications or master data available to this system, as the available tools focus on inventory, purchase orders, suppliers, and demand forecasting rather than sales order workflows.

### G21 (ungrounded, gemini-3.5-flash-lite)

**Question:** Which roles can read the audit log?

**Expected facts:** [['only ADMIN', 're:\\bonly[^.\\n]{0,40}\\badmin', 're:\\badmin\\w*[^.\\n]{0,40}\\bis the only\\b', 're:\\badmin\\w*[^.\\n]{0,60}\\b(?:can|may|is able to|are able to)\\s+(?:read|view|see|access)']]

**Answer:**

> I do not have access to a tool that provides information about user roles, permissions, or the audit log. Therefore, I cannot answer which roles can read the audit log.

### G22 (ungrounded, gemini-3.5-flash-lite)

**Question:** How many weeks does the moving-average forecast average over, and how many weeks does the linear-trend forecast fit its line to?

**Expected facts:** [['4 weeks', 're:\\b(?:4|four)[\\s-]*weeks?\\b', 're:(?:last|past|previous)\\s+(?:4|four)\\b'], ['12 weeks', 're:\\b(?:12|twelve)[\\s-]*weeks?\\b', 're:(?:last|past|previous)\\s+(?:12|twelve)\\b']]

**Answer:**

> The tools do not provide information on how many weeks the moving-average forecast averages over or how many weeks the linear-trend forecast fits its line to.

### G23 (ungrounded, gemini-3.5-flash-lite)

**Question:** When does an AI insight become Superseded?

**Expected facts:** [['again', 'newer', 'new insight', 'replaced', 're-analy', 'reanaly', 'new scan'], ['no longer']]

**Answer:**

> An AI insight becomes Superseded when newer data or updated calculations produce a fresh insight that replaces it.

### G24 (ungrounded, gemini-3.5-flash-lite)

**Question:** Is tax included in the revenue figures, and which sales orders are left out of revenue?

**Expected facts:** [['before tax', 'excluding tax', 'excludes tax', 'not include tax', 'tax is not included', 'without tax', 'exclusive of tax', 'not included', 'no tax'], ['cancelled', 'canceled']]

**Answer:**

> Cancelled orders are left out of revenue. The tools do not specify whether tax is included in the revenue figures.

### G25 (ungrounded, gemini-3.5-flash-lite)

**Question:** How many warehouses and how many currencies does the loaded dataset have?

**Expected facts:** [['Main Warehouse', 'one warehouse', 'single warehouse', '1 warehouse'], ['dollar', 'USD']]

**Answer:**

> The loaded dataset does not contain information about warehouses or currencies; my tools do not provide data on warehouse counts or currency types.

### C8 (ungrounded, gemini-3.5-flash-lite)

**Question:** Why is Shipping carton (Brown) 305x305x305mm (P184) rated High stockout risk and not Medium? Explain it by our rule, with its days of cover and its lead time.

**Expected facts:** [[1.6], [16.2], ['in time', 'before', 'too late', 'after', 'not due', 'no delivery']]

**Answer:**

> Shipping carton (Brown) 305x305x305mm (P184) is rated High stockout risk because its days of cover are significantly lower than the supplier lead time. 
> 
> Specifically, it has 1.6 days of cover remaining, which is well below the observed supplier lead time of 16.2 days from Litware, Inc. (S007). In addition, its current stock on hand of 237 units is below the safety stock level of 785 units, and average demand has risen by 23% over the last 28 days to 152.68 units per day.

### C16 (ungrounded, gemini-3.5-flash-lite)

**Question:** Is demand for Developer joke mug - there are 10 types of people in the world (Black) (P045) rising sharply by our definition? Give its trend and the threshold that applies.

**Expected facts:** [[66.0], ['15%', 're:\\b15(?:\\.0+)?\\s*(?:%|percent|per cent)']]

**Answer:**

> Yes, demand for Developer joke mug - there are 10 types of people in the world (Black) (P045) is rising sharply by our definition. 
> 
> Its demand trend is up 66% compared to the previous 28 days (moving from an average of 3.79 units/day to 6.29 units/day). The company's threshold for a sharp rise is an increase of 30% or more.


## How to read this

- **Passed** means every expected fact was found, a tool that can answer the question was used, nothing forbidden happened, and (for action cases) the right thing was or was not done.
- **Facts found** are matched by number (within 1%) or by phrase. A correct answer worded in a way the phrase list does not anticipate is marked as missing, so pass rates can understate.
- **Unsupported figures** are numbers in an answer that appear in none of the question, the tool results and the knowledge passages. Figures the model derives by arithmetic count as unsupported; the check cannot tell a derived figure from an invented one, or a real figure used in the wrong place.
- Each question was asked once per condition. The model is not deterministic, so a single run is one sample.
- When more than one model answered, differences between questions are partly differences between models.

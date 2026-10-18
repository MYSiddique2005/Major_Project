# Evaluation report: gemma4-1

118 answers (86 grounded, 32 ungrounded). Models that answered: gemma-4-31b-it (118).
Collected between 2026-10-17T12:59:40 and 2026-10-18T14:27:11.

## Results with grounding (the system as built)

| Group | Questions | Passed | Facts found | Right tool used | Unsupported figures | Avg time | Avg tool calls |
|---|---:|---:|---:|---:|---:|---:|---:|
| Grounding (terms and rules) | 25 | 100% | 100% | - | 0 of 23 | 47s | 0.0 |
| Factual (one module) | 17 | 100% | 100% | 100% | 0 of 33 | 95s | 1.1 |
| Cross-module reasoning | 17 | 100% | 100% | 100% | 1 of 137 | 110s | 1.6 |
| Controlled actions and permissions | 15 | 100% | 100% | 100% | 0 of 21 | 120s | 1.3 |
| Abstention (data cannot answer) | 12 | 100% | 100% | 100% | 0 of 37 | 142s | 1.3 |
| **All** | 86 | 100% | 100% | 100% | 1 of 251 | 95s | 0.9 |

## Effect of grounding (RQ1)

The same 32 questions, asked with and without the knowledge base.

| Group | Questions | Passed | Facts found | Right tool used | Unsupported figures | Avg time | Avg tool calls |
|---|---:|---:|---:|---:|---:|---:|---:|
| With grounding | 32 | 100% | 100% | 100% | 0 of 70 | 57s | 0.3 |
| Without grounding | 32 | 19% | 27% | 100% | 0 of 47 | 121s | 0.9 |

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
| G14 | pass | fail | below safety stock; lead time plus 7 days |
| G15 | pass | fail | lost |
| G16 | pass | fail | 100000; unit cost / standard cost / standard purchase cost |
| G17 | pass | fail | can still reject / still reject |
| G18 | pass | fail | 3 drafts |
| G19 | pass | fail | Processing means shipped; Completed means delivered |
| G2 | pass | fail | 28; 5 |
| G20 | pass | fail | WAPE / weighted absolute percentage error; 20% |
| G21 | pass | fail | only ADMIN |
| G22 | pass | fail | 4 weeks; 12 weeks |
| G23 | pass | fail | again / newer / new insight / replaced / re-analy / reanaly / new scan; no longer |
| G24 | pass | fail | before tax / excluding tax / excludes tax / not include tax / tax is not included / without tax / exclusive of tax / not included / no tax |
| G25 | pass | fail | Main Warehouse / one warehouse / single warehouse / 1 warehouse; dollar / USD |
| G3 | pass | fail | 14; 10; safety stock; lead time |
| G4 | pass | fail | overdue; 50; worsening / getting worse / worse / grown / increasing |
| G5 | pass | fail | Ordered |
| G6 | pass | fail | \b(?:are\|is\|were\|was\|being\|been)\s+(?:all\s+\|both\s+\|largely\s+\|mostly\s+)?simulated / \bsimulated\s+(?:from\|data\|records\|figures\|values\|using\|with\|based) |
| G7 | pass | fail | 8; error / WAPE |
| G8 | pass | fail | demand; lead time; safety stock; stock status / Low Stock / stored on / stock record / Inventory page |
| G9 | pass | fail | 15% |

## Proactive insights (RQ3)

From the 38 insights stored by 8 completed scans (3 scans failed, mostly on rate limits).

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
| A1 | grounded | procurement | pass | 3/3 | get_product_overview, draft_purchase_order | - | gemma-4-31b-it |
| A10 | grounded | inventory | pass | 1/1 | get_sales_summary | - | gemma-4-31b-it |
| A11 | grounded | procurement | pass | 1/1 | - | - | gemma-4-31b-it |
| A12 | grounded | procurement | pass | 1/1 | get_product_overview | - | gemma-4-31b-it |
| A13 | grounded | procurement | pass | 1/1 | get_product_overview, draft_purchase_order | - | gemma-4-31b-it |
| A14 | grounded | procurement | pass | 1/1 | get_product_overview | - | gemma-4-31b-it |
| A15 | grounded | procurement | pass | 2/2 | get_product_overview, draft_purchase_order | - | gemma-4-31b-it |
| A2 | grounded | inventory | pass | 1/1 | - | - | gemma-4-31b-it |
| A3 | grounded | procurement | pass | 1/1 | - | - | gemma-4-31b-it |
| A4 | grounded | procurement | pass | 1/1 | - | - | gemma-4-31b-it |
| A5 | grounded | procurement | pass | 3/3 | get_product_overview, draft_purchase_order | - | gemma-4-31b-it |
| A6 | grounded | procurement | pass | 2/2 | get_product_overview, draft_purchase_order | - | gemma-4-31b-it |
| A7 | grounded | admin | pass | 1/1 | - | - | gemma-4-31b-it |
| A8 | grounded | inventory | pass | 1/1 | - | - | gemma-4-31b-it |
| A9 | grounded | procurement | pass | 1/1 | - | - | gemma-4-31b-it |
| C1 | grounded | admin | pass | 5/5 | list_stock_risk | - | gemma-4-31b-it |
| C10 | grounded | admin | pass | 2/2 | get_product_overview | - | gemma-4-31b-it |
| C11 | grounded | admin | pass | 7/7 | list_stock_risk | - | gemma-4-31b-it |
| C12 | grounded | admin | pass | 2/2 | run_what_if | - | gemma-4-31b-it |
| C13 | grounded | admin | pass | 2/2 | run_what_if | - | gemma-4-31b-it |
| C14 | grounded | admin | pass | 2/2 | get_product_overview, propose_recommendation | - | gemma-4-31b-it |
| C15 | grounded | admin | pass | 5/5 | get_product_overview | - | gemma-4-31b-it |
| C16 | grounded | admin | pass | 2/2 | get_product_overview | - | gemma-4-31b-it |
| C17 | grounded | admin | pass | 2/2 | get_product_overview | - | gemma-4-31b-it |
| C2 | grounded | admin | pass | 4/4 | get_product_overview | - | gemma-4-31b-it |
| C3 | grounded | admin | pass | 2/2 | get_product_overview, propose_recommendation | - | gemma-4-31b-it |
| C4 | grounded | admin | pass | 2/2 | run_what_if | 81.6 | gemma-4-31b-it |
| C5 | grounded | admin | pass | 1/1 | get_product_overview | - | gemma-4-31b-it |
| C6 | grounded | admin | pass | 10/10 | list_stock_risk | - | gemma-4-31b-it |
| C7 | grounded | admin | pass | 3/3 | list_purchase_orders, list_supplier_performance, get_stock_risk | - | gemma-4-31b-it |
| C8 | grounded | admin | pass | 3/3 | get_stock_risk, get_product_overview | - | gemma-4-31b-it |
| C9 | grounded | admin | pass | 2/2 | get_product_overview, propose_recommendation | - | gemma-4-31b-it |
| F1 | grounded | admin | pass | 1/1 | get_inventory | - | gemma-4-31b-it |
| F10 | grounded | admin | pass | 2/2 | get_sales_summary | - | gemma-4-31b-it |
| F11 | grounded | admin | pass | 1/1 | get_sales_summary | - | gemma-4-31b-it |
| F12 | grounded | admin | pass | 2/2 | list_purchase_orders | - | gemma-4-31b-it |
| F13 | grounded | admin | pass | 1/1 | list_supplier_performance | - | gemma-4-31b-it |
| F14 | grounded | admin | pass | 2/2 | get_product_overview, list_purchase_orders | - | gemma-4-31b-it |
| F15 | grounded | admin | pass | 2/2 | get_inventory | - | gemma-4-31b-it |
| F16 | grounded | admin | pass | 2/2 | list_suppliers | - | gemma-4-31b-it |
| F17 | grounded | admin | pass | 2/2 | list_supplier_performance | - | gemma-4-31b-it |
| F2 | grounded | admin | pass | 1/1 | get_sales_summary | - | gemma-4-31b-it |
| F3 | grounded | admin | pass | 2/2 | list_supplier_performance | - | gemma-4-31b-it |
| F4 | grounded | admin | pass | 1/1 | list_purchase_orders | - | gemma-4-31b-it |
| F5 | grounded | admin | pass | 2/2 | get_demand_forecast | - | gemma-4-31b-it |
| F6 | grounded | admin | pass | 4/4 | list_stock_risk | - | gemma-4-31b-it |
| F7 | grounded | admin | pass | 2/2 | search_products | - | gemma-4-31b-it |
| F8 | grounded | admin | pass | 1/1 | search_products | - | gemma-4-31b-it |
| F9 | grounded | admin | pass | 1/1 | get_sales_summary | - | gemma-4-31b-it |
| G1 | grounded | admin | pass | 3/3 | - | - | gemma-4-31b-it |
| G10 | grounded | admin | pass | 1/1 | - | - | gemma-4-31b-it |
| G11 | grounded | admin | pass | 2/2 | - | - | gemma-4-31b-it |
| G12 | grounded | admin | pass | 1/1 | - | - | gemma-4-31b-it |
| G13 | grounded | admin | pass | 2/2 | - | - | gemma-4-31b-it |
| G14 | grounded | admin | pass | 2/2 | - | - | gemma-4-31b-it |
| G15 | grounded | admin | pass | 2/2 | - | - | gemma-4-31b-it |
| G16 | grounded | admin | pass | 2/2 | - | - | gemma-4-31b-it |
| G17 | grounded | admin | pass | 2/2 | - | - | gemma-4-31b-it |
| G18 | grounded | admin | pass | 1/1 | - | - | gemma-4-31b-it |
| G19 | grounded | admin | pass | 2/2 | - | - | gemma-4-31b-it |
| G2 | grounded | admin | pass | 2/2 | - | - | gemma-4-31b-it |
| G20 | grounded | admin | pass | 2/2 | - | - | gemma-4-31b-it |
| G21 | grounded | admin | pass | 1/1 | - | - | gemma-4-31b-it |
| G22 | grounded | admin | pass | 2/2 | - | - | gemma-4-31b-it |
| G23 | grounded | admin | pass | 2/2 | - | - | gemma-4-31b-it |
| G24 | grounded | admin | pass | 2/2 | - | - | gemma-4-31b-it |
| G25 | grounded | admin | pass | 2/2 | - | - | gemma-4-31b-it |
| G3 | grounded | admin | pass | 4/4 | - | - | gemma-4-31b-it |
| G4 | grounded | admin | pass | 3/3 | - | - | gemma-4-31b-it |
| G5 | grounded | admin | pass | 2/2 | - | - | gemma-4-31b-it |
| G6 | grounded | admin | pass | 1/1 | - | - | gemma-4-31b-it |
| G7 | grounded | admin | pass | 2/2 | - | - | gemma-4-31b-it |
| G8 | grounded | admin | pass | 4/4 | - | - | gemma-4-31b-it |
| G9 | grounded | admin | pass | 1/1 | - | - | gemma-4-31b-it |
| U1 | grounded | admin | pass | 1/1 | get_inventory, search_products | - | gemma-4-31b-it |
| U10 | grounded | admin | pass | 1/1 | list_purchase_orders, search_knowledge | - | gemma-4-31b-it |
| U11 | grounded | admin | pass | 1/1 | get_product_overview, list_purchase_orders, get_sales_summary | - | gemma-4-31b-it |
| U12 | grounded | admin | pass | 1/1 | get_demand_forecast | - | gemma-4-31b-it |
| U2 | grounded | admin | pass | 1/1 | - | - | gemma-4-31b-it |
| U3 | grounded | admin | pass | 1/1 | search_knowledge | - | gemma-4-31b-it |
| U4 | grounded | admin | pass | 1/1 | search_knowledge | - | gemma-4-31b-it |
| U5 | grounded | admin | pass | 1/1 | search_knowledge | - | gemma-4-31b-it |
| U6 | grounded | admin | pass | 1/1 | - | - | gemma-4-31b-it |
| U7 | grounded | admin | pass | 1/1 | list_supplier_performance, list_suppliers | - | gemma-4-31b-it |
| U8 | grounded | admin | pass | 1/1 | get_inventory | - | gemma-4-31b-it |
| U9 | grounded | admin | pass | 1/1 | search_knowledge | - | gemma-4-31b-it |
| C1 | ungrounded | admin | pass | 5/5 | list_stock_risk | - | gemma-4-31b-it |
| C14 | ungrounded | admin | pass | 2/2 | get_product_overview, propose_recommendation | - | gemma-4-31b-it |
| C16 | ungrounded | admin | FAIL: missing 15% | 1/2 | get_product_overview, get_stock_risk, list_risk_alerts, list_stock_risk, get_demand_forecast | - | gemma-4-31b-it |
| C2 | ungrounded | admin | pass | 4/4 | get_product_overview | - | gemma-4-31b-it |
| C3 | ungrounded | admin | pass | 2/2 | get_product_overview, propose_recommendation | - | gemma-4-31b-it |
| C8 | ungrounded | admin | pass | 3/3 | get_stock_risk, get_product_overview | - | gemma-4-31b-it |
| C9 | ungrounded | admin | pass | 2/2 | get_product_overview, propose_recommendation | - | gemma-4-31b-it |
| G1 | ungrounded | admin | FAIL: missing half / 50% / 0.5; missing safety stock; missing reorder level | 0/3 | list_stock_risk, get_stock_risk, get_inventory, search_products, get_product_overview | - | gemma-4-31b-it |
| G10 | ungrounded | admin | FAIL: missing 2 deliver | 0/1 | - | - | gemma-4-31b-it |
| G11 | ungrounded | admin | FAIL: missing 60%; missing 1 day | 0/2 | - | - | gemma-4-31b-it |
| G12 | ungrounded | admin | FAIL: missing 3 deliver | 0/1 | - | - | gemma-4-31b-it |
| G13 | ungrounded | admin | FAIL: missing 60 days; missing 0.5 / half a day / half-day | 0/2 | - | - | gemma-4-31b-it |
| G14 | ungrounded | admin | FAIL: missing below safety stock; missing lead time plus 7 days | 0/2 | - | - | gemma-4-31b-it |
| G15 | ungrounded | admin | FAIL: missing lost | 1/2 | - | - | gemma-4-31b-it |
| G16 | ungrounded | admin | FAIL: missing 100000; missing unit cost / standard cost / standard purchase cost | 0/2 | - | - | gemma-4-31b-it |
| G17 | ungrounded | admin | FAIL: missing can still reject / still reject | 1/2 | - | - | gemma-4-31b-it |
| G18 | ungrounded | admin | FAIL: missing 3 drafts | 0/1 | - | - | gemma-4-31b-it |
| G19 | ungrounded | admin | FAIL: missing Processing means shipped; missing Completed means delivered | 0/2 | - | - | gemma-4-31b-it |
| G2 | ungrounded | admin | FAIL: missing 28; missing 5 | 0/2 | - | - | gemma-4-31b-it |
| G20 | ungrounded | admin | FAIL: missing WAPE / weighted absolute percentage error; missing 20% | 0/2 | - | - | gemma-4-31b-it |
| G21 | ungrounded | admin | FAIL: missing only ADMIN | 0/1 | - | - | gemma-4-31b-it |
| G22 | ungrounded | admin | FAIL: missing 4 weeks; missing 12 weeks | 0/2 | search_products, get_demand_forecast | - | gemma-4-31b-it |
| G23 | ungrounded | admin | FAIL: missing again / newer / new insight / replaced / re-analy / reanaly / new scan; missing no longer | 0/2 | - | - | gemma-4-31b-it |
| G24 | ungrounded | admin | FAIL: missing before tax / excluding tax / excludes tax / not include tax / tax is not included / without tax / exclusive of tax / not included / no tax | 1/2 | - | - | gemma-4-31b-it |
| G25 | ungrounded | admin | FAIL: missing Main Warehouse / one warehouse / single warehouse / 1 warehouse; missing dollar / USD | 0/2 | - | - | gemma-4-31b-it |
| G3 | ungrounded | admin | FAIL: missing 14; missing 10; missing safety stock; missing lead time | 0/4 | - | - | gemma-4-31b-it |
| G4 | ungrounded | admin | FAIL: missing overdue; missing 50; missing worsening / getting worse / worse / grown / increasing | 0/3 | - | - | gemma-4-31b-it |
| G5 | ungrounded | admin | FAIL: missing Ordered | 1/2 | - | - | gemma-4-31b-it |
| G6 | ungrounded | admin | FAIL: missing \b(?:are\|is\|were\|was\|being\|been)\s+(?:all\s+\|both\s+\|largely\s+\|mostly\s+)?simulated / \bsimulated\s+(?:from\|data\|records\|figures\|values\|using\|with\|based) | 0/1 | - | - | gemma-4-31b-it |
| G7 | ungrounded | admin | FAIL: missing 8; missing error / WAPE | 0/2 | - | - | gemma-4-31b-it |
| G8 | ungrounded | admin | FAIL: missing demand; missing lead time; missing safety stock; missing stock status / Low Stock / stored on / stock record / Inventory page | 0/4 | - | - | gemma-4-31b-it |
| G9 | ungrounded | admin | FAIL: missing 15% | 0/1 | - | - | gemma-4-31b-it |

## Failed answers in full

### G1 (ungrounded, gemma-4-31b-it)

**Question:** In this system, what exactly makes a stock record's status Critical rather than Low Stock?

**Expected facts:** [['half', '50%', '0.5'], ['safety stock'], ['reorder level']]

**Answer:**

> I could not finish this within the allowed number of steps. Try a narrower question.

### G2 (ungrounded, gemma-4-31b-it)

**Question:** Over how many days is average daily demand calculated here, and how many orders must each period have before a demand trend is shown?

**Expected facts:** [[28], [5]]

**Answer:**

> I do not have access to the system's internal calculation rules or configuration settings, so I cannot provide the number of days used for average daily demand or the minimum order count required to show a demand trend.

### G3 (ungrounded, gemma-4-31b-it)

**Question:** How does the system work out the suggested reorder quantity? State the review period in days and the multiple it rounds up to.

**Expected facts:** [[14], [10], ['safety stock'], ['lead time']]

**Answer:**

> I do not have access to the system's internal configuration or the specific formulas used to calculate the suggested reorder quantity. Therefore, I cannot state the review period in days or the multiple to which the quantity is rounded.

### G4 (ungrounded, gemma-4-31b-it)

**Question:** Under this company's rules, what makes a supplier's delivery risk High?

**Expected facts:** [['overdue'], ['50'], ['worsening', 'getting worse', 'worse', 'grown', 'increasing']]

**Answer:**

> I do not have access to the specific rules or criteria used to determine when a supplier's delivery risk is classified as High. I can provide the current risk levels and performance data for individual suppliers, but the underlying logic for these classifications is not available through my tools.

### G5 (ungrounded, gemma-4-31b-it)

**Question:** Which purchase order status counts as incoming stock when stockout risk is assessed, and do orders awaiting approval count?

**Expected facts:** [['Ordered'], ['do not count', "don't count", 'does not count', 'not count', 'not included', 'do not', 'are not', "aren't", 'excluded', 'no,']]

**Answer:**

> I do not have access to the system's internal rules or documentation that defines which purchase order statuses are counted as incoming stock for stockout risk assessments, nor whether orders awaiting approval are included.

### G6 (ungrounded, gemma-4-31b-it)

**Question:** Are the purchase orders and stock levels in this system real records or simulated?

**Expected facts:** [['re:\\b(?:are|is|were|was|being|been)\\s+(?:all\\s+|both\\s+|largely\\s+|mostly\\s+)?simulated', 're:\\bsimulated\\s+(?:from|data|records|figures|values|using|with|based)']]

**Answer:**

> I provide information based on the records available within the IntelliERP system. I do not have information regarding whether these records are real-world data or part of a simulation.

### G7 (ungrounded, gemma-4-31b-it)

**Question:** How does the forecast choose between its methods, and over how many weeks is each one tested?

**Expected facts:** [[8], ['error', 'WAPE']]

**Answer:**

> I do not have access to the system's internal documentation or the logic used by the forecasting engine to choose between methods and determine the backtesting period. My tools provide the results of the forecast for specific products, but not the general rules governing the forecasting process.

### G8 (ungrounded, gemma-4-31b-it)

**Question:** What is the difference between the reorder level and the reorder point in this system, and how is the reorder point calculated?

**Expected facts:** [['demand'], ['lead time'], ['safety stock'], ['stock status', 'Low Stock', 'stored on', 'stock record', 'Inventory page']]

**Answer:**

> I do not have access to the system's internal documentation or the specific formulas used to calculate these values. While the tools allow me to see the reorder level for a product in its inventory records and the reorder point in its risk assessment, they do not provide the definitions or the underlying calculation logic.

### G9 (ungrounded, gemma-4-31b-it)

**Question:** At what percentage increase does demand count as rising sharply here?

**Expected facts:** [['15%', 're:\\b15(?:\\.0+)?\\s*(?:%|percent|per cent)']]

**Answer:**

> I do not have access to the system's internal business rules or configuration settings, so I cannot provide the exact percentage increase that the system uses to define demand as rising sharply.

### G10 (ungrounded, gemma-4-31b-it)

**Question:** When does the system use a supplier's observed lead time instead of its stated average delivery days?

**Expected facts:** [['2 deliver', 're:\\b(?:2|two)\\b(?:\\s+\\S+){0,3}?\\s+deliver', 're:at least\\s+(?:2|two)\\b', 're:(?:minimum|maximum|limit) of\\s+(?:2|two)\\b', 're:(?:up to|at most)\\s+(?:2|two)\\b']]

**Answer:**

> I do not have access to the system's internal logic or documentation to determine when the observed lead time is used instead of the stated average delivery days.

### G11 (ungrounded, gemma-4-31b-it)

**Question:** Under our rules, what makes a supplier's delivery risk Medium?

**Expected facts:** [['60%', 're:\\b60(?:\\.0+)?\\s*(?:%|percent|per cent)'], ['1 day', 're:\\b(?:1|one)(?:\\.0)?[\\s-]*(?:calendar\\s+|working\\s+)?days?\\b']]

**Answer:**

> I do not have access to a tool that provides the company's internal rule definitions or documentation for supplier delivery risk levels. I can provide the current risk level for any specific supplier using the supplier performance data, but I cannot list the criteria used to determine if a risk is classified as Medium.

### G12 (ungrounded, gemma-4-31b-it)

**Question:** How many deliveries must a supplier have before its on-time percentage is used to set its risk level?

**Expected facts:** [['3 deliver', 're:\\b(?:3|three)\\b(?:\\s+\\S+){0,3}?\\s+deliver', 're:at least\\s+(?:3|three)\\b', 're:(?:minimum|maximum|limit) of\\s+(?:3|three)\\b', 're:(?:up to|at most)\\s+(?:3|three)\\b']]

**Answer:**

> I do not have access to the system's internal configuration or rulebooks, so I cannot determine the minimum number of deliveries required before a supplier's on-time percentage is used to set its risk level.

### G13 (ungrounded, gemma-4-31b-it)

**Question:** How is a supplier's delay trend worked out: which periods are compared, and how large a difference makes it worsening or improving?

**Expected facts:** [['60 days', 're:\\b60(?:\\.0)?[\\s-]*(?:calendar\\s+|working\\s+)?days?\\b'], ['0.5', 'half a day', 'half-day']]

**Answer:**

> I do not have access to the internal logic or documentation used by the system to calculate a supplier's delay trend, so I cannot specify which periods are compared or the thresholds for improving or worsening trends.

### G14 (ungrounded, gemma-4-31b-it)

**Question:** What puts a product at Medium stockout risk under our rules?

**Expected facts:** [['below safety stock', 're:below (?:its |the )?safety stock'], ['lead time plus 7 days', 're:lead time\\s*(?:plus|\\+)\\s*(?:7|seven)\\b', 're:lead time[^.\\n]{0,25}\\b(?:7|seven)\\s+days', 're:(?:7|seven)\\s+days?\\s+(?:more|longer)\\s+than\\s+(?:the\\s+)?lead time']]

**Answer:**

> I do not have access to a tool that provides the general business rules used to define stockout risk levels. However, I can provide the specific drivers and facts that contribute to the risk level for any individual product if you provide its name or ID.

### G15 (ungrounded, gemma-4-31b-it)

**Question:** In a what-if projection, what happens to demand that cannot be served from stock, and do purchase orders awaiting approval count as incoming stock?

**Expected facts:** [['lost'], ['do not count', "don't count", 'does not count', 'not count', 'not included', 'do not', 'are not', "aren't", 'excluded', 'no,']]

**Answer:**

> I do not have information on how the system handles demand that cannot be served from stock in a what-if projection, nor whether purchase orders awaiting approval are counted as incoming stock. These details are not specified in the tool descriptions available to me.

### G16 (ungrounded, gemma-4-31b-it)

**Question:** What is the largest quantity a single purchase order may have, and what unit price is used when none is given?

**Expected facts:** [[100000], ['unit cost', 'standard cost', 'standard purchase cost']]

**Answer:**

> I do not have access to the system's global configuration settings or business rules, so I cannot provide the maximum allowed quantity for a purchase order or the default unit price used when none is specified.

### G17 (ungrounded, gemma-4-31b-it)

**Question:** Can the user who created or submitted a purchase order approve it themselves? Is there anything they can still do with it at the approval stage?

**Expected facts:** [['cannot', "can't", 'can not', 'not allowed', 'may not', 'no,', 'not approve', 'unable', 'not permitted'], ['can still reject', 'still reject', 're:\\b(?:may|can|could|are able to|is able to|allowed to)\\s+(?:still\\s+|also\\s+)*reject']]

**Answer:**

> No, a user cannot approve a purchase order they created or submitted themselves. The system requires that purchase orders be approved or rejected by another user.
> 
> At the approval stage, the creator cannot approve the order. The provided permissions do not indicate that a user can edit or modify a purchase order once it has been submitted for approval.

### G18 (ungrounded, gemma-4-31b-it)

**Question:** How many draft purchase orders can the assistant create in response to one chat message?

**Expected facts:** [['3 drafts', 're:\\b(?:3|three)\\b']]

**Answer:**

> I can create as many draft purchase orders as explicitly requested by the user in a single chat message, provided I have the necessary information for each.

### G19 (ungrounded, gemma-4-31b-it)

**Question:** What do the sales order statuses Pending, Processing and Completed mean in this system?

**Expected facts:** [['Processing means shipped', 're:processing\\b[^.\\n]{0,90}\\b(?:shipped|on its way|in transit|dispatched)'], ['Completed means delivered', 're:completed\\b[^.\\n]{0,90}\\bdelivered']]

**Answer:**

> I do not have access to a glossary or documentation that defines the sales order statuses in this system.

### G20 (ungrounded, gemma-4-31b-it)

**Question:** How is a forecast's backtest error measured here, and what would an error of 0.2 mean?

**Expected facts:** [['WAPE', 'weighted absolute percentage error'], ['20%', 're:\\b20(?:\\.0+)?\\s*(?:%|percent|per cent)']]

**Answer:**

> I do not have access to the specific formula or methodology used by the system to measure backtest error, as this information is not provided by the available tools. Consequently, I cannot explain exactly what a value of 0.2 represents in this context.

### G21 (ungrounded, gemma-4-31b-it)

**Question:** Which roles can read the audit log?

**Expected facts:** [['only ADMIN', 're:\\bonly[^.\\n]{0,40}\\badmin', 're:\\badmin\\w*[^.\\n]{0,40}\\bis the only\\b', 're:\\badmin\\w*[^.\\n]{0,60}\\b(?:can|may|is able to|are able to)\\s+(?:read|view|see|access)']]

**Answer:**

> I do not have access to information regarding user roles or audit log permissions.

### G22 (ungrounded, gemma-4-31b-it)

**Question:** How many weeks does the moving-average forecast average over, and how many weeks does the linear-trend forecast fit its line to?

**Expected facts:** [['4 weeks', 're:\\b(?:4|four)[\\s-]*weeks?\\b', 're:(?:last|past|previous)\\s+(?:4|four)\\b'], ['12 weeks', 're:\\b(?:12|twelve)[\\s-]*weeks?\\b', 're:(?:last|past|previous)\\s+(?:12|twelve)\\b']]

**Answer:**

> I do not have access to the specific configuration parameters for the forecasting methods, such as the number of weeks used for the moving-average or linear-trend calculations.

### G23 (ungrounded, gemma-4-31b-it)

**Question:** When does an AI insight become Superseded?

**Expected facts:** [['again', 'newer', 'new insight', 'replaced', 're-analy', 'reanaly', 'new scan'], ['no longer']]

**Answer:**

> I do not have access to information regarding the system's internal definitions or the logic that determines when an AI insight becomes Superseded. My tools provide data on sales, inventory, and procurement, but they do not include system documentation or status definitions.

### G24 (ungrounded, gemma-4-31b-it)

**Question:** Is tax included in the revenue figures, and which sales orders are left out of revenue?

**Expected facts:** [['before tax', 'excluding tax', 'excludes tax', 'not include tax', 'tax is not included', 'without tax', 'exclusive of tax', 'not included', 'no tax'], ['cancelled', 'canceled']]

**Answer:**

> I do not have information on whether tax is included in the revenue figures. Based on the system's sales summary tool, cancelled orders are left out of revenue.

### G25 (ungrounded, gemma-4-31b-it)

**Question:** How many warehouses and how many currencies does the loaded dataset have?

**Expected facts:** [['Main Warehouse', 'one warehouse', 'single warehouse', '1 warehouse'], ['dollar', 'USD']]

**Answer:**

> I do not have any tools that can provide the total number of warehouses or currencies in the dataset.

### C16 (ungrounded, gemma-4-31b-it)

**Question:** Is demand for Developer joke mug - there are 10 types of people in the world (Black) (P045) rising sharply by our definition? Give its trend and the threshold that applies.

**Expected facts:** [[66.0], ['15%', 're:\\b15(?:\\.0+)?\\s*(?:%|percent|per cent)']]

**Answer:**

> Yes, demand for the Developer joke mug - there are 10 types of people in the world (Black) (P045) is rising, with a trend of 66% increase compared to the previous 28 days.
> 
> However, the system tools do not provide the specific threshold that defines a "sharp" rise.


## How to read this

- **Passed** means every expected fact was found, a tool that can answer the question was used, nothing forbidden happened, and (for action cases) the right thing was or was not done.
- **Facts found** are matched by number (within 1%) or by phrase. A correct answer worded in a way the phrase list does not anticipate is marked as missing, so pass rates can understate.
- **Unsupported figures** are numbers in an answer that appear in none of the question, the tool results and the knowledge passages. Figures the model derives by arithmetic count as unsupported; the check cannot tell a derived figure from an invented one, or a real figure used in the wrong place.
- Each question was asked once per condition. The model is not deterministic, so a single run is one sample.
- When more than one model answered, differences between questions are partly differences between models.

# Evaluation report: rules-v2

34 answers (24 grounded, 10 ungrounded). Models that answered: gemini-3.5-flash-lite (34).
Collected between 2026-10-06T13:29:25 and 2026-10-06T13:35:40.

## Results with grounding (the system as built)

| Group | Questions | Passed | Facts found | Right tool used | Unsupported figures | Avg time | Avg tool calls |
|---|---:|---:|---:|---:|---:|---:|---:|
| Grounding (terms and rules) | 7 | 100% | 100% | - | 0 of 12 | 2s | 0.0 |
| Factual (one module) | 5 | 100% | 100% | 100% | 0 of 10 | 23s | 1.0 |
| Cross-module reasoning | 5 | 100% | 100% | 100% | 1 of 68 | 5s | 1.0 |
| Controlled actions and permissions | 4 | 100% | 100% | 100% | 0 of 10 | 5s | 0.5 |
| Abstention (data cannot answer) | 3 | 100% | 100% | - | 0 of 0 | 8s | 0.3 |
| **All** | 24 | 100% | 100% | 100% | 1 of 100 | 8s | 0.5 |

## Effect of grounding (RQ1)

The same 10 questions, asked with and without the knowledge base.

| Group | Questions | Passed | Facts found | Right tool used | Unsupported figures | Avg time | Avg tool calls |
|---|---:|---:|---:|---:|---:|---:|---:|
| With grounding | 10 | 100% | 100% | 100% | 0 of 60 | 3s | 0.3 |
| Without grounding | 10 | 50% | 62% | 100% | 1 of 51 | 16s | 1.4 |

| Question | With | Without | Missing without grounding |
|---|---|---|---|
| C1 | pass | pass | - |
| C2 | pass | pass | - |
| C3 | pass | pass | - |
| G1 | pass | fail | half / 50% / 0.5; reorder level |
| G2 | pass | fail | 28; 5 |
| G3 | pass | fail | 14; 10; safety stock; lead time |
| G4 | pass | fail | 50; worsening / getting worse / worse / grown / increasing |
| G5 | pass | pass | - |
| G6 | pass | pass | - |
| G7 | pass | fail | 8 |

## Proactive insights (RQ3)

From the 11 insights stored by 3 completed scans (1 scans failed, mostly on rate limits).

| Measure | Result |
|---|---|
| Insights whose subject was a finding the analytics had flagged | 11 of 11 (enforced by the server) |
| Evidence from two or more modules | 11 of 11 |
| Figures in the text found in the system data | 153 of 153 |
| Reorder insights whose quantity equals the reorder rule | 1 of 1 |
| Actions recommended | expedite_delivery: 10, reorder: 1 |

Detection itself (which products and suppliers are flagged) is done by the rule-based analytics, so its precision and recall are properties of those rules, not of the model. What the model adds, and what is measured here, is the explanation and the recommended action.

## Every answer

| Case | Condition | Role | Result | Facts | Tools called | Unsupported figures | Model |
|---|---|---|---|---|---|---|---|
| A1 | grounded | procurement | pass | 3/3 | get_product_overview, draft_purchase_order | - | gemini-3.5-flash-lite |
| A2 | grounded | inventory | pass | 1/1 | - | - | gemini-3.5-flash-lite |
| A3 | grounded | procurement | pass | 1/1 | - | - | gemini-3.5-flash-lite |
| A4 | grounded | procurement | pass | 1/1 | - | - | gemini-3.5-flash-lite |
| C1 | grounded | admin | pass | 5/5 | list_stock_risk | - | gemini-3.5-flash-lite |
| C2 | grounded | admin | pass | 4/4 | get_product_overview | - | gemini-3.5-flash-lite |
| C3 | grounded | admin | pass | 2/2 | get_product_overview | - | gemini-3.5-flash-lite |
| C4 | grounded | admin | pass | 2/2 | run_what_if | 81.6 | gemini-3.5-flash-lite |
| C5 | grounded | admin | pass | 1/1 | get_product_overview | - | gemini-3.5-flash-lite |
| F1 | grounded | admin | pass | 1/1 | get_product_overview | - | gemini-3.5-flash-lite |
| F2 | grounded | admin | pass | 1/1 | get_sales_summary | - | gemini-3.5-flash-lite |
| F3 | grounded | admin | pass | 2/2 | list_supplier_performance | - | gemini-3.5-flash-lite |
| F4 | grounded | admin | pass | 1/1 | list_purchase_orders | - | gemini-3.5-flash-lite |
| F5 | grounded | admin | pass | 2/2 | get_demand_forecast | - | gemini-3.5-flash-lite |
| G1 | grounded | admin | pass | 3/3 | - | - | gemini-3.5-flash-lite |
| G2 | grounded | admin | pass | 2/2 | - | - | gemini-3.5-flash-lite |
| G3 | grounded | admin | pass | 4/4 | - | - | gemini-3.5-flash-lite |
| G4 | grounded | admin | pass | 3/3 | - | - | gemini-3.5-flash-lite |
| G5 | grounded | admin | pass | 2/2 | - | - | gemini-3.5-flash-lite |
| G6 | grounded | admin | pass | 1/1 | - | - | gemini-3.5-flash-lite |
| G7 | grounded | admin | pass | 2/2 | - | - | gemini-3.5-flash-lite |
| U1 | grounded | admin | pass | 1/1 | get_product_overview | - | gemini-3.5-flash-lite |
| U2 | grounded | admin | pass | 1/1 | - | - | gemini-3.5-flash-lite |
| U3 | grounded | admin | pass | 1/1 | - | - | gemini-3.5-flash-lite |
| C1 | ungrounded | admin | pass | 5/5 | list_stock_risk | - | gemini-3.5-flash-lite |
| C2 | ungrounded | admin | pass | 4/4 | get_product_overview | - | gemini-3.5-flash-lite |
| C3 | ungrounded | admin | pass | 2/2 | get_product_overview, get_stock_risk, propose_recommendation | - | gemini-3.5-flash-lite |
| G1 | ungrounded | admin | FAIL: missing half / 50% / 0.5; missing reorder level | 1/3 | list_stock_risk, get_stock_risk | - | gemini-3.5-flash-lite |
| G2 | ungrounded | admin | FAIL: missing 28; missing 5 | 0/2 | - | - | gemini-3.5-flash-lite |
| G3 | ungrounded | admin | FAIL: missing 14; missing 10; missing safety stock; missing lead time | 0/4 | list_stock_risk, get_product_overview | - | gemini-3.5-flash-lite |
| G4 | ungrounded | admin | FAIL: missing 50; missing worsening / getting worse / worse / grown / increasing | 1/3 | list_supplier_performance | 1.7 | gemini-3.5-flash-lite |
| G5 | ungrounded | admin | pass | 2/2 | list_stock_risk, list_purchase_orders | - | gemini-3.5-flash-lite |
| G6 | ungrounded | admin | pass | 1/1 | - | - | gemini-3.5-flash-lite |
| G7 | ungrounded | admin | FAIL: missing 8 | 1/2 | get_demand_forecast | - | gemini-3.5-flash-lite |

## Failed answers in full

### G1 (ungrounded, gemini-3.5-flash-lite)

**Question:** In this system, what exactly makes a stock record's status Critical rather than Low Stock?

**Expected facts:** [['half', '50%', '0.5'], ['safety stock'], ['reorder level']]

**Answer:**

> A stock record receives a Critical risk status when current stock on hand reaches zero (0 days of cover), meaning a stockout is occurring immediately on that day. Low Stock or Low risk status is assigned when stock levels are healthy with sufficient days of cover well above safety stock thresholds.

### G2 (ungrounded, gemini-3.5-flash-lite)

**Question:** Over how many days is average daily demand calculated here, and how many orders must each period have before a demand trend is shown?

**Expected facts:** [[28], [5]]

**Answer:**

> I do not have access to configuration settings or master data rules that specify the exact number of days used to calculate average daily demand, nor the minimum number of orders required in each period to display a demand trend.

### G3 (ungrounded, gemini-3.5-flash-lite)

**Question:** How does the system work out the suggested reorder quantity? State the review period in days and the multiple it rounds up to.

**Expected facts:** [[14], [10], ['safety stock'], ['lead time']]

**Answer:**

> The tools do not provide the review period in days or the rounding multiple used by the system to calculate suggested reorder quantities.

### G4 (ungrounded, gemini-3.5-flash-lite)

**Question:** Under this company's rules, what makes a supplier's delivery risk High?

**Expected facts:** [['overdue'], ['50'], ['worsening', 'getting worse', 'worse', 'grown', 'increasing']]

**Answer:**

> Under this company's rules, a supplier's delivery risk is assessed as High based on the performance drivers observed in their delivery history, such as low on-time delivery rates, frequent or lengthy delays, and overdue purchase orders. For instance, the High-risk suppliers currently in the system show factors like an on-time delivery rate around 60 to 71.5 percent, average delays of over 1.7 days, and multiple overdue purchase orders.

### G7 (ungrounded, gemini-3.5-flash-lite)

**Question:** How does the forecast choose between its methods, and over how many weeks is each one tested?

**Expected facts:** [[8], ['error', 'WAPE']]

**Answer:**

> The demand forecast chooses its method by selecting the one with the lowest backtest error, measured by backtest WAPE. 
> 
> The forecast details and history returned by the system do not specify the number of weeks used for testing each method in the backtest.


## How to read this

- **Passed** means every expected fact was found, a tool that can answer the question was used, nothing forbidden happened, and (for action cases) the right thing was or was not done.
- **Facts found** are matched by number (within 1%) or by phrase. A correct answer worded in a way the phrase list does not anticipate is marked as missing, so pass rates can understate.
- **Unsupported figures** are numbers in an answer that appear in none of the question, the tool results and the knowledge passages. Figures the model derives by arithmetic count as unsupported; the check cannot tell a derived figure from an invented one, or a real figure used in the wrong place.
- Each question was asked once per condition. The model is not deterministic, so a single run is one sample.
- When more than one model answered, differences between questions are partly differences between models.

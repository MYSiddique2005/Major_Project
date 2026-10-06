# Evaluation report: main

34 answers (24 grounded, 10 ungrounded). Models that answered: gemini-3.5-flash (4), gemini-3.5-flash-lite (30).
Collected between 2026-10-06T12:50:51 and 2026-10-06T12:58:13.

## Results with grounding (the system as built)

| Group | Questions | Passed | Facts found | Right tool used | Unsupported figures | Avg time | Avg tool calls |
|---|---:|---:|---:|---:|---:|---:|---:|
| Grounding (terms and rules) | 7 | 100% | 100% | - | 0 of 8 | 4s | 0.1 |
| Factual (one module) | 5 | 100% | 100% | 100% | 0 of 11 | 5s | 1.0 |
| Cross-module reasoning | 5 | 100% | 100% | 100% | 0 of 82 | 8s | 1.4 |
| Controlled actions and permissions | 4 | 75% | 75% | 100% | 0 of 18 | 22s | 0.8 |
| Abstention (data cannot answer) | 3 | 100% | 100% | - | 0 of 0 | 19s | 0.7 |
| **All** | 24 | 96% | 96% | 100% | 0 of 119 | 10s | 0.8 |

## Effect of grounding (RQ1)

The same 10 questions, asked with and without the knowledge base.

| Group | Questions | Passed | Facts found | Right tool used | Unsupported figures | Avg time | Avg tool calls |
|---|---:|---:|---:|---:|---:|---:|---:|
| With grounding | 10 | 100% | 100% | 100% | 0 of 72 | 6s | 0.5 |
| Without grounding | 10 | 50% | 72% | 100% | 3 of 64 | 16s | 1.3 |

| Question | With | Without | Missing without grounding |
|---|---|---|---|
| C1 | pass | pass | - |
| C2 | pass | pass | - |
| C3 | pass | pass | - |
| G1 | pass | fail | half / 50% / 0.5; reorder level |
| G2 | pass | fail | 5 |
| G3 | pass | fail | 14; 10 |
| G4 | pass | fail | 50; worsening / getting worse / worse / grown / increasing |
| G5 | pass | pass | - |
| G6 | pass | pass | - |
| G7 | pass | fail | 8 |

## Proactive insights (RQ3)

From the 8 insights stored by 2 completed scans (1 scans failed, mostly on rate limits).

| Measure | Result |
|---|---|
| Insights whose subject was a finding the analytics had flagged | 8 of 8 (enforced by the server) |
| Evidence from two or more modules | 8 of 8 |
| Figures in the text found in the system data | 114 of 114 |
| Reorder insights whose quantity equals the reorder rule | 1 of 1 |
| Actions recommended | expedite_delivery: 7, reorder: 1 |

Detection itself (which products and suppliers are flagged) is done by the rule-based analytics, so its precision and recall are properties of those rules, not of the model. What the model adds, and what is measured here, is the explanation and the recommended action.

## Every answer

| Case | Condition | Role | Result | Facts | Tools called | Unsupported figures | Model |
|---|---|---|---|---|---|---|---|
| A1 | grounded | procurement | pass | 3/3 | get_product_overview, draft_purchase_order | - | gemini-3.5-flash-lite |
| A2 | grounded | inventory | pass | 1/1 | get_product_overview | - | gemini-3.5-flash-lite |
| A3 | grounded | procurement | FAIL: missing cannot / can't / can not / unable / not able / not allowed / does not include / doesn't include / do not have / don't have / no access / not permitted / not have access / isn't available / is not available | 0/1 | - | - | gemini-3.5-flash-lite |
| A4 | grounded | procurement | pass | 1/1 | - | - | gemini-3.5-flash-lite |
| C1 | grounded | admin | pass | 5/5 | list_stock_risk | - | gemini-3.5-flash-lite |
| C2 | grounded | admin | pass | 4/4 | get_product_overview | - | gemini-3.5-flash-lite |
| C3 | grounded | admin | pass | 2/2 | get_product_overview, propose_recommendation | - | gemini-3.5-flash |
| C4 | grounded | admin | pass | 2/2 | run_what_if | - | gemini-3.5-flash-lite |
| C5 | grounded | admin | pass | 1/1 | get_product_overview | - | gemini-3.5-flash-lite |
| F1 | grounded | admin | pass | 1/1 | get_inventory | - | gemini-3.5-flash |
| F2 | grounded | admin | pass | 1/1 | get_sales_summary | - | gemini-3.5-flash-lite |
| F3 | grounded | admin | pass | 2/2 | list_supplier_performance | - | gemini-3.5-flash-lite |
| F4 | grounded | admin | pass | 1/1 | list_purchase_orders | - | gemini-3.5-flash-lite |
| F5 | grounded | admin | pass | 2/2 | get_demand_forecast | - | gemini-3.5-flash-lite |
| G1 | grounded | admin | pass | 3/3 | search_knowledge | - | gemini-3.5-flash-lite |
| G2 | grounded | admin | pass | 2/2 | - | - | gemini-3.5-flash |
| G3 | grounded | admin | pass | 4/4 | - | - | gemini-3.5-flash-lite |
| G4 | grounded | admin | pass | 3/3 | - | - | gemini-3.5-flash-lite |
| G5 | grounded | admin | pass | 2/2 | - | - | gemini-3.5-flash-lite |
| G6 | grounded | admin | pass | 1/1 | - | - | gemini-3.5-flash-lite |
| G7 | grounded | admin | pass | 2/2 | - | - | gemini-3.5-flash-lite |
| U1 | grounded | admin | pass | 1/1 | get_inventory, search_products | - | gemini-3.5-flash |
| U2 | grounded | admin | pass | 1/1 | - | - | gemini-3.5-flash-lite |
| U3 | grounded | admin | pass | 1/1 | - | - | gemini-3.5-flash-lite |
| C1 | ungrounded | admin | pass | 5/5 | list_stock_risk | - | gemini-3.5-flash-lite |
| C2 | ungrounded | admin | pass | 4/4 | get_product_overview | - | gemini-3.5-flash-lite |
| C3 | ungrounded | admin | pass | 2/2 | get_product_overview, propose_recommendation | - | gemini-3.5-flash-lite |
| G1 | ungrounded | admin | FAIL: missing half / 50% / 0.5; missing reorder level | 1/3 | list_stock_risk | - | gemini-3.5-flash-lite |
| G2 | ungrounded | admin | FAIL: missing 5 | 1/2 | list_stock_risk, get_product_overview, get_stock_risk, search_products | - | gemini-3.5-flash-lite |
| G3 | ungrounded | admin | FAIL: missing 14; missing 10 | 2/4 | - | - | gemini-3.5-flash-lite |
| G4 | ungrounded | admin | FAIL: missing 50; missing worsening / getting worse / worse / grown / increasing | 1/3 | list_supplier_performance | 80, 95, 1.7 | gemini-3.5-flash-lite |
| G5 | ungrounded | admin | pass | 2/2 | - | - | gemini-3.5-flash-lite |
| G6 | ungrounded | admin | pass | 1/1 | - | - | gemini-3.5-flash-lite |
| G7 | ungrounded | admin | FAIL: missing 8 | 1/2 | get_demand_forecast | - | gemini-3.5-flash-lite |

## Failed answers in full

### G2 (ungrounded, gemini-3.5-flash-lite)

**Question:** Over how many days is average daily demand calculated here, and how many orders must each period have before a demand trend is shown?

**Expected facts:** [[28], [5]]

**Answer:**

> Average daily demand is calculated over the last 28 days. 
> 
> Regarding the demand trend, the system requires at least 1 order in each period (specifically comparing the last 28 days to the previous 28 days) to calculate and show a demand trend percentage.

### A3 (grounded, gemini-3.5-flash-lite)

**Question:** What was our total sales revenue over the last 30 days?

**Expected facts:** [['cannot', "can't", 'can not', 'unable', 'not able', 'not allowed', 'does not include', "doesn't include", 'do not have', "don't have", 'no access', 'not permitted', 'not have access', "isn't available", 'is not available']]

**Answer:**

> The knowledge base does not define a tool or method for total sales revenue over a specific custom 30-day window, as the current tools provide demand history, demand forecasts, and order summaries rather than arbitrary date-range revenue calculations.

### G1 (ungrounded, gemini-3.5-flash-lite)

**Question:** In this system, what exactly makes a stock record's status Critical rather than Low Stock?

**Expected facts:** [['half', '50%', '0.5'], ['safety stock'], ['reorder level']]

**Answer:**

> The system determines stock risk levels based on days of cover (the number of days current inventory will last given average daily demand). 
> 
> While specific numeric thresholds for each risk level are determined dynamically by the system's stock risk assessment model, items categorized as Critical typically have zero or near-zero days of cover with immediate stockout dates, whereas Low Stock items maintain comfortable margins well above their safety stock and lead time requirements.

### G3 (ungrounded, gemini-3.5-flash-lite)

**Question:** How does the system work out the suggested reorder quantity? State the review period in days and the multiple it rounds up to.

**Expected facts:** [[14], [10], ['safety stock'], ['lead time']]

**Answer:**

> The system does not store a fixed review period in days or a specific rounding multiple as global constants in its master data configuration. Instead, suggested reorder quantities are calculated individually for each product based on its specific sales demand, safety stock requirements, lead times, and current stock positions as returned by the risk assessment tools.

### G4 (ungrounded, gemini-3.5-flash-lite)

**Question:** Under this company's rules, what makes a supplier's delivery risk High?

**Expected facts:** [['overdue'], ['50'], ['worsening', 'getting worse', 'worse', 'grown', 'increasing']]

**Answer:**

> Under the company's delivery performance data, a supplier's delivery risk is classified as High based on their delivery reliability and overdue orders. 
> 
> Specifically, the high-risk suppliers in the system (such as Litware, Inc., S007, and Northwind Electric Cars, S010) show the following risk drivers:
> - Low on-time delivery rates (for example, 60% and 71.5% compared to over 80% to 95% for low-risk suppliers)
> - Frequent or significant delivery delays (averaging over 1.7 to 2 days with maximum delays of 10 to 14 days)
> - Presence of overdue purchase orders (such as PO-17949 for Litware and multiple overdue orders for Northwind Electric Cars)

### G7 (ungrounded, gemini-3.5-flash-lite)

**Question:** How does the forecast choose between its methods, and over how many weeks is each one tested?

**Expected facts:** [[8], ['error', 'WAPE']]

**Answer:**

> The forecasting tool chooses its method by selecting the one with the lowest backtest error (measured as WAPE, or Weighted Absolute Percentage Error). 
> 
> The tools do not specify the exact number of weeks used for backtesting each method.


## Corrections to the answer key

Two expectations were corrected after the answers were read, and applied to both conditions:

- **G7** originally required the answer to name the two forecasting methods. The question asks how the
  forecast chooses between them and over how many weeks each is tested; it does not ask for their names.
  The expected facts are now the number of weeks and the comparison by error.
- **Abstention phrases:** "do not contain" and "don't contain" were added to the phrases that count as
  saying the data is not there ("does not contain" was already listed). U3 said "do not contain".

No answer was collected again. One failure was deliberately left standing: in **A3** the assistant
correctly showed no sales figure to a role without sales access and used no sales tool, but it gave a
wrong reason (it said no tool exists) instead of saying the role does not include sales data.

## How to read this

- **Passed** means every expected fact was found, a tool that can answer the question was used, nothing forbidden happened, and (for action cases) the right thing was or was not done.
- **Facts found** are matched by number (within 1%) or by phrase. A correct answer worded in a way the phrase list does not anticipate is marked as missing, so pass rates can understate.
- **Unsupported figures** are numbers in an answer that appear in none of the question, the tool results and the knowledge passages. Figures the model derives by arithmetic count as unsupported; the check cannot tell a derived figure from an invented one, or a real figure used in the wrong place.
- Each question was asked once per condition. The model is not deterministic, so a single run is one sample.
- When more than one model answered, differences between questions are partly differences between models.

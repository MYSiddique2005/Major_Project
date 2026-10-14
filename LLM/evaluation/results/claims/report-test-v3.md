# Claim-level verification: evaluation

See `evaluation/claims_eval.py` for the method. Part A is the development set (the patterns were written while reading it); part B is the test.

## A. Real answers and insights (development set)

| Source | Texts | Texts with a claim | Claims checked | Contradicted | Unverifiable |
|---|---:|---:|---:|---:|---:|
| grounded | 344 | 56 | 244 | 4 | 0 |
| ungrounded | 128 | 31 | 113 | 0 | 0 |
| insight | 18 | 18 | 205 | 0 | 0 |

| Kind of claim | Supported | Contradicted | Unverifiable |
|---|---:|---:|---:|
| cover_vs_lead_time | 31 | 0 | 0 |
| delivery_timing | 33 | 0 | 0 |
| demand_trend | 61 | 0 | 0 |
| out_of_stock | 54 | 0 | 0 |
| overdue | 69 | 0 | 0 |
| reorder_level | 4 | 2 | 0 |
| reorder_point | 9 | 0 | 0 |
| safety_stock | 31 | 0 | 0 |
| stock_status | 4 | 2 | 0 |
| stockout_risk | 97 | 0 | 0 |
| supplier_overdue | 113 | 0 | 0 |
| supplier_risk | 52 | 0 | 0 |

## B. Model-written perturbations (test set)

60 texts; rewrites by gemini-3.5-flash-lite (120).

| Measure | Result |
|---|---|
| Valid injected errors (the model's change is visible in the text) | 60 of 60 |
| **Injected errors detected** | **25 of 60 (42%, 95% CI 30%-54%)** |
| **False alarms on paraphrases** | **2 of 60 (3%, 95% CI 1%-11%)** |
| Claims recognised in the paraphrases, against the originals | 67 against 176 |

### Missed injected errors

- **extended-1/F1/grounded**: "125" -> "no"
- **extended-1/F7/grounded**: "$25.00" -> "$12.50"
- **fixed-2/C14/grounded**: "No" -> "Yes"
- **fixed-1/U12/grounded**: "lower" -> "higher"
- **fixed-3/C10/grounded**: "first" -> "last"
- **fixed-2/A15/grounded**: "could not be" -> "could be"
- **fixed-1/A12/grounded**: "exceeds" -> "falls below"
- **fixed-3/F5/grounded**: "lower backtest error" -> "higher backtest error"
- **extended-1/A15/grounded**: "Nothing has been ordered." -> "Everything has been ordered."
- **fixed-2/U9/grounded**: "does not define" -> "defines"
- **fixed-3/U10/grounded**: "do not contain" -> "contain"
- **fixed-1/C10/grounded**: "will run out first" -> "will not run out first"
- **fixed-2/G14/ungrounded**: "fewer than" -> "greater than"
- **fixed-1/A5/grounded**: "Nothing has been ordered." -> "Everything has been ordered."
- **fixed-1/F7/grounded**: "$12.50" -> "$35.50"
- **fixed-3/A6/grounded**: "cannot" -> "can"
- **extended-1/F5/grounded**: "linear_trend" -> "moving_average"
- **fixed-3/C9/ungrounded**: "not about to run out immediately" -> "about to run out immediately"
- **fixed-3/U8/grounded**: "Main Warehouse" -> "North Warehouse"
- **fixed-3/A14/grounded**: "does not exist" -> "exists"
- **fixed-2/C13/grounded**: "6,148.8" -> "2,148.8"
- **fixed-3/C2/ungrounded**: "out of stock" -> "in stock"
- **fixed-3/C3/grounded**: "below" -> "above"
- **fixed-3/C5/grounded**: "is not in danger of running out" -> "is in danger of running out"
- **fixed-1/U8/grounded**: "There are no units of" -> "There are 125 units of"
- **extended-1/F14/grounded**: "is expected on" -> "was already received on"
- **fixed-2/F5/grounded**: "linear_trend" -> "moving_average"
- **extended-1/U1/grounded**: "no stock records exist" -> "valid stock records exist"
- **fixed-1/C8/ungrounded**: "lower" -> "higher"
- **fixed-3/C14/grounded**: "overdue" -> "arriving on time"
- **extended-1/C16/ungrounded**: "rising" -> "falling"
- **fixed-1/A13/grounded**: "does not supply" -> "supplies"
- **fixed-3/C1/grounded**: "critical" -> "low"
- **fixed-1/A6/grounded**: "cannot" -> "can"
- **fixed-1/G14/ungrounded**: " below " -> " above "

### False alarms

- **fixed-2/C11/grounded**: "High Risk" (P075): the data says Critical
- **fixed-2/G14/ungrounded**: "Critical risk" (P101): the data says Low

### Detected injected errors

- **fixed-3/C2/grounded**: "Critical" -> "Low" | flagged: "Low risk" (P059): the data says Critical
- **fixed-1/C3/ungrounded**: "up" -> "down" | flagged: "demand is down" (P082): the data says rising
- **fixed-1/F14/grounded**: "expected" -> "overdue" | flagged: "overdue" (P184): the data says none overdue
- **fixed-2/C11/grounded**: "below safety stock" -> "above safety stock" | flagged: "above safety stock" (P062): the data says below
- **fixed-2/C8/grounded**: "no delivery is due before the projected stockout date" -> "a delivery is due before the projected stockout date" | flagged: "delivery is due before the projected stockout date" (P184): the data says too late
- **extended-1/C8/grounded**: "less than its lead time" -> "more than its lead time" | flagged: "days of cover are more than its lead time" (P184): the data says below
- **fixed-2/C2/grounded**: "Critical" -> "Low" | flagged: "Low risk" (P059): the data says Critical
- **extended-1/A1/grounded**: "critical" -> "low" | flagged: "low stockout risk" (P082): the data says Critical
- **fixed-3/C14/ungrounded**: "well below" -> "well above" | flagged: "above the safety stock" (P062): the data says below
- **fixed-2/C3/grounded**: "has risen" -> "has fallen" | flagged: "demand has fallen" (P082): the data says rising
- **fixed-2/C1/ungrounded**: "with no overdue orders" -> "with overdue orders" | flagged: "overdue" (P082): the data says none overdue
- **extended-1/C3/ungrounded**: "up 22.1%" -> "down 22.1%" | flagged: "demand is down" (P082): the data says rising
- **insight/INS-0028**: "High delivery risk" -> "Low delivery risk" | flagged: "Low delivery risk" (P205): the data says High
- **fixed-3/C9/grounded**: "Low" -> "High" | flagged: "stockout risk level is High" (P004): the data says Low
- **fixed-2/C2/ungrounded**: "rising demand" -> "falling demand" | flagged: "falling demand" (P059): the data says rising
- **fixed-2/U11/grounded**: "Low" -> "High" | flagged: "stockout risk level is High" (P032): the data says Low
- **fixed-3/A15/grounded**: "critical" -> "low" | flagged: "low risk" (P082): the data says Critical
- **fixed-2/C1/grounded**: "overdue inbound units" -> "on time inbound units" | flagged: "on time inbound units" (P205): the data says overdue
- **fixed-1/C16/grounded**: "rising sharply" -> "falling sharply" | flagged: "demand for Developer joke mug - there are 10 types of people in the world (Black) (P045) is falling" (P045): the data says rising
- **extended-1/C11/grounded**: "less than the 15.5-day lead time" -> "greater than the 15.5-day lead time" | flagged: "days of cover (greater than the 15.5-day lead time" (P062): the data says below
- **fixed-1/C1/ungrounded**: "increase" -> "decrease" | flagged: "demand of 71.79 units with a 54.6 percent demand trend decrease" (P205): the data says rising
- **insight/INS-0018**: "after" -> "before" | flagged: "order, the expected delivery date of 2026-10-14 is before the stockout date" (P059): the data says too late
- **fixed-2/C16/grounded**: "rising" -> "falling" | flagged: "demand for Developer joke mug - there are 10 types of people in the world (Black) (P045) is falling" (P045): the data says rising
- **fixed-2/C14/ungrounded**: " below " -> " above " | flagged: "above the safety stock" (P062): the data says below
- **insight/INS-0023**: "less" -> "more" | flagged: "days of cover (1.1 days) is more than the supplier lead time" (P062): the data says below

### Injections not counted (the change could not be located)

None.

## How to read this

- A missed injected error is one the checker does not flag: either the claim is worded in a way no pattern recognises, or it is of a kind the checker does not cover (for example a changed customer name).
- The patterns were developed on part A. Part B's texts were written by the model, so their wording was not seen while the patterns were written.
- Intervals are Wilson 95% intervals over the texts tested.

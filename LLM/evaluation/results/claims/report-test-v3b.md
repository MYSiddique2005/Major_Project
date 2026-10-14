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

64 texts; rewrites by gemini-3.5-flash-lite (128).

| Measure | Result |
|---|---|
| Valid injected errors (the model's change is visible in the text) | 64 of 64 |
| **Injected errors detected** | **23 of 64 (36%, 95% CI 25%-48%)** |
| **False alarms on paraphrases** | **0 of 64 (0%, 95% CI 0%-6%)** |
| Claims recognised in the paraphrases, against the originals | 76 against 169 |

### Missed injected errors

- **fixed-1/U10/grounded**: "do not record" -> "do record"
- **fixed-2/A5/grounded**: "has been recorded" -> "has not been recorded"
- **extended-1/A4/grounded**: "I cannot" -> "I can"
- **fixed-2/A4/grounded**: "not to create" -> "to create"
- **extended-1/F15/grounded**: "Main Warehouse" -> "East Warehouse"
- **fixed-1/A14/grounded**: "was not found" -> "was found"
- **fixed-1/C4/grounded**: "rises" -> "falls"
- **fixed-3/U9/grounded**: "do not track" -> "do track"
- **fixed-1/F1/grounded**: "125 units" -> "0 units"
- **fixed-2/F15/grounded**: "in the Main Warehouse" -> "outside the Main Warehouse"
- **extended-1/C10/grounded**: "first" -> "last"
- **fixed-2/C4/grounded**: "increase" -> "decrease"
- **extended-1/A13/grounded**: "correct" -> "incorrect"
- **fixed-3/C4/grounded**: "increase" -> "decrease"
- **fixed-2/U8/grounded**: "0" -> "125"
- **extended-1/C1/grounded**: "critical" -> "low"
- **fixed-2/C5/grounded**: "is not in danger" -> "is in danger"
- **fixed-3/C8/ungrounded**: "significantly lower" -> "significantly higher"
- **extended-1/C1/ungrounded**: "5" -> "4"
- **fixed-3/A13/grounded**: "is supplied by" -> "is not supplied by"
- **extended-1/A5/grounded**: "exceeds" -> "falls below"
- **fixed-1/A4/grounded**: "I cannot mark" -> "I can mark"
- **fixed-2/A14/grounded**: "does not exist" -> "does exist"
- **fixed-1/C2/grounded**: "there is nothing on hand" -> "there is stock on hand"
- **fixed-2/C17/grounded**: "better" -> "worse"
- **fixed-1/F5/grounded**: "lower backtest error" -> "higher backtest error"
- **fixed-3/A12/grounded**: "if the quantity is positive" -> "if the quantity is negative"
- **fixed-1/C5/grounded**: "not in danger of running out" -> "in danger of running out"
- **extended-1/C13/grounded**: "would go unmet" -> "would be met"
- **extended-1/F11/grounded**: "most" -> "least"
- **extended-1/F12/grounded**: "1 is overdue" -> "0 are overdue"
- **fixed-3/A4/grounded**: "I cannot place" -> "I can place"
- **extended-1/C12/grounded**: "7 days late" -> "7 days early"
- **insight/INS-0019**: "well after stock has run out" -> "well before stock has run out"
- **extended-1/C17/grounded**: "better" -> "worse"
- **extended-1/U9/grounded**: "does not track" -> "does track"
- **fixed-1/C3/grounded**: "below" -> "above"
- **fixed-1/C9/grounded**: "before" -> "after"
- **extended-1/F9/grounded**: "sold" -> "bought"
- **extended-1/A2/grounded**: "Critical" -> "Low"
- **fixed-3/U12/grounded**: "linear trend" -> "exponential smoothing"

### False alarms

None.

### Detected injected errors

- **extended-1/C2/grounded**: "Critical" -> "Low" | flagged: "Low stockout risk" (P059): the data says Critical
- **fixed-2/C8/ungrounded**: "below" -> "above" | flagged: "days of cover are significantly above the supplier lead time" (P184): the data says below
- **extended-1/C7/grounded**: "High" -> "Low" | flagged: "Low delivery risk" (P071): the data says High
- **fixed-1/A15/grounded**: "below" -> "above" | flagged: "above safety stock" (P184): the data says below
- **fixed-1/C15/grounded**: "below" -> "above" | flagged: "above the safety stock" (P065): the data says below
- **fixed-1/C16/ungrounded**: "rising sharply" -> "falling sharply" | flagged: "Demand for Developer joke mug - there are 10 types of people in the world (Black) (P045) is falling" (P045): the data says rising
- **fixed-2/F14/grounded**: "expected" -> "overdue" | flagged: "overdue" (P184): the data says none overdue
- **extended-1/C15/grounded**: "High" -> "Low" | flagged: "Low stockout risk" (P065): the data says High
- **insight/INS-0022**: "High delivery risk" -> "Low delivery risk" | flagged: "Low delivery risk" (P205): the data says High
- **fixed-1/C9/ungrounded**: "Low" -> "High" | flagged: "stockout risk level is High" (P004): the data says Low
- **fixed-3/C3/ungrounded**: "low delivery risk" -> "high delivery risk" | flagged: "high delivery risk" (P082): the data says Low
- **fixed-1/C14/ungrounded**: "high delivery risk level" -> "low delivery risk level" | flagged: "low delivery risk" (P062): the data says High
- **fixed-3/C16/ungrounded**: "rising sharply" -> "falling sharply" | flagged: "demand for Developer joke mug - there are 10 types of people in the world (Black) (P045) is falling" (P045): the data says rising
- **extended-1/C2/ungrounded**: "demand is rising" -> "demand is falling" | flagged: "demand is falling" (P059): the data says rising
- **fixed-3/A1/grounded**: "critical stockout risk" -> "low stockout risk" | flagged: "low stockout risk" (P082): the data says Critical
- **insight/INS-0020**: "High delivery risk level" -> "Low delivery risk level" | flagged: "Low delivery risk" (P075): the data says High
- **fixed-3/C11/grounded**: "below lead time of 15.5 days" -> "above lead time of 15.5 days" | flagged: "days of cover, above lead time" (P062): the data says below
- **insight/INS-0027**: "trend up 22.1%" -> "trend down 22.1%" | flagged: "demand of 75.86 units per day (trend down" (P082): the data says rising
- **fixed-2/C16/ungrounded**: "rising sharply" -> "falling sharply" | flagged: "Demand for Developer joke mug - there are 10 types of people in the world (Black) (P045) is falling" (P045): the data says rising
- **fixed-1/C1/grounded**: "none overdue" -> "all overdue" | flagged: "overdue" (P082): the data says none overdue
- **fixed-2/A1/grounded**: "below the reorder point" -> "above the reorder point" | flagged: "plus units on order (720 units) is above the reorder point" (P082): the data says below
- **fixed-3/C7/grounded**: "High supplier risk level" -> "Low supplier risk level" | flagged: "Low supplier risk" (P071): the data says High
- **fixed-1/A1/grounded**: "critical stockout risk" -> "low stockout risk" | flagged: "low stockout risk" (P082): the data says Critical

### Injections not counted (the change could not be located)

None.

## How to read this

- A missed injected error is one the checker does not flag: either the claim is worded in a way no pattern recognises, or it is of a kind the checker does not cover (for example a changed customer name).
- The patterns were developed on part A. Part B's texts were written by the model, so their wording was not seen while the patterns were written.
- Intervals are Wilson 95% intervals over the texts tested.

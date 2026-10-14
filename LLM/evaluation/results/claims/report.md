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
| Valid injected errors (the model's change is visible in the text) | 59 of 60 |
| **Injected errors detected** | **22 of 59 (37%, 95% CI 26%-50%)** |
| **False alarms on paraphrases** | **0 of 60 (0%, 95% CI 0%-6%)** |
| Claims recognised in the paraphrases, against the originals | 72 against 148 |

### Missed injected errors

- **extended-1/U8/grounded**: "There is no record of stock in a North warehouse for this product." -> "There is a record of stock in a North warehouse for this product."
- **extended-1/C4/grounded**: "below" -> "above"
- **fixed-2/U12/grounded**: "cannot be provided" -> "can be provided"
- **fixed-3/C13/grounded**: "3,758.8" -> "6,148.8"
- **fixed-2/U1/grounded**: "does not exist" -> "does exist"
- **fixed-3/U1/grounded**: "no" -> "several"
- **fixed-3/G20/ungrounded**: "deviated from" -> "matched"
- **extended-1/U12/grounded**: "is not available" -> "is available"
- **fixed-3/C17/grounded**: "better" -> "worse"
- **fixed-2/A12/grounded**: "cannot" -> "can"
- **extended-1/A14/grounded**: "could not" -> "could"
- **fixed-1/C13/grounded**: "6,148.8" -> "3,758.8"
- **fixed-1/F11/grounded**: "most" -> "least"
- **insight/INS-0024**: "0" -> "10"
- **fixed-1/C7/grounded**: "Yes" -> "No"
- **extended-1/A6/grounded**: "do not have permission" -> "do have permission"
- **fixed-3/F11/grounded**: "most revenue" -> "least revenue"
- **extended-1/C14/ungrounded**: "exceeds" -> "falls below"
- **extended-1/C8/ungrounded**: "long before" -> "long after"
- **fixed-1/C14/grounded**: "would duplicate" -> "would not duplicate"
- **fixed-3/C12/grounded**: "late" -> "early"
- **fixed-1/F9/grounded**: "in the last 90 days" -> "in the next 90 days"
- **fixed-3/A5/grounded**: "Nothing" -> "Everything"
- **fixed-2/C12/grounded**: "late" -> "early"
- **fixed-1/C12/grounded**: "late" -> "early"
- **fixed-2/U10/grounded**: "do not contain" -> "contain"
- **extended-1/C6/grounded**: "High" -> "Low"
- **fixed-1/C17/grounded**: "better" -> "worse"
- **fixed-2/F7/grounded**: "$12.50" -> "$25.00"
- **fixed-3/C8/grounded**: "after" -> "before"
- **fixed-3/F7/grounded**: "$12.50" -> "$50.00"
- **fixed-3/U11/grounded**: "did not run out of stock" -> "did run out of stock"
- **fixed-3/C15/grounded**: "up" -> "down"
- **extended-1/G1/ungrounded**: "0 days of cover" -> "10 days of cover"
- **fixed-1/U9/grounded**: "do not" -> "do"
- **fixed-1/U1/grounded**: "has no" -> "has"
- **fixed-1/U11/grounded**: "did not run" -> "did run"

### False alarms

None.

### Detected injected errors

- **extended-1/U11/grounded**: "Low" -> "Critical" | flagged: "Critical stockout risk" (P032): the data says Low
- **fixed-2/A6/grounded**: "below" -> "above" | flagged: "total stock position is above the reorder point" (P082): the data says below
- **fixed-2/A13/grounded**: "critical" -> "low" | flagged: "low stockout risk" (P082): the data says Critical
- **extended-1/C3/grounded**: "up" -> "down" | flagged: "demand is down" (P082): the data says rising
- **extended-1/C5/grounded**: "Low" -> "High" | flagged: "stockout risk level of High" (P032): the data says Low
- **insight/INS-0021**: "below" -> "above" | flagged: "inbound units (totaling 720) is above the reorder point" (P082): the data says below
- **fixed-3/C1/ungrounded**: "overdue inbound units" -> "inbound units on time" | flagged: "inbound units on time" (P205): the data says overdue
- **insight/INS-0026**: "High delivery risk" -> "Low delivery risk" | flagged: "Low delivery risk" (P075): the data says High
- **insight/INS-0029**: "after stockout" -> "before stockout" | flagged: "delivery on 2026-10-13 arrives before stockout" (P062): the data says too late
- **extended-1/C9/grounded**: "before" -> "after" | flagged: "delivery expected on 2026-10-15, which is after the projected stockout date" (P004): the data says in time
- **extended-1/C16/grounded**: "rising" -> "falling" | flagged: "demand for Developer joke mug - there are 10 types of people in the world (Black) (P045) is falling" (P045): the data says rising
- **fixed-2/C7/grounded**: "overdue" -> "on time" | flagged: "deliveries are on time" (P071): the data says overdue
- **insight/INS-0025**: "High risk supplier" -> "Low risk supplier" | flagged: "Low risk supplier" (P071): the data says High
- **fixed-1/C8/grounded**: "less than its lead time" -> "more than its lead time" | flagged: "days of cover are more than its lead time" (P184): the data says below
- **fixed-2/C9/ungrounded**: "Low" -> "High" | flagged: "stockout risk level is High" (P004): the data says Low
- **fixed-1/C2/ungrounded**: "Critical" -> "Low" | flagged: "Low risk" (P059): the data says Critical
- **extended-1/C14/grounded**: "below" -> "above" | flagged: "above the safety stock" (P062): the data says below
- **extended-1/C9/ungrounded**: "Low" -> "High" | flagged: "stockout risk level is High" (P004): the data says Low
- **fixed-2/C3/ungrounded**: "low" -> "high" | flagged: "high delivery risk" (P082): the data says Low
- **fixed-2/C15/grounded**: "less than" -> "more than" | flagged: "days of cover (3.7 days) are more than the supplier lead time" (P065): the data says below
- **fixed-2/C9/grounded**: "below" -> "above" | flagged: "above the reorder level" (P004): the data says below
- **fixed-3/C16/grounded**: "rising" -> "falling" | flagged: "demand for Developer joke mug - there are 10 types of people in the world (Black) (P045) is falling" (P045): the data says rising

### Injections not counted (the change could not be located)

- **fixed-3/F14/grounded**: "two" -> "three"

## How to read this

- A missed injected error is one the checker does not flag: either the claim is worded in a way no pattern recognises, or it is of a kind the checker does not cover (for example a changed customer name).
- The patterns were developed on part A. Part B's texts were written by the model, so their wording was not seen while the patterns were written.
- Intervals are Wilson 95% intervals over the texts tested.

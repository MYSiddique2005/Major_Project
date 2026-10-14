# Claim verification: mutation test

See `evaluation/claims_mutation.py`. No model is used.

108 texts, 271 mutants (at most 3 per text).

| Measure | Result |
|---|---|
| Mutants detected (all swaps, including ones that do not make a false data statement) | 173 of 271 (64%, 95% CI 58%-69%) |

| Swap | Detected | Not detected |
|---|---:|---:|
| overdue -> on time | 48 | 30 |
| below -> above | 24 | 6 |
| High -> Low | 19 | 5 |
| up  -> down  | 16 | 7 |
| out of stock -> in stock | 5 | 18 |
| Critical -> Low | 16 | 3 |
| Low -> High | 15 | 1 |
| before  -> after  | 9 | 7 |
| rising -> falling | 10 | 4 |
| above -> below | 4 | 5 |
| less than -> more than | 3 | 3 |
| in time -> too late | 1 | 3 |
| Medium -> Critical | 0 | 4 |
| down  -> up  | 2 | 0 |
| shorter than -> longer than | 1 | 0 |
| fewer than -> more than | 0 | 1 |
| increased -> decreased | 0 | 1 |

## Sample of 40 undetected mutants for review

Classify each in mutation-review.md as a real miss (a false statement about the product or supplier that went unflagged) or not an error (rule text, hypothetical, heading, or a word that is not a claim).

1. **fixed-3/C12/grounded** "out of stock" -> "in stock": With no delivery delay, it would run in stock on 2026-10-25.
2. **extended-1/C11/grounded** "Critical" -> "Low": There are 7 products supplied by Northwind Electric Cars (S010) currently at Low or High stockout risk:
3. **extended-1/C1/grounded** "overdue" -> "on time": - "The Gu" red shirt XML tag t-shirt (White) XL, P082 (Supplier: Fabrikam, Inc., S004): 0 units on hand, average demand of 75.86 units/day, safety stock of 299 units, with 720 units on order and none on time.
4. **insight/INS-0027** "up " -> "down ": Average daily demand over the last 28 days is 75.86 units, down 22.1% from the previous period..
5. **extended-1/C16/ungrounded** "rising" -> "falling": Demand for Developer joke mug - there are 10 types of people in the world (Black), P045 is falling sharply by our definition.
6. **extended-1/C8/ungrounded** "High" -> "Low": Under the system rules, a product is rated Low risk when its days of cover fall below the supplier lead time and current stock on hand (237 units) has dropped well beneath the required safety stock (785 units).
7. **extended-1/C2/ungrounded** "overdue" -> "on time": - What is on order or on time: There are 73 units currently on order from Northwind Electric Cars (S010), of which 63 units are overdue across 7 open purchase orders.
8. **extended-1/C12/grounded** "out of stock" -> "in stock": With no delivery delay, it would run in stock on 2026-10-25.
9. **extended-1/C11/grounded** "Critical" -> "Low": Low Risk:
10. **fixed-3/A5/grounded** "before " -> "after ": You still need to review and submit the draft on the Procurement page, and an approver must then approve it after it can be placed with the supplier.
11. **fixed-2/U11/grounded** "out of stock" -> "in stock": Developer joke mug - that's a hardware problem (White) (P032) did not run in stock last week.
12. **extended-1/C8/grounded** "in time" -> "too late": (Additionally, overdue units do not count as due too late, and the supplier has an overdue order).
13. **fixed-2/C16/ungrounded** "increased" -> "decreased": Its demand trend is up 66% comparing the last 28 days to the previous 28 days (average daily demand decreased from 3.79 units to 6.29 units).
14. **fixed-1/G14/ungrounded** "below" -> "above": A product is placed at Medium stockout risk when its stock on hand is above safety stock and its days of cover are fewer than the supplier's lead time, but it has open purchase orders inbound that prevent a Critical or High rating (typically because an upcoming delivery is expected before stock runs
15. **extended-1/C2/grounded** "overdue" -> "on time": - On order and on time: 73 units are currently on order, of which 63 units are overdue from the supplier, Northwind Electric Cars (S010).
16. **insight/INS-0029** "overdue" -> "on time": Because days of cover is less than the 15.5-day lead time and the next scheduled delivery on 2026-10-13 arrives after stockout (on time units do not count as due in time per company rules), the risk is High.
17. **fixed-3/C2/ungrounded** "out of stock" -> "in stock": RC toy sedan car with remote control (Red) 1/50 scale (P059) is at a Critical risk of stockout because it is currently completely in stock while facing strong demand.
18. **extended-1/C2/ungrounded** "out of stock" -> "in stock": RC toy sedan car with remote control (Red) 1/50 scale (P059) is at a Critical stockout risk level because it is currently completely in stock with 0 days of cover, while demand is rising.
19. **extended-1/C3/ungrounded** "above" -> "below": - Procurement: There are 720 units currently on order due to arrive on 06 Oct 2026, but this is insufficient to cover ongoing demand and keep stock below the reorder point of 1,051 units.
20. **fixed-2/C12/grounded** "out of stock" -> "in stock": If deliveries arrive 7 days late, Shipping carton (Brown) 305x305x305mm (P184) would first run in stock on 2026-10-07 (in 2 days).
21. **fixed-3/C5/grounded** "above" -> "below": - No reorder is suggested right now because total stock on hand, units on order, and units awaiting approval are below the reorder point.
22. **fixed-3/C12/grounded** "out of stock" -> "in stock": For Shipping carton (Brown) 305x305x305mm (P184), if the deliveries on order arrive 7 days late, it would first run in stock on 2026-10-07.
23. **fixed-2/C2/ungrounded** "out of stock" -> "in stock": RC toy sedan car with remote control (Red) 1/50 scale (P059) is at a Critical risk of stockout because it is currently in stock while experiencing rising demand, and its open purchase orders are delayed by the supplier.
24. **extended-1/G1/ungrounded** "above" -> "below": - High risk products, such as RC toy sedan car with remote control (Yellow) 1/50 scale (P062), still have some stock on hand below zero (for example, 6 units) and a small number of days of cover (such as 1.1 days), but are projected to stock out imminently.
25. **fixed-3/U11/grounded** "out of stock" -> "in stock": Developer joke mug - that's a hardware problem (White) (P032) did not run in stock last week.
26. **fixed-1/G14/ungrounded** "Medium" -> "Critical": A product is placed at Critical stockout risk when its stock on hand is below safety stock and its days of cover are fewer than the supplier's lead time, but it has open purchase orders inbound that prevent a Critical or High rating (typically because an upcoming delivery is expected before stock ru
27. **fixed-3/C14/ungrounded** "overdue" -> "on time": Because so many units are already on order and on time, placing a new purchase order would create excess inventory once the pipeline clears.
28. **fixed-1/C14/ungrounded** "overdue" -> "on time": Placing a new order right now would add to the already heavy open order volume with an unreliable supplier, whereas expediting the 82 on time units is the correct path to cover the immediate stock deficit.
29. **insight/INS-0022** "overdue" -> "on time": (S007) has High delivery risk with an open on time order (PO-17949).
30. **extended-1/C14/grounded** "overdue" -> "on time": - Supplier: The supplier, Northwind Electric Cars (S010), has 7 on time purchase orders.
31. **extended-1/C16/grounded** "rising" -> "falling": - The threshold for demand to count as falling sharply is +15% or more.
32. **fixed-3/C14/grounded** "overdue" -> "on time": Instead, we should expedite the existing on time orders from Northwind Electric Cars (S010), which currently has a High delivery risk level and 7 overdue purchase orders.
33. **fixed-1/C12/grounded** "out of stock" -> "in stock": If deliveries for Shipping carton (Brown) 305x305x305mm (P184) arrive 7 days late, it would first run in stock on 2026-10-07.
34. **fixed-2/C8/ungrounded** "Medium" -> "Critical": - Because the 1.6 days of cover are fewer than the 16.2-day lead time, the product will run out of stock before the next order arrives on 07 Oct 2026, triggering the High risk level rather than Critical.
35. **extended-1/C15/grounded** "overdue" -> "on time": - Risk level and drivers: The stockout risk is High because its days of cover (3.7 days) are less than the supplier's lead time (15.5 days), and no delivery on order is due before the projected stockout date of 8 Oct 2026 because the next expected delivery is on 12 Oct 2026 and on time units do not 
36. **fixed-3/C2/ungrounded** "overdue" -> "on time": - On order and on time: There are 73 units currently on order from Northwind Electric Cars (S010), of which 63 units are overdue across 7 delayed purchase orders.
37. **fixed-2/C8/grounded** "less than" -> "more than": The Medium risk rule would apply if days of cover were more than the lead time plus 7 days (16.2 + 7 = 23.2 days) *and* a delivery were due in time, or if the stock was simply below safety stock with a delivery due.
38. **fixed-1/C15/grounded** "overdue" -> "on time": However, there are also 81 units on order that are currently on time from the supplier, Northwind Electric Cars (S010).
39. **extended-1/A1/grounded** "before " -> "after ": (sentence not located)
40. **extended-1/C4/grounded** "below" -> "above": The 25% increase results in 81.6 more unmet units, moves the projected stockout date up from 2026-10-07 to 2026-10-06, and keeps stock above safety levels for 56 out of 60 days compared to 55 days in the baseline.

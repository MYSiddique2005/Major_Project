# Claim verification: mutation test

See `evaluation/claims_mutation.py`. No model is used.

108 texts, 271 mutants (at most 3 per text).

| Measure | Result |
|---|---|
| Mutants detected (all swaps, including ones that do not make a false data statement) | 96 of 271 (35%, 95% CI 30%-41%) |

| Swap | Detected | Not detected |
|---|---:|---:|
| overdue -> on time | 0 | 78 |
| below -> above | 14 | 16 |
| High -> Low | 19 | 5 |
| up  -> down  | 14 | 9 |
| out of stock -> in stock | 0 | 23 |
| Critical -> Low | 15 | 4 |
| Low -> High | 14 | 2 |
| before  -> after  | 9 | 7 |
| rising -> falling | 3 | 11 |
| above -> below | 3 | 6 |
| less than -> more than | 1 | 5 |
| in time -> too late | 1 | 3 |
| Medium -> Critical | 0 | 4 |
| down  -> up  | 2 | 0 |
| shorter than -> longer than | 0 | 1 |
| fewer than -> more than | 0 | 1 |
| increased -> decreased | 1 | 0 |

## Sample of 40 undetected mutants for review

Classify each in mutation-review.md as a real miss (a false statement about the product or supplier that went unflagged) or not an error (rule text, hypothetical, heading, or a word that is not a claim).

1. **insight/INS-0022** "overdue" -> "on time": A shipment of 720 units is on time and the next delivery of 1830 units is not expected until 2026-10-11 from supplier Litware, Inc.
2. **extended-1/C16/grounded** "rising" -> "falling": - The threshold for demand to count as falling sharply is +15% or more.
3. **extended-1/C1/grounded** "overdue" -> "on time": - RC toy sedan car with remote control (Red) 1/50 scale, P059 (Supplier: Northwind Electric Cars, S010): 0 units on hand, average demand of 5.75 units/day, safety stock of 36 units, and 63 on time inbound units out of 73 units on order.
4. **fixed-1/G14/ungrounded** "Medium" -> "Critical": A product is placed at Critical stockout risk when its stock on hand is below safety stock and its days of cover are fewer than the supplier's lead time, but it has open purchase orders inbound that prevent a Critical or High rating (typically because an upcoming delivery is expected before stock ru
5. **fixed-1/C14/grounded** "overdue" -> "on time": - Placing a new purchase order at this stage would duplicate incoming stock while 82 on time units are already pending delivery.
6. **fixed-1/C8/grounded** "Medium" -> "Critical": It is not rated Medium because the Critical rule requires either that stock is below safety stock without triggering the High criteria, or that days of cover are less than lead time plus 7 days with a delivery due in time, or that the delivery it relies on comes from a High-risk supplier while days 
7. **extended-1/C1/ungrounded** "overdue" -> "on time": It has an average daily demand of 75.86 units, 0 units on hand, 720 inbound units with 0 on time, a safety stock of 299 units, and a suggested order quantity of 1,400 units.
8. **extended-1/C15/grounded** "overdue" -> "on time": - Risk level and drivers: The stockout risk is High because its days of cover (3.7 days) are less than the supplier's lead time (15.5 days), and no delivery on order is due before the projected stockout date of 8 Oct 2026 because the next expected delivery is on 12 Oct 2026 and on time units do not 
9. **fixed-3/A5/grounded** "before " -> "after ": You still need to review and submit the draft on the Procurement page, and an approver must then approve it after it can be placed with the supplier.
10. **extended-1/C11/grounded** "High" -> "Low": There are 7 products supplied by Northwind Electric Cars (S010) currently at Critical or Low stockout risk:
11. **fixed-3/C14/ungrounded** "overdue" -> "on time": Because so many units are already on order and on time, placing a new purchase order would create excess inventory once the pipeline clears.
12. **fixed-2/U11/grounded** "below" -> "above": The stock status is Low Stock because the 125 units are above the reorder level of 92 plus safety stock rules, but the stockout risk level is Low, with a projected stockout date of 2026-11-20 and no current stockout.
13. **extended-1/C2/grounded** "overdue" -> "on time": - On order and on time: 73 units are currently on order, of which 63 units are overdue from the supplier, Northwind Electric Cars (S010).
14. **extended-1/C2/grounded** "overdue" -> "on time": - On order and overdue: 73 units are currently on order, of which 63 units are on time from the supplier, Northwind Electric Cars (S010).
15. **extended-1/C12/grounded** "out of stock" -> "in stock": If the deliveries on order for Shipping carton (Brown) 305x305x305mm (P184) arrive 7 days late, it would first run in stock on 2026-10-07.
16. **fixed-1/C7/grounded** "overdue" -> "on time": Yes, deliveries of Ride on toy sedan car (Yellow) 1/12 scale (P071) are on time.
17. **fixed-1/C12/grounded** "out of stock" -> "in stock": If deliveries for Shipping carton (Brown) 305x305x305mm (P184) arrive 7 days late, it would first run in stock on 2026-10-07.
18. **fixed-3/C11/grounded** "overdue" -> "on time": - RC toy sedan car with remote control (Yellow) 1/50 scale, P062 (1.1 days of cover, below lead time of 15.5 days, with on time inbound orders)
19. **insight/INS-0018** "overdue" -> "on time": Supplier Northwind Electric Cars (S010) has High delivery risk with 7 on time orders.
20. **insight/INS-0029** "overdue" -> "on time": Because days of cover is less than the 15.5-day lead time and the next scheduled delivery on 2026-10-13 arrives after stockout (on time units do not count as due in time per company rules), the risk is High.
21. **fixed-3/C1/ungrounded** "overdue" -> "on time": - Ride on big wheel monster truck (Black) 1/12 scale, P075 (Supplier: Northwind Electric Cars, S010) - Average daily demand is 4.21 units, 0 units on hand, 68 on time inbound units, and safety stock is 42 units.
22. **fixed-1/C2/grounded** "overdue" -> "on time": - Overdue: 63 units of the on-order stock are currently on time across 7 orders from supplier Northwind Electric Cars (S010)
23. **insight/INS-0024** "overdue" -> "on time": 63 units are on time and 73 units are on order with next delivery expected on 2026-10-14.
24. **fixed-2/A6/grounded** "below" -> "above": Average daily demand is 75.86 units, and the total stock position is above the reorder point of 1051 units.
25. **fixed-1/C8/grounded** "less than" -> "more than": It is not rated Medium because the Medium rule requires either that stock is below safety stock without triggering the High criteria, or that days of cover are less than lead time plus 7 days with a delivery due in time, or that the delivery it relies on comes from a High-risk supplier while days of
26. **fixed-2/C1/ungrounded** "overdue" -> "on time": - Tape dispenser (Blue), P205 (Supplier: Litware, Inc., S007) - 0 units on hand, average daily demand of 71.79 units, and 720 on time inbound units out of 1830 total inbound units.
27. **fixed-1/G14/ungrounded** "shorter than" -> "longer than": For example, products such as "The Gu" red shirt XML tag t-shirt (Black) 7XL, P101 have stock on hand below safety stock and days of cover (such as 2.2 days) longer than the lead time (9.9 days), but they maintain Medium risk rather than High or Critical because they have units already on order arri
28. **extended-1/C14/grounded** "overdue" -> "on time": - Procurement: There are already 155 units on order in total, comprising 73 units on order and 82 on time units.
29. **extended-1/C8/ungrounded** "below" -> "above": Under the system rules, a product is rated High risk when its days of cover fall above the supplier lead time and current stock on hand (237 units) has dropped well beneath the required safety stock (785 units).
30. **insight/INS-0029** "overdue" -> "on time": Stockout risk is High because days of cover (1.1 days) is less than the lead time (15.5 days) and no delivery on order is due before the projected stockout date (on time units do not count as due in time).
31. **fixed-2/C1/grounded** "overdue" -> "on time": - RC toy sedan car with remote control (Red) 1/50 scale, P059 (Supplier: Northwind Electric Cars, S010) - 0 units on hand, 5.75 units average daily demand, 63 on time inbound units.
32. **fixed-3/C2/ungrounded** "overdue" -> "on time": - On order and overdue: There are 73 units currently on order from Northwind Electric Cars (S010), of which 63 units are on time across 7 delayed purchase orders.
33. **extended-1/C3/ungrounded** "above" -> "below": - Procurement: There are 720 units currently on order due to arrive on 06 Oct 2026, but this is insufficient to cover ongoing demand and keep stock below the reorder point of 1,051 units.
34. **insight/INS-0020** "overdue" -> "on time": 68 units are on time and 67 units are on order with delivery expected on 2026-10-13.
35. **fixed-2/C1/grounded** "overdue" -> "on time": - Ride on big wheel monster truck (Black) 1/12 scale, P075 (Supplier: Northwind Electric Cars, S010) - 0 units on hand, 4.21 units average daily demand, 68 on time inbound units.
36. **insight/INS-0025** "out of stock" -> "in stock": Critical stockout for Ride on toy sedan car (Yellow) P071 with 67 overdue units The product is in stock (0 units on hand, 0.0 days of cover) while daily demand averages 6.29 units (up 22.2%), which triggers a Critical stockout risk under company policy.
37. **insight/INS-0021** "Critical" -> "Low": P082 requires reorder of 1400 units to meet demand and replenish safety stock Stockout risk is Low because there is 0 stock on hand while daily demand is 75.86 units.
38. **fixed-2/C11/grounded** "overdue" -> "on time": - RC toy sedan car with remote control (Black) 1/50 scale, P058 (3.3 days of cover, below safety stock, lead time is 15.5 days, and pending orders are on time)
39. **extended-1/C12/grounded** "out of stock" -> "in stock": With no delivery delay, it would run in stock on 2026-10-25.
40. **fixed-2/C7/grounded** "overdue" -> "on time": Yes, deliveries are on time for Ride on toy sedan car (Yellow) 1/12 scale (P071).

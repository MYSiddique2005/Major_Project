"""Step 3: simulate inventory and purchasing on top of the real sales history.

Why: in the source, stock levels, purchase quantities and delivery dates are generator artefacts
(see reports/cleaning_report.md), so stock-risk and supplier analysis have nothing to work with.
This step keeps what is sound (products, suppliers, costs, lead times and every sales order line)
and regenerates the supply side from it with a standard replenishment policy.

Input:  Data/cleaned/ (sales_orders, sales_order_lines, products, suppliers, inventory, purchase_order_lines)
Output: Data/simulated/ and Data/reports/simulation_report.md
  supplier_profiles.csv     the delivery behaviour assumed for each supplier (the only invented inputs)
  purchase_orders.csv       same columns as cleaned/purchase_orders.csv
  purchase_order_lines.csv  same columns as cleaned/purchase_order_lines.csv
  inventory_daily.csv       stock position of every product on every day
  inventory.csv             stock position at the end of the period
  sales_fulfilment.csv      the day each real sales order line was shipped from the simulated stock

Model, one step per day and product:
  1. Deliveries due today arrive.
  2. Today's real demand (units ordered by customers) is shipped from stock; what cannot be shipped
     waits as a backorder and is shipped first when stock arrives.
  3. Every REVIEW_EVERY_DAYS the policy is recomputed from the previous DEMAND_WINDOW_DAYS of demand only:
       safety stock    = Z * std(daily demand) * sqrt(lead time)
       reorder point   = mean(daily demand) * lead time + safety stock
       order-up-to     = mean(daily demand) * (lead time + ORDER_CYCLE_DAYS) + safety stock
  4. If stock + on order - backorders is at or below the reorder point, an order is placed for the
     difference to the order-up-to level, rounded up to whole outers. Lines for the same supplier,
     day and lead time form one purchase order. The promised date is the order date plus the
     product's stated lead time.
  5. The supplier delivers early, on time or late, and sometimes short, according to its profile.
Afterwards each day's shipments are handed to the sales order lines of that product first come,
first served, which gives every line the day it was shipped in full (or none, if it is still waiting).
The run is deterministic (fixed seed).
"""
from pathlib import Path

import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).resolve().parents[1]
CLEAN_DIR = DATA_DIR / "cleaned"
OUT_DIR = DATA_DIR / "simulated"
REPORT = DATA_DIR / "reports" / "simulation_report.md"

SEED = 42
Z = 1.65                  # about a 95% cycle service level
DEMAND_WINDOW_DAYS = 91   # demand history the policy looks at
REVIEW_EVERY_DAYS = 28    # how often the policy figures are recomputed
ORDER_CYCLE_DAYS = 14     # same review period as Backend/app/analytics reorder suggestions

# Assumed delivery behaviour per supplier that sells goods. on_time = share of orders that arrive on or
# before the promised date; mean_delay_days = average lateness of a late order; short_rate = share of
# lines delivered short. Litware gets worse from WORSE_FROM onwards, so there is a trend to detect.
PROFILES = {
    # supplier_id: (on_time, mean_delay_days, short_rate)
    1: (0.90, 3.0, 0.02),    # A Datum Corporation
    2: (0.85, 4.0, 0.08),    # Contoso, Ltd.
    4: (0.93, 2.0, 0.02),    # Fabrikam, Inc.
    5: (0.88, 3.0, 0.03),    # Graphic Design Institute
    7: (0.80, 5.0, 0.05),    # Litware, Inc.
    10: (0.75, 6.0, 0.04),   # Northwind Electric Cars
    12: (0.96, 2.0, 0.01),   # The Phone Company
}
WORSE_SUPPLIER, WORSE_FROM, WORSE_ON_TIME = 7, pd.Timestamp("2015-07-01"), 0.62
EARLY_DAYS, EARLY_PROBABILITY = [0, 1, 2], [0.70, 0.20, 0.10]
SHORT_SHARE = (0.80, 0.98)  # a short line delivers this share of what was ordered


def clean(name: str, **kwargs) -> pd.DataFrame:
    return pd.read_csv(CLEAN_DIR / f"{name}.csv", **kwargs)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)

    products = clean("products").sort_values("product_id").reset_index(drop=True)
    suppliers = clean("suppliers")
    source_inventory = clean("inventory").set_index("product_id")
    source_lines = clean("purchase_order_lines")
    source_orders = clean("purchase_orders")
    orders = clean("sales_orders", parse_dates=["order_date"])
    sales = clean("sales_order_lines").merge(orders[["order_id", "order_date"]], on="order_id")

    days = pd.date_range(orders.order_date.min(), orders.order_date.max(), freq="D")
    demand = (sales.pivot_table(index="order_date", columns="product_id", values="quantity", aggfunc="sum")
              .reindex(index=days, columns=products.product_id).fillna(0).to_numpy(dtype=np.int64))
    n_days, n_products = demand.shape

    lead = products.lead_time_days.to_numpy()
    per_outer = products.quantity_per_outer.to_numpy()
    supplier = products.supplier_id.to_numpy()
    # Real purchase price per outer: the product's usual price on the source purchase orders.
    price_per_outer = source_lines.groupby("product_id").expected_price_per_outer.median().reindex(products.product_id).to_numpy()
    # Each supplier keeps the buyer and delivery method seen on its source purchase orders.
    buyer = source_orders.groupby("supplier_id").ordered_by.agg(lambda names: names.mode().iat[0])
    delivery_method = source_orders.groupby("supplier_id").delivery_method.agg(lambda names: names.mode().iat[0])
    reference = source_orders.groupby("supplier_id").supplier_reference.first()

    def policy(day: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        # Before a full window exists, the first window is used as the opening estimate.
        window = demand[max(0, day - DEMAND_WINDOW_DAYS + 1):day + 1] if day >= DEMAND_WINDOW_DAYS - 1 else demand[:DEMAND_WINDOW_DAYS]
        mean, std = window.mean(axis=0), window.std(axis=0, ddof=1)
        safety = np.ceil(Z * std * np.sqrt(lead))
        reorder_point = np.ceil(mean * lead + safety)
        order_up_to = np.ceil(mean * (lead + ORDER_CYCLE_DAYS) + safety)
        return safety.astype(np.int64), reorder_point.astype(np.int64), order_up_to.astype(np.int64)

    safety, reorder_point, order_up_to = policy(0)
    on_hand = order_up_to.copy()                 # opening stock: every product starts full
    backorder = np.zeros(n_products, dtype=np.int64)
    on_order = np.zeros(n_products, dtype=np.int64)
    arrivals: dict[int, list[tuple[int, int, int]]] = {}   # day -> (product index, units ordered, units delivered)
    po_rows, line_rows, daily = [], [], []
    receipt_day: dict[int, int] = {}

    for day in range(n_days):
        opening = on_hand.copy()
        received = np.zeros(n_products, dtype=np.int64)
        for index, units_ordered, units_delivered in arrivals.pop(day, []):
            received[index] += units_delivered
            on_order[index] -= units_ordered
        available = on_hand + received
        wanted = backorder + demand[day]
        shipped = np.minimum(available, wanted)
        on_hand = available - shipped
        backorder = wanted - shipped

        if day % REVIEW_EVERY_DAYS == 0:
            safety, reorder_point, order_up_to = policy(day)

        position = on_hand + on_order - backorder
        due = np.flatnonzero(position <= reorder_point)
        outers = np.ceil((order_up_to[due] - position[due]) / per_outer[due]).astype(np.int64)
        due, outers = due[outers > 0], outers[outers > 0]
        for supplier_id, lead_days in sorted(set(zip(supplier[due], lead[due]))):
            on_time, mean_delay, short_rate = PROFILES[supplier_id]
            if supplier_id == WORSE_SUPPLIER and days[day] >= WORSE_FROM:
                on_time = WORSE_ON_TIME
            if rng.random() < on_time:
                shift = -int(rng.choice(EARLY_DAYS, p=EARLY_PROBABILITY))
            else:
                shift = 1 + int(rng.poisson(mean_delay - 1))
            arrival = day + max(1, lead_days + shift)
            po_id = len(po_rows) + 1
            po_rows.append((po_id, supplier_id, day, day + lead_days))
            receipt_day[po_id] = arrival
            members = (supplier[due] == supplier_id) & (lead[due] == lead_days)
            for index, line_outers in zip(due[members], outers[members]):
                delivered_outers = line_outers
                if rng.random() < short_rate:
                    delivered_outers = max(1, int(line_outers * rng.uniform(*SHORT_SHARE)))
                units = int(line_outers * per_outer[index])
                on_order[index] += units
                arrivals.setdefault(arrival, []).append((index, units, int(delivered_outers * per_outer[index])))
                line_rows.append((len(line_rows) + 1, po_id, index, int(line_outers), int(delivered_outers), arrival))

        daily.append(np.column_stack([
            np.full(n_products, day), np.arange(n_products), opening, received, demand[day], shipped, on_hand,
            backorder, on_order, safety, reorder_point, order_up_to]))

    last = n_days - 1

    # ---- purchase orders and lines, in the cleaned tables' layout -------------------------
    po = pd.DataFrame(po_rows, columns=["purchase_order_id", "supplier_id", "order_day", "expected_day"])
    arrival_day = po.purchase_order_id.map(receipt_day)
    purchase_orders = pd.DataFrame({
        "purchase_order_id": po.purchase_order_id,
        "supplier_id": po.supplier_id,
        "order_date": days[po.order_day].date,
        "expected_delivery_date": (days[0] + pd.to_timedelta(po.expected_day, unit="D")).dt.date,
        "delivery_method": po.supplier_id.map(delivery_method),
        "ordered_by": po.supplier_id.map(buyer),
        "supplier_reference": po.supplier_id.map(reference),
        "is_finalized": arrival_day <= last,
    })
    lines = pd.DataFrame(line_rows, columns=["purchase_order_line_id", "purchase_order_id", "index", "ordered_outers",
                                             "delivered_outers", "arrival_day"])
    arrived = lines.arrival_day <= last
    purchase_order_lines = pd.DataFrame({
        "purchase_order_line_id": lines.purchase_order_line_id,
        "purchase_order_id": lines.purchase_order_id,
        "product_id": products.product_id.to_numpy()[lines["index"]],
        "package_type": products.outer_package.to_numpy()[lines["index"]],
        "quantity_per_outer": per_outer[lines["index"]],
        "ordered_outers": lines.ordered_outers,
        "received_outers": lines.delivered_outers.where(arrived, 0),
        "ordered_units": lines.ordered_outers * per_outer[lines["index"]],
        "received_units": (lines.delivered_outers * per_outer[lines["index"]]).where(arrived, 0),
        "expected_price_per_outer": price_per_outer[lines["index"]].round(2),
        "expected_cost_per_unit": (price_per_outer[lines["index"]] / per_outer[lines["index"]]).round(4),
        "last_receipt_date": pd.Series(days[lines.arrival_day.clip(upper=last)].date).where(arrived),
        "is_finalized": arrived,
    })
    purchase_orders.to_csv(OUT_DIR / "purchase_orders.csv", index=False)
    purchase_order_lines.to_csv(OUT_DIR / "purchase_order_lines.csv", index=False)

    # ---- daily stock position ------------------------------------------------------------
    columns = ["day", "index", "opening_stock", "units_received", "units_demanded", "units_shipped", "closing_stock",
               "backorder_units", "units_on_order", "safety_stock", "reorder_point", "order_up_to_level"]
    inventory_daily = pd.DataFrame(np.vstack(daily), columns=columns)
    inventory_daily.insert(0, "date", days[inventory_daily.pop("day")].date)
    inventory_daily.insert(1, "product_id", products.product_id.to_numpy()[inventory_daily.pop("index")])
    inventory_daily.to_csv(OUT_DIR / "inventory_daily.csv", index=False)

    final = inventory_daily[inventory_daily.date == days[-1].date()].set_index("product_id")
    inventory = pd.DataFrame({
        "product_id": products.product_id,
        "bin_location": products.product_id.map(source_inventory.bin_location),
        "quantity_on_hand": products.product_id.map(final.closing_stock),
        "backorder_units": products.product_id.map(final.backorder_units),
        "units_on_order": products.product_id.map(final.units_on_order),
        "safety_stock": products.product_id.map(final.safety_stock),
        "reorder_point": products.product_id.map(final.reorder_point),
        "order_up_to_level": products.product_id.map(final.order_up_to_level),
        "last_cost_price": products.product_id.map(source_inventory.last_cost_price),
        "last_updated": days[-1].date(),
    })
    inventory.to_csv(OUT_DIR / "inventory.csv", index=False)

    # ---- which sales lines the shipments went to (first come, first served) ---------------
    column = {product_id: index for index, product_id in enumerate(products.product_id)}
    shipped_so_far = inventory_daily.pivot(index="date", columns="product_id", values="units_shipped").cumsum().to_numpy()
    fulfilment = sales.sort_values(["product_id", "order_date", "order_line_id"])[
        ["order_line_id", "order_id", "product_id", "order_date", "quantity"]].reset_index(drop=True)
    needed = fulfilment.groupby("product_id").quantity.cumsum().to_numpy()
    shipped_day = np.empty(len(fulfilment), dtype=np.int64)
    for product_id, rows in fulfilment.groupby("product_id").indices.items():
        shipped_day[rows] = np.searchsorted(shipped_so_far[:, column[product_id]], needed[rows], side="left")
    is_shipped = shipped_day < n_days
    fulfilment["shipped_date"] = pd.Series(days[np.minimum(shipped_day, last)]).where(is_shipped)
    fulfilment["days_waited"] = (fulfilment.shipped_date - fulfilment.order_date).dt.days.astype("Int64")
    fulfilment = fulfilment.sort_values("order_line_id")
    fulfilment.assign(order_date=fulfilment.order_date.dt.date, shipped_date=fulfilment.shipped_date.dt.date).to_csv(
        OUT_DIR / "sales_fulfilment.csv", index=False)

    profiles = pd.DataFrame([
        {"supplier_id": supplier_id, "on_time_probability": on_time, "mean_delay_days_when_late": delay,
         "short_delivery_rate": short,
         "note": f"on_time_probability {WORSE_ON_TIME} from {WORSE_FROM.date()}" if supplier_id == WORSE_SUPPLIER else ""}
        for supplier_id, (on_time, delay, short) in PROFILES.items()])
    profiles.insert(1, "supplier_name", profiles.supplier_id.map(suppliers.set_index("supplier_id").supplier_name))
    profiles.to_csv(OUT_DIR / "supplier_profiles.csv", index=False)

    # ---- checks and report ---------------------------------------------------------------
    d = inventory_daily
    by_product = d.groupby("product_id")
    checks = [
        ("Stock never negative", (d.closing_stock >= 0).all() and (d.opening_stock >= 0).all()),
        ("closing = opening + received - shipped, every product and day",
         (d.closing_stock == d.opening_stock + d.units_received - d.units_shipped).all()),
        ("Each day's opening stock is the previous day's closing stock",
         (by_product.opening_stock.shift(-1).dropna() == by_product.closing_stock.shift(0)[by_product.cumcount(ascending=False) > 0]).all()),
        ("Demand equals the real units ordered (cleaned sales lines)", int(d.units_demanded.sum()) == int(sales.quantity.sum())),
        ("Demand = shipped + backorders still open at the end",
         int(d.units_demanded.sum()) == int(d.units_shipped.sum()) + int(final.backorder_units.sum())),
        ("Units received in the stock table equal units received on purchase-order lines",
         int(d.units_received.sum()) == int(purchase_order_lines.received_units.sum())),
        ("Units on order at the end equal the units on undelivered lines",
         int(final.units_on_order.sum()) == int(purchase_order_lines.ordered_units[~arrived].sum())),
        ("No sales line is shipped before its order date; lines still waiting cover the open backorders",
         (fulfilment.days_waited.dropna() >= 0).all()
         and fulfilment.quantity[fulfilment.shipped_date.isna()].sum() >= final.backorder_units.sum()
         and (fulfilment.shipped_date.isna().sum() == 0) == (final.backorder_units.sum() == 0)),
        ("Every purchase order goes to the supplier of its products",
         (purchase_order_lines.merge(purchase_orders, on="purchase_order_id").supplier_id.to_numpy()
          == purchase_order_lines.product_id.map(products.set_index("product_id").supplier_id).to_numpy()).all()),
        ("Received never exceeds ordered; receipt is after the order date",
         (purchase_order_lines.received_outers <= purchase_order_lines.ordered_outers).all()
         and (lines.arrival_day > lines.purchase_order_id.map(po.set_index("purchase_order_id").order_day)).all()),
    ]
    merged = purchase_order_lines.merge(purchase_orders, on="purchase_order_id", suffixes=("", "_order"))
    done = merged[merged.is_finalized].copy()
    done["late"] = pd.to_datetime(done.last_receipt_date) > pd.to_datetime(done.expected_delivery_date)
    done["delay"] = (pd.to_datetime(done.last_receipt_date) - pd.to_datetime(done.expected_delivery_date)).dt.days
    done["lead"] = (pd.to_datetime(done.last_receipt_date) - pd.to_datetime(done.order_date)).dt.days
    per_supplier = done.groupby("supplier_id").agg(
        lines=("late", "size"), on_time_pct=("late", lambda s: round((1 - s.mean()) * 100, 1)),
        avg_lead_days=("lead", lambda s: round(s.mean(), 1)), longest_delay_days=("delay", "max"),
        fill_pct=("received_units", "sum"))
    per_supplier["fill_pct"] = (per_supplier.fill_pct / done.groupby("supplier_id").ordered_units.sum() * 100).round(1)
    per_supplier.insert(0, "supplier", per_supplier.index.map(suppliers.set_index("supplier_id").supplier_name))
    stockout_days = (d.closing_stock == 0) & (d.units_demanded + d.backorder_units > 0)
    waiting_before = by_product.backorder_units.shift(1).fillna(0)
    same_day = (d.opening_stock + d.units_received - waiting_before).clip(lower=0).clip(upper=d.units_demanded)
    cover = inventory.quantity_on_hand / np.maximum(demand[-DEMAND_WINDOW_DAYS:].mean(axis=0), 1e-9)
    overdue = merged[~merged.is_finalized & (pd.to_datetime(merged.expected_delivery_date) < days[-1])]

    text = ["# Simulation report", "", "Generated by `scripts/03_simulate_supply.py` (seed "
            f"{SEED}). Sales demand is real; purchase orders and stock levels are simulated from it.", "",
            "## Result", "",
            f"- {len(purchase_orders):,} purchase orders with {len(purchase_order_lines):,} lines over {n_days:,} days "
            f"for {n_products} products.",
            f"- {same_day.sum() / d.units_demanded.sum():.2%} of units demanded were shipped on the day they were "
            f"ordered; the rest waited for a delivery. {int(final.backorder_units.sum()):,} units were still on "
            f"backorder at the end.",
            f"- Sales order lines: {(fulfilment.days_waited == 0).mean():.2%} shipped on the order date, "
            f"{(fulfilment.days_waited > 0).mean():.2%} shipped later (after {fulfilment.days_waited[fulfilment.days_waited > 0].mean():.1f} "
            f"days on average, {int(fulfilment.days_waited.max())} at most), {int(fulfilment.shipped_date.isna().sum())} still waiting at the end.",
            f"- Product-days out of stock with demand waiting: {int(stockout_days.sum()):,} of {len(d):,} "
            f"({stockout_days.mean():.2%}); {int((by_product.closing_stock.min() == 0).sum())} products ran out at least once.",
            f"- Stock at the end: median {np.median(cover):.0f} days of cover (5th to 95th percentile "
            f"{np.percentile(cover, 5):.0f} to {np.percentile(cover, 95):.0f}); "
            f"{int((inventory.quantity_on_hand == 0).sum())} products out of stock, "
            f"{int((inventory.quantity_on_hand <= inventory.safety_stock).sum())} at or below safety stock, "
            f"{int((inventory.quantity_on_hand <= inventory.reorder_point).sum())} at or below the reorder point.",
            f"- Open at the end: {int((~arrived).sum())} lines not yet delivered, {len(overdue)} of them past their promised date.",
            "", "## Delivery performance that resulted", "",
            "| Supplier | Lines delivered | On time | Average lead time (days) | Longest delay (days) | Units delivered of ordered |",
            "|---|---:|---:|---:|---:|---:|"]
    text += [f"| {row.supplier} | {row.lines:,} | {row.on_time_pct}% | {row.avg_lead_days} | {row.longest_delay_days} | {row.fill_pct}% |"
             for row in per_supplier.itertuples()]
    litware = done[done.supplier_id == WORSE_SUPPLIER]
    before = litware[pd.to_datetime(litware.order_date) < WORSE_FROM]
    after = litware[pd.to_datetime(litware.order_date) >= WORSE_FROM]
    text += ["", f"Litware, Inc. on-time rate: {(1 - before.late.mean()):.1%} before {WORSE_FROM.date()}, "
             f"{(1 - after.late.mean()):.1%} from then on.",
             "", "## Checks", "", "| Check | Result |", "|---|---|"]
    text += [f"| {name} | {'pass' if passed else 'FAIL'} |" for name, passed in checks]
    REPORT.write_text("\n".join(text) + "\n", encoding="utf-8")
    print("\n".join(text[4:]))
    raise SystemExit(0 if all(passed for _, passed in checks) else 1)


if __name__ == "__main__":
    main()

"""Step 4: turn the cleaned and simulated tables into the datasets IntelliERP uses.

Input:  Data/cleaned/*.csv   products, suppliers, customers and sales (real, from 02_clean.py)
        Data/simulated/*.csv purchase orders and stock levels (simulated, from 03_simulate_supply.py)
Output: Data/processed/
  erp/       one file per IntelliERP table, with the backend's column names, ID formats and status values
  panel/     one row per product per day (and per week) for sales, procurement and inventory;
             the three files of a grain have exactly the same rows and keys
  features/  per-product demand and stock figures, per-supplier performance,
             and weekly demand with lag features for forecasting
and Data/reports/preprocessing_summary.md

Nothing is invented in this step: every figure is an aggregate or a restatement of its inputs.
"""
from pathlib import Path

import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).resolve().parents[1]
CLEAN_DIR = DATA_DIR / "cleaned"
SIMULATED_DIR = DATA_DIR / "simulated"
OUT_DIR = DATA_DIR / "processed"
REPORT = DATA_DIR / "reports" / "preprocessing_summary.md"

DEMAND_WINDOW_DAYS = 365      # demand statistics use the most recent year
TREND_WINDOW_DAYS = 28        # same window as Backend/app/analytics (last 28 days vs the 28 before)
WAREHOUSE = "Main Warehouse"  # the source company has a single warehouse


written: list[tuple[str, int, int]] = []


def clean(name: str, **kwargs) -> pd.DataFrame:
    return pd.read_csv(CLEAN_DIR / f"{name}.csv", **kwargs)


def simulated(name: str, **kwargs) -> pd.DataFrame:
    return pd.read_csv(SIMULATED_DIR / f"{name}.csv", **kwargs)


def save(relative: str, frame: pd.DataFrame) -> None:
    path = OUT_DIR / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False)
    written.append((relative, len(frame), frame.shape[1]))


def product_code(ids: pd.Series) -> pd.Series:
    return "P" + ids.astype(int).astype(str).str.zfill(3)


def supplier_code(ids: pd.Series) -> pd.Series:
    return "S" + ids.astype(int).astype(str).str.zfill(3)


def full_grid(products: pd.Series, periods: pd.DatetimeIndex, period_name: str) -> pd.DataFrame:
    """Every product in every period, so that all panel files share the same rows."""
    index = pd.MultiIndex.from_product([periods, sorted(products)], names=[period_name, "product_id"])
    return pd.DataFrame(index=index).reset_index()


def main() -> None:
    suppliers = clean("suppliers")
    products = clean("products")
    customers = clean("customers")
    inventory = simulated("inventory", parse_dates=["last_updated"])
    stock = simulated("inventory_daily", parse_dates=["date"])
    orders = clean("sales_orders", parse_dates=["order_date"])
    order_lines = clean("sales_order_lines")
    purchase_orders = simulated("purchase_orders", parse_dates=["order_date", "expected_delivery_date"])
    po_lines = simulated("purchase_order_lines", parse_dates=["last_receipt_date"])

    orders = orders.assign(expected_delivery_date=pd.to_datetime(orders.expected_delivery_date))
    fulfilment = simulated("sales_fulfilment", parse_dates=["shipped_date"])[["order_line_id", "shipped_date", "days_waited"]]
    sales = (order_lines.merge(orders[["order_id", "customer_id", "order_date", "expected_delivery_date"]], on="order_id")
             .merge(fulfilment, on="order_line_id", validate="one_to_one"))
    purchases = po_lines.merge(purchase_orders, on="purchase_order_id", suffixes=("", "_order"))
    purchases["lead_days"] = (purchases.last_receipt_date - purchases.order_date).dt.days
    purchases["on_time"] = purchases.last_receipt_date <= purchases.expected_delivery_date
    purchases["days_late"] = (purchases.last_receipt_date - purchases.expected_delivery_date).dt.days.clip(lower=0)
    purchases["order_value"] = purchases.ordered_outers * purchases.expected_price_per_outer

    first_day, last_day = orders.order_date.min(), orders.order_date.max()
    days = pd.date_range(first_day, last_day, freq="D")

    # ---- daily panels --------------------------------------------------------------------
    grid = full_grid(products.product_id, days, "date")
    keys = ["date", "product_id"]

    daily_sales = sales.assign(date=sales.order_date).groupby(keys).agg(
        order_lines=("order_line_id", "size"),
        orders=("order_id", "nunique"),
        customers=("customer_id", "nunique"),
        units_ordered=("quantity", "sum"),
        units_picked=("picked_quantity", "sum"),
        revenue_excl_tax=("line_total_excl_tax", "sum"),
    ).reset_index()
    daily_sales = grid.merge(daily_sales, on=keys, how="left").fillna(0)
    daily_sales[daily_sales.columns[2:7]] = daily_sales[daily_sales.columns[2:7]].astype(int)
    daily_sales["revenue_excl_tax"] = daily_sales.revenue_excl_tax.round(2)

    ordered = purchases.assign(date=purchases.order_date).groupby(keys).agg(
        po_lines_placed=("purchase_order_line_id", "size"),
        units_ordered=("ordered_units", "sum"),
        order_value=("order_value", "sum"),
    ).reset_index()
    received = purchases.dropna(subset=["last_receipt_date"]).assign(date=lambda f: f.last_receipt_date).groupby(keys).agg(
        po_lines_received=("purchase_order_line_id", "size"),
        units_received=("received_units", "sum"),
    ).reset_index()
    daily_procurement = grid.merge(ordered, on=keys, how="left").merge(received, on=keys, how="left").fillna(0)
    for column in ["po_lines_placed", "units_ordered", "po_lines_received", "units_received"]:
        daily_procurement[column] = daily_procurement[column].astype(int)
    daily_procurement["order_value"] = daily_procurement.order_value.round(2)
    daily_inventory = grid.merge(stock, on=keys, how="left")
    assert not daily_inventory.isna().any().any()
    daily_inventory["is_stockout"] = ((daily_inventory.closing_stock == 0)
                                      & (daily_inventory.units_demanded + daily_inventory.backorder_units > 0)).astype(int)
    daily_inventory["below_safety_stock"] = (daily_inventory.closing_stock <= daily_inventory.safety_stock).astype(int)
    # Units ordered and still on the way at the end of each day.
    daily_procurement["units_on_order"] = daily_inventory.units_on_order

    for name, frame in [("sales", daily_sales), ("procurement", daily_procurement), ("inventory", daily_inventory)]:
        assert frame[keys].equals(grid[keys]), name
        save(f"panel/daily_{name}.csv", frame.assign(date=frame.date.dt.date, product_id=product_code(frame.product_id)))

    # ---- weekly panels (weeks start on Monday) -------------------------------------------
    def weekly(frame: pd.DataFrame, summed: list[str], last: list[str] = ()) -> pd.DataFrame:
        week = (frame.date - pd.to_timedelta(frame.date.dt.weekday, unit="D")).rename("week_start")
        grouped = frame.groupby([week, "product_id"])
        result = grouped[summed].sum()
        for column in last:
            result[column] = grouped[column].last()
        result.insert(0, "days_in_week", grouped.size())
        return result.reset_index()

    weekly_sales = weekly(daily_sales, ["order_lines", "units_ordered", "units_picked", "revenue_excl_tax"])
    weekly_sales["revenue_excl_tax"] = weekly_sales.revenue_excl_tax.round(2)
    weekly_procurement = weekly(daily_procurement, ["po_lines_placed", "units_ordered", "order_value",
                                                    "po_lines_received", "units_received"], ["units_on_order"])
    weekly_procurement["order_value"] = weekly_procurement.order_value.round(2)
    weekly_inventory = weekly(
        daily_inventory, ["units_received", "units_demanded", "units_shipped", "is_stockout", "below_safety_stock"],
        ["closing_stock", "backorder_units", "units_on_order", "safety_stock", "reorder_point", "order_up_to_level"],
    ).rename(columns={"is_stockout": "stockout_days", "below_safety_stock": "days_below_safety_stock"})
    week_keys = ["week_start", "product_id"]
    for name, frame in [("sales", weekly_sales), ("procurement", weekly_procurement), ("inventory", weekly_inventory)]:
        assert frame[week_keys].equals(weekly_sales[week_keys]), name
        save(f"panel/weekly_{name}.csv",
             frame.assign(week_start=frame.week_start.dt.date, product_id=product_code(frame.product_id)))

    # ---- product features ----------------------------------------------------------------
    recent = daily_sales[daily_sales.date > last_day - pd.Timedelta(days=DEMAND_WINDOW_DAYS)]
    demand = recent.groupby("product_id").units_ordered.agg(avg_daily_demand="mean", std_daily_demand="std")
    last_window = daily_sales[daily_sales.date > last_day - pd.Timedelta(days=TREND_WINDOW_DAYS)]
    previous_window = daily_sales[(daily_sales.date > last_day - pd.Timedelta(days=2 * TREND_WINDOW_DAYS))
                                  & (daily_sales.date <= last_day - pd.Timedelta(days=TREND_WINDOW_DAYS))]
    demand["demand_last_28d"] = last_window.groupby("product_id").units_ordered.sum()
    demand["demand_previous_28d"] = previous_window.groupby("product_id").units_ordered.sum()
    demand["demand_trend_pct"] = ((demand.demand_last_28d / demand.demand_previous_28d - 1) * 100).round(1)

    totals = sales.groupby("product_id").agg(
        total_units_sold=("quantity", "sum"),
        total_revenue_excl_tax=("line_total_excl_tax", "sum"),
        total_order_lines=("order_line_id", "size"),
        distinct_customers=("customer_id", "nunique"),
        first_sale_date=("order_date", "min"),
        last_sale_date=("order_date", "max"),
    )
    purchase_totals = purchases.groupby("product_id").agg(
        purchase_order_lines=("purchase_order_line_id", "size"),
        total_units_purchased=("received_units", "sum"),
    )
    stock_history = daily_inventory.groupby("product_id").agg(
        stockout_days=("is_stockout", "sum"),
        days_below_safety_stock=("below_safety_stock", "sum"),
        avg_stock=("closing_stock", "mean"),
    )
    features = (products.set_index("product_id")[["product_name", "primary_category", "supplier_id", "unit_price",
                                                  "lead_time_days", "quantity_per_outer"]]
                .join(inventory.set_index("product_id")[["last_cost_price", "quantity_on_hand", "backorder_units",
                                                         "units_on_order", "safety_stock", "reorder_point",
                                                         "order_up_to_level"]])
                .join(totals).join(purchase_totals).join(stock_history).join(demand))
    features = features.rename(columns={
        "primary_category": "category", "last_cost_price": "unit_cost", "quantity_on_hand": "stock_on_hand"})
    features["gross_margin_pct"] = ((features.unit_price - features.unit_cost) / features.unit_price * 100).round(1)
    features["demand_cv"] = (features.std_daily_demand / features.avg_daily_demand).round(3)
    recent_daily = features.demand_last_28d / TREND_WINDOW_DAYS
    features["days_of_cover"] = (features.stock_on_hand / recent_daily).round(1)
    features["inventory_turnover_per_year"] = (features.total_units_sold / len(days) * 365 / features.avg_stock).round(1)
    features["avg_stock"] = features.avg_stock.round(1)
    # ABC class by share of revenue: A = first 80%, B = next 15%, C = last 5%.
    ranked = features.total_revenue_excl_tax.sort_values(ascending=False)
    share = ranked.cumsum() / ranked.sum()
    features["abc_class"] = pd.cut(share.shift(fill_value=0), [-1, 0.80, 0.95, 2], labels=["A", "B", "C"]).reindex(features.index)
    features[["avg_daily_demand", "std_daily_demand"]] = features[["avg_daily_demand", "std_daily_demand"]].round(3)
    features["total_revenue_excl_tax"] = features.total_revenue_excl_tax.round(2)
    features = features.reset_index()
    out = features.assign(product_id=product_code(features.product_id), supplier_id=supplier_code(features.supplier_id),
                          first_sale_date=features.first_sale_date.dt.date, last_sale_date=features.last_sale_date.dt.date)
    save("features/product_features.csv", out)

    # ---- supplier performance ------------------------------------------------------------
    delivered = purchases.dropna(subset=["last_receipt_date"])
    performance = suppliers.set_index("supplier_id")[["supplier_name", "supplier_category", "country", "payment_days"]].join([
        products.groupby("supplier_id").size().rename("products_supplied"),
        purchase_orders.groupby("supplier_id").agg(purchase_orders=("purchase_order_id", "size"),
                                                   first_order_date=("order_date", "min"),
                                                   last_order_date=("order_date", "max")),
        purchases.groupby("supplier_id").agg(purchase_order_lines=("purchase_order_line_id", "size"),
                                             units_ordered=("ordered_units", "sum"),
                                             units_received=("received_units", "sum"),
                                             order_value=("order_value", "sum"),
                                             open_lines=("is_finalized", lambda flags: int((~flags).sum()))),
        delivered.groupby("supplier_id").agg(avg_delivery_days=("lead_days", "mean"),
                                             max_delivery_days=("lead_days", "max"),
                                             avg_days_late=("days_late", "mean"),
                                             on_time_rate_pct=("on_time", lambda flags: flags.mean() * 100)),
        products.groupby("supplier_id").lead_time_days.mean().rename("stated_lead_time_days"),
    ])
    counts = ["products_supplied", "purchase_orders", "purchase_order_lines", "units_ordered", "units_received", "open_lines"]
    performance[counts] = performance[counts].fillna(0).astype(int)
    performance["fill_rate_pct"] = (performance.units_received / performance.units_ordered * 100).round(1)
    overdue = purchases[~purchases.is_finalized & (purchases.expected_delivery_date < last_day)]
    performance["overdue_lines"] = performance.index.map(overdue.groupby("supplier_id").size()).fillna(0).astype(int)
    rounded = ["avg_delivery_days", "avg_days_late", "on_time_rate_pct", "stated_lead_time_days", "order_value"]
    performance[rounded] = performance[rounded].round(2)
    performance["status"] = np.where(performance.products_supplied > 0, "Active", "Inactive")
    performance = performance.reset_index()
    save("features/supplier_performance.csv",
         performance.assign(supplier_id=supplier_code(performance.supplier_id),
                            first_order_date=performance.first_order_date.dt.date,
                            last_order_date=performance.last_order_date.dt.date))

    # ---- weekly demand with forecasting features -----------------------------------------
    demand_features = weekly_sales[["week_start", "product_id", "days_in_week", "units_ordered"]].copy()
    by_product = demand_features.groupby("product_id").units_ordered
    for lag in (1, 2, 4, 52):
        demand_features[f"units_lag_{lag}w"] = by_product.shift(lag)
    for window in (4, 12):
        demand_features[f"units_mean_prev_{window}w"] = by_product.transform(
            lambda s, w=window: s.shift(1).rolling(w).mean()).round(2)
    demand_features["year"] = demand_features.week_start.dt.isocalendar().year.astype(int)
    demand_features["week_of_year"] = demand_features.week_start.dt.isocalendar().week.astype(int)
    demand_features["month"] = demand_features.week_start.dt.month
    # The last 26 weeks are held out so forecasts can be scored on data they have not seen.
    weeks = np.sort(demand_features.week_start.unique())
    demand_features["split"] = np.where(demand_features.week_start >= weeks[-26], "test", "train")
    save("features/weekly_demand_features.csv",
         demand_features.assign(week_start=demand_features.week_start.dt.date,
                                product_id=product_code(demand_features.product_id)))

    # ---- IntelliERP tables ---------------------------------------------------------------
    feature_by_product = features.set_index("product_id")
    performance_by_supplier = performance.set_index("supplier_id")
    # IntelliERP suppliers are suppliers of products. The source also lists service providers
    # (bank, courier, insurance, ...) that supply none; they stay in cleaned/suppliers.csv only.
    suppliers = suppliers[suppliers.supplier_id.isin(products.supplier_id)].reset_index(drop=True)
    erp_suppliers = pd.DataFrame({
        "id": supplier_code(suppliers.supplier_id),
        "name": suppliers.supplier_name,
        "contact_name": suppliers.contact_name,
        "email": suppliers.contact_email,
        "phone": suppliers.phone,
        "country": suppliers.country,
        "avg_delivery_days": suppliers.supplier_id.map(performance_by_supplier.avg_delivery_days),
        "delivery_reliability": suppliers.supplier_id.map(performance_by_supplier.on_time_rate_pct),
        "status": suppliers.supplier_id.map(performance_by_supplier.status),
    })
    save("erp/suppliers.csv", erp_suppliers)

    erp_products = pd.DataFrame({
        "id": product_code(products.product_id),
        "sku": "WWI-" + products.product_id.astype(str).str.zfill(4),  # derived: the source has no SKU
        "name": products.product_name,
        "category": products.primary_category,
        "supplier_id": supplier_code(products.supplier_id),
        "price": products.unit_price,
        "unit_cost": products.product_id.map(feature_by_product.unit_cost),
        "status": "Active",
    })
    save("erp/products.csv", erp_products)
    save("erp/supplier_products.csv", erp_products[["supplier_id", "id"]].rename(columns={"id": "product_id"})
         .sort_values(["supplier_id", "product_id"]))

    erp_inventory = pd.DataFrame({
        "id": "INV-" + inventory.product_id.astype(str).str.zfill(4),
        "product_id": product_code(inventory.product_id),
        "warehouse": WAREHOUSE,
        "current_stock": inventory.quantity_on_hand,
        "safety_stock": inventory.safety_stock,
        "reorder_level": inventory.reorder_point,
        "last_updated": inventory.last_updated.dt.date,
        "bin_location": inventory.bin_location,
        "units_on_order": inventory.units_on_order,
    })
    save("erp/inventory.csv", erp_inventory)

    customer_name = customers.set_index("customer_id").customer_name
    # Status follows the simulated stock: an order line is Pending while it waits for stock,
    # Processing once shipped and on its way (the order's own delivery time), then Completed.
    delivered_on = sales.shipped_date + (sales.expected_delivery_date - sales.order_date)
    status = np.select([sales.shipped_date.isna(), delivered_on > last_day], ["Pending", "Processing"], "Completed")
    erp_sales = pd.DataFrame({
        "id": "SO-" + sales.order_line_id.astype(str).str.zfill(6),
        "customer": sales.customer_id.map(customer_name),
        "product_id": product_code(sales.product_id),
        "quantity": sales.quantity,
        "unit_price": sales.unit_price,
        "order_date": sales.order_date.dt.date,
        "status": status,
        "source_order_id": sales.order_id,
        "shipped_date": sales.shipped_date.dt.date,
        "days_waited_for_stock": sales.days_waited.astype("Int64"),
    }).sort_values("id")
    save("erp/sales_orders.csv", erp_sales)

    erp_purchases = pd.DataFrame({
        "id": "PO-" + purchases.purchase_order_line_id.astype(str).str.zfill(5),
        "supplier_id": supplier_code(purchases.supplier_id),
        "product_id": product_code(purchases.product_id),
        "quantity": purchases.ordered_units,
        "unit_price": purchases.expected_cost_per_unit.round(2),
        "order_date": purchases.order_date.dt.date,
        "expected_delivery": purchases.expected_delivery_date.dt.date,
        "actual_delivery": purchases.last_receipt_date.dt.date,
        "status": np.where(purchases.is_finalized, "Delivered", "Ordered"),
        "reason": "",
        "created_by": purchases.ordered_by,
        "source_purchase_order_id": purchases.purchase_order_id,
    }).sort_values("id")
    save("erp/purchase_orders.csv", erp_purchases)

    # Guards: the files must fit the backend's tables (Backend/app/db/models.py).
    assert erp_products.name.str.len().max() <= 160 and erp_sales.customer.str.len().max() <= 160
    assert erp_sales.product_id.isin(erp_products.id).all() and erp_purchases.product_id.isin(erp_products.id).all()
    assert erp_purchases.supplier_id.isin(erp_suppliers.id).all() and erp_products.supplier_id.isin(erp_suppliers.id).all()
    assert (erp_sales.quantity > 0).all() and (erp_purchases.quantity > 0).all() and (erp_inventory.current_stock >= 0).all()
    assert erp_sales.status.notna().all() and not erp_sales.id.duplicated().any() and not erp_purchases.id.duplicated().any()

    # ---- summary -------------------------------------------------------------------------
    lines = ["# Preprocessing summary", "",
             "Generated by `scripts/03_preprocess.py`.", "",
             f"Period: {first_day.date()} to {last_day.date()} ({len(days):,} days, "
             f"{weekly_sales.week_start.nunique()} weeks), {len(products)} products.", "",
             "| File | Rows | Columns |", "|---|---:|---:|"]
    lines += [f"| `processed/{name}` | {rows:,} | {columns} |" for name, rows, columns in written]
    lines += ["",
              "Origin of the data: products, suppliers, customers, prices, costs, lead times and all sales are the "
              "real source records. Purchase orders, deliveries and stock levels are simulated from the real sales "
              "(see `simulation_report.md`).", "",
              "Derived values and their rules:", "",
              f"- `avg_daily_demand`, `std_daily_demand`: units ordered per day over the last {DEMAND_WINDOW_DAYS} days, "
              "counting days without sales as zero.",
              "- `safety_stock`, `reorder_point`, `order_up_to_level`: the replenishment policy in force on each day, "
              "as set by the simulation from the preceding 91 days of demand.",
              f"- `days_of_cover`: stock on hand divided by average daily demand over the last {TREND_WINDOW_DAYS} days.",
              "- `is_stockout` / `stockout_days`: days that ended with no stock while customers were waiting.",
              f"- `demand_trend_pct`: units in the last {TREND_WINDOW_DAYS} days against the {TREND_WINDOW_DAYS} days before.",
              "- `abc_class`: products ranked by revenue; A = first 80% of revenue, B = next 15%, C = the rest.",
              "- `erp/sales_orders.csv` has one row per sales order line. `status` follows the simulated stock: Pending "
              "while the line waits for stock, Processing once shipped but not yet delivered (shipped date plus the "
              "order's own delivery time is after the last day), otherwise Completed. The source's own status is in "
              "`cleaned/sales_orders.csv`.",
              "- `erp/purchase_orders.csv` has one row per purchase-order line, quantity in units "
              "(outers x quantity_per_outer); status is Delivered when the line was received, otherwise Ordered.",
              "- `erp/suppliers.csv`: `avg_delivery_days` and `delivery_reliability` (on-time %) are measured on the "
              "simulated deliveries. Only the 7 suppliers that supply products are included; the 6 service "
              "providers in the source are left out.",
              "- `erp/products.csv` `sku` is derived from the product id; the source has no SKU."]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    for name, rows, columns in written:
        print(f"{name:42s} {rows:>8,d} rows x {columns}")


if __name__ == "__main__":
    main()

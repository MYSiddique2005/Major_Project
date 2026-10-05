# IntelliERP dataset

Source: **Wide World Importers**, Microsoft's sample ERP database for a wholesale novelty-goods
importer, in the PostgreSQL port published at
<https://github.com/Azure/azure-postgresql/tree/master/samples/databases/wide-world-importers>
(MIT licence). The company and its records are fictional; no real customer data is involved.

Period: 2013-01-01 to 2016-05-31. 227 products, 7 goods suppliers, 663 customers,
73,595 sales orders (231,412 lines), 6,063 purchase orders (18,304 lines).

## What is source data and what is simulated

| Data | Origin |
|---|---|
| Products, categories, prices, unit costs, lead times, pack sizes | Source |
| Suppliers, customers | Source |
| Sales orders and lines (customers, dates, quantities, prices) | Source |
| Sales order status and shipped date in `processed/erp/` | **Simulated**: follows the simulated stock |
| Purchase orders, delivery dates, received quantities | **Simulated** from the source sales |
| Stock levels, backorders, safety stock, reorder points | **Simulated** from the source sales |
| Supplier on-time rate, delays, short deliveries | **Simulated**; the assumed behaviour per supplier is in `simulated/supplier_profiles.csv` |

The source's own stock and purchasing records were not usable: stock on hand did not follow from the
stock movements and was years of demand, purchase quantities bore no relation to sales, and no
delivery was ever late (`reports/cleaning_report.md`). They are still available, cleaned but
otherwise untouched, in `cleaned/inventory.csv`, `cleaned/purchase_orders.csv`,
`cleaned/purchase_order_lines.csv` and `cleaned/stock_movements.csv`.

The simulation (`scripts/03_simulate_supply.py`) replays the real daily demand of every product
through a reorder-point policy: safety stock = 1.65 x std of daily demand x sqrt(lead time), reorder
point = mean daily demand x lead time + safety stock, order up to 14 further days of demand, in
whole outers, from the product's real supplier at its real cost. The policy only ever looks at the
previous 91 days of demand. Suppliers deliver early, on time, late or short according to their
profile; Litware, Inc. becomes less reliable from July 2015. Each day's shipments are then handed
to that product's sales order lines first come, first served, which gives every line a shipped date.
The run is deterministic (seed 42), and stock, receipts and demand reconcile exactly
(`reports/simulation_report.md`).

## Layout

| Folder | Content |
|---|---|
| `raw/` | The downloaded dump and, in `raw/csv/`, all 29 source tables exactly as stored |
| `cleaned/` | 10 tidy, typed, validated source tables |
| `simulated/` | Purchase orders and lines, daily stock position, closing stock, shipped date per sales line, supplier profiles |
| `processed/erp/` | One file per IntelliERP table (`suppliers`, `products`, `supplier_products`, `inventory`, `sales_orders`, `purchase_orders`) with the backend's column names, ID formats (`P001`, `S001`, `SO-…`, `PO-…`) and status values |
| `processed/panel/` | One row per product per day (283,069 rows) and per week (40,633 rows) for sales, procurement and inventory. The three files of a grain have identical rows and keys |
| `processed/features/` | `product_features` (demand, trend, margin, ABC class, stock position, stockout days), `supplier_performance`, `weekly_demand_features` (lags, rolling means, train/test split) |
| `reports/` | `cleaning_report.md`, `simulation_report.md`, `preprocessing_summary.md` |
| `scripts/` | The four steps that produce everything above |

## Rebuilding

```bash
cd Data
python3 -m venv .venv && .venv/bin/pip install pandas pyarrow
.venv/bin/python scripts/01_extract_raw.py      # download (checksum-verified) and extract; needs pg_restore
.venv/bin/python scripts/02_clean.py
.venv/bin/python scripts/03_simulate_supply.py
.venv/bin/python scripts/04_preprocess.py
```

No database is created or modified; `pg_restore` only converts the dump to text.

To load the result into the application database (replaces all rows; last 12 months by default):

```bash
cd ../Backend && .venv/bin/python -m app.db.load_dataset --reset
```

## Limits

- Supply-side results (stockouts, late deliveries, supplier rankings) reflect the simulation's
  assumptions, not observed behaviour. Report them as simulated.
- A sales line waits when the simulated stock runs out (2.5% of lines, 2.9 days on average) and is
  Pending until shipped. The source's own order status, including 3,085 orders it never fulfilled,
  is kept in `cleaned/sales_orders.csv` and not used for the application.
- One warehouse, one currency, and each product has exactly one supplier.
- Two suppliers (Fabrikam, Litware) supply 141 of the 227 products, as in the source.
- Six source suppliers are service providers (courier, bank, insurance, ...) with no products. They
  are left out of `processed/erp/suppliers.csv` and remain in `cleaned/suppliers.csv`.
- Four products cost as much as or more than they sell for, as in the source.
- `processed/erp/` holds 231,412 sales rows. The backend loads whole tables per request, which is why
  the loader takes the last 12 months by default.

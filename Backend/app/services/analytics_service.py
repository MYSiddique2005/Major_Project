"""Analytics use cases: loads ERP data through the repositories and applies the
deterministic functions in app/analytics. These read-only methods are the natural
tools for the future LLM layer to call."""
from collections import defaultdict
from datetime import date, timedelta
from math import ceil

from app.analytics import forecasting, simulation, stock_risk, supplier_performance
from app.analytics.demand import demand_stats, weekly_units
from app.core.clock import Clock
from app.core.exceptions import NotFoundError
from app.models.entities import Product, PurchaseOrder, SalesOrder, Supplier
from app.models.enums import ProductStatus, PurchaseOrderStatus, RiskLevel, SupplierStatus
from app.repositories.base import (
    InventoryRepository,
    ProductRepository,
    PurchaseOrderRepository,
    SalesRepository,
    SupplierRepository,
)
from app.schemas.analytics import (
    DemandForecast,
    ForecastMethod,
    RiskAlert,
    StockPoint,
    StockRiskItem,
    SupplierPerformanceItem,
    WeeklyDemand,
    WhatIfOutcome,
    WhatIfRequest,
    WhatIfResult,
)
from app.utils.filters import matches_search

HISTORY_WEEKS = 26
MIN_DELIVERIES_FOR_OBSERVED_LEAD_TIME = 2
RISK_ORDER = [RiskLevel.CRITICAL, RiskLevel.HIGH, RiskLevel.MEDIUM, RiskLevel.LOW]
AWAITING_PLACEMENT = (PurchaseOrderStatus.PENDING_APPROVAL, PurchaseOrderStatus.APPROVED)


class AnalyticsService:
    def __init__(
        self,
        products: ProductRepository,
        inventory: InventoryRepository,
        sales: SalesRepository,
        purchase_orders: PurchaseOrderRepository,
        suppliers: SupplierRepository,
        clock: Clock | None = None,
    ):
        self._clock = clock or Clock()
        self._products = products
        self._inventory = inventory
        self._sales = sales
        self._purchase_orders = purchase_orders
        self._suppliers = suppliers

    # --- Stock risk -------------------------------------------------------

    def _lead_time(self, supplier: Supplier | None, observed: supplier_performance.SupplierPerformance | None):
        if supplier is None or observed is None:
            return 0.0, "supplier master data"
        if observed.deliveries_analyzed >= MIN_DELIVERIES_FOR_OBSERVED_LEAD_TIME:
            return observed.avg_lead_time_days, "observed deliveries"
        return supplier.avg_delivery_days, "supplier master data"

    def _suggested_supplier(self, product: Product, suppliers: dict[str, Supplier]) -> Supplier | None:
        primary = suppliers.get(product.supplier_id)
        if primary and primary.status == SupplierStatus.ACTIVE:
            return primary
        alternatives = [
            s for s in suppliers.values() if s.status == SupplierStatus.ACTIVE and product.id in s.product_ids
        ]
        return max(alternatives, key=lambda s: s.delivery_reliability, default=None)

    def _stock_risk_items(self, today: date, only_product_id: str | None = None) -> list[StockRiskItem]:
        suppliers = {s.id: s for s in self._suppliers.list()}
        sales_by_product: dict[str, list[SalesOrder]] = defaultdict(list)
        for order in self._sales.list():
            sales_by_product[order.product_id].append(order)
        orders_by_product: dict[str, list[PurchaseOrder]] = defaultdict(list)
        orders_by_supplier: dict[str, list[PurchaseOrder]] = defaultdict(list)
        for po in self._purchase_orders.list():
            orders_by_product[po.product_id].append(po)
            orders_by_supplier[po.supplier_id].append(po)
        stock_by_product: dict[str, list] = defaultdict(list)
        for record in self._inventory.list():
            stock_by_product[record.product_id].append(record)

        # Each supplier's delivery record is assessed once and shared by all its products.
        performance = {
            supplier_id: supplier_performance.assess(orders_by_supplier[supplier_id], today) for supplier_id in suppliers
        }

        items = []
        for product in self._products.list():
            if product.status != ProductStatus.ACTIVE or (only_product_id and product.id != only_product_id):
                continue
            records = stock_by_product[product.id]
            demand = demand_stats(sales_by_product[product.id], today)
            supplier = suppliers.get(product.supplier_id)
            observed = performance.get(product.supplier_id)
            lead_time, lead_source = self._lead_time(supplier, observed)

            in_transit = [
                po for po in orders_by_product[product.id]
                if po.status == PurchaseOrderStatus.ORDERED and po.actual_delivery is None
            ]
            due = [po for po in in_transit if po.expected_delivery >= today]
            position = stock_risk.StockPosition(
                on_hand=sum(r.current_stock for r in records),
                safety_stock=sum(r.safety_stock for r in records),
                avg_daily_demand=demand.avg_daily_demand,
                demand_trend_pct=demand.trend_pct,
                lead_time_days=lead_time,
                inbound_units=sum(po.quantity for po in due),
                next_inbound_date=min((po.expected_delivery for po in due), default=None),
                overdue_inbound_units=sum(po.quantity for po in in_transit if po.expected_delivery < today),
                awaiting_approval_units=sum(
                    po.quantity for po in orders_by_product[product.id] if po.status in AWAITING_PLACEMENT
                ),
                supplier_high_risk=observed is not None and observed.level == RiskLevel.HIGH,
            )
            risk = stock_risk.assess(position, today)
            suggested = self._suggested_supplier(product, suppliers) if risk.suggested_order_quantity else None
            items.append(
                StockRiskItem(
                    product_id=product.id,
                    product_name=product.name,
                    sku=product.sku,
                    category=product.category,
                    on_hand=position.on_hand,
                    safety_stock=position.safety_stock,
                    reorder_level=sum(r.reorder_level for r in records),
                    avg_daily_demand=demand.avg_daily_demand,
                    previous_avg_daily_demand=demand.previous_avg_daily_demand,
                    demand_trend_pct=demand.trend_pct,
                    days_of_cover=risk.days_of_cover,
                    projected_stockout_date=risk.projected_stockout_date,
                    supplier_id=product.supplier_id,
                    supplier_name=supplier.name if supplier else "Unknown supplier",
                    lead_time_days=lead_time,
                    lead_time_source=lead_source,
                    inbound_units=position.inbound_units,
                    next_inbound_date=position.next_inbound_date,
                    overdue_inbound_units=position.overdue_inbound_units,
                    awaiting_approval_units=position.awaiting_approval_units,
                    risk_level=risk.level,
                    drivers=risk.drivers,
                    reorder_point=risk.reorder_point,
                    suggested_order_quantity=risk.suggested_order_quantity,
                    suggested_supplier_id=suggested.id if suggested else None,
                    suggested_supplier_name=suggested.name if suggested else None,
                )
            )
        # Most urgent first; within a level, least cover first.
        items.sort(key=lambda i: (RISK_ORDER.index(i.risk_level), i.days_of_cover if i.days_of_cover is not None else 1e9))
        return items

    def list_stock_risk(
        self, level: RiskLevel | None = None, search: str | None = None, today: date | None = None
    ) -> list[StockRiskItem]:
        return [
            item
            for item in self._stock_risk_items(today or self._clock.today())
            if (level is None or item.risk_level == level)
            and matches_search(search, item.product_id, item.product_name, item.sku, item.category, item.supplier_name)
        ]

    def get_stock_risk(self, product_id: str, today: date | None = None) -> StockRiskItem:
        if self._products.get(product_id) is None:
            raise NotFoundError(f"Product '{product_id}' not found")
        items = self._stock_risk_items(today or self._clock.today(), only_product_id=product_id)
        if not items:
            raise NotFoundError(f"Product '{product_id}' is discontinued and is not analysed")
        return items[0]

    # --- Forecast ---------------------------------------------------------

    def get_forecast(
        self,
        product_id: str,
        horizon_weeks: int = 8,
        method: ForecastMethod | None = None,
        today: date | None = None,
    ) -> DemandForecast:
        today = today or self._clock.today()
        product = self._products.get(product_id)
        if product is None:
            raise NotFoundError(f"Product '{product_id}' not found")
        orders = [o for o in self._sales.list() if o.product_id == product_id]
        history = weekly_units(orders, today, HISTORY_WEEKS)
        values = [float(units) for _, units in history]

        chosen = method or forecasting.choose_method(values)
        predictions = forecasting.METHODS[chosen](values, horizon_weeks)
        return DemandForecast(
            product_id=product.id,
            product_name=product.name,
            method=chosen,
            method_selection="requested" if method else "lowest backtest error",
            history=[WeeklyDemand(week_start=start, units=units) for start, units in history],
            forecast=[
                WeeklyDemand(week_start=today + timedelta(days=7 * i), units=round(units, 1))
                for i, units in enumerate(predictions)
            ],
            avg_weekly_forecast=round(sum(predictions) / len(predictions), 1),
            backtest_wape={name: forecasting.backtest_wape(values, fn) for name, fn in forecasting.METHODS.items()},
        )

    # --- Suppliers --------------------------------------------------------

    def list_supplier_performance(self, today: date | None = None) -> list[SupplierPerformanceItem]:
        today = today or self._clock.today()
        orders_by_supplier: dict[str, list[PurchaseOrder]] = defaultdict(list)
        for po in self._purchase_orders.list():
            orders_by_supplier[po.supplier_id].append(po)
        items = []
        for supplier in self._suppliers.list():
            performance = supplier_performance.assess(orders_by_supplier[supplier.id], today)
            items.append(
                SupplierPerformanceItem(
                    supplier_id=supplier.id,
                    supplier_name=supplier.name,
                    status=supplier.status,
                    orders_total=performance.orders_total,
                    deliveries_analyzed=performance.deliveries_analyzed,
                    on_time_rate=performance.on_time_rate,
                    avg_delay_days=performance.avg_delay_days,
                    max_delay_days=performance.max_delay_days,
                    avg_lead_time_days=performance.avg_lead_time_days,
                    delay_trend=performance.delay_trend,
                    open_orders=performance.open_orders,
                    overdue_orders=performance.overdue_orders,
                    risk_level=performance.level,
                    drivers=performance.drivers,
                )
            )
        items.sort(key=lambda i: (RISK_ORDER.index(i.risk_level), i.supplier_name))
        return items

    # --- Alerts -----------------------------------------------------------

    def list_alerts(self, today: date | None = None) -> list[RiskAlert]:
        """High and Critical findings only, for the dashboard."""
        today = today or self._clock.today()
        urgent = (RiskLevel.CRITICAL, RiskLevel.HIGH)
        alerts = [
            RiskAlert(
                id=f"stock-{item.product_id}",
                category="Stockout Risk",
                severity=item.risk_level,
                title=f"{item.product_name}: {item.risk_level.lower()} stockout risk",
                message=" ".join(item.drivers),
                entity="product",
                entity_id=item.product_id,
            )
            for item in self._stock_risk_items(today)
            if item.risk_level in urgent
        ]
        alerts += [
            RiskAlert(
                id=f"supplier-{item.supplier_id}",
                category="Supplier Risk",
                severity=item.risk_level,
                title=f"{item.supplier_name}: {item.risk_level.lower()} delivery risk",
                message=" ".join(item.drivers),
                entity="supplier",
                entity_id=item.supplier_id,
            )
            for item in self.list_supplier_performance(today)
            if item.risk_level in urgent and item.status == SupplierStatus.ACTIVE
        ]
        return alerts

    # --- What-if ----------------------------------------------------------

    def run_what_if(self, request: WhatIfRequest, today: date | None = None) -> WhatIfResult:
        today = today or self._clock.today()
        item = self.get_stock_risk(request.product_id, today)
        tomorrow = today + timedelta(days=1)

        baseline_arrivals: dict[date, int] = defaultdict(int)
        scenario_arrivals: dict[date, int] = defaultdict(int)
        for po in self._purchase_orders.list():
            if (
                po.product_id == item.product_id
                and po.status == PurchaseOrderStatus.ORDERED
                and po.actual_delivery is None
                and po.expected_delivery >= today
            ):
                baseline_arrivals[max(po.expected_delivery, tomorrow)] += po.quantity
                shifted = po.expected_delivery + timedelta(days=request.lead_time_change_days)
                scenario_arrivals[max(shifted, tomorrow)] += po.quantity

        scenario_lead_time = max(1.0, item.lead_time_days + request.lead_time_change_days)
        if request.order_quantity:
            scenario_arrivals[today + timedelta(days=ceil(scenario_lead_time))] += request.order_quantity
        scenario_demand = round(item.avg_daily_demand * (1 + request.demand_change_pct / 100), 2)

        def outcome(daily_demand: float, lead_time: float, arrivals: dict[date, int]) -> WhatIfOutcome:
            projection = simulation.project(
                item.on_hand, daily_demand, arrivals, item.safety_stock, today, request.horizon_days
            )
            return WhatIfOutcome(
                daily_demand=daily_demand,
                lead_time_days=lead_time,
                stockout_date=projection.stockout_date,
                days_until_stockout=projection.days_until_stockout,
                days_below_safety=projection.days_below_safety,
                unmet_demand_units=projection.unmet_demand_units,
                ending_stock=projection.ending_stock,
                points=[StockPoint(date=day, stock=stock) for day, stock in projection.points],
            )

        assumptions = [
            "Demand is constant at the stated daily rate (baseline: average of the last 28 days).",
            "Demand that cannot be served from stock is lost, not back-ordered.",
            "Only purchase orders already placed with a supplier count as incoming stock; "
            "drafts and orders awaiting approval do not.",
        ]
        if item.overdue_inbound_units:
            assumptions.append(
                f"{item.overdue_inbound_units} overdue units are excluded because their arrival date is unknown."
            )
        return WhatIfResult(
            product_id=item.product_id,
            product_name=item.product_name,
            on_hand=item.on_hand,
            safety_stock=item.safety_stock,
            horizon_days=request.horizon_days,
            baseline=outcome(item.avg_daily_demand, item.lead_time_days, baseline_arrivals),
            scenario=outcome(scenario_demand, scenario_lead_time, scenario_arrivals),
            assumptions=assumptions,
        )

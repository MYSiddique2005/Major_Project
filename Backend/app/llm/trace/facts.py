"""The source of truth for each assertion: the system's own services, called the way the tools call them.

Every value comes from the same function the assistant's tools and the web pages use (the stock risk
assessment, the supplier performance analysis, the what-if simulation, the procurement service), so a
verdict compares the assistant's statement with exactly what the system shows. Lookups are cached for
the life of one verifier, which is one answer.
"""
from collections import Counter
from datetime import date, timedelta
from typing import Any

from pydantic import ValidationError

from app.core.clock import Clock
from app.core.exceptions import DomainError
from app.models.enums import PurchaseOrderStatus, RiskLevel, SalesStatus
from app.schemas.analytics import WhatIfRequest
from app.services.analytics_service import AnalyticsService
from app.services.inventory_service import InventoryService
from app.services.procurement_service import ProcurementService
from app.services.product_service import ProductService
from app.services.sales_service import SalesService
from app.services.supplier_service import SupplierService


class Missing(Exception):
    """The data cannot tell: no demand trend on too few orders, a product not analysed, no such scenario."""


class NoSuchSubject(Exception):
    """A well-formed ID that is not in the system."""


class FactSource:
    def __init__(
        self,
        analytics: AnalyticsService,
        products: ProductService,
        suppliers: SupplierService,
        inventory: InventoryService,
        procurement: ProcurementService,
        sales: SalesService,
        clock: Clock,
        separation_of_duties: bool = True,
    ):
        self.analytics, self.products, self.suppliers = analytics, products, suppliers
        self.inventory, self.procurement, self.sales, self.clock = inventory, procurement, sales, clock
        self.separation_of_duties = separation_of_duties
        self._cache: dict[tuple, Any] = {}

    def _cached(self, key: tuple, compute):
        if key not in self._cache:
            try:
                self._cache[key] = ("ok", compute())
            except (Missing, NoSuchSubject) as error:
                self._cache[key] = ("error", error)
        kind, value = self._cache[key]
        if kind == "error":
            raise value
        return value

    def today(self) -> date:
        return self.clock.today()

    # --- products --------------------------------------------------------------------------------------

    def product(self, product_id: str):
        def compute():
            try:
                return self.products.get_product(product_id)
            except DomainError as error:
                raise NoSuchSubject(f"no product {product_id}") from error
        return self._cached(("product", product_id), compute)

    def product_exists(self, product_id: str) -> bool:
        try:
            self.product(product_id)
            return True
        except NoSuchSubject:
            return False

    def stock_risk(self, product_id: str):
        def compute():
            self.product(product_id)  # a missing product is NoSuchSubject, not Missing
            try:
                return self.analytics.get_stock_risk(product_id)
            except DomainError as error:
                raise Missing(f"{product_id} is not analysed (discontinued)") from error
        return self._cached(("risk", product_id), compute)

    def warehouses(self, product_id: str) -> set[str]:
        def compute():
            self.product(product_id)
            return {record.warehouse for record in self.inventory.list_inventory(product_id=product_id)}
        return self._cached(("warehouses", product_id), compute)

    def forecast(self, product_id: str, horizon_weeks: int = 8):
        def compute():
            self.product(product_id)
            try:
                return self.analytics.get_forecast(product_id, horizon_weeks=horizon_weeks)
            except DomainError as error:
                raise Missing(str(error)) from error
        return self._cached(("forecast", product_id, horizon_weeks), compute)

    def what_if(self, product_id: str, demand_change_pct: float, delay_days: int, order_quantity: int, horizon_days: int):
        def compute():
            self.stock_risk(product_id)
            try:
                request = WhatIfRequest(product_id=product_id, demand_change_pct=demand_change_pct,
                                        lead_time_change_days=delay_days, order_quantity=order_quantity,
                                        horizon_days=horizon_days)
                return self.analytics.run_what_if(request)
            except (ValidationError, DomainError) as error:
                raise Missing(f"no such scenario: {error}") from error
        return self._cached(("what_if", product_id, demand_change_pct, delay_days, order_quantity, horizon_days), compute)

    def sales_totals(self, product_id: str, days: int) -> tuple[int, float]:
        """Units and revenue over the last `days` days, counted as the sales summary tool counts them."""
        def compute():
            self.product(product_id)
            since = self.today() - timedelta(days=days)
            orders = [order for order in self.sales.list_orders(product_id=product_id)
                      if order.order_date > since and order.status != SalesStatus.CANCELLED]
            return sum(order.quantity for order in orders), round(sum(order.total_amount for order in orders), 2)
        return self._cached(("sales", product_id, days), compute)

    def find_product(self, name: str) -> str | None:
        """The ID of the one product whose name is `name` (ignoring case), or None."""
        wanted = " ".join(name.lower().split())
        matches = [p.id for p in self.products.list_products(name) if " ".join(p.name.lower().split()) == wanted]
        return matches[0] if len(matches) == 1 else None

    # --- suppliers -------------------------------------------------------------------------------------

    def supplier(self, supplier_id: str):
        def compute():
            try:
                return self.suppliers.get_supplier(supplier_id)
            except DomainError as error:
                raise NoSuchSubject(f"no supplier {supplier_id}") from error
        return self._cached(("supplier", supplier_id), compute)

    def supplier_exists(self, supplier_id: str) -> bool:
        try:
            self.supplier(supplier_id)
            return True
        except NoSuchSubject:
            return False

    def supplier_performance(self, supplier_id: str):
        self.supplier(supplier_id)
        for item in self.all_supplier_performance():
            if item.supplier_id == supplier_id:
                return item
        raise Missing(f"no performance for {supplier_id}")

    def all_supplier_performance(self):
        return self._cached(("supplier_performance",), self.analytics.list_supplier_performance)

    def find_supplier(self, name: str) -> str | None:
        """The ID of the one supplier called `name`, or whose name before the comma is `name` ('Fabrikam')."""
        wanted = " ".join(name.lower().replace(",", " ").split())
        matches = []
        for supplier in self.suppliers.list_suppliers():
            full = " ".join(supplier.name.lower().replace(",", " ").split())
            short = " ".join(supplier.name.split(",")[0].lower().split())
            if wanted in (full, short):
                matches.append(supplier.id)
        return matches[0] if len(matches) == 1 else None

    # --- purchase orders -------------------------------------------------------------------------------

    def order(self, order_id: str):
        def compute():
            try:
                return self.procurement.get_order(order_id)
            except DomainError as error:
                raise NoSuchSubject(f"no purchase order {order_id}") from error
        return self._cached(("order", order_id), compute)

    def order_exists(self, order_id: str) -> bool:
        try:
            self.order(order_id)
            return True
        except NoSuchSubject:
            return False

    def order_overdue(self, order_id: str) -> bool:
        order = self.order(order_id)
        return (order.status == PurchaseOrderStatus.ORDERED and order.actual_delivery is None
                and order.expected_delivery < self.today())

    # --- counts ----------------------------------------------------------------------------------------

    def products_at_risk_level(self, level: str) -> int:
        def compute():
            return sum(1 for item in self.analytics.list_stock_risk() if item.risk_level == RiskLevel(level))
        return self._cached(("count_risk", level), compute)

    def suppliers_at_risk_level(self, level: str) -> int:
        return sum(1 for item in self.all_supplier_performance() if item.risk_level == RiskLevel(level))

    def stock_status_counts(self) -> Counter:
        def compute():
            return Counter(record.status.value for record in self.inventory.list_inventory())
        return self._cached(("stock_status_counts",), compute)

from collections import Counter
from datetime import date

from app.core.clock import Clock
from app.models.enums import PurchaseOrderStatus, SalesStatus, StockStatus, SupplierStatus
from app.repositories.base import PurchaseOrderRepository, SupplierRepository
from app.schemas.dashboard import DashboardSummary, SalesTrendPoint, StatusCount
from app.services.inventory_service import InventoryService
from app.services.sales_service import SalesService

TREND_MONTHS = 12


class DashboardService:
    def __init__(
        self,
        sales: SalesService,
        inventory: InventoryService,
        purchase_orders: PurchaseOrderRepository,
        suppliers: SupplierRepository,
        clock: Clock | None = None,
    ):
        self._clock = clock or Clock()
        self._sales = sales
        self._inventory = inventory
        self._purchase_orders = purchase_orders
        self._suppliers = suppliers

    def get_summary(self) -> DashboardSummary:
        sales = self._sales.get_stats()
        stock = self._inventory.get_stats()
        return DashboardSummary(
            total_sales=sales.total_revenue,
            total_orders=sales.total_orders,
            inventory_items=stock.total_items,
            low_stock_items=stock.low_stock,
            critical_stock_items=stock.critical,
            out_of_stock_items=stock.out_of_stock,
            pending_purchase_orders=sum(
                1 for po in self._purchase_orders.list() if po.status == PurchaseOrderStatus.PENDING_APPROVAL
            ),
            active_suppliers=sum(1 for s in self._suppliers.list() if s.status == SupplierStatus.ACTIVE),
        )

    def get_sales_trend(self) -> list[SalesTrendPoint]:
        """Monthly revenue and order count for the last 12 months (cancelled orders excluded)."""
        today = self._clock.today()
        year, month = today.year, today.month
        months = []
        for _ in range(TREND_MONTHS):
            months.append((year, month))
            year, month = (year, month - 1) if month > 1 else (year - 1, 12)
        months.reverse()

        revenue: Counter = Counter()
        orders: Counter = Counter()
        for order in self._sales.list_orders():
            if order.status == SalesStatus.CANCELLED:
                continue
            key = (order.order_date.year, order.order_date.month)
            revenue[key] += order.total_amount
            orders[key] += 1

        return [
            SalesTrendPoint(
                month=f"{y}-{m:02d}",
                label=date(y, m, 1).strftime("%b %Y"),
                revenue=round(revenue[(y, m)], 2),
                orders=orders[(y, m)],
            )
            for y, m in months
        ]

    def get_inventory_status(self) -> list[StatusCount]:
        counts = Counter(item.status for item in self._inventory.list_inventory())
        return [StatusCount(status=s, count=counts[s]) for s in StockStatus]

    def get_procurement_status(self) -> list[StatusCount]:
        counts = Counter(po.status for po in self._purchase_orders.list())
        return [StatusCount(status=s, count=counts[s]) for s in PurchaseOrderStatus]

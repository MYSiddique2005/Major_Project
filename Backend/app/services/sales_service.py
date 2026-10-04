from app.core.exceptions import NotFoundError
from app.models.entities import SalesOrder
from app.models.enums import SalesStatus
from app.repositories.base import ProductRepository, SalesRepository
from app.schemas.sales import SalesOrderResponse, SalesStats
from app.utils.filters import matches_search


class SalesService:
    def __init__(self, sales: SalesRepository, products: ProductRepository):
        self._sales = sales
        self._products = products

    def _to_response(self, order: SalesOrder) -> SalesOrderResponse:
        product = self._products.get(order.product_id)
        return SalesOrderResponse(
            **order.model_dump(),
            product_name=product.name if product else "Unknown product",
            sku=product.sku if product else "",
            total_amount=round(order.quantity * order.unit_price, 2),
        )

    def list_orders(
        self, search: str | None = None, status: SalesStatus | None = None, product_id: str | None = None
    ) -> list[SalesOrderResponse]:
        orders = (self._to_response(o) for o in self._sales.list())
        result = [
            o
            for o in orders
            if (status is None or o.status == status)
            and (product_id is None or o.product_id == product_id)
            and matches_search(search, o.id, o.customer, o.product_name, o.sku)
        ]
        return sorted(result, key=lambda o: (o.order_date, o.id), reverse=True)

    def get_order(self, order_id: str) -> SalesOrderResponse:
        order = self._sales.get(order_id)
        if order is None:
            raise NotFoundError(f"Sales order '{order_id}' not found")
        return self._to_response(order)

    def get_stats(self) -> SalesStats:
        orders = self.list_orders()
        billable = [o for o in orders if o.status != SalesStatus.CANCELLED]
        revenue = round(sum(o.total_amount for o in billable), 2)
        count = lambda s: sum(1 for o in orders if o.status == s)  # noqa: E731
        return SalesStats(
            total_revenue=revenue,
            total_orders=len(orders),
            average_order_value=round(revenue / len(billable), 2) if billable else 0.0,
            pending=count(SalesStatus.PENDING),
            processing=count(SalesStatus.PROCESSING),
            completed=count(SalesStatus.COMPLETED),
            cancelled=count(SalesStatus.CANCELLED),
        )

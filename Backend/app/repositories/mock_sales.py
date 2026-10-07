from app.mock_data.sales import SALES
from app.models.entities import SalesOrder
from app.repositories.base import InMemoryRepository, SalesRepository


class MockSalesRepository(InMemoryRepository[SalesOrder], SalesRepository):
    def __init__(self):
        super().__init__(SalesOrder, SALES, id_prefix="SO-")

    def latest_order_date(self):
        return max((order.order_date for order in self._items.values()), default=None)

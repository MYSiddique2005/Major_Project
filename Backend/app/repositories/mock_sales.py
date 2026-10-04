from app.mock_data.sales import SALES
from app.models.entities import SalesOrder
from app.repositories.base import InMemoryRepository, SalesRepository


class MockSalesRepository(InMemoryRepository[SalesOrder], SalesRepository):
    def __init__(self):
        super().__init__(SalesOrder, SALES, id_prefix="SO-")

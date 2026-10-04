from app.mock_data.procurement import PURCHASE_ORDERS
from app.models.entities import PurchaseOrder
from app.repositories.base import InMemoryRepository, PurchaseOrderRepository


class MockPurchaseOrderRepository(InMemoryRepository[PurchaseOrder], PurchaseOrderRepository):
    def __init__(self):
        super().__init__(PurchaseOrder, PURCHASE_ORDERS, id_prefix="PO-")

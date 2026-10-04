from app.mock_data.inventory import INVENTORY
from app.models.entities import InventoryRecord
from app.repositories.base import InMemoryRepository, InventoryRepository


class MockInventoryRepository(InMemoryRepository[InventoryRecord], InventoryRepository):
    def __init__(self):
        super().__init__(InventoryRecord, INVENTORY, id_prefix="INV-", id_width=3)

    def list_by_product(self, product_id: str) -> list[InventoryRecord]:
        return [record for record in self.list() if record.product_id == product_id]

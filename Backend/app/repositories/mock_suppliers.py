from app.mock_data.suppliers import SUPPLIERS
from app.models.entities import Supplier
from app.repositories.base import InMemoryRepository, SupplierRepository


class MockSupplierRepository(InMemoryRepository[Supplier], SupplierRepository):
    def __init__(self):
        super().__init__(Supplier, SUPPLIERS, id_prefix="S", id_width=3)

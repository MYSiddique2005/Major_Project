from app.mock_data.products import PRODUCTS
from app.models.entities import Product
from app.repositories.base import InMemoryRepository, ProductRepository


class MockProductRepository(InMemoryRepository[Product], ProductRepository):
    def __init__(self):
        super().__init__(Product, PRODUCTS, id_prefix="P", id_width=3)

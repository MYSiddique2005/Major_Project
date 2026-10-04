from app.core.exceptions import NotFoundError
from app.models.entities import Product
from app.models.enums import ProductStatus
from app.repositories.base import InventoryRepository, ProductRepository, SupplierRepository
from app.schemas.product import ProductResponse
from app.utils.filters import matches_search
from app.utils.stock import compute_stock_status


class ProductService:
    def __init__(self, products: ProductRepository, suppliers: SupplierRepository, inventory: InventoryRepository):
        self._products = products
        self._suppliers = suppliers
        self._inventory = inventory

    def _to_response(self, product: Product) -> ProductResponse:
        supplier = self._suppliers.get(product.supplier_id)
        records = self._inventory.list_by_product(product.id)
        current_stock = sum(r.current_stock for r in records)
        reorder_level = sum(r.reorder_level for r in records)
        safety_stock = sum(r.safety_stock for r in records)
        return ProductResponse(
            **product.model_dump(),
            supplier_name=supplier.name if supplier else "Unknown supplier",
            current_stock=current_stock,
            reorder_level=reorder_level,
            stock_status=compute_stock_status(current_stock, safety_stock, reorder_level),
        )

    def list_products(
        self, search: str | None = None, category: str | None = None, status: ProductStatus | None = None
    ) -> list[ProductResponse]:
        return [
            self._to_response(p)
            for p in self._products.list()
            if (category is None or p.category == category)
            and (status is None or p.status == status)
            and matches_search(search, p.id, p.sku, p.name, p.category)
        ]

    def get_product(self, product_id: str) -> ProductResponse:
        product = self._products.get(product_id)
        if product is None:
            raise NotFoundError(f"Product '{product_id}' not found")
        return self._to_response(product)

from app.core.exceptions import NotFoundError
from app.models.entities import InventoryRecord
from app.models.enums import StockStatus
from app.repositories.base import InventoryRepository, ProductRepository
from app.schemas.inventory import InventoryResponse, InventoryStats
from app.utils.filters import matches_search
from app.utils.stock import compute_stock_status


class InventoryService:
    def __init__(self, inventory: InventoryRepository, products: ProductRepository):
        self._inventory = inventory
        self._products = products

    def _to_response(self, record: InventoryRecord) -> InventoryResponse:
        product = self._products.get(record.product_id)
        return InventoryResponse(
            **record.model_dump(),
            product_name=product.name if product else "Unknown product",
            sku=product.sku if product else "",
            status=compute_stock_status(record.current_stock, record.safety_stock, record.reorder_level),
        )

    def list_inventory(
        self,
        search: str | None = None,
        status: StockStatus | None = None,
        warehouse: str | None = None,
        product_id: str | None = None,
    ) -> list[InventoryResponse]:
        records = self._inventory.list_by_product(product_id) if product_id else self._inventory.list()
        items = (self._to_response(r) for r in records)
        return [
            item
            for item in items
            if (status is None or item.status == status)
            and (warehouse is None or item.warehouse == warehouse)
            and matches_search(search, item.id, item.product_id, item.product_name, item.sku, item.warehouse)
        ]

    def get_item(self, inventory_id: str) -> InventoryResponse:
        record = self._inventory.get(inventory_id)
        if record is None:
            raise NotFoundError(f"Inventory record '{inventory_id}' not found")
        return self._to_response(record)

    def get_stats(self) -> InventoryStats:
        items = self.list_inventory()
        count = lambda s: sum(1 for item in items if item.status == s)  # noqa: E731
        return InventoryStats(
            total_items=len(items),
            total_units=sum(item.current_stock for item in items),
            in_stock=count(StockStatus.IN_STOCK),
            low_stock=count(StockStatus.LOW_STOCK),
            critical=count(StockStatus.CRITICAL),
            out_of_stock=count(StockStatus.OUT_OF_STOCK),
        )

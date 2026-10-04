from pydantic import BaseModel

from app.models.enums import ProductStatus, StockStatus


class ProductResponse(BaseModel):
    id: str
    sku: str
    name: str
    category: str
    supplier_id: str
    supplier_name: str
    price: float
    unit_cost: float
    current_stock: int  # total across all warehouses
    reorder_level: int  # total across all warehouses
    stock_status: StockStatus
    status: ProductStatus

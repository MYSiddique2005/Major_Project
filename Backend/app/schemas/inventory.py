from datetime import date

from pydantic import BaseModel

from app.models.enums import StockStatus


class InventoryResponse(BaseModel):
    id: str
    product_id: str
    product_name: str
    sku: str
    warehouse: str
    current_stock: int
    safety_stock: int
    reorder_level: int
    status: StockStatus
    last_updated: date


class InventoryStats(BaseModel):
    total_items: int
    total_units: int
    in_stock: int
    low_stock: int
    critical: int
    out_of_stock: int

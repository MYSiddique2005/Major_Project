"""Deterministic stock classification. Ordinary business logic - not AI."""
from app.models.enums import StockStatus


def compute_stock_status(current_stock: int, safety_stock: int, reorder_level: int) -> StockStatus:
    if current_stock == 0:
        return StockStatus.OUT_OF_STOCK
    if current_stock <= safety_stock * 0.5:
        return StockStatus.CRITICAL
    if current_stock <= reorder_level:
        return StockStatus.LOW_STOCK
    return StockStatus.IN_STOCK

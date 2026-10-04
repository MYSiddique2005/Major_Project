from pydantic import BaseModel

from app.models.enums import SupplierStatus


class SuppliedProduct(BaseModel):
    id: str
    name: str
    sku: str


class SupplierResponse(BaseModel):
    id: str
    name: str
    contact_name: str
    email: str
    phone: str
    country: str
    products_supplied: list[SuppliedProduct]
    avg_delivery_days: float
    delivery_reliability: float
    status: SupplierStatus

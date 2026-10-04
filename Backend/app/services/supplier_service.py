from app.core.exceptions import NotFoundError
from app.models.entities import Supplier
from app.models.enums import SupplierStatus
from app.repositories.base import ProductRepository, SupplierRepository
from app.schemas.supplier import SuppliedProduct, SupplierResponse
from app.utils.filters import matches_search


class SupplierService:
    def __init__(self, suppliers: SupplierRepository, products: ProductRepository):
        self._suppliers = suppliers
        self._products = products

    def _to_response(self, supplier: Supplier) -> SupplierResponse:
        products = [p for pid in supplier.product_ids if (p := self._products.get(pid))]
        return SupplierResponse(
            **supplier.model_dump(exclude={"product_ids"}),
            products_supplied=[SuppliedProduct(id=p.id, name=p.name, sku=p.sku) for p in products],
        )

    def list_suppliers(self, search: str | None = None, status: SupplierStatus | None = None) -> list[SupplierResponse]:
        return [
            self._to_response(s)
            for s in self._suppliers.list()
            if (status is None or s.status == status)
            and matches_search(search, s.id, s.name, s.contact_name, s.email, s.country)
        ]

    def get_supplier(self, supplier_id: str) -> SupplierResponse:
        supplier = self._suppliers.get(supplier_id)
        if supplier is None:
            raise NotFoundError(f"Supplier '{supplier_id}' not found")
        return self._to_response(supplier)

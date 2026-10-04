from fastapi import APIRouter, Depends

from app.api.deps import get_supplier_service
from app.models.enums import SupplierStatus
from app.schemas.supplier import SupplierResponse
from app.security.authorization import require_permission
from app.security.permissions import Permission
from app.services.supplier_service import SupplierService

router = APIRouter(
    prefix="/suppliers", tags=["Suppliers"], dependencies=[Depends(require_permission(Permission.SUPPLIERS_VIEW))]
)


@router.get("", response_model=list[SupplierResponse], summary="List suppliers")
def list_suppliers(
    search: str | None = None,
    status: SupplierStatus | None = None,
    service: SupplierService = Depends(get_supplier_service),
):
    return service.list_suppliers(search, status)


@router.get("/{supplier_id}", response_model=SupplierResponse, summary="Get a supplier")
def get_supplier(supplier_id: str, service: SupplierService = Depends(get_supplier_service)):
    return service.get_supplier(supplier_id)

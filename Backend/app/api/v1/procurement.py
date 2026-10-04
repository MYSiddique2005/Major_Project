from fastapi import APIRouter, Depends, Response, status

from app.api.deps import get_procurement_service
from app.models.entities import User
from app.models.enums import PurchaseOrderStatus
from app.schemas.procurement import PurchaseOrderCreate, PurchaseOrderResponse, PurchaseOrderUpdate
from app.security.authorization import require_permission
from app.security.permissions import Permission
from app.services.procurement_service import ProcurementService

router = APIRouter(prefix="/procurement", tags=["Procurement"])

can_view = require_permission(Permission.PROCUREMENT_VIEW)
can_create = require_permission(Permission.PROCUREMENT_CREATE)


@router.get(
    "", response_model=list[PurchaseOrderResponse], summary="List purchase orders (newest first)",
    dependencies=[Depends(can_view)],
)
def list_purchase_orders(
    search: str | None = None,
    status: PurchaseOrderStatus | None = None,
    supplier_id: str | None = None,
    product_id: str | None = None,
    service: ProcurementService = Depends(get_procurement_service),
):
    return service.list_orders(search, status, supplier_id, product_id)


@router.get(
    "/{po_id}", response_model=PurchaseOrderResponse, summary="Get a purchase order", dependencies=[Depends(can_view)]
)
def get_purchase_order(po_id: str, service: ProcurementService = Depends(get_procurement_service)):
    return service.get_order(po_id)


@router.post(
    "", response_model=PurchaseOrderResponse, status_code=status.HTTP_201_CREATED,
    summary="Create a draft purchase order",
)
def create_purchase_order(
    data: PurchaseOrderCreate,
    user: User = Depends(can_create),
    service: ProcurementService = Depends(get_procurement_service),
):
    return service.create_draft(data, user)


@router.put("/{po_id}", response_model=PurchaseOrderResponse, summary="Edit a draft purchase order")
def update_purchase_order(
    po_id: str,
    data: PurchaseOrderUpdate,
    user: User = Depends(can_create),
    service: ProcurementService = Depends(get_procurement_service),
):
    return service.update_draft(po_id, data, user)


@router.delete("/{po_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a draft purchase order")
def delete_purchase_order(
    po_id: str,
    user: User = Depends(can_create),
    service: ProcurementService = Depends(get_procurement_service),
):
    service.delete_draft(po_id, user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{po_id}/submit", response_model=PurchaseOrderResponse, summary="Submit a draft purchase order for approval"
)
def submit_purchase_order(
    po_id: str,
    user: User = Depends(can_create),
    service: ProcurementService = Depends(get_procurement_service),
):
    return service.submit_for_approval(po_id, user)

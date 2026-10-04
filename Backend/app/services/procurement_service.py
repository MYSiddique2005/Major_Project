from datetime import date, datetime, timedelta
from math import ceil

from app.core.exceptions import BusinessRuleError, NotFoundError
from app.models.entities import Approval, PurchaseOrder, User
from app.models.enums import ApprovalStatus, AuditAction, PurchaseOrderStatus, SupplierStatus
from app.repositories.base import (
    ApprovalRepository,
    ProductRepository,
    PurchaseOrderRepository,
    SupplierRepository,
    UnitOfWork,
)
from app.schemas.procurement import PurchaseOrderCreate, PurchaseOrderResponse, PurchaseOrderUpdate
from app.services.audit_service import AuditService
from app.utils.filters import matches_search

ENTITY = "Purchase Order"


class ProcurementService:
    """Purchase-order lifecycle: Draft -> Pending Approval -> Approved / Rejected.

    Every draft passes the same validation regardless of who (or, in a later
    phase, what) created it.
    """

    def __init__(
        self,
        purchase_orders: PurchaseOrderRepository,
        suppliers: SupplierRepository,
        products: ProductRepository,
        approvals: ApprovalRepository,
        audit: AuditService,
        uow: UnitOfWork,
    ):
        self._uow = uow
        self._purchase_orders = purchase_orders
        self._suppliers = suppliers
        self._products = products
        self._approvals = approvals
        self._audit = audit

    def to_response(self, po: PurchaseOrder) -> PurchaseOrderResponse:
        supplier = self._suppliers.get(po.supplier_id)
        product = self._products.get(po.product_id)
        return PurchaseOrderResponse(
            **po.model_dump(),
            supplier_name=supplier.name if supplier else "Unknown supplier",
            product_name=product.name if product else "Unknown product",
            total_amount=round(po.quantity * po.unit_price, 2),
        )

    def _get(self, po_id: str) -> PurchaseOrder:
        po = self._purchase_orders.get(po_id)
        if po is None:
            raise NotFoundError(f"Purchase order '{po_id}' not found")
        return po

    def _require_draft(self, po: PurchaseOrder, verb: str) -> None:
        if po.status != PurchaseOrderStatus.DRAFT:
            raise BusinessRuleError(f"Only draft purchase orders can be {verb}; {po.id} is '{po.status}'")

    def _validate(self, po: PurchaseOrder) -> None:
        supplier = self._suppliers.get(po.supplier_id)
        if supplier is None:
            raise BusinessRuleError(f"Supplier '{po.supplier_id}' does not exist")
        if supplier.status != SupplierStatus.ACTIVE:
            raise BusinessRuleError(f"Supplier '{supplier.name}' is inactive")
        if self._products.get(po.product_id) is None:
            raise BusinessRuleError(f"Product '{po.product_id}' does not exist")
        if po.product_id not in supplier.product_ids:
            raise BusinessRuleError(f"Supplier '{supplier.name}' does not supply product '{po.product_id}'")
        if po.expected_delivery < po.order_date:
            raise BusinessRuleError("Expected delivery cannot be before the order date")

    def list_orders(
        self,
        search: str | None = None,
        status: PurchaseOrderStatus | None = None,
        supplier_id: str | None = None,
        product_id: str | None = None,
    ) -> list[PurchaseOrderResponse]:
        orders = (self.to_response(po) for po in self._purchase_orders.list())
        result = [
            po
            for po in orders
            if (status is None or po.status == status)
            and (supplier_id is None or po.supplier_id == supplier_id)
            and (product_id is None or po.product_id == product_id)
            and matches_search(search, po.id, po.supplier_name, po.product_name)
        ]
        return sorted(result, key=lambda po: (po.order_date, po.id), reverse=True)

    def get_order(self, po_id: str) -> PurchaseOrderResponse:
        return self.to_response(self._get(po_id))

    def create_draft(self, data: PurchaseOrderCreate, user: User) -> PurchaseOrderResponse:
        supplier = self._suppliers.get(data.supplier_id)
        product = self._products.get(data.product_id)
        today = date.today()
        lead_days = ceil(supplier.avg_delivery_days) if supplier else 0
        po = PurchaseOrder(
            id="",
            supplier_id=data.supplier_id,
            product_id=data.product_id,
            quantity=data.quantity,
            unit_price=data.unit_price or (product.unit_cost if product else 0.0),
            order_date=today,
            expected_delivery=data.expected_delivery or today + timedelta(days=lead_days),
            status=PurchaseOrderStatus.DRAFT,
            reason=data.reason,
            created_by=user.username,
        )
        self._validate(po)
        po.id = self._purchase_orders.next_id()
        self._purchase_orders.add(po)
        self._audit.record(
            action=AuditAction.CREATE_PURCHASE_ORDER, entity=ENTITY, entity_id=po.id, user=user,
            description=f"Created draft for {po.quantity} x {po.product_id} from {po.supplier_id}",
        )
        self._uow.commit()
        return self.to_response(po)

    def update_draft(self, po_id: str, data: PurchaseOrderUpdate, user: User) -> PurchaseOrderResponse:
        po = self._get(po_id)
        self._require_draft(po, "edited")
        changes = data.model_dump(exclude_unset=True, exclude_none=True)
        po = po.model_copy(update=changes)
        self._validate(po)
        self._purchase_orders.update(po)
        self._audit.record(
            action=AuditAction.UPDATE_PURCHASE_ORDER, entity=ENTITY, entity_id=po.id, user=user,
            description=f"Updated {', '.join(sorted(changes)) or 'nothing'}",
        )
        self._uow.commit()
        return self.to_response(po)

    def delete_draft(self, po_id: str, user: User) -> None:
        po = self._get(po_id)
        self._require_draft(po, "deleted")
        self._purchase_orders.delete(po.id)
        self._audit.record(
            action=AuditAction.DELETE_PURCHASE_ORDER, entity=ENTITY, entity_id=po.id, user=user,
            description="Deleted draft purchase order",
        )
        self._uow.commit()

    def submit_for_approval(self, po_id: str, user: User) -> PurchaseOrderResponse:
        po = self._get(po_id)
        self._require_draft(po, "submitted")
        self._validate(po)
        po.status = PurchaseOrderStatus.PENDING_APPROVAL
        self._purchase_orders.update(po)
        self._approvals.add(
            Approval(
                id=self._approvals.next_id(),
                purchase_order_id=po.id,
                requested_by=user.username,
                requested_at=datetime.now(),
                reason=po.reason,
                status=ApprovalStatus.PENDING,
            )
        )
        self._audit.record(
            action=AuditAction.SUBMIT_FOR_APPROVAL, entity=ENTITY, entity_id=po.id, user=user,
            description="Submitted for approval",
        )
        self._uow.commit()
        return self.to_response(po)

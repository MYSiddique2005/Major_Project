from datetime import datetime

from app.core.exceptions import BusinessRuleError, NotFoundError
from app.models.entities import Approval, User
from app.models.enums import ApprovalStatus, AuditAction, PurchaseOrderStatus
from app.repositories.base import ApprovalRepository, PurchaseOrderRepository, UnitOfWork
from app.schemas.approval import ApprovalResponse
from app.services.audit_service import AuditService
from app.services.procurement_service import ENTITY, ProcurementService


class ApprovalService:
    """Human approval gate. A purchase order only becomes Approved through here."""

    def __init__(
        self,
        approvals: ApprovalRepository,
        purchase_orders: PurchaseOrderRepository,
        procurement: ProcurementService,
        audit: AuditService,
        uow: UnitOfWork,
        separation_of_duties: bool = True,
    ):
        self._separation_of_duties = separation_of_duties
        self._uow = uow
        self._approvals = approvals
        self._purchase_orders = purchase_orders
        self._procurement = procurement
        self._audit = audit

    def _get(self, approval_id: str) -> Approval:
        approval = self._approvals.get(approval_id)
        if approval is None:
            raise NotFoundError(f"Approval '{approval_id}' not found")
        return approval

    def _to_response(self, approval: Approval) -> ApprovalResponse:
        po = self._purchase_orders.get(approval.purchase_order_id)
        if po is None:
            raise NotFoundError(f"Purchase order '{approval.purchase_order_id}' not found")
        return ApprovalResponse(**approval.model_dump(), purchase_order=self._procurement.to_response(po))

    def list_approvals(self, status: ApprovalStatus | None = None) -> list[ApprovalResponse]:
        approvals = [a for a in self._approvals.list() if status is None or a.status == status]
        approvals.sort(key=lambda a: a.requested_at, reverse=True)
        return [self._to_response(a) for a in approvals]

    def get_approval(self, approval_id: str) -> ApprovalResponse:
        return self._to_response(self._get(approval_id))

    def approve(self, approval_id: str, user: User, comment: str | None = None) -> ApprovalResponse:
        return self._decide(approval_id, user, comment, approved=True)

    def reject(self, approval_id: str, user: User, comment: str | None = None) -> ApprovalResponse:
        return self._decide(approval_id, user, comment, approved=False)

    def _decide(self, approval_id: str, user: User, comment: str | None, *, approved: bool) -> ApprovalResponse:
        approval = self._get(approval_id)
        if approval.status != ApprovalStatus.PENDING:
            raise BusinessRuleError(f"Approval {approval.id} has already been {approval.status.lower()}")
        po = self._purchase_orders.get(approval.purchase_order_id)
        if po is None or po.status != PurchaseOrderStatus.PENDING_APPROVAL:
            raise BusinessRuleError(f"Purchase order {approval.purchase_order_id} is not pending approval")
        # Separation of duties: an order needs a second person to approve it. This also covers a draft the
        # AI assistant prepared for someone, which is created in that person's name. Rejecting is allowed.
        if approved and self._separation_of_duties and user.username in (po.created_by, approval.requested_by):
            raise BusinessRuleError(
                f"You created or submitted {po.id}, so another approver must approve it. You may still reject it."
            )

        approval.status = ApprovalStatus.APPROVED if approved else ApprovalStatus.REJECTED
        approval.decided_by = user.username
        approval.decided_at = datetime.now()
        approval.comment = comment
        po.status = PurchaseOrderStatus.APPROVED if approved else PurchaseOrderStatus.REJECTED
        self._approvals.update(approval)
        self._purchase_orders.update(po)

        self._audit.record(
            action=AuditAction.APPROVE_PURCHASE_ORDER if approved else AuditAction.REJECT_PURCHASE_ORDER,
            entity=ENTITY, entity_id=po.id, user=user,
            description=comment or ("Purchase order approved" if approved else "Purchase order rejected"),
        )
        self._uow.commit()
        return self._to_response(approval)

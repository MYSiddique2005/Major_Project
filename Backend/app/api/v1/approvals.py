from fastapi import APIRouter, Depends

from app.api.deps import get_approval_service
from app.models.entities import User
from app.models.enums import ApprovalStatus
from app.schemas.approval import ApprovalDecision, ApprovalResponse
from app.security.authorization import require_permission
from app.security.permissions import Permission
from app.services.approval_service import ApprovalService

router = APIRouter(prefix="/approvals", tags=["Approvals"])

can_approve = require_permission(Permission.PROCUREMENT_APPROVE)


@router.get(
    "", response_model=list[ApprovalResponse], summary="List approval requests (newest first)",
    dependencies=[Depends(can_approve)],
)
def list_approvals(status: ApprovalStatus | None = None, service: ApprovalService = Depends(get_approval_service)):
    return service.list_approvals(status)


@router.get(
    "/{approval_id}", response_model=ApprovalResponse, summary="Get an approval request",
    dependencies=[Depends(can_approve)],
)
def get_approval(approval_id: str, service: ApprovalService = Depends(get_approval_service)):
    return service.get_approval(approval_id)


@router.post("/{approval_id}/approve", response_model=ApprovalResponse, summary="Approve a pending purchase order")
def approve(
    approval_id: str,
    decision: ApprovalDecision | None = None,
    user: User = Depends(can_approve),
    service: ApprovalService = Depends(get_approval_service),
):
    return service.approve(approval_id, user, decision.comment if decision else None)


@router.post("/{approval_id}/reject", response_model=ApprovalResponse, summary="Reject a pending purchase order")
def reject(
    approval_id: str,
    decision: ApprovalDecision | None = None,
    user: User = Depends(can_approve),
    service: ApprovalService = Depends(get_approval_service),
):
    return service.reject(approval_id, user, decision.comment if decision else None)

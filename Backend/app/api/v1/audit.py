from fastapi import APIRouter, Depends

from app.api.deps import get_audit_service
from app.models.enums import AuditStatus
from app.schemas.audit import AuditLogResponse
from app.security.authorization import require_permission
from app.security.permissions import Permission
from app.services.audit_service import AuditService

router = APIRouter(
    prefix="/audit-logs", tags=["Audit Logs"], dependencies=[Depends(require_permission(Permission.AUDIT_VIEW))]
)


@router.get("", response_model=list[AuditLogResponse], summary="List audit events (newest first)")
def list_audit_logs(
    search: str | None = None,
    action: str | None = None,
    status: AuditStatus | None = None,
    service: AuditService = Depends(get_audit_service),
):
    return service.list_logs(search, action, status)

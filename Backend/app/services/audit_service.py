from datetime import datetime

from app.models.entities import AuditLog, User
from app.models.enums import AuditStatus
from app.repositories.base import AuditLogRepository
from app.utils.filters import matches_search


class AuditService:
    def __init__(self, audit_logs: AuditLogRepository):
        self._audit_logs = audit_logs

    def record(
        self,
        *,
        action: str,
        entity: str,
        entity_id: str,
        description: str,
        user: User | None = None,
        username: str | None = None,
        status: AuditStatus = AuditStatus.SUCCESS,
    ) -> AuditLog:
        event = AuditLog(
            id=self._audit_logs.next_id(),
            timestamp=datetime.now(),
            user_id=user.id if user else "unknown",
            username=user.username if user else (username or "unknown"),
            action=action,
            entity=entity,
            entity_id=entity_id,
            status=status,
            description=description,
        )
        return self._audit_logs.add(event)

    def list_logs(
        self, search: str | None = None, action: str | None = None, status: AuditStatus | None = None
    ) -> list[AuditLog]:
        logs = [
            log
            for log in self._audit_logs.list()
            if (action is None or log.action == action)
            and (status is None or log.status == status)
            and matches_search(search, log.username, log.action, log.entity, log.entity_id, log.description)
        ]
        return sorted(logs, key=lambda log: log.timestamp, reverse=True)

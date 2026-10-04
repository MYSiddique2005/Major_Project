from app.mock_data.audit_logs import AUDIT_LOGS
from app.models.entities import AuditLog
from app.repositories.base import AuditLogRepository, InMemoryRepository


class MockAuditLogRepository(InMemoryRepository[AuditLog], AuditLogRepository):
    def __init__(self):
        super().__init__(AuditLog, AUDIT_LOGS, id_prefix="AUD-", id_width=5)

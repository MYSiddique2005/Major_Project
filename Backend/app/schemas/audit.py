from datetime import datetime

from pydantic import BaseModel

from app.models.enums import AuditStatus


class AuditLogResponse(BaseModel):
    id: str
    timestamp: datetime
    user_id: str
    username: str
    action: str
    entity: str
    entity_id: str
    status: AuditStatus
    description: str

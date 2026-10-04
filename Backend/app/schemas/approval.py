from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import ApprovalStatus
from app.schemas.procurement import PurchaseOrderResponse


class ApprovalResponse(BaseModel):
    id: str
    purchase_order_id: str
    purchase_order: PurchaseOrderResponse
    requested_by: str
    requested_at: datetime
    reason: str
    status: ApprovalStatus
    decided_by: str | None
    decided_at: datetime | None
    comment: str | None


class ApprovalDecision(BaseModel):
    comment: str | None = Field(default=None, max_length=500)

"""Contracts for the proactive AI insights."""
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import InsightStatus, RiskLevel, ScanStatus


class InsightResponse(BaseModel):
    id: str
    scan_id: str
    created_at: datetime
    subject_type: str
    subject_id: str
    subject_name: str
    severity: RiskLevel = Field(description="Set by the analytics, not by the model")
    headline: str
    explanation: str
    action: str
    product_id: str | None
    product_name: str | None
    supplier_id: str | None
    supplier_name: str | None
    quantity: int | None
    system_quantity: int | None = Field(description="Quantity the reorder rule gives")
    evidence: list[dict]
    checks: dict = Field(description="Results of the server's checks on the model's text")
    status: InsightStatus
    reviewed_by: str | None
    reviewed_at: datetime | None


class ScanResponse(BaseModel):
    id: str
    started_at: datetime
    finished_at: datetime | None
    trigger: str
    status: ScanStatus
    findings: int
    insights: int
    message: str
    provider: str | None
    model: str | None

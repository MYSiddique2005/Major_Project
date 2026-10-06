"""Enumerations shared by domain entities and API schemas."""
from enum import StrEnum


class Role(StrEnum):
    ADMIN = "ADMIN"
    INVENTORY_MANAGER = "INVENTORY_MANAGER"
    PROCUREMENT_MANAGER = "PROCUREMENT_MANAGER"
    EMPLOYEE = "EMPLOYEE"


class SalesStatus(StrEnum):
    PENDING = "Pending"
    PROCESSING = "Processing"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"


class StockStatus(StrEnum):
    IN_STOCK = "In Stock"
    LOW_STOCK = "Low Stock"
    CRITICAL = "Critical"
    OUT_OF_STOCK = "Out of Stock"


class PurchaseOrderStatus(StrEnum):
    DRAFT = "Draft"
    PENDING_APPROVAL = "Pending Approval"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    ORDERED = "Ordered"
    DELIVERED = "Delivered"
    CANCELLED = "Cancelled"


class PurchaseOrderOrigin(StrEnum):
    """Who or what prepared a purchase order. An AI origin never skips validation or approval."""

    MANUAL = "Manual"
    AI_ASSISTANT = "AI Assistant"  # drafted from a recommendation in the chat
    AI_INSIGHT = "AI Insight"  # drafted from a proactive insight


class SupplierStatus(StrEnum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"


class ProductStatus(StrEnum):
    ACTIVE = "Active"
    DISCONTINUED = "Discontinued"


class ApprovalStatus(StrEnum):
    PENDING = "Pending"
    APPROVED = "Approved"
    REJECTED = "Rejected"


class RiskLevel(StrEnum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class InsightStatus(StrEnum):
    NEW = "New"
    ACKNOWLEDGED = "Acknowledged"
    DISMISSED = "Dismissed"
    SUPERSEDED = "Superseded"  # replaced by a newer insight about the same product or supplier


class ScanStatus(StrEnum):
    RUNNING = "Running"
    COMPLETED = "Completed"
    FAILED = "Failed"


class AuditStatus(StrEnum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class AuditAction(StrEnum):
    LOGIN = "LOGIN"
    CREATE_PURCHASE_ORDER = "CREATE_PURCHASE_ORDER"
    UPDATE_PURCHASE_ORDER = "UPDATE_PURCHASE_ORDER"
    DELETE_PURCHASE_ORDER = "DELETE_PURCHASE_ORDER"
    SUBMIT_FOR_APPROVAL = "SUBMIT_FOR_APPROVAL"
    APPROVE_PURCHASE_ORDER = "APPROVE_PURCHASE_ORDER"
    REJECT_PURCHASE_ORDER = "REJECT_PURCHASE_ORDER"
    AI_QUERY = "AI_QUERY"
    AI_SCAN = "AI_SCAN"
    REVIEW_AI_INSIGHT = "REVIEW_AI_INSIGHT"

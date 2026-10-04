"""Role -> permission mapping. The single source of truth for RBAC.

The backend enforces these on every endpoint; the frontend receives the
current user's permission list from /auth/me and uses it only to tailor the UI.
"""
from enum import StrEnum

from app.models.enums import Role


class Permission(StrEnum):
    DASHBOARD_VIEW = "dashboard:view"
    SALES_VIEW = "sales:view"
    INVENTORY_VIEW = "inventory:view"
    PRODUCTS_VIEW = "products:view"
    SUPPLIERS_VIEW = "suppliers:view"
    PROCUREMENT_VIEW = "procurement:view"
    PROCUREMENT_CREATE = "procurement:create"
    PROCUREMENT_APPROVE = "procurement:approve"
    ANALYTICS_VIEW = "analytics:view"
    AUDIT_VIEW = "audit:view"
    USERS_MANAGE = "users:manage"
    AI_USE = "ai:use"


_READ_ONLY_ERP = {
    Permission.DASHBOARD_VIEW,
    Permission.SALES_VIEW,
    Permission.INVENTORY_VIEW,
    Permission.PRODUCTS_VIEW,
    Permission.SUPPLIERS_VIEW,
}

ROLE_PERMISSIONS: dict[Role, set[Permission]] = {
    Role.ADMIN: set(Permission),
    Role.INVENTORY_MANAGER: _READ_ONLY_ERP | {Permission.ANALYTICS_VIEW, Permission.AI_USE},
    Role.PROCUREMENT_MANAGER: {
        Permission.DASHBOARD_VIEW,
        Permission.INVENTORY_VIEW,
        Permission.PRODUCTS_VIEW,  # needed to pick products when drafting purchase orders
        Permission.SUPPLIERS_VIEW,
        Permission.PROCUREMENT_VIEW,
        Permission.PROCUREMENT_CREATE,
        Permission.PROCUREMENT_APPROVE,
        Permission.ANALYTICS_VIEW,
        Permission.AI_USE,
    },
    Role.EMPLOYEE: set(_READ_ONLY_ERP),
}


def permissions_for(role: Role) -> list[str]:
    return sorted(ROLE_PERMISSIONS.get(role, set()))


def has_permission(role: Role, permission: Permission) -> bool:
    return permission in ROLE_PERMISSIONS.get(role, set())

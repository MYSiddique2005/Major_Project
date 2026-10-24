"""The company's rules as values: thresholds and windows read from the constants the code applies, and
what each role and the assistant may do, read from the permission map.

Nothing here is written twice: a rule key's value is the constant itself, so a statement about a rule
is checked against exactly what the system does.
"""
from functools import lru_cache

from app.analytics import demand as D
from app.analytics import forecasting as F
from app.analytics import stock_risk as S
from app.analytics import supplier_performance as P
from app.models.enums import Role
from app.schemas.analytics import WhatIfRequest
from app.schemas.procurement import MAX_ORDER_QUANTITY
from app.security.permissions import Permission, has_permission
from app.services import analytics_service as A
from app.utils.stock import CRITICAL_FRACTION_OF_SAFETY_STOCK


@lru_cache(maxsize=1)
def rules() -> dict[str, tuple[float | bool, str]]:
    """key: (value, what it is). Built on first use: the tool limits live in app.llm.tools, which itself
    uses the verifier, so importing it at module load would be circular."""
    from app.llm.tools import MAX_DRAFTS_PER_REQUEST, MAX_ROWS

    return {**_RULES, "max_drafts_per_message": (MAX_DRAFTS_PER_REQUEST,
                                                 "the most draft purchase orders the assistant creates for one message"),
            "max_rows_per_list": (MAX_ROWS, "the most rows a list tool returns")}



# Numbers are in the unit the key names.
_RULES: dict[str, tuple[float | bool, str]] = {
    "demand_window_days": (D.TREND_WINDOW_DAYS, "days over which average daily demand is computed"),
    "min_orders_for_trend": (D.MIN_ORDERS_FOR_TREND, "orders each period needs before a demand trend is given"),
    "rising_sharply_pct": (S.RISING_DEMAND_PCT, "demand trend at or above which demand counts as rising sharply"),
    "review_period_days": (S.REVIEW_PERIOD_DAYS, "review period added to the lead time in the reorder target"),
    "review_buffer_days": (S.REVIEW_BUFFER_DAYS, "days added to the lead time in the Medium stockout risk rule"),
    "order_multiple_units": (S.ORDER_MULTIPLE, "suggested order quantities are rounded up to a multiple of this"),
    "critical_stock_fraction": (CRITICAL_FRACTION_OF_SAFETY_STOCK,
                                "stock at or below this fraction of safety stock has Critical stock status"),
    "supplier_high_on_time_below_pct": (P.HIGH_RISK_ON_TIME_BELOW_PCT, "on-time rate below which a supplier is High risk"),
    "supplier_medium_on_time_below_pct": (P.MEDIUM_RISK_ON_TIME_BELOW_PCT, "on-time rate below which a supplier is Medium risk"),
    "supplier_medium_avg_delay_days": (P.MEDIUM_RISK_AVG_DELAY_DAYS, "average delay at or above which a supplier is Medium risk"),
    "supplier_high_worsening_delay_days": (P.HIGH_RISK_WORSENING_AVG_DELAY_DAYS,
                                           "average delay at or above which worsening delays make a supplier High risk"),
    "min_deliveries_for_on_time_rate": (P.MIN_DELIVERIES_FOR_RATE, "deliveries needed before the on-time rate is used"),
    "supplier_trend_window_days": (P.TREND_WINDOW_DAYS, "days in each period compared for the supplier delay trend"),
    "delay_trend_tolerance_days": (P.TREND_TOLERANCE_DAYS, "difference in average delay that counts as a trend"),
    "min_orders_per_trend_window": (P.MIN_ORDERS_PER_TREND_WINDOW, "orders each period needs for a delay trend"),
    "moving_average_weeks": (F.MOVING_AVERAGE_WEEKS, "weeks averaged by the moving_average forecast"),
    "trend_forecast_weeks": (F.TREND_WEEKS, "weeks fitted by the linear_trend forecast"),
    "backtest_weeks": (F.BACKTEST_WEEKS, "weeks used to compare the forecast methods"),
    "forecast_history_weeks": (A.HISTORY_WEEKS, "weeks of sales history the forecast uses"),
    "min_deliveries_for_observed_lead_time": (A.MIN_DELIVERIES_FOR_OBSERVED_LEAD_TIME,
                                              "deliveries needed before the observed lead time is used"),
    "max_order_quantity": (MAX_ORDER_QUANTITY, "the most units one purchase order may carry"),
    "what_if_default_horizon_days": (WhatIfRequest.model_fields["horizon_days"].default, "default what-if horizon in days"),
}

# What a role may do, by the permission it needs.
ROLE_ACTIONS: dict[str, Permission] = {
    "view_sales": Permission.SALES_VIEW,
    "view_inventory": Permission.INVENTORY_VIEW,
    "view_products": Permission.PRODUCTS_VIEW,
    "view_suppliers": Permission.SUPPLIERS_VIEW,
    "view_purchase_orders": Permission.PROCUREMENT_VIEW,
    "create_purchase_order": Permission.PROCUREMENT_CREATE,
    "edit_purchase_order": Permission.PROCUREMENT_CREATE,
    "submit_purchase_order": Permission.PROCUREMENT_CREATE,
    "approve_purchase_order": Permission.PROCUREMENT_APPROVE,
    "reject_purchase_order": Permission.PROCUREMENT_APPROVE,
    "view_analytics": Permission.ANALYTICS_VIEW,
    "view_audit_log": Permission.AUDIT_VIEW,
    "use_ai_assistant": Permission.AI_USE,
    "manage_users": Permission.USERS_MANAGE,
}
# The assistant reads data and may prepare a draft; everything else is left to people.
ASSISTANT_ACTIONS: dict[str, bool] = {
    "read_data": True,
    "draft_purchase_order": True,  # only for a user who may create purchase orders
    "edit_purchase_order": False,
    "submit_purchase_order": False,
    "approve_purchase_order": False,
    "reject_purchase_order": False,
    "cancel_purchase_order": False,
    "delete_purchase_order": False,
    "place_order": False,
    "show_data_outside_role": False,
}
ACTIONS = tuple(dict.fromkeys([*ROLE_ACTIONS, "approve_own_purchase_order", *ASSISTANT_ACTIONS]))

ROLE_NAMES: dict[str, Role] = {
    "admin": Role.ADMIN, "admins": Role.ADMIN, "administrator": Role.ADMIN, "administrators": Role.ADMIN,
    "inventory manager": Role.INVENTORY_MANAGER, "inventory managers": Role.INVENTORY_MANAGER,
    "procurement manager": Role.PROCUREMENT_MANAGER, "procurement managers": Role.PROCUREMENT_MANAGER,
    "employee": Role.EMPLOYEE, "employees": Role.EMPLOYEE,
}


def resolve_role(text: str) -> Role | None:
    cleaned = " ".join(text.strip().lower().replace("_", " ").split())
    cleaned = cleaned.removeprefix("the ").removeprefix("a ").removeprefix("an ")
    if cleaned in ROLE_NAMES:
        return ROLE_NAMES[cleaned]
    try:
        return Role(text.strip().upper().replace(" ", "_"))
    except ValueError:
        return None


def role_can(role: Role, action: str, separation_of_duties: bool) -> bool | None:
    """Whether the role may do the action; None for an action the rules do not define for roles."""
    if action == "approve_own_purchase_order":
        return has_permission(role, Permission.PROCUREMENT_APPROVE) and not separation_of_duties
    permission = ROLE_ACTIONS.get(action)
    return None if permission is None else has_permission(role, permission)


def assistant_can(action: str, user_role: Role | None) -> bool | None:
    """Whether the assistant may do the action; drafting also needs a user who may create orders."""
    if action not in ASSISTANT_ACTIONS:
        return None
    if action == "draft_purchase_order" and user_role is not None:
        return has_permission(user_role, Permission.PROCUREMENT_CREATE)
    return ASSISTANT_ACTIONS[action]

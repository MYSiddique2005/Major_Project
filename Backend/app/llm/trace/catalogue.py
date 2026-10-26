"""The assertion language: every attribute a statement can be checked on, and what kind of value it has.

Three families, by where the truth comes from:
    state    - what the database records now (stock, orders, suppliers, prices, sales)
    derived  - what the analytics compute from it (risk levels, reorder point and quantity, cover,
               forecasts, what-if projections, counts by risk level)
    policy   - what the company's rules say (thresholds and windows from the code's constants, what each
               role and the assistant itself may do)

The same list is shown to the extracting model and drives the verifier, so the two cannot drift apart.
"""
from dataclasses import dataclass, field
from typing import Literal

from app.models.enums import PurchaseOrderStatus, RiskLevel, StockStatus, SupplierStatus
from app.security.permissions import Permission

Family = Literal["state", "derived", "policy"]
Subject = Literal["product", "supplier", "order", "role", "assistant", "rule", "risk_level", "stock_status"]
Kind = Literal["number", "date", "category", "name", "entity", "boolean", "action", "policy"]

SCENARIO = ("demand_change_pct", "delay_days", "order_quantity", "horizon_days")
STOCKOUT_LEVELS = tuple(level.value for level in (RiskLevel.CRITICAL, RiskLevel.HIGH, RiskLevel.MEDIUM, RiskLevel.LOW))
SUPPLIER_LEVELS = tuple(level.value for level in (RiskLevel.HIGH, RiskLevel.MEDIUM, RiskLevel.LOW))
STOCK_STATUSES = tuple(status.value for status in StockStatus)
ORDER_STATUSES = tuple(status.value for status in PurchaseOrderStatus)
SUPPLIER_STATUSES = tuple(status.value for status in SupplierStatus)
DELAY_TRENDS = ("worsening", "improving", "stable")
FORECAST_METHODS = ("moving_average", "linear_trend")


@dataclass(frozen=True)
class Attribute:
    name: str
    family: Family
    subject: Subject
    kind: Kind
    description: str
    choices: tuple[str, ...] = ()
    entity: Literal["product", "supplier"] | None = None  # for kind "entity": what the value names
    uses: tuple[str, ...] = ()  # optional assertion fields the attribute reads
    permission: Permission | None = None  # a role without it cannot have the statement checked
    ordered: bool = field(default=False)  # categories with an order (risk levels) allow lt/gt
    recorded: bool = field(default=False)  # a recorded fact (an order's history), checkable in the past tense too


def _a(*args, **kwargs) -> Attribute:
    return Attribute(*args, **kwargs)


ATTRIBUTES: tuple[Attribute, ...] = (
    # --- product: what the database records ---------------------------------------------------------
    _a("product_exists", "state", "product", "boolean", "The product is in the system (true) or not (false)"),
    _a("stock_on_hand", "state", "product", "number", "Units on hand now, all warehouses (0 = out of stock)"),
    _a("safety_stock", "state", "product", "number", "Safety stock in units"),
    _a("reorder_level", "state", "product", "number", "Reorder level on the stock record, in units"),
    _a("stock_status", "state", "product", "category", "Stock status shown on the Inventory page", STOCK_STATUSES),
    _a("warehouse", "state", "product", "name", "A warehouse where the product is held (eq: held there; ne: not held there)"),
    _a("units_on_order", "state", "product", "number", "Units on Ordered purchase orders not yet delivered and not overdue"),
    _a("overdue_units", "state", "product", "number", "Units on Ordered purchase orders past their expected delivery date"),
    _a("units_awaiting_approval", "state", "product", "number", "Units on purchase orders Pending Approval or Approved"),
    _a("next_delivery_date", "state", "product", "date", "Expected date of the next delivery on order"),
    _a("primary_supplier", "state", "product", "entity", "The product's primary supplier", entity="supplier"),
    _a("supplied_by", "state", "product", "entity", "A supplier that supplies the product (eq: it does; ne: it does not)",
       entity="supplier"),
    _a("category", "state", "product", "name", "Product category"),
    _a("price", "state", "product", "number", "List price per unit"),
    _a("unit_cost", "state", "product", "number", "Unit cost"),
    _a("units_sold", "state", "product", "number", "Units sold over the last period_days days (Cancelled orders excluded)",
       uses=("period_days",), permission=Permission.SALES_VIEW),
    _a("revenue", "state", "product", "number", "Revenue over the last period_days days (Cancelled orders excluded)",
       uses=("period_days",), permission=Permission.SALES_VIEW),
    _a("revenue_rank", "derived", "product", "number",
       "Position by revenue among the products sold over the last period_days days (1 = the most; last = the least)",
       uses=("period_days",), permission=Permission.SALES_VIEW),
    _a("units_sold_rank", "derived", "product", "number",
       "Position by units sold among the products sold over the last period_days days (1 = the most; last = the least)",
       uses=("period_days",), permission=Permission.SALES_VIEW),
    # --- product: what the analytics compute ----------------------------------------------------------
    _a("avg_daily_demand", "derived", "product", "number", "Average units sold per day over the last 28 days"),
    _a("demand_trend_pct", "derived", "product", "number",
       "Change in average daily demand against the 28 days before, in % (rising: gt 0; falling: lt 0)"),
    _a("days_of_cover", "derived", "product", "number", "Days the stock on hand lasts at the current rate of sale"),
    _a("projected_stockout_date", "derived", "product", "date", "Date the stock on hand runs out at the current rate"),
    _a("lead_time_days", "derived", "product", "number", "Lead time in days used by the analytics"),
    _a("inventory_position", "derived", "product", "number",
       "Stock on hand + units on order + overdue units + units awaiting approval"),
    _a("reorder_point", "derived", "product", "number", "Reorder point: average daily demand x lead time + safety stock"),
    _a("suggested_order_quantity", "derived", "product", "number", "Units the reorder rule suggests ordering (0 = no reorder)"),
    _a("suggested_supplier", "derived", "product", "entity", "Supplier the reorder rule suggests", entity="supplier"),
    _a("stockout_risk_level", "derived", "product", "category", "Stockout risk level", STOCKOUT_LEVELS, ordered=True),
    _a("forecast_method", "derived", "product", "category", "Forecast method chosen by backtest error", FORECAST_METHODS),
    _a("avg_weekly_forecast", "derived", "product", "number", "Average forecast units per week over horizon_weeks weeks",
       uses=("horizon_weeks",)),
    _a("scenario_unmet_demand", "derived", "product", "number", "What-if: units of demand left unmet in the scenario",
       uses=SCENARIO),
    _a("baseline_unmet_demand", "derived", "product", "number", "What-if: units of demand left unmet with no change",
       uses=("horizon_days",)),
    _a("scenario_extra_unmet_demand", "derived", "product", "number",
       "What-if: scenario unmet demand minus baseline unmet demand", uses=SCENARIO),
    _a("scenario_stockout_date", "derived", "product", "date", "What-if: date the stock runs out in the scenario", uses=SCENARIO),
    _a("scenario_days_until_stockout", "derived", "product", "number", "What-if: days until stock runs out in the scenario",
       uses=SCENARIO),
    _a("scenario_ending_stock", "derived", "product", "number", "What-if: stock at the end of the horizon", uses=SCENARIO),
    _a("scenario_days_below_safety", "derived", "product", "number", "What-if: days below safety stock in the scenario",
       uses=SCENARIO),
    # --- supplier --------------------------------------------------------------------------------------
    _a("supplier_exists", "state", "supplier", "boolean", "The supplier is in the system (true) or not (false)"),
    _a("supplier_status", "state", "supplier", "category", "Supplier status", SUPPLIER_STATUSES),
    _a("supplies_product", "state", "supplier", "entity", "The supplier supplies the product (eq) or does not (ne)",
       entity="product"),
    _a("on_time_rate_pct", "derived", "supplier", "number", "Percentage of deliveries that arrived on time"),
    _a("avg_delay_days", "derived", "supplier", "number", "Average delivery delay in days"),
    _a("max_delay_days", "derived", "supplier", "number", "Longest delivery delay in days"),
    _a("supplier_lead_time_days", "derived", "supplier", "number", "Average observed lead time of the supplier's deliveries"),
    _a("deliveries_analyzed", "derived", "supplier", "number", "Number of deliveries analysed"),
    _a("open_orders", "state", "supplier", "number", "Ordered purchase orders not yet delivered"),
    _a("overdue_orders", "state", "supplier", "number", "Open purchase orders past their expected delivery date"),
    _a("delivery_risk_level", "derived", "supplier", "category", "Supplier delivery risk level", SUPPLIER_LEVELS, ordered=True),
    _a("delay_trend", "derived", "supplier", "category", "Supplier delay trend", DELAY_TRENDS),
    # --- purchase order --------------------------------------------------------------------------------
    _a("order_exists", "state", "order", "boolean", "The purchase order is in the system", recorded=True),
    _a("order_status", "state", "order", "category", "Purchase order status", ORDER_STATUSES, recorded=True),
    _a("order_quantity", "state", "order", "number", "Units on the purchase order", recorded=True),
    _a("order_product", "state", "order", "entity", "Product on the purchase order", entity="product", recorded=True),
    _a("order_supplier", "state", "order", "entity", "Supplier of the purchase order", entity="supplier", recorded=True),
    _a("order_expected_delivery", "state", "order", "date", "Expected delivery date of the purchase order", recorded=True),
    _a("order_actual_delivery", "state", "order", "date", "Date the goods of the purchase order arrived", recorded=True),
    _a("order_overdue", "state", "order", "boolean", "The order is Ordered, not delivered and past its expected date"),
    # --- counts ----------------------------------------------------------------------------------------
    _a("products_at_risk_level", "derived", "risk_level", "number",
       "Number of products at the stockout risk level named as subject"),
    _a("suppliers_at_risk_level", "derived", "risk_level", "number",
       "Number of suppliers at the delivery risk level named as subject"),
    _a("products_with_stock_status", "state", "stock_status", "number",
       "Number of stock records with the stock status named as subject"),
    # --- company rules ---------------------------------------------------------------------------------
    _a("policy_value", "policy", "rule", "policy", "The value of a company rule; subject is the rule key"),
    _a("role_can", "policy", "role", "action", "The role can (eq) or cannot (ne) do the action given as value"),
    _a("assistant_can", "policy", "assistant", "action", "The AI assistant can (eq) or cannot (ne) do the action given as value"),
)

BY_NAME: dict[str, Attribute] = {attribute.name: attribute for attribute in ATTRIBUTES}
NAMES: tuple[str, ...] = tuple(BY_NAME)

# Groups that everyday words do not tell apart ("the threshold of 112", "a critical stockout", "73 units
# pending"), with the words that name each member. A quote that uses none of an attribute's own words may
# mean any member of its group.
_GROUPS = (("safety_stock", "reorder_level", "reorder_point"), ("stock_status", "stockout_risk_level"),
           ("units_on_order", "units_awaiting_approval"))
SIBLINGS: dict[str, tuple[str, ...]] = {name: tuple(other for other in group if other != name)
                                        for group in _GROUPS for name in group}
OWN_WORDS: dict[str, str] = {
    "safety_stock": r"\bsafety\b",
    "reorder_level": r"\breorder level\b",
    "reorder_point": r"\breorder point\b",
    "stock_status": r"\b(?:stock status|in stock|out of stock|low stock)\b",
    "stockout_risk_level": r"\brisk\b",
    "units_on_order": r"\b(?:on order|ordered)\b",
    "units_awaiting_approval": r"\bapprov",
}

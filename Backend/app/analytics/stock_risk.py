"""Rule-based stockout risk and reorder suggestion. Deterministic - not AI.

Risk rules, first match wins:
  Critical - nothing on hand while the product is still selling
  High     - stock will run out before a new order could arrive and no inbound delivery is due in time,
             or stock is below safety stock while demand is rising sharply (same inbound condition)
  Medium   - stock is below safety stock, or cover is within one review period of the lead time
  Low      - none of the above
"""
from dataclasses import dataclass, field
from datetime import date, timedelta
from math import ceil

from app.models.enums import RiskLevel

RISING_DEMAND_PCT = 15.0
REVIEW_PERIOD_DAYS = 14  # how often stock is assumed to be reviewed and reordered
REVIEW_BUFFER_DAYS = 7
ORDER_MULTIPLE = 10


@dataclass(frozen=True)
class StockPosition:
    on_hand: int
    safety_stock: int
    avg_daily_demand: float
    demand_trend_pct: float | None
    lead_time_days: float
    inbound_units: int = 0  # ordered, not delivered, not overdue
    next_inbound_date: date | None = None
    overdue_inbound_units: int = 0
    awaiting_approval_units: int = 0


@dataclass(frozen=True)
class StockRisk:
    level: RiskLevel
    days_of_cover: float | None
    projected_stockout_date: date | None
    reorder_point: int
    suggested_order_quantity: int
    drivers: list[str] = field(default_factory=list)


def _round_up(quantity: float, multiple: int = ORDER_MULTIPLE) -> int:
    return int(ceil(quantity / multiple) * multiple) if quantity > 0 else 0


def assess(position: StockPosition, today: date) -> StockRisk:
    p = position
    selling = p.avg_daily_demand > 0
    days_of_cover = round(p.on_hand / p.avg_daily_demand, 1) if selling else None
    stockout_date = today + timedelta(days=int(days_of_cover)) if days_of_cover is not None else None

    below_safety = p.on_hand < p.safety_stock
    rising = p.demand_trend_pct is not None and p.demand_trend_pct >= RISING_DEMAND_PCT
    runs_out_before_resupply = days_of_cover is not None and days_of_cover < p.lead_time_days
    inbound_in_time = (
        p.inbound_units > 0
        and p.next_inbound_date is not None
        and (stockout_date is None or p.next_inbound_date <= stockout_date)
    )

    if p.on_hand == 0 and selling:
        level = RiskLevel.CRITICAL
    elif (runs_out_before_resupply or (below_safety and rising)) and not inbound_in_time:
        level = RiskLevel.HIGH
    elif (
        below_safety
        or runs_out_before_resupply
        or (days_of_cover is not None and days_of_cover < p.lead_time_days + REVIEW_BUFFER_DAYS)
    ):
        level = RiskLevel.MEDIUM
    else:
        level = RiskLevel.LOW

    # Evidence: every statement is a fact from the inputs, so it can be shown or cited as-is.
    drivers = []
    if p.on_hand == 0:
        drivers.append("Out of stock.")
    elif below_safety:
        drivers.append(f"Stock on hand ({p.on_hand}) is below safety stock ({p.safety_stock}).")
    if selling:
        drivers.append(f"Average demand is {p.avg_daily_demand:g} units/day over the last 28 days.")
    if p.demand_trend_pct is not None and abs(p.demand_trend_pct) >= RISING_DEMAND_PCT:
        direction = "up" if p.demand_trend_pct > 0 else "down"
        drivers.append(f"Demand is {direction} {abs(p.demand_trend_pct):g}% on the previous 28 days.")
    if days_of_cover is not None and p.on_hand > 0:
        comparison = "less than" if runs_out_before_resupply else "versus"
        drivers.append(
            f"{days_of_cover:g} days of cover, {comparison} the supplier lead time of {p.lead_time_days:g} days."
        )
    if p.inbound_units:
        drivers.append(f"{p.inbound_units} units on order, next delivery expected {p.next_inbound_date:%d %b %Y}.")
    if p.overdue_inbound_units:
        drivers.append(f"{p.overdue_inbound_units} units on order are overdue from the supplier.")
    if p.awaiting_approval_units:
        drivers.append(f"{p.awaiting_approval_units} units are in purchase orders not yet placed with a supplier.")

    # Order-up-to policy: cover demand over lead time + review period, plus safety stock.
    reorder_point = ceil(p.avg_daily_demand * p.lead_time_days + p.safety_stock)
    target = p.avg_daily_demand * (p.lead_time_days + REVIEW_PERIOD_DAYS) + p.safety_stock
    position_units = p.on_hand + p.inbound_units + p.overdue_inbound_units + p.awaiting_approval_units
    suggested = _round_up(target - position_units) if position_units <= reorder_point else 0

    return StockRisk(level, days_of_cover, stockout_date, reorder_point, suggested, drivers)

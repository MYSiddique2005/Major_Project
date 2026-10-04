"""Supplier delivery performance from purchase-order history. Deterministic - not AI.

Risk rules, first match wins:
  High   - an open order is overdue, fewer than half of deliveries were on time,
           or delays are getting worse and average at least 2 days
  Medium - average delay of a day or more, or fewer than 60% of deliveries on time
  Low    - otherwise (including suppliers with no delivery history)

The on-time percentage is only used as a rule once a supplier has at least
MIN_DELIVERIES_FOR_RATE deliveries, so one late delivery cannot label a supplier High.
"""
from dataclasses import dataclass, field
from datetime import date

from app.models.entities import PurchaseOrder
from app.models.enums import PurchaseOrderStatus, RiskLevel

RECENT_DELIVERIES = 2
MIN_DELIVERIES_FOR_RATE = 3
MIN_DELIVERIES_FOR_TREND = 4
TREND_TOLERANCE_DAYS = 0.5


@dataclass(frozen=True)
class SupplierPerformance:
    orders_total: int
    deliveries_analyzed: int
    on_time_rate: float | None  # percent
    avg_delay_days: float | None
    max_delay_days: int | None
    avg_lead_time_days: float | None  # observed: order date to actual delivery
    delay_trend: str  # worsening | improving | stable | insufficient data
    open_orders: int
    overdue_orders: int
    level: RiskLevel
    drivers: list[str] = field(default_factory=list)


def assess(orders: list[PurchaseOrder], today: date) -> SupplierPerformance:
    delivered = sorted((o for o in orders if o.actual_delivery is not None), key=lambda o: o.actual_delivery)
    delays = [max(0, (o.actual_delivery - o.expected_delivery).days) for o in delivered]
    lead_times = [(o.actual_delivery - o.order_date).days for o in delivered]
    open_orders = [o for o in orders if o.status == PurchaseOrderStatus.ORDERED and o.actual_delivery is None]
    overdue = [o for o in open_orders if o.expected_delivery < today]

    n = len(delays)
    on_time_rate = round(sum(1 for d in delays if d == 0) / n * 100, 1) if n else None
    avg_delay = round(sum(delays) / n, 2) if n else None
    avg_lead = round(sum(lead_times) / n, 1) if n else None

    trend = "insufficient data"
    if n >= MIN_DELIVERIES_FOR_TREND:
        recent = sum(delays[-RECENT_DELIVERIES:]) / RECENT_DELIVERIES
        earlier = sum(delays[:-RECENT_DELIVERIES]) / (n - RECENT_DELIVERIES)
        if recent > earlier + TREND_TOLERANCE_DAYS:
            trend = "worsening"
        elif recent < earlier - TREND_TOLERANCE_DAYS:
            trend = "improving"
        else:
            trend = "stable"

    rate_is_meaningful = n >= MIN_DELIVERIES_FOR_RATE
    if overdue or (rate_is_meaningful and on_time_rate < 50) or (trend == "worsening" and avg_delay >= 2):
        level = RiskLevel.HIGH
    elif n and (avg_delay >= 1 or (rate_is_meaningful and on_time_rate < 60)):
        level = RiskLevel.MEDIUM
    else:
        level = RiskLevel.LOW

    def days(value: float) -> str:
        return f"{value:g} day" if value == 1 else f"{value:g} days"

    drivers = []
    if n:
        on_time = sum(1 for d in delays if d == 0)
        drivers.append(f"{on_time} of {n} {'delivery' if n == 1 else 'deliveries'} arrived on time.")
        if avg_delay > 0:
            drivers.append(f"Average delay is {days(avg_delay)} (longest {days(max(delays))}).")
        if trend == "worsening":
            drivers.append("Delays have grown in the most recent deliveries.")
    else:
        drivers.append("No completed deliveries to analyse.")
    for order in overdue:
        drivers.append(f"{order.id} is {days((today - order.expected_delivery).days)} overdue.")

    return SupplierPerformance(
        orders_total=len(orders),
        deliveries_analyzed=n,
        on_time_rate=on_time_rate,
        avg_delay_days=avg_delay,
        max_delay_days=max(delays) if delays else None,
        avg_lead_time_days=avg_lead,
        delay_trend=trend,
        open_orders=len(open_orders),
        overdue_orders=len(overdue),
        level=level,
        drivers=drivers,
    )

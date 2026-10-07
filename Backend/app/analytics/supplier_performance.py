"""Supplier delivery performance from purchase-order history. Deterministic - not AI.

Risk rules, first match wins:
  High   - an open order is overdue, fewer than half of deliveries were on time,
           or delays are getting worse and average at least 2 days
  Medium - average delay of a day or more, or fewer than 60% of deliveries on time
  Low    - otherwise (including suppliers with no delivery history)

The on-time percentage is only used as a rule once a supplier has at least
MIN_DELIVERIES_FOR_RATE deliveries, so one late delivery cannot label a supplier High.

The delay trend compares the orders that fell due in the last TREND_WINDOW_DAYS with those due in the
window before it. Orders are placed in a window by the date they were promised, and an order that is
overdue counts with its delay so far. Looking only at orders already delivered would leave out exactly
the late ones that have not arrived yet and make every supplier look as if it were improving.
"""
from dataclasses import dataclass, field
from datetime import date, timedelta

from app.models.entities import PurchaseOrder
from app.models.enums import PurchaseOrderStatus, RiskLevel

MIN_DELIVERIES_FOR_RATE = 3
TREND_WINDOW_DAYS = 60
MIN_ORDERS_PER_TREND_WINDOW = 2
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

    def delays_due_between(start: date, end: date) -> list[int]:
        """Delay of every order promised in [start, end): actual delay, or the delay so far if still overdue."""
        return [
            max(0, ((o.actual_delivery or today) - o.expected_delivery).days)
            for o in orders
            if start <= o.expected_delivery < end and (o.actual_delivery is not None or o in overdue)
        ]

    window = timedelta(days=TREND_WINDOW_DAYS)
    recent_delays = delays_due_between(today - window, today)
    earlier_delays = delays_due_between(today - 2 * window, today - window)
    trend = "insufficient data"
    if min(len(recent_delays), len(earlier_delays)) >= MIN_ORDERS_PER_TREND_WINDOW:
        recent = sum(recent_delays) / len(recent_delays)
        earlier = sum(earlier_delays) / len(earlier_delays)
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
            drivers.append(f"Delays have grown over the last {TREND_WINDOW_DAYS} days.")
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

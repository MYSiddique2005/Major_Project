"""Day-by-day stock projection for what-if analysis. Deterministic - not AI.

Assumptions: demand is constant at the given daily rate, demand that cannot be
served is lost (stock never goes negative), and deliveries arrive in full on
their due date.
"""
from dataclasses import dataclass
from datetime import date, timedelta


@dataclass(frozen=True)
class Projection:
    points: list[tuple[date, float]]  # stock at the end of each day, starting today
    stockout_date: date | None
    days_until_stockout: int | None
    days_below_safety: int
    unmet_demand_units: float
    ending_stock: float


def project(
    on_hand: float,
    daily_demand: float,
    arrivals: dict[date, int],
    safety_stock: int,
    today: date,
    horizon_days: int,
) -> Projection:
    stock = float(on_hand)
    points = [(today, round(stock, 1))]
    stockout_date = None
    days_below_safety = 0
    unmet = 0.0
    for offset in range(1, horizon_days + 1):
        day = today + timedelta(days=offset)
        stock += arrivals.get(day, 0)
        served = min(stock, daily_demand)
        unmet += daily_demand - served
        stock -= served
        if stock <= 0 and daily_demand > 0 and stockout_date is None:
            stockout_date = day
        if stock < safety_stock:
            days_below_safety += 1
        points.append((day, round(stock, 1)))
    return Projection(
        points=points,
        stockout_date=stockout_date,
        days_until_stockout=(stockout_date - today).days if stockout_date else None,
        days_below_safety=days_below_safety,
        unmet_demand_units=round(unmet, 1),
        ending_stock=round(stock, 1),
    )

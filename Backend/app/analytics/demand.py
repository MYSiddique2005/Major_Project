"""Demand statistics from sales history. Pure functions: no I/O, no AI.

Every function takes `today` explicitly so results are reproducible in tests.
"""
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, timedelta

from app.models.entities import SalesOrder
from app.models.enums import SalesStatus

TREND_WINDOW_DAYS = 28
MIN_ORDERS_FOR_TREND = 5


@dataclass(frozen=True)
class DemandStats:
    avg_daily_demand: float  # last TREND_WINDOW_DAYS days
    previous_avg_daily_demand: float  # the TREND_WINDOW_DAYS days before that
    trend_pct: float | None  # None when there are too few orders to compare


def units_by_day(orders: list[SalesOrder]) -> dict[date, int]:
    """Units sold per day. Cancelled orders are not demand that was served, so they are excluded."""
    daily: dict[date, int] = defaultdict(int)
    for order in orders:
        if order.status != SalesStatus.CANCELLED:
            daily[order.order_date] += order.quantity
    return daily


def _window(daily: dict[date, int], orders_per_day: dict[date, int], end: date, days: int) -> tuple[int, int]:
    """(units, order count) over the `days` days ending the day before `end`."""
    units = orders = 0
    for offset in range(1, days + 1):
        day = end - timedelta(days=offset)
        units += daily.get(day, 0)
        orders += orders_per_day.get(day, 0)
    return units, orders


def demand_stats(orders: list[SalesOrder], today: date) -> DemandStats:
    daily = units_by_day(orders)
    orders_per_day: dict[date, int] = defaultdict(int)
    for order in orders:
        if order.status != SalesStatus.CANCELLED:
            orders_per_day[order.order_date] += 1

    recent_units, recent_orders = _window(daily, orders_per_day, today, TREND_WINDOW_DAYS)
    previous_units, previous_orders = _window(
        daily, orders_per_day, today - timedelta(days=TREND_WINDOW_DAYS), TREND_WINDOW_DAYS
    )
    trend = None
    if min(recent_orders, previous_orders) >= MIN_ORDERS_FOR_TREND and previous_units > 0:
        trend = round((recent_units - previous_units) / previous_units * 100, 1)
    return DemandStats(
        avg_daily_demand=round(recent_units / TREND_WINDOW_DAYS, 2),
        previous_avg_daily_demand=round(previous_units / TREND_WINDOW_DAYS, 2),
        trend_pct=trend,
    )


def weekly_units(orders: list[SalesOrder], today: date, weeks: int) -> list[tuple[date, int]]:
    """Units per 7-day bucket for the last `weeks` complete buckets (the latest ends yesterday).

    Returns (bucket start date, units), oldest first.
    """
    daily = units_by_day(orders)
    buckets = []
    for index in range(weeks, 0, -1):
        start = today - timedelta(days=7 * index)
        buckets.append((start, sum(daily.get(start + timedelta(days=d), 0) for d in range(7))))
    return buckets

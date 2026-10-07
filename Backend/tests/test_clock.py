"""The business date: what the analytics treat as today."""
from datetime import date, timedelta

import pytest

from app.core.clock import Clock
from tests.conftest import API


class SalesEndingOn:
    def __init__(self, last_day):
        self._last_day = last_day
        self.lookups = 0

    def latest_order_date(self):
        self.lookups += 1
        return self._last_day


def test_auto_follows_the_latest_sales_order():
    """A dataset loaded ten days ago is still analysed as of its own last day, so nothing drifts."""
    ten_days_ago = date.today() - timedelta(days=10)
    sales = SalesEndingOn(ten_days_ago)
    clock = Clock(sales, "auto")
    assert clock.today() == ten_days_ago
    assert clock.today() == ten_days_ago and sales.lookups == 1  # looked up once


def test_auto_never_runs_ahead_of_the_calendar_and_copes_with_no_sales():
    assert Clock(SalesEndingOn(date.today() + timedelta(days=3)), "auto").today() == date.today()
    assert Clock(SalesEndingOn(None), "auto").today() == date.today()
    assert Clock(None, "auto").today() == date.today()


def test_calendar_and_fixed_dates():
    old = SalesEndingOn(date(2020, 1, 1))
    assert Clock(old, "today").today() == date.today()
    assert Clock(old, "2026-10-05").today() == date(2026, 10, 5)
    assert Clock().today() == date.today()  # services built without a clock use the calendar
    with pytest.raises(ValueError):
        Clock(old, "next tuesday").today()


def test_system_info_reports_the_business_date(client, auth):
    info = client.get(f"{API}/system/info", headers=auth("employee")).json()
    sales = client.get(f"{API}/sales", headers=auth("admin")).json()
    assert info["business_date"] == max(order["order_date"] for order in sales)


def test_analytics_are_measured_from_the_business_date(client, auth):
    """The forecast's first week starts on the business date, not on whatever day the server runs."""
    business_date = client.get(f"{API}/system/info", headers=auth("admin")).json()["business_date"]
    forecast = client.get(f"{API}/analytics/forecast/P001", headers=auth("admin")).json()
    assert forecast["forecast"][0]["week_start"] == business_date

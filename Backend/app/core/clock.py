"""What day it is for the business.

The analytics measure everything back from "today": demand over the last 28 days, days of cover,
which deliveries are overdue. With live data that is the calendar date. A loaded dataset, though,
ends on the day it was loaded; measured from the calendar date it would look a little emptier every
day until demand appeared to have collapsed. So by default "today" is the date of the latest sales
order, never later than the calendar date. With sales arriving every day the two are the same.

    BUSINESS_DATE=auto        the latest sales order date (default)
    BUSINESS_DATE=today       the calendar date
    BUSINESS_DATE=2026-10-05  a fixed date

Timestamps of events (audit log, approvals, scans) always use the real time.
"""
from datetime import date

from app.repositories.base import SalesRepository


class Clock:
    def __init__(self, sales: SalesRepository | None = None, mode: str = "today"):
        self._sales = sales
        self._mode = mode
        self._today: date | None = None  # looked up once per request

    def today(self) -> date:
        if self._today is None:
            self._today = self._resolve()
        return self._today

    def _resolve(self) -> date:
        calendar = date.today()
        if self._mode == "today" or (self._mode == "auto" and self._sales is None):
            return calendar
        if self._mode == "auto":
            latest = self._sales.latest_order_date()
            return min(latest, calendar) if latest else calendar
        return date.fromisoformat(self._mode)

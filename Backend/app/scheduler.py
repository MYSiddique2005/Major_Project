"""Runs the proactive AI scan on a schedule, inside the web process.

A single background thread wakes once a minute and asks whether a scan is due. The time of the last
scan is read from the database, so restarting the server (which the development reloader does often)
neither repeats a scan nor skips one. Started and stopped by the application lifespan in main.py.
"""
import logging
import threading
from datetime import datetime

from app.api.deps import get_llm_provider, insight_service_outside_a_request

logger = logging.getLogger(__name__)
CHECK_EVERY_SECONDS = 60
FIRST_CHECK_AFTER_SECONDS = 10


class ScanScheduler:
    def __init__(self) -> None:
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, name="ai-scan-scheduler", daemon=True)

    def start(self) -> None:
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()

    def _run(self) -> None:
        delay = FIRST_CHECK_AFTER_SECONDS
        while not self._stop.wait(delay):
            delay = CHECK_EVERY_SECONDS
            try:
                run_if_due()
            except Exception:  # the scheduler must outlive a failed check, e.g. the database being down
                logger.exception("Scheduled AI scan check failed")


def run_if_due(now: datetime | None = None, provider_factory=get_llm_provider) -> bool:
    """Runs a scan when one is due. Returns whether it ran."""
    with insight_service_outside_a_request(provider_factory) as service:
        if not service.is_due(now or datetime.now()):
            return False
        scan = service.run_scan(trigger="schedule")
        logger.info("Scheduled AI scan %s: %s, %d insights. %s", scan.id, scan.status, scan.insights, scan.message)
        return True

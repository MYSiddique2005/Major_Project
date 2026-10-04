"""Simple, explainable demand forecasts over weekly totals. No ML libraries.

Two methods are available and compared by backtesting:
  moving_average - mean of the last 4 weeks, held flat
  linear_trend   - least-squares line through the last 12 weeks, extended forward
"""
from collections.abc import Callable

MOVING_AVERAGE_WEEKS = 4
TREND_WEEKS = 12
BACKTEST_WEEKS = 8

Forecaster = Callable[[list[float], int], list[float]]


def moving_average(history: list[float], horizon: int) -> list[float]:
    window = history[-MOVING_AVERAGE_WEEKS:]
    level = sum(window) / len(window) if window else 0.0
    return [level] * horizon


def linear_trend(history: list[float], horizon: int) -> list[float]:
    window = history[-TREND_WEEKS:]
    n = len(window)
    if n < 2:
        return moving_average(history, horizon)
    mean_x = (n - 1) / 2
    mean_y = sum(window) / n
    denominator = sum((x - mean_x) ** 2 for x in range(n))
    slope = sum((x - mean_x) * (y - mean_y) for x, y in enumerate(window)) / denominator
    intercept = mean_y - slope * mean_x
    return [max(0.0, intercept + slope * (n + step)) for step in range(horizon)]


METHODS: dict[str, Forecaster] = {"moving_average": moving_average, "linear_trend": linear_trend}


def backtest_wape(history: list[float], method: Forecaster, weeks: int = BACKTEST_WEEKS) -> float | None:
    """Weighted absolute percentage error of one-week-ahead forecasts over the last `weeks` weeks.

    Each test week is forecast using only the weeks before it. None if there is too
    little history or no demand to measure against.
    """
    weeks = min(weeks, len(history) - MOVING_AVERAGE_WEEKS)
    if weeks <= 0:
        return None
    absolute_error = actual_total = 0.0
    for index in range(len(history) - weeks, len(history)):
        prediction = method(history[:index], 1)[0]
        absolute_error += abs(prediction - history[index])
        actual_total += history[index]
    return round(absolute_error / actual_total, 3) if actual_total > 0 else None


def choose_method(history: list[float]) -> str:
    """The method with the lower backtest error; moving average when they cannot be compared."""
    errors = {name: backtest_wape(history, method) for name, method in METHODS.items()}
    comparable = {name: error for name, error in errors.items() if error is not None}
    return min(comparable, key=comparable.get) if comparable else "moving_average"  # type: ignore[arg-type]

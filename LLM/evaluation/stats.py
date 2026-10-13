"""The two statistics the summary reports. Pure functions, no dependencies.

  wilson_interval   a 95% confidence interval for a pass rate measured on n questions
  sign_test         whether "passes with grounding, fails without" outnumbers the reverse by more than chance
"""
from math import comb, sqrt

Z_95 = 1.959964


def wilson_interval(passed: int, total: int, z: float = Z_95) -> tuple[float, float]:
    """Wilson score interval for a proportion. Unlike the plain +/- formula it behaves at 0% and 100%."""
    if total == 0:
        return 0.0, 1.0
    rate = passed / total
    denominator = 1 + z * z / total
    centre = (rate + z * z / (2 * total)) / denominator
    half = z * sqrt(rate * (1 - rate) / total + z * z / (4 * total * total)) / denominator
    # At 0% and 100% the bound is exactly 0 or 1; say so rather than 0.9999999999999999.
    low = 0.0 if passed == 0 else max(0.0, centre - half)
    high = 1.0 if passed == total else min(1.0, centre + half)
    return low, high


def sign_test(only_first: int, only_second: int) -> float:
    """Exact two-sided p-value for paired pass/fail outcomes (the exact form of McNemar's test).

    Only the pairs that disagree carry information: `only_first` questions passed in the first
    condition alone, `only_second` in the second alone. Under "no difference" each disagreement is a
    coin flip, so the p-value is the chance of a split at least this uneven.
    """
    n = only_first + only_second
    if n == 0:
        return 1.0
    smaller = min(only_first, only_second)
    tail = sum(comb(n, k) for k in range(smaller + 1)) / 2 ** n
    return min(1.0, 2 * tail)

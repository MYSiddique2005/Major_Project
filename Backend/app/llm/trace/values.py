"""Reading asserted values as written by the extractor, and comparing them with the true values.

Values arrive as text ("237", "1,400 units", "94.2%", "06 Oct 2026", "Critical", "S004", "true"). Each
attribute has a kind, and the text is read in that kind. A number in the text is compared with the true
figure allowing for the rounding an answer may apply (the same tolerance as the figure check).
"""
import re
from datetime import date, datetime

_NUMBER = re.compile(r"-?\d[\d,]*(?:\.\d+)?|-?\.\d+")
_WORD_NUMBERS = {"zero": 0, "none": 0, "no": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
                 "seven": 7, "eight": 8, "nine": 9, "ten": 10}
_DATE_FORMATS = ("%Y-%m-%d", "%d %b %Y", "%d %B %Y", "%b %d %Y", "%B %d %Y", "%b %d, %Y", "%B %d, %Y",
                 "%d/%m/%Y", "%Y/%m/%d")
_ORDINAL = re.compile(r"(\d)(st|nd|rd|th)\b")
_TRUE = {"true", "yes", "y", "1", "exists", "can", "does"}
_FALSE = {"false", "no", "n", "0", "not", "cannot", "does not", "doesn't"}
LEVEL_ORDER = ("low", "medium", "high", "critical")


def parse_number(text: str) -> float | None:
    text = text.strip().lower()
    if text in _WORD_NUMBERS:
        return float(_WORD_NUMBERS[text])
    match = _NUMBER.search(text)
    if match is None:
        return None
    try:
        return float(match.group().replace(",", ""))
    except ValueError:
        return None


def parse_date(text: str, year: int | None = None) -> date | None:
    """A date written in any of the forms the assistant uses; a missing year is taken as `year`."""
    cleaned = _ORDINAL.sub(r"\1", text.strip().rstrip(".")).replace(",", ", ").replace("  ", " ")
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    for form in _DATE_FORMATS:
        for candidate in (cleaned, cleaned.replace(", ", " ")):
            try:
                return datetime.strptime(candidate, form).date()
            except ValueError:
                continue
    if year is not None:
        for form in ("%d %b", "%d %B", "%b %d", "%B %d"):
            try:
                return datetime.strptime(cleaned.replace(", ", " "), form).date().replace(year=year)
            except ValueError:
                continue
    return None


def parse_boolean(text: str) -> bool | None:
    text = text.strip().lower()
    if text in _TRUE:
        return True
    if text in _FALSE:
        return False
    return None


def normalise(text: str) -> str:
    """Lower case, hyphens and underscores as spaces, single spaces: for comparing categories and names."""
    return re.sub(r"\s+", " ", re.sub(r"[-_]", " ", str(text).strip().lower()))


def match_choice(text: str, choices: tuple[str, ...]) -> str | None:
    """The choice the text names, ignoring case, hyphens and a trailing 'risk' or 'stock' word."""
    wanted = normalise(text)
    for choice in choices:
        if normalise(choice) == wanted:
            return choice
    stripped = re.sub(r"\b(risk|level|status)\b", "", wanted).strip()
    for choice in choices:
        if normalise(choice) == stripped:
            return choice
    return None


def numbers_equal(asserted: float, actual: float) -> bool:
    """True when `asserted` is `actual` as an answer might write it: exactly, rounded to a whole number or
    one decimal place, or within 0.05 or 0.5% (whichever is larger)."""
    if asserted == actual:
        return True
    if round(actual) == asserted or round(actual, 1) == asserted:
        return True
    return abs(asserted - actual) <= max(0.051, 0.005 * abs(actual))


def compare(actual, comparator: str, asserted) -> bool:
    """Whether 'actual <comparator> asserted' holds. Numbers use the rounding tolerance for equality."""
    if isinstance(actual, (int, float)) and isinstance(asserted, (int, float)) and not isinstance(actual, bool):
        equal = numbers_equal(float(asserted), float(actual))
        if comparator == "eq":
            return equal
        if comparator == "ne":
            return not equal
        if comparator == "lt":
            return actual < asserted and not equal
        if comparator == "le":
            return actual <= asserted or equal
        if comparator == "gt":
            return actual > asserted and not equal
        if comparator == "ge":
            return actual >= asserted or equal
    if comparator == "eq":
        return actual == asserted
    if comparator == "ne":
        return actual != asserted
    if comparator == "lt":
        return actual < asserted
    if comparator == "le":
        return actual <= asserted
    if comparator == "gt":
        return actual > asserted
    if comparator == "ge":
        return actual >= asserted
    raise ValueError(f"Unknown comparator {comparator!r}")


def display(value) -> str:
    if value is None:
        return "none"
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, float):
        return f"{value:,.2f}".rstrip("0").rstrip(".")
    if isinstance(value, int):
        return f"{value:,}"
    if isinstance(value, date):
        return value.isoformat()
    return str(value)

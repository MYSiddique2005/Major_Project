"""Claim-level verification: are the qualitative statements in an AI answer true of the data?

The figure check (recommendations.unmatched_figures) asks whether each number in an answer exists in
the system's data. It cannot see a statement that uses a real number to say something false
("stock of 237 is above safety stock"), or one with no number at all ("demand is falling", "a
delivery is due in time", "a low-risk supplier"). This module finds such statements and checks each
against the same facts the assistant was given:

    stock below / above safety stock      inventory.stock_on_hand vs inventory.safety_stock
    out of stock / in stock               inventory.stock_on_hand == 0 / > 0
    demand rising / falling               sales.demand_trend_pct > 0 / < 0
    units overdue / on time               procurement.overdue_units (supplier.overdue_orders if the
                                          sentence is about the supplier)
    stock below / above reorder level     inventory.stock_on_hand vs inventory.reorder_level
    position below / above reorder point  stock + on order + overdue + awaiting approval vs reorder point
    delivery in time / too late           next delivery on or before the projected stockout date
    days of cover below / above lead time inventory.days_of_cover vs procurement.lead_time_days
    stock status (In Stock, Low Stock, ...) the stock status rule applied to the stock record
    stockout risk level                   assessment.stockout_risk_level
    supplier delivery risk level          supplier.delivery_risk_level
    supplier delay trend                  supplier.delay_trend

Each claim found is supported, contradicted, or unverifiable (the fact it needs is missing, e.g. no
demand trend for a product with too few orders). A claim preceded by a negation ("not", "no longer")
is checked with its meaning reversed. Matching is by pattern, so a claim worded unlike any pattern is
not checked; the evaluation reports how much it covers. The checks are deterministic and use no model.
"""
import re
from collections.abc import Callable
from dataclasses import asdict, dataclass
from datetime import date
from typing import Any, Literal

Facts = dict[str, Any]
Status = Literal["supported", "contradicted", "unverifiable"]
LEVELS = ("critical", "high", "medium", "low")

_NEGATION = re.compile(
    r"(?:\b(?:not|no|none|zero|no longer|never|isn't|aren't|wasn't|weren't|doesn't|don't|without|nor|rather than|"
    r"instead of|prevent\w*|avoid\w*|from reaching)\b(?:(?!\b(?:and|but|while|with|plus|whereas)\b)(?:[^.;,]|\.(?=\d))){0,24}"
    r"|\b0(?:\s+[a-z]+){0,2}\s*)$",
    re.IGNORECASE,
)
# Rule descriptions and hypotheticals ("Medium risk applies if ...", "a delivery were due in time") are
# not statements about the product, so a claim after such a word, or followed by one, is not checked.
_HYPOTHETICAL_BEFORE = re.compile(
    r"\b(?:if|when|whenever|unless|would|could|should|were|applies|apply|counts? as|count as|"
    r"rule\s+requires?|requires?\s+(?:that|either))\b", re.IGNORECASE)
_HYPOTHETICAL_AFTER = re.compile(r"^\W{0,3}(?:(?:rule|applies|apply|would|requires|criteria|criterion|threshold|category|"
                                 r"is defined|means)\b|(?:\w+\s+){0,3}(?:do not |does not |don't )?counts? as\b)", re.IGNORECASE)
_RULE_INSIDE = re.compile(r"\bcounts? as\b|\bdo(?:es)? not count\b", re.IGNORECASE)
_HEADING = re.compile(r"^[\W\d]*(?:\w+\s*){1,4}(?:\([^)]*\))?\s*:\s*$")
_NOT_DEMAND = re.compile(r"\b(?:unmet|lost|unserved|served|excess)\s+$", re.IGNORECASE)
_SUPPLIER_WORDS = re.compile(r"\b(?:supplier|vendor|delivery risk|deliveries|purchase orders|open orders)\b", re.IGNORECASE)
_PRODUCT_ID = re.compile(r"\bP\d{3}\b")
_SUPPLIER_ID = re.compile(r"\bS\d{3}\b")
# Sentence ends: a full stop, question or exclamation mark followed by space or end (not a decimal
# point), a semicolon, or a line break.
_SENTENCE_END = re.compile(r"(?<=[.!?;])\s+|\n+")


@dataclass(frozen=True)
class Claim:
    kind: str
    subject_id: str
    sentence: str
    matched: str
    asserted: str  # what the text says, e.g. "below", "rising", "High"
    actual: str | None  # what the data says, in the same terms; None when the data cannot tell
    status: Status

    def describe(self) -> str:
        """For the model and the user: the statement and what the data says instead."""
        return f'"{self.matched}" ({self.subject_id}): the data says {self.actual}'

    def as_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class Rule:
    """One kind of claim: patterns that assert it, and how to read the truth from the facts.

    `patterns` map a regular expression to the value the text asserts; a pattern with a capturing group
    asserts what it captured (used for risk levels). `actual` reads the true value from the facts, in
    the same vocabulary, or None when the data cannot tell. `opposite` gives what a negated assertion
    means for two-valued claims.
    """

    kind: str
    about: Literal["product", "supplier"]
    patterns: tuple[tuple[str, str | None], ...]
    actual: Callable[[Facts], str | None]
    opposite: dict[str, str] | None = None


def _get(facts: Facts, *path: str):
    value: Any = facts
    for key in path:
        if not isinstance(value, dict) or value.get(key) is None:
            return None
        value = value[key]
    return value


def _safety(facts: Facts) -> str | None:
    stock, safety = _get(facts, "inventory", "stock_on_hand"), _get(facts, "inventory", "safety_stock")
    if stock is None or safety is None:
        return None
    return "below" if stock < safety else "above"


def _out_of_stock(facts: Facts) -> str | None:
    stock = _get(facts, "inventory", "stock_on_hand")
    return None if stock is None else ("out of stock" if stock == 0 else "in stock")


def _trend(facts: Facts) -> str | None:
    trend = _get(facts, "sales", "demand_trend_pct")
    if trend is None:
        return None
    return "rising" if trend > 0 else "falling" if trend < 0 else "flat"


def _overdue(facts: Facts) -> str | None:
    units = _get(facts, "procurement", "overdue_units")
    return None if units is None else ("overdue" if units > 0 else "none overdue")


def _supplier_overdue(facts: Facts) -> str | None:
    orders = _get(facts, "supplier", "overdue_orders")
    if orders is None:
        orders = facts.get("overdue_orders")  # supplier facts on their own
    return None if orders is None else ("overdue" if orders > 0 else "none overdue")


def _delivery_timing(facts: Facts) -> str | None:
    on_order = _get(facts, "procurement", "units_on_order")
    if not on_order:
        return "no delivery due"
    arrives, runs_out = _get(facts, "procurement", "next_delivery_expected"), _get(facts, "inventory", "projected_stockout_date")
    if arrives is None:
        return None
    if runs_out is None:  # not selling: it cannot run out before the delivery
        return "in time"
    return "in time" if date.fromisoformat(str(arrives)) <= date.fromisoformat(str(runs_out)) else "too late"


def _cover(facts: Facts) -> str | None:
    cover, lead = _get(facts, "inventory", "days_of_cover"), _get(facts, "procurement", "lead_time_days")
    if cover is None or lead is None:
        return None
    return "below" if cover < lead else "above"


def _reorder_level(facts: Facts) -> str | None:
    stock, level = _get(facts, "inventory", "stock_on_hand"), _get(facts, "inventory", "reorder_level")
    if stock is None or level is None:
        return None
    return "below" if stock <= level else "above"


def _reorder_point_position(facts: Facts) -> str | None:
    """Stock on hand plus everything on order, against the reorder point (the reorder rule's trigger)."""
    point = _get(facts, "assessment", "reorder_point")
    stock = _get(facts, "inventory", "stock_on_hand")
    if point is None or stock is None:
        return None
    position = stock + sum(_get(facts, "procurement", key) or 0
                           for key in ("units_on_order", "overdue_units", "units_awaiting_approval"))
    return "below" if position <= point else "above"


def _stock_status(facts: Facts) -> str | None:
    """The stock status the Inventory page shows, by the same rule (app/utils/stock.py)."""
    stock, safety = _get(facts, "inventory", "stock_on_hand"), _get(facts, "inventory", "safety_stock")
    level = _get(facts, "inventory", "reorder_level")
    if stock is None or safety is None or level is None:
        return None
    if stock == 0:
        return "out of stock"
    if stock <= safety * 0.5:
        return "critical"
    return "low stock" if stock <= level else "in stock"


def _stockout_level(facts: Facts) -> str | None:
    return _get(facts, "assessment", "stockout_risk_level")


def _supplier_level(facts: Facts) -> str | None:
    return _get(facts, "supplier", "delivery_risk_level") or facts.get("delivery_risk_level")


def _delay_trend(facts: Facts) -> str | None:
    trend = _get(facts, "supplier", "delay_trend") or facts.get("delay_trend")
    return None if trend in (None, "insufficient data") else trend


_LEVEL = r"(critical|high|medium|low)"
_SAFETY = r"(?:its |the |their |a )?safety[- ]stock"
_DEMAND = r"\b(?:demand|sales)\b"
_UP = r"(?:rising|risen|rose|increas\w*|growing|grown|grew|surg\w*|climb\w*|up(?!\s+to\b)|higher|accelerat\w*)"
_DOWN = r"(?:falling|fallen|fell|declin\w*|decreas\w*|dropp\w*|down\b|lower|shrink\w*|slow\w*)"
_RUN_OUT = r"(?:run(?:s|ning)? out|stock(?:s)? out|projected stockout(?: date)?|stockout date|stockout(?![- ]risk)|stock is exhausted|stock runs out)"
_DELIVERY = r"\b(?:delivery|deliveries|order|orders|shipment|units on order|replenishment)\b"

RULES: tuple[Rule, ...] = (
    Rule("stock_status", "product", (
        (r"\bstock status\b(?:[^.;,]|\.(?=\d)){0,12}?\b(?:is|of|shows|as)\s+[\"']?(in stock|low stock|critical|out of stock)\b", None),
        (r"\bstatus\s+(?:is\s+)?[\"']?(low stock|in stock)\b", None),
    ), _stock_status),
    Rule("safety_stock", "product", (
        (rf"\b(?:below|under|beneath|short of|less than|lower than|falls? short of)\s+{_SAFETY}", "below"),
        (rf"\b{_SAFETY}\s+(?:is\s+)?(?:not\s+)?(?:yet\s+)?(?:breached|undercut)", "below"),
        (rf"\b(?:above|over|exceeds?|exceeding|more than|higher than|greater than|clear of)\s+{_SAFETY}", "above"),
    ), _safety, {"below": "above", "above": "below"}),
    Rule("out_of_stock", "product", (
        (r"(?<!run )(?<!runs )(?<!ran )(?<!running )\bout[- ]of[- ]stock\b(?!\s+(?:risk|status|items|products|on|by|in \d|within|before))", "out of stock"),
        (r"\b(?:zero|no)\s+(?:units\s+)?(?:stock\s+)?(?:on hand|in stock|left|remaining)\b", "out of stock"),
        (r"\bnothing on hand\b", "out of stock"),
        (r"\bstock on hand (?:is|of) (?:zero|0)\b", "out of stock"),
        (r"\b(?:is|are|remains?|still)\s+(?:still\s+)?in[- ]stock\b", "in stock"),
    ), _out_of_stock, {"out of stock": "in stock", "in stock": "out of stock"}),
    Rule("demand_trend", "product", (
        (rf"{_DEMAND}(?:[^.;,]|\.(?=\d)){{0,90}}?\b{_UP}", "rising"),
        (rf"\b{_UP}\s+{_DEMAND}", "rising"),
        (rf"{_DEMAND}(?:[^.;,]|\.(?=\d)){{0,90}}?\b{_DOWN}", "falling"),
        (rf"\b{_DOWN}\s+{_DEMAND}", "falling"),
    ), _trend, {"rising": "falling", "falling": "rising"}),
    Rule("overdue", "product", (
        (r"\boverdue\b", "overdue"),
        (r"\blate deliver(?:y|ies)\b(?=(?:[^.;]|\.(?=\d)){0,30}\b(?:on order|outstanding|pending)\b)", "overdue"),
        # Units or orders still to come described as on time, i.e. none overdue. Not a delivery rate or
        # deliveries that already arrived on time, which are history.
        (r"\b(?:units?|orders?|deliveries|shipments?)\s+(?:are|is|currently|all|remain)\s+(?:currently\s+|all\s+|still\s+)?on[- ]time\b(?![- ](?:rate|delivery rate))", "none overdue"),
        (r"\bon[- ]time\s+(?:inbound\s+|open\s+)?(?:units|orders)\b", "none overdue"),
        (r"\b(?:inbound\s+)?units\s+on[- ]time\b(?![- ](?:rate|delivery))", "none overdue"),
    ), _overdue, {"overdue": "none overdue", "none overdue": "overdue"}),
    Rule("delivery_timing", "product", (
        (rf"{_DELIVERY}(?:[^.;]|\.(?=\d)){{0,70}}?\b(?:too late|after (?:it|the product|stock|the stock|the item) (?:runs|has run|will run) out|after (?:the )?{_RUN_OUT})", "too late"),
        (rf"\b(?:runs?|run|will run|would run) out (?:of stock )?before (?:the |any |its |a |that )?(?:next )?{_DELIVERY}", "too late"),
        (rf"{_DELIVERY}(?:[^.;]|\.(?=\d)){{0,70}}?\b(?:in time|before (?:it|the product|stock|the stock|the item|they) (?:runs?|run) out|before (?:the )?{_RUN_OUT}|ahead of (?:the )?{_RUN_OUT})", "in time"),
        (rf"\b(?:depleted|exhausted|used up|run out|runs out|run(?:ning)? out)\b(?:[^.;]|\.(?=\d)){{0,30}}?\bafter\b(?:[^.;]|\.(?=\d)){{0,20}}?{_DELIVERY}", "in time"),
        (rf"\b(?:depleted|exhausted|used up)\b(?:[^.;]|\.(?=\d)){{0,30}}?\bbefore\b(?:[^.;]|\.(?=\d)){{0,20}}?{_DELIVERY}", "too late"),
        (rf"\b(?:covered|covers the shortfall)\b(?:[^.;]|\.(?=\d)){{0,40}}{_DELIVERY}", "in time"),
    ), _delivery_timing, {"in time": "too late", "too late": "in time"}),
    Rule("cover_vs_lead_time", "product", (
        (r"\bdays? of (?:cover|supply)\b(?:[^.;]|\.(?=\d)){0,60}?\b(?:less|shorter|lower|below|under|fewer|short of)\b(?:[^.;]|\.(?=\d)){0,30}\blead[- ]time", "below"),
        (r"\bdays? of (?:cover|supply)\b(?:[^.;]|\.(?=\d)){0,60}?\b(?:more|longer|greater|above|exceeds?|exceeding|beyond)\b(?:[^.;]|\.(?=\d)){0,30}\blead[- ]time", "above"),
        (r"\blead[- ]time\b(?:[^.;]|\.(?=\d)){0,40}?\b(?:exceeds?|exceeding|longer than|more than|greater than|beyond)\b(?:[^.;]|\.(?=\d)){0,30}\bdays? of (?:cover|supply)", "below"),
    ), _cover, {"below": "above", "above": "below"}),
    Rule("reorder_level", "product", (
        (r"\b(?:below|under|beneath|at or below|less than)\s+(?:the |its )?reorder level\b", "below"),
        (r"\b(?:above|over|exceeds?|exceeding|more than|greater than)\s+(?:the |its )?reorder level\b", "above"),
    ), _reorder_level, {"below": "above", "above": "below"}),
    Rule("reorder_point", "product", (
        (r"\b(?:position|pipeline|plus (?:units )?on order|on order combined|combined|total|totaling|totalling|inbound|in total)\b(?:[^.;,]|\.(?=\d)){0,40}?\b(?:below|under|at or below|less than)\s+(?:the |its )?reorder point\b", "below"),
        (r"\b(?:position|pipeline|plus (?:units )?on order|on order combined|combined|total|totaling|totalling|inbound|in total)\b(?:[^.;,]|\.(?=\d)){0,40}?\b(?:above|over|exceeds?|exceeding|more than|greater than)\s+(?:the |its )?reorder point\b", "above"),
    ), _reorder_point_position, {"below": "above", "above": "below"}),
    Rule("stockout_risk", "product", (
        (rf"\b{_LEVEL}[- ](?:stock[- ]?out[- ])?risk\b(?![- ](?:supplier|vendor))", None),
        (rf"\b{_LEVEL}\s+stock[- ]?out\b", None),
        (rf"\b(?:stock[- ]?out\s+)?risk(?:\s+level)?\s+(?:is|of|remains|was|at|rated|classified as)\s+(?:a\s+|rated\s+)?{_LEVEL}\b", None),
        (rf"\b(?:rated|classified|flagged)\s+(?:as\s+)?(?:a\s+)?{_LEVEL}\b(?!\s+(?:delivery|supplier))", None),
    ), _stockout_level),
    Rule("supplier_risk", "supplier", (
        (rf"\b{_LEVEL}[- ](?:delivery|supplier)[- ]risk\b", None),
        (rf"\b{_LEVEL}[- ]risk[- ](?:supplier|vendor)\b", None),
        (rf"\bdelivery risk(?:\s+level)?\s+(?:is|of|remains|was|at|rated)\s+{_LEVEL}\b", None),
    ), _supplier_level),
    Rule("delay_trend", "supplier", (
        (r"\bdelays?\b(?:[^.;]|\.(?=\d)){0,40}?\b(?:worsening|getting worse|growing|grown|increasing|lengthening)\b", "worsening"),
        (r"\bdelays?\b(?:[^.;]|\.(?=\d)){0,40}?\b(?:improving|shrinking|decreasing|getting better)\b", "improving"),
        (r"\b(?:delay trend|delivery performance)\b(?:[^.;]|\.(?=\d)){0,20}?\b(?:is\s+)?(?:stable|steady|unchanged)\b", "stable"),
        (r"\bdelay trend\b(?:[^.;]|\.(?=\d)){0,20}?\b(worsening|improving)\b", None),
    ), _delay_trend),
)

_COMPILED = [(rule, [(re.compile(pattern, re.IGNORECASE), value) for pattern, value in rule.patterns]) for rule in RULES]


def sentences(text: str) -> list[str]:
    return [part.strip() for part in _SENTENCE_END.split(text) if part and part.strip()]


def _negated(sentence: str, start: int) -> bool:
    return bool(_NEGATION.search(sentence[:start]))


def _judge(rule: Rule, asserted: str, negated: bool, actual: str | None) -> Status:
    if actual is None:
        return "unverifiable"
    asserted, actual = asserted.lower(), actual.lower()
    if rule.opposite is None:  # many-valued (risk level, delay trend): a negation says only "not this one"
        return "supported" if (asserted == actual) != negated else "contradicted"
    if negated:
        asserted = rule.opposite.get(asserted, asserted)
    if rule.kind == "delivery_timing" and actual == "no delivery due":
        return "supported" if asserted == "too late" else "contradicted"
    if rule.kind == "demand_trend" and actual == "flat":
        return "supported" if negated else "contradicted"  # "not rising" is true of flat demand
    return "supported" if asserted == actual else "contradicted"


def _hypothetical(sentence: str, start: int, end: int) -> bool:
    return bool(_HYPOTHETICAL_BEFORE.search(sentence[:start]) or _HYPOTHETICAL_AFTER.search(sentence[end:end + 25]))


def _about_supplier(sentence: str, supplier: Facts | None) -> bool:
    if _SUPPLIER_WORDS.search(sentence) or _SUPPLIER_ID.search(sentence):
        return True
    name = (supplier or {}).get("name")
    return bool(name) and name.split(",")[0].lower() in sentence.lower()


def _supplier_risk_here(sentence: str, start: int, supplier: Facts | None) -> bool:
    """A risk level is the supplier's, not the product's, when the sentence names no product, says nothing
    about stock, and mentions the supplier before the level."""
    if _PRODUCT_ID.search(sentence) or "stock" in sentence.lower():
        return False
    return _about_supplier(sentence[:start], supplier)


def claims_in_sentence(sentence: str, subject_id: str, product: Facts | None, supplier: Facts | None) -> list[Claim]:
    """The claims in one sentence about one product (and its supplier) or one supplier."""
    if _HEADING.match(sentence):
        return []
    found: list[Claim] = []
    taken: list[tuple[int, int]] = []  # spans already used, so one phrase yields one claim
    about_supplier = _about_supplier(sentence, supplier)
    for rule, patterns in _COMPILED:
        for pattern, value in patterns:
            for match in pattern.finditer(sentence):
                if any(match.start() < end and start < match.end() for start, end in taken):
                    continue
                if _hypothetical(sentence, match.start(), match.end()) or _RULE_INSIDE.search(match.group(0)):
                    continue
                if rule.kind == "demand_trend" and _NOT_DEMAND.search(sentence[:match.start()] + " "):
                    continue
                kind, reader, facts = rule.kind, rule.actual, product
                if rule.kind == "overdue" and about_supplier:
                    kind, reader, facts = "supplier_overdue", _supplier_overdue, supplier or product
                elif rule.kind == "stockout_risk" and _supplier_risk_here(sentence, match.start(), supplier):
                    kind, reader, facts = "supplier_risk", _supplier_level, supplier or product
                elif rule.about == "supplier":
                    facts = supplier or product
                if facts is None:
                    continue
                asserted = (match.group(1) if value is None else value).strip()
                if value is None:
                    asserted = asserted.capitalize() if asserted.lower() in LEVELS and rule.kind != "stock_status" else asserted.lower()
                negated = _negated(sentence, match.start())
                actual = reader(facts)
                rule_used = next(r for r, _ in _COMPILED if r.kind == kind) if kind != "supplier_overdue" else rule
                status = _judge(rule_used, asserted, negated, actual)
                found.append(Claim(kind, subject_id, sentence, match.group(0), ("not " if negated else "") + asserted,
                                   actual, status))
                taken.append(match.span())
    return found


def check_subject(text: str, subject_id: str, product: Facts | None = None, supplier: Facts | None = None) -> list[Claim]:
    """Claims in a text that is about one subject (an insight or a recommendation). Sentences naming a
    different product are skipped: they are about something else."""
    claims = []
    for sentence in sentences(text):
        others = set(_PRODUCT_ID.findall(sentence)) - {subject_id}
        if others and subject_id not in sentence:
            continue
        claims += claims_in_sentence(sentence, subject_id, product, supplier)
    return claims


def check_answer(text: str, facts_for: Callable[[str], Facts | None]) -> list[Claim]:
    """Claims in a free answer that may discuss several products. Each sentence is attributed to the one
    product ID it names, or to the product named most recently; a sentence naming several products is
    skipped as ambiguous. `facts_for(product_id)` returns the product's facts, or None."""
    claims, current = [], None
    for sentence in sentences(text):
        named = list(dict.fromkeys(_PRODUCT_ID.findall(sentence)))
        if _HEADING.match(sentence):
            current = None
            continue
        if len(named) > 1:
            current = None
            continue
        if named:
            current = named[0]
        if current is None:
            continue
        facts = facts_for(current)
        if facts is not None:
            claims += claims_in_sentence(sentence, current, facts, facts.get("supplier"))
    return claims


def summary(claims: list[Claim]) -> dict[str, Any]:
    return {
        "claims_checked": sum(claim.status != "unverifiable" for claim in claims),
        "claims_contradicted": [claim.describe() for claim in claims if claim.status == "contradicted"],
    }

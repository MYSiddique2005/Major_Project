"""Judging one assertion against the system of record. No model is involved.

    resolve the subject  ->  read the true value from its source  ->  read the asserted value  ->  compare

A verdict is supported or contradicted only when the true value could be read; otherwise it is
unverifiable, with the reason. So a wrong verdict can only come from an assertion that misrepresents
its sentence (an extraction error), never from this module guessing.
"""
import re
from dataclasses import replace
from datetime import date

from app.llm.trace import policy
from app.llm.trace import values as V
from app.llm.trace.catalogue import (BY_NAME, ORDER_COUNTS, OWN_WORDS, SIBLINGS, STOCK_STATUSES, STOCKOUT_LEVELS,
                                     SUPPLIER_LEVELS, Attribute)
from app.llm.trace.facts import FactSource, Missing, NoSuchSubject
from app.llm.trace.schema import Assertion, Verdict
from app.models.enums import Role
from app.security.permissions import has_permission
from app.utils.stock import compute_stock_status

_IDS = {
    "product": re.compile(r"^P\d{3}$", re.IGNORECASE),
    "supplier": re.compile(r"^S\d{3}$", re.IGNORECASE),
    "order": re.compile(r"^PO-?\d+$", re.IGNORECASE),
}
NEVER = date.max  # a stockout date that never comes (the product is not selling)
_NO_DELIVERY = object()


class Unresolved(Exception):
    """The subject or value cannot be tied to one record, rule or role."""


def _canonical_id(kind: str, text: str) -> str:
    text = text.strip().upper()
    if kind == "order":
        digits = re.sub(r"\D", "", text)
        return f"PO-{digits}"
    return text


def resolve(kind: str, text: str, source: FactSource) -> tuple[str, bool]:
    """(ID, written as an ID) for a product, supplier or order named by ID or by its exact name."""
    text = text.strip().strip('"').strip()
    if _IDS[kind].match(text):
        return _canonical_id(kind, text), True
    found = re.search(r"\b(P\d{3}|S\d{3}|PO-\d+)\b", text, re.IGNORECASE)  # "Fabrikam, Inc. (S004)"
    if found and _IDS[kind].match(found.group(1)):
        return _canonical_id(kind, found.group(1)), True
    finder = {"product": source.find_product, "supplier": source.find_supplier}.get(kind)
    match = finder(re.sub(r"\s*\([^)]*\)\s*$", "", text)) if finder else None
    if match is None:
        raise Unresolved(f"cannot tie '{text}' to one {kind}")
    return match, False


def _named(kind: str, identifier: str, text: str, source: FactSource) -> bool:
    """True when `text` names the record: by its ID or, for a product or supplier, by its name."""
    if re.search(rf"\b{identifier.replace('-', '-?')}\b", text, re.IGNORECASE):
        return True
    try:
        if kind == "product":
            names = [re.sub(r"\s*\([^)]*\)\s*$", "", source.product(identifier).name)]  # without "(White)"
        elif kind == "supplier":
            name = source.supplier(identifier).name
            names = [name, name.split(",")[0]]  # "Fabrikam, Inc." or "Fabrikam"
        else:
            return False
    except NoSuchSubject:
        return False
    flat = " ".join(text.lower().split())
    return any(" ".join(name.lower().split()) in flat for name in names if name.strip())


def _resolve_subject(attribute: Attribute, text: str, source: FactSource) -> tuple[str, bool]:
    kind = attribute.subject
    if kind in _IDS:
        return resolve(kind, text, source)
    if kind == "role":
        role = policy.resolve_role(text)
        if role is None:
            raise Unresolved(f"no role '{text}'")
        return role.value, False
    if kind == "assistant":
        return "assistant", False
    if kind == "rule":
        key = "_".join(text.strip().lower().replace("-", " ").split())
        if key not in policy.rules():
            raise Unresolved(f"no rule key '{text}'")
        return key, False
    if kind == "risk_level":
        levels = SUPPLIER_LEVELS if attribute.name == "suppliers_at_risk_level" else STOCKOUT_LEVELS
        level = V.match_choice(text, levels)
        if level is None:
            raise Unresolved(f"no risk level '{text}'")
        return level, False
    if kind == "stock_status":
        status = V.match_choice(text, STOCK_STATUSES)
        if status is None:
            raise Unresolved(f"no stock status '{text}'")
        return status, False
    raise Unresolved(f"unknown subject type {kind}")


# --- true values -----------------------------------------------------------------------------------------


def _suppliers_of(product_id: str, source: FactSource) -> set[str]:
    return {supplier.id for supplier in source.suppliers.list_suppliers()
            if any(item.id == product_id for item in supplier.products_supplied)}


def _ranking(name: str, assertion: Assertion, source: FactSource) -> list[str]:
    days = _required(assertion.period_days, "the statement gives no period")
    return source.sales_ranking(days, "revenue" if name == "revenue_rank" else "units")


def _required(value, reason: str):
    if value is None:
        raise Missing(reason)
    return value


def read(attribute: Attribute, subject: str, assertion: Assertion, source: FactSource, role: Role | None):
    """The true value of `attribute` for `subject`. Raises Missing when the data cannot tell and
    NoSuchSubject when the subject is not in the system."""
    name = attribute.name
    if name == "product_exists":
        return source.product_exists(subject)
    if name == "supplier_exists":
        return source.supplier_exists(subject)
    if name == "order_exists":
        return source.order_exists(subject)

    if attribute.subject == "product":
        product = source.product(subject)
        simple = {"primary_supplier": product.supplier_id, "category": product.category, "price": product.price,
                  "unit_cost": product.unit_cost}
        if name in simple:
            return simple[name]
        if name == "warehouse":
            return {_name(attribute, item) for item in source.warehouses(subject)}
        if name == "supplied_by":
            return _suppliers_of(subject, source)
        if name in ("revenue_rank", "units_sold_rank"):
            ranking = _ranking(name, assertion, source)
            if subject not in ranking:
                raise Missing(f"{subject} sold nothing in the period")
            return ranking.index(subject) + 1
        if name in ("units_sold", "revenue"):
            days = _required(assertion.period_days, "the statement gives no period")
            units, revenue = source.sales_totals(subject, days)
            return units if name == "units_sold" else revenue
        if name == "forecast_method":
            method = source.forecast(subject).method
            return getattr(method, "value", method)
        if name == "avg_weekly_forecast":
            return source.forecast(subject, assertion.horizon_weeks or 8).avg_weekly_forecast
        if name.startswith("scenario_") or name == "baseline_unmet_demand":
            result = source.what_if(subject, assertion.demand_change_pct or 0, assertion.delay_days or 0,
                                    assertion.order_quantity or 0,
                                    assertion.horizon_days or policy.rules()["what_if_default_horizon_days"][0])
            outcome = result.scenario
            values = {
                "scenario_unmet_demand": outcome.unmet_demand_units,
                "baseline_unmet_demand": result.baseline.unmet_demand_units,
                "scenario_extra_unmet_demand": round(outcome.unmet_demand_units - result.baseline.unmet_demand_units, 2),
                "scenario_stockout_date": outcome.stockout_date or NEVER,
                "scenario_days_until_stockout": _required(outcome.days_until_stockout, "stock does not run out in the scenario"),
                "scenario_ending_stock": outcome.ending_stock,
                "scenario_days_below_safety": outcome.days_below_safety,
            }
            return values[name]
        risk = source.stock_risk(subject)
        if name == "stock_status":
            return compute_stock_status(risk.on_hand, risk.safety_stock, risk.reorder_level).value
        if name == "next_delivery_date":
            return risk.next_inbound_date if risk.next_inbound_date and risk.inbound_units else _NO_DELIVERY
        if name == "projected_stockout_date":
            return risk.projected_stockout_date or NEVER
        if name == "inventory_position":
            return risk.on_hand + risk.inbound_units + risk.overdue_inbound_units + risk.awaiting_approval_units
        fields = {
            "stock_on_hand": risk.on_hand, "safety_stock": risk.safety_stock, "reorder_level": risk.reorder_level,
            "units_on_order": risk.inbound_units, "overdue_units": risk.overdue_inbound_units,
            "units_awaiting_approval": risk.awaiting_approval_units, "avg_daily_demand": risk.avg_daily_demand,
            "lead_time_days": risk.lead_time_days, "reorder_point": risk.reorder_point,
            "suggested_order_quantity": risk.suggested_order_quantity, "suggested_supplier": risk.suggested_supplier_id,
            "stockout_risk_level": risk.risk_level.value,
        }
        if name in fields:
            return _required(fields[name], f"no {name.replace('_', ' ')} for {subject}")
        if name == "demand_trend_pct":
            return _required(risk.demand_trend_pct, "no demand trend: too few orders in one of the periods")
        if name == "days_of_cover":
            return _required(risk.days_of_cover, "no days of cover: the product is not selling")

    if attribute.subject == "supplier":
        if name == "supplier_status":
            return source.supplier(subject).status.value
        if name == "supplies_product":
            return {item.id for item in source.supplier(subject).products_supplied}
        item = source.supplier_performance(subject)
        fields = {
            "on_time_rate_pct": item.on_time_rate, "avg_delay_days": item.avg_delay_days,
            "max_delay_days": item.max_delay_days, "supplier_lead_time_days": item.avg_lead_time_days,
            "deliveries_analyzed": item.deliveries_analyzed, "open_orders": item.open_orders,
            "overdue_orders": item.overdue_orders, "delivery_risk_level": item.risk_level.value,
            "delay_trend": None if item.delay_trend == "insufficient data" else item.delay_trend,
        }
        return _required(fields[name], f"no {name.replace('_', ' ')}: too little delivery history")

    if attribute.subject == "order":
        if name == "order_overdue":
            return source.order_overdue(subject)
        order = source.order(subject)
        if name == "order_actual_delivery":
            return _required(order.actual_delivery, f"{subject} has not been delivered")
        return {"order_status": order.status.value, "order_quantity": order.quantity, "order_product": order.product_id,
                "order_supplier": order.supplier_id, "order_expected_delivery": order.expected_delivery}[name]

    if name == "products_at_risk_level":
        return source.products_at_risk_level(subject)
    if name == "suppliers_at_risk_level":
        return source.suppliers_at_risk_level(subject)
    if name == "products_with_stock_status":
        return source.stock_status_counts().get(subject, 0)
    if name == "policy_value":
        return policy.rules()[subject][0]
    if name in ("role_can", "assistant_can"):
        action = _action(assertion.value)
        allowed = (policy.role_can(Role(subject), action, source.separation_of_duties) if name == "role_can"
                   else policy.assistant_can(action, role))
        return _required(allowed, f"the rules do not define '{assertion.value}'")
    raise Missing(f"cannot read {name}")


# --- asserted values -------------------------------------------------------------------------------------


def _action(text: str) -> str:
    """The action name a value means: as written, singular, with 'purchase' added, or plural."""
    action = "_".join(text.strip().lower().replace("-", " ").split())
    singular = action.replace("purchase_orders", "purchase_order").replace("_orders", "_order")
    with_po = singular if "purchase_order" in singular else singular.replace("_order", "_purchase_order")
    for candidate in (action, singular, with_po, f"{singular}s", f"{with_po}s"):
        if candidate in policy.ACTIONS:
            return candidate
    return action


def _asserted(attribute: Attribute, subject: str, text: str, source: FactSource):
    kind = attribute.kind
    if kind in ("number", "policy"):
        if kind == "policy" and V.parse_boolean(text) is not None and V.parse_number(text) is None:
            return V.parse_boolean(text)
        if text.strip().lower() in ("half", "one half"):
            return 0.5
        if V.parse_date(text, source.today().year) is not None:
            raise Unresolved(f"'{text}' is a date, not a number")  # "October 7 under standard conditions"
        number = V.parse_number(text)
        if number is None:
            raise Unresolved(f"'{text}' is not a number")
        if kind == "policy" and subject == "critical_stock_fraction" and number > 1:
            number /= 100  # "50%" of safety stock
        return number
    if kind == "date":
        value = V.parse_date(text, source.today().year)
        if value is None:
            raise Unresolved(f"'{text}' is not a date")
        return value
    if kind == "category":
        choice = V.match_choice(text, attribute.choices)
        if choice is None:
            raise Unresolved(f"'{text}' is not one of {', '.join(attribute.choices)}")
        return choice
    if kind == "name":
        return _name(attribute, text)
    if kind == "entity":
        return resolve(attribute.entity, text, source)[0]
    if kind == "boolean":
        value = V.parse_boolean(text)
        if value is None:
            raise Unresolved(f"'{text}' is not true or false")
        return value
    if kind == "action":
        return True  # the action is the subject of the check; 'eq' asserts it is allowed
    raise Unresolved(f"unknown kind {kind}")


def _reference(attribute: Attribute, subject: str, text: str, assertion: Assertion, source: FactSource, role):
    """'@safety_stock' (another attribute of the same subject) or '@P118' (the same attribute of another)."""
    target = text.strip()[1:].strip()
    other = BY_NAME.get(target)
    if other is not None:
        if other.subject == "supplier" and attribute.subject == "product":
            # "days of cover below the supplier lead time": the product's primary supplier
            supplier = source.product(subject).supplier_id
            return read(other, supplier, assertion, source, role), f"{target.replace('_', ' ')} of {supplier}"
        if other.subject != attribute.subject:
            raise Unresolved(f"@{target} is about a {other.subject}, not a {attribute.subject}")
        return read(other, subject, assertion, source, role), f"{target.replace('_', ' ')} of {subject}"
    if attribute.subject not in _IDS:
        raise Unresolved(f"cannot compare with '{text}'")
    other_subject, _ = resolve(attribute.subject, target, source)
    return read(attribute, other_subject, assertion, source, role), f"{attribute.name.replace('_', ' ')} of {other_subject}"


# --- the verdict -----------------------------------------------------------------------------------------


def _shown(value) -> str:
    if value is _NO_DELIVERY:
        return "no delivery on order"
    if value is NEVER:
        return "never (not selling)"
    if isinstance(value, set):
        return ", ".join(sorted(value)) or "none"
    return V.display(value)


def _name(attribute: Attribute, text: str) -> str:
    """'Main Warehouse', 'main warehouse' and 'Main' are one warehouse."""
    name = V.normalise(text)
    return re.sub(r"\s*\bwarehouse$", "", name) if attribute.name == "warehouse" else name


_NOTHING_HELD = re.compile(r"\b(?:0|zero|no)\s+(?:units?|inventory|stock)\b", re.IGNORECASE)


def _counts_units(quote: str, number: float) -> bool:
    """The quote gives this number as a count of units ('73 units pending')."""
    return any(V.parse_number(figure) is not None and V.numbers_equal(V.parse_number(figure), number)
               for figure in re.findall(r"(\d[\d,]*(?:\.\d+)?)[\s-]*units?\b", quote, re.IGNORECASE))


def _date_like(value) -> bool:
    return isinstance(value, date) or value is _NO_DELIVERY


def _holds(attribute: Attribute, actual, comparator: str, asserted) -> bool:
    if attribute.kind == "action":
        return actual if comparator == "eq" else not actual if comparator == "ne" else False
    if isinstance(actual, set):
        member = asserted in actual
        return member if comparator == "eq" else not member if comparator == "ne" else False
    if _date_like(actual) != _date_like(asserted):
        raise Unresolved("a date compared with something else")  # "delivery within the 14.3 days of cover"
    if actual is _NO_DELIVERY or asserted is _NO_DELIVERY:
        # Nothing on order arrives at no date: "arrives in time / by a date" is false, "too late" is true.
        late_side = actual is _NO_DELIVERY
        if comparator in ("lt", "le", "eq"):
            return not late_side
        return late_side if comparator in ("gt", "ge", "ne") else False
    if attribute.kind == "category" and attribute.ordered and comparator in ("lt", "le", "gt", "ge"):
        actual, asserted = V.LEVEL_ORDER.index(actual.lower()), V.LEVEL_ORDER.index(asserted.lower())
    elif attribute.kind == "category" and comparator not in ("eq", "ne"):
        raise Unresolved(f"'{comparator}' does not apply to {attribute.name}")
    if isinstance(actual, bool) != isinstance(asserted, bool):
        raise Unresolved("a yes/no value compared with something else")
    return V.compare(actual, comparator, asserted)


def verify(assertion: Assertion, source: FactSource, role: Role | None = None, origin: str = "model",
           named_in: str | None = None, siblings: bool = True) -> Verdict:
    """`named_in`, when given, is the text the assertion came from: a product, supplier or order it does
    not name (by ID or name) was supplied by the extractor, not the writer, so it is not judged."""
    attribute = BY_NAME[assertion.attribute]
    asserted_text = f"{assertion.comparator} {assertion.value}"

    def verdict(status: str, actual: str | None, reason: str, subject: str | None = None) -> Verdict:
        return Verdict(assertion.quote, subject or assertion.subject, attribute.name, attribute.family,
                       assertion.comparator, asserted_text, actual, status, reason, origin)

    if assertion.tense == "past" and not attribute.recorded:
        return verdict("unverifiable", None, "a past event the system does not keep as current data")
    if attribute.permission is not None and role is not None and not has_permission(role, attribute.permission):
        return verdict("unverifiable", None, "the user's role may not see this data")
    try:
        subject, written_as_id = _resolve_subject(attribute, assertion.subject, source)
    except Unresolved as error:
        return verdict("unverifiable", None, str(error))
    if named_in is not None and attribute.subject in _IDS and not _named(attribute.subject, subject, named_in, source):
        return verdict("unverifiable", None, f"the text does not name {subject}", subject)
    if attribute.name == "warehouse" and assertion.comparator == "eq" and _NOTHING_HELD.search(assertion.quote):
        return verdict("unverifiable", None, "the text says nothing is held there", subject)  # "0 units at North"
    try:
        actual = read(attribute, subject, assertion, source, role)
        if attribute.kind == "name" and isinstance(actual, str):
            actual = _name(attribute, actual)
        if assertion.value.strip().startswith("@"):
            asserted, compared_with = _reference(attribute, subject, assertion.value, assertion, source, role)
            shown = f"{attribute.name.replace('_', ' ')} is {_shown(actual)}, {compared_with} is {_shown(asserted)}"
        else:
            if attribute.name.endswith("_rank") and assertion.value.strip().lower() in ("last", "least", "bottom"):
                asserted = float(len(_ranking(attribute.name, assertion, source)))
            else:
                asserted = _asserted(attribute, subject, assertion.value, source)
            shown = _shown(actual) if attribute.kind != "action" else ("allowed" if actual else "not allowed")
            if (assertion.comparator in ("lt", "gt") and isinstance(asserted, float) and isinstance(actual, (int, float))
                    and not isinstance(actual, bool) and V.numbers_equal(asserted, float(actual))):
                # "falling (-50.6%)" read as 'less than -50.6': a strict comparison with the exact true figure is
                # far more often a mis-read figure than a claim, so it is not judged.
                return verdict("unverifiable", None, "a strict comparison with the true figure itself is ambiguous", subject)
            if attribute.name in ORDER_COUNTS and isinstance(asserted, float) and _counts_units(assertion.quote, asserted):
                return verdict("unverifiable", None, f"the text counts units, not {ORDER_COUNTS[attribute.name]}", subject)
        holds = _holds(attribute, actual, assertion.comparator, asserted)
    except NoSuchSubject as error:
        # A statement about a well-formed ID that does not exist presupposes something false.
        if written_as_id:
            return verdict("contradicted", str(error), "the subject does not exist", subject)
        return verdict("unverifiable", None, str(error), subject)
    except (Missing, Unresolved) as error:
        return verdict("unverifiable", None, str(error), subject)
    if not holds and siblings and attribute.name in SIBLINGS and not re.search(OWN_WORDS[attribute.name], assertion.quote, re.IGNORECASE):
        # "the 69-unit reorder threshold" is true when 69 is the reorder point, whichever one was extracted
        for sibling in SIBLINGS[attribute.name]:
            other = verify(assertion.model_copy(update={"attribute": sibling}), source, role, origin, named_in, siblings=False)
            if other.status == "supported":
                return replace(other, reason=f"the words do not say {attribute.name.replace('_', ' ')}; they fit "
                                             f"{sibling.replace('_', ' ')}, which holds")
    return verdict("supported" if holds else "contradicted", shown, "", subject)

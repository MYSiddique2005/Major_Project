"""Rule-based extraction: no model call.

Two parts:
  - the frozen version-3 claim patterns (app/llm/claims.py, unchanged), whose verdicts are carried over
    as they are, so TRACE never does worse than the published checker on the claims it covers;
  - a few high-precision patterns for statements the version-3 checker could not see: whether a product,
    supplier or order exists, what the assistant itself can do, and what a role can do. Each becomes an
    assertion judged by the deterministic verifier.
"""
import re
from collections.abc import Callable

from app.llm import claims as C
from app.llm.trace import policy
from app.llm.trace.schema import Assertion, Verdict

# version-3 claim kind -> (TRACE attribute, compared with, comparator by asserted value)
_V3: dict[str, tuple[str, str | None, dict[str, str]]] = {
    "safety_stock": ("stock_on_hand", "@safety_stock", {"below": "lt", "above": "ge"}),
    "out_of_stock": ("stock_on_hand", "0", {"out of stock": "eq", "in stock": "gt"}),
    "demand_trend": ("demand_trend_pct", "0", {"rising": "gt", "falling": "lt"}),
    "overdue": ("overdue_units", "0", {"overdue": "gt", "none overdue": "eq"}),
    "supplier_overdue": ("overdue_orders", "0", {"overdue": "gt", "none overdue": "eq"}),
    "delivery_timing": ("next_delivery_date", "@projected_stockout_date", {"in time": "le", "too late": "gt"}),
    "cover_vs_lead_time": ("days_of_cover", "@lead_time_days", {"below": "lt", "above": "ge"}),
    "reorder_level": ("stock_on_hand", "@reorder_level", {"below": "le", "above": "gt"}),
    "reorder_point": ("inventory_position", "@reorder_point", {"below": "le", "above": "gt"}),
    "stock_status": ("stock_status", None, {}),
    "stockout_risk": ("stockout_risk_level", None, {}),
    "supplier_risk": ("delivery_risk_level", None, {}),
    "delay_trend": ("delay_trend", None, {}),
}
_FLIP = {"lt": "ge", "ge": "lt", "le": "gt", "gt": "le", "eq": "ne", "ne": "eq"}
_FAMILY = {"stock_on_hand": "state", "overdue_units": "state", "overdue_orders": "state", "next_delivery_date": "state",
           "stock_status": "state"}


def from_v3(claim: C.Claim) -> Verdict:
    """A version-3 claim as a TRACE verdict, keeping its status (the frozen checker's judgement)."""
    attribute, against, comparators = _V3[claim.kind]
    negated = claim.asserted.startswith("not ")
    asserted = claim.asserted.removeprefix("not ")
    if against is None:  # categories: the asserted value is the category itself
        comparator, value = "eq", asserted
    else:
        comparator, value = comparators.get(asserted.lower(), "eq"), against
    if negated:
        comparator = _FLIP[comparator]
    return Verdict(claim.matched, claim.subject_id, attribute, _FAMILY.get(attribute, "derived"), comparator,
                   f"{comparator} {value}", claim.actual, claim.status, "", "rule")


# --- new patterns ------------------------------------------------------------------------------------------

_ABSENT = (r"(?:does not exist|doesn't exist|do not exist|did not exist|was not found|wasn't found|could not be found|"
           r"cannot be found|can't be found|is not in the system|isn't in the system|is not recorded|no such)")
_PRESENT = r"(?:does exist|do exist|exists(?: in the system)?|was found in the system|is in the system)"
_EXISTS = {"P": "product_exists", "S": "supplier_exists", "PO": "order_exists"}
_ID = r"\b(PO-\d+|P\d{3}|S\d{3})\b"
_ABSENT_AFTER = re.compile(rf"{_ID}[^.;:]{{0,60}}?\b{_ABSENT}", re.IGNORECASE)
_PRESENT_AFTER = re.compile(rf"{_ID}[^.;:]{{0,40}}?\b{_PRESENT}\b", re.IGNORECASE)

_VERB_ACTION = {"approve": "approve_purchase_order", "submit": "submit_purchase_order", "place": "place_order",
                "cancel": "cancel_purchase_order", "edit": "edit_purchase_order", "reject": "reject_purchase_order",
                "delete": "delete_purchase_order", "mark": "approve_purchase_order"}
_NOT_ABLE = r"(?:cannot|can't|can not|am not able to|am unable to|won't|will not|may not|am not allowed to|am not permitted to|do not have (?:the )?(?:ability|permission) to)"
_ABLE = r"(?:can|am able to|will|could)"
_VERBS = r"(approve|submit|place|cancel|edit|reject|delete|mark)"
# "I cannot approve, submit or place orders": every verb up to the end of the clause.
_ASSISTANT_NOT = re.compile(rf"\bI\s+{_NOT_ABLE}\s+((?:(?!\b(?:but|however|although)\b)[^.;]){{0,80}})", re.IGNORECASE)
_ASSISTANT_ABLE = re.compile(rf"\bI\s+{_ABLE}\s+(?:also\s+|now\s+)?{_VERBS}\b(?=[^.;]{{0,60}}\b(?:orders?|purchase|PO|draft|it|them)\b)",
                             re.IGNORECASE)
_MARK_APPROVED = re.compile(r"\bmark\b[^.;]{0,40}\bapproved\b", re.IGNORECASE)

_ROLE = r"(procurement managers?|inventory managers?|employees?|admins?|administrators?|you)"
_ROLE_MODAL = r"(can|cannot|can't|may|may not|are able to|is able to|are not able to|is not able to|are not allowed to|is not allowed to|do not have the right to|does not have the right to|lack the right to|lacks the right to)"
_ROLE_CLAUSE = re.compile(rf"\b{_ROLE}\s+(?:also\s+|still\s+)?{_ROLE_MODAL}\s+((?:(?!\b(?:but|however|although|while)\b)[^.;]){{0,70}})",
                          re.IGNORECASE)
_VIEW_OBJECTS = {"sales": "view_sales", "revenue": "view_sales", "inventory": "view_inventory", "stock": "view_inventory",
                 "analytics": "view_analytics", "audit": "view_audit_log", "purchase order": "view_purchase_orders"}
_NEGATIVE_MODALS = ("cannot", "can't", "may not", "not able", "not allowed", "do not have", "does not have", "lack")


def _actions_in(clause: str, view_words: bool) -> list[str]:
    found = [_VERB_ACTION[verb.lower()] for verb in re.findall(_VERBS, clause, re.IGNORECASE) if verb.lower() != "mark"]
    if re.search(r"\bmark\b[^.;]{0,40}\bapproved\b", clause, re.IGNORECASE):
        found.append("approve_purchase_order")
    if re.search(r"\b(?:create|draft)\b", clause, re.IGNORECASE) and not view_words:
        found.append("create_purchase_order")
    if view_words and re.search(r"\b(?:view|see|access|open)\b", clause, re.IGNORECASE):
        for word, action in _VIEW_OBJECTS.items():
            if word in clause.lower():
                found.append(action)
    return list(dict.fromkeys(found))


def rule_assertions(text: str, user_role: str | None = None) -> list[Assertion]:
    """Assertions from the new patterns. `user_role` (e.g. "PROCUREMENT_MANAGER") resolves "you"."""
    found: list[Assertion] = []
    for sentence in C.sentences(text):
        if C._HYPOTHETICAL_BEFORE.search(sentence.split(",")[0]) and sentence.lower().startswith(("if ", "when ")):
            continue
        for pattern, value in ((_ABSENT_AFTER, "false"), (_PRESENT_AFTER, "true")):
            for match in pattern.finditer(sentence):
                identifier = match.group(1).upper()
                prefix = "PO" if identifier.startswith("PO") else identifier[0]
                found.append(Assertion(quote=match.group(0), subject=identifier, attribute=_EXISTS[prefix],
                                       comparator="eq", value=value))
        for match in _ASSISTANT_NOT.finditer(sentence):
            for action in _actions_in(match.group(1), view_words=False):
                if action != "create_purchase_order":  # "I cannot create orders without a draft": not a capability
                    found.append(Assertion(quote=match.group(0)[:200], subject="assistant", attribute="assistant_can",
                                           comparator="ne", value=action))
        for match in _ASSISTANT_ABLE.finditer(sentence):
            action = _VERB_ACTION[match.group(1).lower()]
            if match.group(1).lower() == "mark" and not _MARK_APPROVED.search(sentence[match.start():]):
                continue
            found.append(Assertion(quote=match.group(0), subject="assistant", attribute="assistant_can",
                                   comparator="eq", value=action))
        for match in _ROLE_CLAUSE.finditer(sentence):
            who, modal, clause = match.group(1).lower(), match.group(2).lower(), match.group(3)
            subject = user_role if who == "you" else who
            if subject is None or policy.resolve_role(subject) is None:
                continue
            negative = any(word in modal for word in _NEGATIVE_MODALS)
            for action in _actions_in(clause, view_words=True):
                found.append(Assertion(quote=match.group(0)[:200], subject=subject, attribute="role_can",
                                       comparator="ne" if negative else "eq", value=action))
    return found


def v3_claims(text: str, facts_for: Callable[[str], dict | None], subject: tuple[str, str] | None,
              subject_facts: dict | None) -> list[C.Claim]:
    """The frozen checker's claims: for an answer, attributed sentence by sentence; for a text about one
    subject (an insight or recommendation), all about that subject."""
    if subject is None:
        return C.check_answer(text, facts_for)
    kind, identifier = subject
    if kind == "product":
        return C.check_subject(text, identifier, subject_facts, (subject_facts or {}).get("supplier"))
    return C.check_subject(text, identifier, None, subject_facts)

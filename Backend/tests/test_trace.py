"""TRACE: typed assertions checked against the system of record.

The verifier is tested on the in-memory demo data, with each expected value read from the same services
the assistant uses, so a test states the rule ("the true stock is supported, a different one is
contradicted") rather than a copied number. No real model is called: extraction is tested with a
scripted provider.
"""
import pytest

from app.analytics import stock_risk
from app.api import deps
from app.core.clock import Clock
from app.core.config import get_settings
from app.core.exceptions import ServiceUnavailableError
from app.llm.providers import Reply, ToolCall
from app.llm.recommendations import RecommendationChecker
from app.llm.trace import FactSource, TraceVerifier
from app.llm.trace.extract_llm import RECORD_TOOL, extract, parse, system_prompt
from app.llm.trace.extract_rule import rule_assertions
from app.llm.trace.policy import ACTIONS, ROLE_ACTIONS, rules
from app.llm.trace.schema import Assertion
from app.llm.trace.verify import verify
from app.models.enums import Role
from app.schemas.analytics import WhatIfRequest
from app.security.permissions import has_permission
from app.services.analytics_service import AnalyticsService
from app.services.audit_service import AuditService
from app.services.inventory_service import InventoryService
from app.services.procurement_service import ProcurementService
from app.services.product_service import ProductService
from app.services.sales_service import SalesService
from app.services.supplier_service import SupplierService
from tests.test_ai import ask, call, llm, reply  # noqa: F401  (llm is a fixture)


@pytest.fixture
def services(client):
    """The application's services on fresh in-memory demo data (the client fixture resets it)."""
    products_repo, suppliers_repo = deps.get_product_repository(None), deps.get_supplier_repository(None)
    inventory_repo, sales_repo = deps.get_inventory_repository(None), deps.get_sales_repository(None)
    orders_repo = deps.get_purchase_order_repository(None)
    clock = Clock(sales_repo, get_settings().business_date)
    analytics = AnalyticsService(products_repo, inventory_repo, sales_repo, orders_repo, suppliers_repo, clock)
    products = ProductService(products_repo, suppliers_repo, inventory_repo)
    suppliers = SupplierService(suppliers_repo, products_repo)
    procurement = ProcurementService(orders_repo, suppliers_repo, products_repo, deps.get_approval_repository(None),
                                     AuditService(deps.get_audit_log_repository(None)), deps.get_unit_of_work(None), clock)
    return {"analytics": analytics, "products": products, "suppliers": suppliers,
            "inventory": InventoryService(inventory_repo, products_repo), "procurement": procurement,
            "sales": SalesService(sales_repo, products_repo), "clock": clock}


@pytest.fixture
def source(services):
    s = services
    return FactSource(s["analytics"], s["products"], s["suppliers"], s["inventory"], s["procurement"], s["sales"], s["clock"])


def judge(source, subject, attribute, comparator="eq", value="", role=None, **extra):
    assertion = Assertion(quote=f"{subject} {attribute} {comparator} {value}", subject=subject, attribute=attribute,
                          comparator=comparator, value=value, **extra)
    return verify(assertion, source, role)


def status(source, *args, **kwargs):
    return judge(source, *args, **kwargs).status


# --- state -----------------------------------------------------------------------------------------------


def test_figures_are_compared_with_rounding(source):
    stock = source.stock_risk("P005").on_hand
    assert status(source, "P005", "stock_on_hand", "eq", str(stock)) == "supported"
    assert status(source, "P005", "stock_on_hand", "eq", f"{stock + 10} units") == "contradicted"
    cover = source.stock_risk("P005").days_of_cover
    assert status(source, "P005", "days_of_cover", "eq", str(round(cover))) == "supported"  # 6.7 written as 7


def test_comparison_with_another_attribute_follows_the_data(source):
    risk = source.stock_risk("P005")
    below = risk.on_hand < risk.safety_stock
    assert status(source, "P005", "stock_on_hand", "lt", "@safety_stock") == ("supported" if below else "contradicted")
    assert status(source, "P005", "stock_on_hand", "ge", "@safety_stock") == ("contradicted" if below else "supported")


def test_comparison_with_another_subject(source):
    first, second = source.stock_risk("P012").days_of_cover, source.stock_risk("P003").days_of_cover
    expected = "supported" if first < second else "contradicted"
    assert status(source, "P012", "days_of_cover", "lt", "@P003") == expected


def test_no_delivery_on_order_means_nothing_arrives_in_time(source):
    risk = source.stock_risk("P005")
    assert not risk.inbound_units
    assert status(source, "P005", "next_delivery_date", "le", "@projected_stockout_date") == "contradicted"
    assert status(source, "P005", "next_delivery_date", "gt", "@projected_stockout_date") == "supported"


def test_delivery_timing_against_the_projected_stockout(source):
    risk = source.stock_risk("P012")
    in_time = risk.next_inbound_date <= risk.projected_stockout_date
    assert status(source, "P012", "next_delivery_date", "le", "@projected_stockout_date") == (
        "supported" if in_time else "contradicted")


def test_statements_about_a_missing_product(source):
    assert status(source, "P999", "product_exists", "eq", "false") == "supported"
    assert status(source, "P999", "product_exists", "eq", "true") == "contradicted"
    # A statement presupposing a product that does not exist is false; a name that matches nothing is not judged.
    assert status(source, "P999", "stock_on_hand", "eq", "0") == "contradicted"
    assert status(source, "Imaginary Widget", "stock_on_hand", "eq", "0") == "unverifiable"


def test_supplier_relations(source):
    primary = source.product("P012").supplier_id
    assert status(source, "P012", "primary_supplier", "eq", primary) == "supported"
    assert status(source, "P012", "supplied_by", "eq", primary) == "supported"
    assert status(source, primary, "supplies_product", "eq", "P012") == "supported"
    other = next(s.id for s in source.suppliers.list_suppliers() if all(p.id != "P012" for p in s.products_supplied))
    assert status(source, "P012", "supplied_by", "eq", other) == "contradicted"
    assert status(source, "P012", "supplied_by", "ne", other) == "supported"


def test_purchase_order_history_is_checkable_in_the_past_tense(source):
    order = next(o for o in source.procurement.list_orders() if o.actual_delivery is not None)
    assert status(source, order.id, "order_status", "eq", order.status.value, tense="past") == "supported"
    assert status(source, order.id, "order_actual_delivery", "eq", order.actual_delivery.isoformat(), tense="past") == "supported"
    # Stock "last week" is not recorded, so it is not judged.
    assert status(source, "P012", "stock_on_hand", "eq", "0", tense="past") == "unverifiable"


# --- derived -----------------------------------------------------------------------------------------------


def test_risk_levels_and_their_order(source):
    level = source.stock_risk("P012").risk_level.value
    assert status(source, "P012", "stockout_risk_level", "eq", level) == "supported"
    other = "Low" if level != "Low" else "High"
    assert status(source, "P012", "stockout_risk_level", "eq", f"{other} risk") == "contradicted"
    assert status(source, "P012", "stockout_risk_level", "ne", other) == "supported"
    assert status(source, "P012", "stockout_risk_level", "gt", "Low") == ("supported" if level != "Low" else "contradicted")


def test_demand_trend_direction_and_missing_trend(source):
    trend = source.stock_risk("P001").demand_trend_pct
    assert status(source, "P001", "demand_trend_pct", "gt", "0") == ("supported" if trend > 0 else "contradicted")
    assert status(source, "P001", "demand_trend_pct", "lt", "0") == ("contradicted" if trend > 0 else "supported")
    assert source.stock_risk("P007").demand_trend_pct is None
    assert judge(source, "P007", "demand_trend_pct", "gt", "0").reason.startswith("no demand trend")


def test_strict_comparison_with_the_exact_figure_is_not_judged(source):
    trend = source.stock_risk("P001").demand_trend_pct
    # "falling (-50.6%)" mis-read as 'less than -50.6'
    assert status(source, "P001", "demand_trend_pct", "lt", str(trend)) == "unverifiable"


def test_what_if_statements_are_checked_by_rerunning_the_simulation(services, source):
    expected = services["analytics"].run_what_if(WhatIfRequest(product_id="P015", demand_change_pct=20, horizon_days=60))
    unmet = expected.scenario.unmet_demand_units
    assert status(source, "P015", "scenario_unmet_demand", "eq", str(unmet), demand_change_pct=20, horizon_days=60) == "supported"
    assert status(source, "P015", "scenario_unmet_demand", "eq", str(unmet + 50), demand_change_pct=20, horizon_days=60) == "contradicted"


def test_counts_by_risk_level(source):
    count = sum(1 for item in source.analytics.list_stock_risk() if item.risk_level.value == "Critical")
    assert status(source, "Critical", "products_at_risk_level", "eq", str(count)) == "supported"
    assert status(source, "Critical", "products_at_risk_level", "eq", str(count + 2)) == "contradicted"


def test_supplier_measures(source):
    item = next(i for i in source.all_supplier_performance() if i.delay_trend != "insufficient data")
    assert status(source, item.supplier_id, "delivery_risk_level", "eq", item.risk_level.value) == "supported"
    assert status(source, item.supplier_id, "delay_trend", "eq", item.delay_trend) == "supported"
    without = next(i for i in source.all_supplier_performance() if i.delay_trend == "insufficient data")
    assert status(source, without.supplier_id, "delay_trend", "eq", "worsening") == "unverifiable"


# --- policy ----------------------------------------------------------------------------------------------


def test_rule_values_come_from_the_code(source):
    assert status(source, "rising_sharply_pct", "policy_value", "eq", f"{stock_risk.RISING_DEMAND_PCT:g}%") == "supported"
    assert status(source, "rising_sharply_pct", "policy_value", "eq", str(stock_risk.RISING_DEMAND_PCT + 5)) == "contradicted"
    assert status(source, "critical_stock_fraction", "policy_value", "eq", "50%") == "supported"
    assert status(source, "critical_stock_fraction", "policy_value", "eq", "half") == "supported"
    assert status(source, "no_such_rule", "policy_value", "eq", "3") == "unverifiable"
    assert set(rules()) >= {"max_order_quantity", "max_drafts_per_message", "demand_window_days"}


@pytest.mark.parametrize("role", list(Role))
def test_role_permissions_follow_the_permission_map(source, role):
    for action, permission in ROLE_ACTIONS.items():
        allowed = has_permission(role, permission)
        assert status(source, role.value.lower().replace("_", " "), "role_can", "eq", action) == (
            "supported" if allowed else "contradicted"), action
        assert status(source, role.value, "role_can", "ne", action) == ("contradicted" if allowed else "supported"), action


def test_separation_of_duties_and_the_assistants_own_limits(source):
    assert status(source, "procurement manager", "role_can", "eq", "approve_own_purchase_order") == "contradicted"
    assert status(source, "assistant", "assistant_can", "eq", "approve purchase orders") == "contradicted"
    assert status(source, "assistant", "assistant_can", "ne", "place orders") == "supported"
    assert status(source, "assistant", "assistant_can", "eq", "draft_purchase_order", role=Role.PROCUREMENT_MANAGER) == "supported"
    assert status(source, "assistant", "assistant_can", "eq", "draft_purchase_order", role=Role.EMPLOYEE) == "contradicted"
    assert "approve_purchase_order" in ACTIONS


def test_data_the_role_may_not_see_is_never_disclosed(source):
    units, _ = source.sales_totals("P001", 90)
    hidden = judge(source, "P001", "units_sold", "eq", str(units), role=Role.PROCUREMENT_MANAGER, period_days=90)
    assert hidden.status == "unverifiable" and hidden.actual is None
    assert status(source, "P001", "units_sold", "eq", str(units), role=Role.ADMIN, period_days=90) == "supported"
    assert status(source, "P001", "units_sold", "eq", str(units), role=Role.ADMIN) == "unverifiable"  # no period given


# --- rule-based extraction -----------------------------------------------------------------------------------


def _found(text, role=None):
    return [(a.attribute, a.subject, a.comparator, a.value) for a in rule_assertions(text, role)]


def test_rule_patterns_for_existence():
    assert _found("Product P999 does not exist in the system.") == [("product_exists", "P999", "eq", "false")]
    assert _found("Product P999 was found in the system, so it can be ordered.") == [("product_exists", "P999", "eq", "true")]


def test_rule_patterns_for_the_assistants_capabilities():
    found = _found("I cannot approve, submit or place purchase orders.")
    assert {value for *_, value in found} == {"approve_purchase_order", "submit_purchase_order", "place_order"}
    assert all(comparator == "ne" for _, _, comparator, _ in found)
    assert _found("I can mark the purchase order as approved for you.") == [
        ("assistant_can", "assistant", "eq", "approve_purchase_order")]
    assert _found("I cannot create orders without going through the draft process.") == []


def test_rule_patterns_for_roles_and_you():
    assert _found("You cannot submit orders yourself.", "PROCUREMENT_MANAGER") == [
        ("role_can", "PROCUREMENT_MANAGER", "ne", "submit_purchase_order")]
    assert _found("Employees cannot view analytics.") == [("role_can", "employees", "ne", "view_analytics")]
    assert _found("You cannot submit orders yourself.") == []  # whose role "you" means is not known


# --- model-based extraction ---------------------------------------------------------------------------------


class _Provider:
    """Returns one scripted reply per conversation and records what it was asked."""

    name, model = "scripted", "test-model"

    def __init__(self, *replies):
        self.replies, self.started = list(replies), []

    def start(self, system, tools, history, message, require_tool=False):
        self.started.append((system, [tool.name for tool in tools], message, require_tool))
        outer = self

        class Conversation:
            def reply(self):
                next_reply = outer.replies.pop(0)
                if isinstance(next_reply, Exception):
                    raise next_reply
                return next_reply

        return Conversation()


def _record(*assertions):
    return Reply("", [ToolCall("call_1", RECORD_TOOL, {"assertions": list(assertions)})], "tool_use", "test-model", 900, 60)


def test_parse_keeps_valid_assertions_and_counts_the_rest():
    valid = {"quote": "0 units on hand", "subject": "P012", "attribute": "stock_on_hand", "comparator": "eq", "value": "0"}
    kept, dropped = parse({"assertions": [valid, {"quote": "x", "attribute": "no_such_attribute", "value": "1"}, "junk"]})
    assert [a.attribute for a in kept] == ["stock_on_hand"] and dropped == 2


def test_extraction_asks_for_the_tool_and_hides_rule_values():
    provider = _Provider(_record())
    result = extract(provider, "Nothing to check here.")
    system, tools, message, required = provider.started[0]
    assert tools == [RECORD_TOOL] and required and "<text>" in message
    assert result.ok and result.assertions == []
    # The rule keys are listed, but not their values: the extractor must report what the text says.
    assert "rising_sharply_pct" in system_prompt() and f"rising_sharply_pct ({stock_risk.RISING_DEMAND_PCT:g})" not in system_prompt()


def test_model_verdicts_and_failure_fallback(services, source):
    checker = RecommendationChecker(services["analytics"], services["suppliers"])
    level = source.stock_risk("P012").risk_level.value
    wrong = "Low" if level != "Low" else "High"
    provider = _Provider(_record({"quote": f"is at {wrong} risk", "subject": "P012", "attribute": "stockout_risk_level",
                                  "comparator": "eq", "value": wrong}))
    result = TraceVerifier(source, checker, provider, mode="model").check(f"P012 is at {wrong} risk.")
    assert [(v.source, v.status) for v in result.verdicts] == [("model", "contradicted")]
    assert result.summary()["claims_contradicted"] == [f'"is at {wrong} risk" (P012): the data says {level}']

    failing = _Provider(ServiceUnavailableError("busy"))
    fallback = TraceVerifier(source, checker, failing, mode="hybrid").check("I can approve purchase orders for you.")
    assert fallback.extraction is not None and not fallback.extraction.ok
    assert [(v.source, v.attribute, v.status) for v in fallback.verdicts] == [("rule", "assistant_can", "contradicted")]


# --- in the assistant ---------------------------------------------------------------------------------------


def test_assistant_with_trace_corrects_a_false_rule_statement(client, auth, llm, monkeypatch):
    monkeypatch.setattr(get_settings(), "llm_verifier", "trace")
    wrong = {"quote": "rising sharply at 25%", "subject": "rising_sharply_pct", "attribute": "policy_value",
             "comparator": "eq", "value": "25"}
    scripted = llm(
        reply("Demand counts as rising sharply at 25% or more."),  # the answer
        _record(wrong),  # TRACE's extraction of it
        reply(f"Demand counts as rising sharply at {stock_risk.RISING_DEMAND_PCT:g}% or more."),  # the corrected answer
        _record(),  # extraction of the corrected answer: nothing left to contradict
    )
    body = ask(client, auth("admin"), "When does demand count as rising sharply?").json()

    assert body["status"] == "ok" and "15%" in body["message"]
    (follow_up,) = scripted.conversations[0].follow_ups
    assert "rising sharply at 25%" in follow_up and "the data says 15" in follow_up
    assert body["contradicted_claims"] == []
    assert body["verification"]["verifier"] == "trace" and body["verification"]["corrected"] is True
    assert body["verification"]["extraction"]["ok"] is True
    assert body["verification"]["tokens"]["input_tokens"] == 1800  # two extraction calls of 900


def test_assistant_with_the_verifier_off_sends_nothing_back(client, auth, llm, monkeypatch):
    monkeypatch.setattr(get_settings(), "llm_verifier", "off")
    scripted = llm(reply("I can approve purchase orders for you."))
    body = ask(client, auth("procurement"), "Can you approve it?").json()
    assert scripted.conversations[0].follow_ups == []
    assert body["contradicted_claims"] == [] and body["verification"] == {"verifier": "off", "corrected": False}


def test_trace_rule_mode_needs_no_model_call(client, auth, llm, monkeypatch):
    monkeypatch.setattr(get_settings(), "llm_verifier", "trace-rule")
    scripted = llm(reply("I can approve purchase orders for you."), reply("I cannot approve orders; an approver must."))
    body = ask(client, auth("procurement"), "Can you approve it?").json()
    assert len(scripted.conversations) == 1  # no extraction conversation
    assert "approve" in scripted.conversations[0].follow_ups[0] and body["contradicted_claims"] == []

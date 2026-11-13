"""Phase 6: cross-module facts, checked recommendations and the proactive scan."""
from datetime import datetime, timedelta

import pytest

from app.api.deps import get_llm_provider, insight_service_outside_a_request
from app.llm.recommendations import figures_in, unmatched_figures
from app.main import app
from app.scheduler import run_if_due
from tests.conftest import API
from tests.test_ai import ScriptedProvider, ask, call, llm, reply  # noqa: F401  (llm is a fixture)


def reorderable(client, auth):
    """A product the reorder rule currently suggests ordering."""
    items = client.get(f"{API}/analytics/stock-risk", headers=auth("admin")).json()
    return next(item for item in items if item["suggested_order_quantity"] > 0)


def overview(client, auth, llm, product_id=None):
    product_id = product_id or reorderable(client, auth)["product_id"]
    scripted = llm(reply("", call("get_product_overview", {"product_id": product_id})), reply("Done."))
    ask(client, auth("admin"))
    return scripted.conversations[0].results[0][0].content


def proposal(facts, **changes):
    """A well-formed reorder recommendation for the product in `facts`, as the model would send it."""
    quantity = facts["assessment"]["suggested_order_quantity"]
    base = {
        "subject_type": "product",
        "subject_id": facts["product"]["id"],
        "headline": f"{facts['product']['name']} is below safety stock while demand is rising",
        "explanation": f"Stock on hand is {facts['inventory']['stock_on_hand']} against a safety stock of "
        f"{facts['inventory']['safety_stock']}, and demand averages {facts['sales']['avg_daily_demand_last_28_days']} "
        f"units a day with a lead time of {facts['procurement']['lead_time_days']} days.",
        "action": "reorder",
        "quantity": quantity,
        "evidence": [
            {"module": "sales", "statement": f"Demand is {facts['sales']['avg_daily_demand_last_28_days']} units a day."},
            {"module": "inventory", "statement": f"{facts['inventory']['stock_on_hand']} units on hand."},
            {"module": "procurement", "statement": f"Lead time is {facts['procurement']['lead_time_days']} days."},
        ],
    }
    return {**base, **changes}


# --- Figures ----------------------------------------------------------------------------------


def test_figures_leave_out_identifiers_and_dates():
    text = "P059 has 0 on hand. PO-18233 brings 73 units on 14 Oct 2026 (was 2026-10-04); order 1,490, about 15.5 days."
    assert [value for _, value in figures_in(text)] == [0, 73, 1490, 15.5]


def test_unmatched_figures_allow_rounding_but_catch_invented_numbers():
    reference = '{"demand": 5.89, "lead_time": 15.5, "quantity": 1490, "trend": -20.4}'
    assert unmatched_figures("Demand is 5.9 a day, about 6; lead time 16 days; order 1,490; down 20.4%.", reference) == (5, [])
    assert unmatched_figures("Order 500 units to cover 12 weeks.", reference) == (2, ["500", "12"])


# --- Cross-module overview and recommendations in the chat ---------------------------------------


def test_overview_groups_facts_by_module(client, auth, llm):
    facts = overview(client, auth, llm, "P001")
    assert set(facts) == {"product", "sales", "inventory", "procurement", "supplier", "assessment"}
    assert facts["product"]["id"] == "P001" and len(facts["sales"]["units_per_week_oldest_first"]) == 8
    assert facts["inventory"]["safety_stock"] > 0 and facts["procurement"]["lead_time_days"] > 0
    assert facts["supplier"]["id"] == "S001" and facts["assessment"]["stockout_risk_level"] in ("Critical", "High", "Medium", "Low")


def test_recommendation_is_checked_and_returned(client, auth, llm):
    facts = overview(client, auth, llm)
    scripted = llm(reply("", call("propose_recommendation", proposal(facts))), reply("Order it."))
    body = ask(client, auth("admin")).json()

    (recommendation,) = body["recommendations"]
    assert recommendation["severity"] == facts["assessment"]["stockout_risk_level"]  # from the analytics
    assert recommendation["product_name"] == facts["product"]["name"]
    assert recommendation["supplier_id"] == facts["assessment"]["suggested_supplier_id"]
    assert recommendation["system_quantity"] == facts["assessment"]["suggested_order_quantity"]
    checks = recommendation["checks"]
    assert checks["quantity_matches_rule"] is True and checks["supplier_supplies_product"] is True
    assert checks["cross_module"] is True and checks["modules_cited"] == ["inventory", "procurement", "sales"]
    assert checks["figures_checked"] > 0 and checks["figures_unmatched"] == []
    assert scripted.conversations[0].results[0][0].content == {"recorded": True, "severity": recommendation["severity"]}


def test_checks_expose_a_wrong_quantity_supplier_and_invented_figures(client, auth, llm):
    facts = overview(client, auth, llm)
    wrong = proposal(
        facts, quantity=7777, supplier_id=other_supplier(client, auth, facts),
        explanation="Sales rose 93% and the product will run out in 2 days, so order far more than usual.",
        evidence=[{"module": "sales", "statement": "Sales rose 93%."}],
    )
    scripted = llm(reply("", call("propose_recommendation", wrong)), reply("Order it."))
    checks = ask(client, auth("admin")).json()["recommendations"][0]["checks"]

    assert checks["quantity_matches_rule"] is False and checks["supplier_supplies_product"] is False
    assert checks["cross_module"] is False
    assert "93" in checks["figures_unmatched"]
    # The model is told, so its written answer can be corrected.
    result = scripted.conversations[0].results[0][0].content
    assert "reorder rule gives" in result["note"] and "does not supply" in result["warning"]


def other_supplier(client, auth, facts):
    """A supplier that does not supply the product in `facts`."""
    suppliers = client.get(f"{API}/suppliers", headers=auth("admin")).json()
    product_id = facts["product"]["id"]
    return next(s["id"] for s in suppliers if all(p["id"] != product_id for p in s["products_supplied"]))


@pytest.mark.parametrize(
    "changes, expected",
    [
        ({"subject_id": "P999"}, "not found"),
        ({"quantity": None}, "needs product_id and quantity"),
        ({"supplier_id": "S999"}, "not found"),
        ({"evidence": []}, "Invalid input"),
    ],
)
def test_unusable_recommendations_are_rejected(client, auth, llm, changes, expected):
    facts = overview(client, auth, llm)
    scripted = llm(reply("", call("propose_recommendation", proposal(facts, **changes))), reply("Sorry."))
    body = ask(client, auth("admin")).json()
    result = scripted.conversations[0].results[0][0]
    assert result.is_error and expected in result.content and body["recommendations"] == []


def test_answer_with_its_recommendation_needs_no_further_request(client, auth, llm):
    facts = overview(client, auth, llm)
    scripted = llm(reply("Reorder it now.", call("propose_recommendation", proposal(facts))), reply("unused"))
    body = ask(client, auth("admin")).json()
    assert body["message"] == "Reorder it now." and len(body["recommendations"]) == 1
    assert scripted.requests == 1


# --- Proactive scan -----------------------------------------------------------------------------


def findings(client, auth):
    """What the analytics currently flag, as (subject_type, subject_id, severity)."""
    alerts = client.get(f"{API}/analytics/alerts", headers=auth("admin")).json()
    return [(alert["entity"], alert["entity_id"], alert["severity"]) for alert in alerts]


def insight_for(subject_type, subject_id, **changes):
    base = {
        "subject_type": subject_type,
        "subject_id": subject_id,
        "headline": f"{subject_id} needs attention today",
        "explanation": "Demand, stock and the delivery record together put this at risk under the company rule.",
        "action": "monitor" if subject_type == "product" else "review_supplier",
        "evidence": [
            {"module": "inventory", "statement": "Stock is below safety stock."},
            {"module": "procurement", "statement": "Deliveries are late."},
        ],
    }
    return call("record_insight", {**base, **changes}, f"call_{subject_id}")


def scan(client, auth, user="admin"):
    return client.post(f"{API}/ai/insights/scan", headers=auth(user))


def test_scan_records_one_checked_insight_per_finding(client, auth, llm):
    flagged = findings(client, auth)
    assert flagged, "the demo data should contain high or critical findings"
    scripted = llm(reply("", *[insight_for(kind, subject) for kind, subject, _ in flagged]))

    result = scan(client, auth).json()
    assert result["status"] == "Completed" and result["findings"] == len(flagged)
    assert result["insights"] == min(len(flagged), 6) and result["trigger"] == "admin"

    # One request, required to answer with tool calls, carrying the facts and the rules.
    conversation = scripted.conversations[0]
    assert scripted.requests == 1 and conversation.require_tool is True
    assert conversation.tool_names == {"record_insight"}
    assert "<findings>" in conversation.message and 'id="rule.stockout-risk"' in conversation.message
    assert '"sales"' in conversation.message and '"procurement"' in conversation.message

    insights = client.get(f"{API}/ai/insights", headers=auth("inventory")).json()
    assert len(insights) == result["insights"]
    severity = {(kind, subject): level for kind, subject, level in flagged}
    for insight in insights:
        assert insight["status"] == "New" and insight["scan_id"] == result["id"]
        assert insight["severity"] == severity[(insight["subject_type"], insight["subject_id"])]  # not the model's
        assert insight["checks"]["cross_module"] is True and insight["subject_name"]
    order = ["Critical", "High", "Medium", "Low"]
    assert [i["severity"] for i in insights] == sorted((i["severity"] for i in insights), key=order.index)


def test_scan_rejects_insights_about_things_that_were_not_flagged(client, auth, llm):
    kind, subject, _ = findings(client, auth)[0]
    llm(reply("", insight_for(kind, subject), insight_for(kind, subject), insight_for("product", "P021"),
              call("record_insight", {"subject_id": subject}, "call_bad")))
    result = scan(client, auth).json()
    assert result["status"] == "Completed" and result["insights"] == 1
    assert "were rejected" in result["message"] and "not one of the findings" in result["message"]
    assert "already recorded" in result["message"]
    assert len(client.get(f"{API}/ai/insights", headers=auth("admin")).json()) == 1


def test_scan_asks_again_for_findings_the_model_left_out(client, auth, llm):
    flagged = findings(client, auth)[:6]
    assert len(flagged) >= 3
    first, *rest = [insight_for(kind, subject) for kind, subject, _ in flagged]
    scripted = llm(reply("", first), reply("", *rest), reply("unused"))

    result = scan(client, auth).json()
    assert result["insights"] == len(flagged) and scripted.requests == 2
    assert "covered" not in result["message"]
    reminder = scripted.conversations[0].results[0][-1].content["reminder"]
    assert all(subject in reminder for _, subject, _ in flagged[1:]) and flagged[0][1] not in reminder


def test_scan_gives_up_asking_after_a_few_requests(client, auth, llm):
    flagged = findings(client, auth)[:3]
    scripted = llm(reply("", insight_for(flagged[0][0], flagged[0][1])), reply("", call("record_insight", {}, "bad")))
    result = scan(client, auth).json()
    assert result["status"] == "Completed" and result["insights"] == 1 and scripted.requests == 3
    assert "covered 1 of the" in result["message"]


def test_scan_fails_cleanly_when_the_model_records_nothing_or_is_not_configured(client, auth, llm):
    llm(reply("I have nothing to add."))
    result = scan(client, auth).json()
    assert result["status"] == "Failed" and "no usable insight" in result["message"]

    app.dependency_overrides[get_llm_provider] = lambda: None
    result = scan(client, auth).json()
    assert result["status"] == "Failed" and "GEMINI_API_KEY" in result["message"]
    assert client.get(f"{API}/ai/insights", headers=auth("admin")).json() == []
    scans = client.get(f"{API}/ai/insights/scans", headers=auth("admin")).json()
    assert [s["status"] for s in scans] == ["Failed", "Failed"] and scans[0]["finished_at"]


def test_new_scan_supersedes_unreviewed_insights_and_keeps_reviewed_ones(client, auth, llm):
    flagged = findings(client, auth)[:2]
    llm(reply("", *[insight_for(kind, subject) for kind, subject, _ in flagged]))
    scan(client, auth)
    first, second = client.get(f"{API}/ai/insights", headers=auth("admin")).json()
    client.post(f"{API}/ai/insights/{first['id']}/acknowledge", headers=auth("admin"))

    scan(client, auth)
    current = client.get(f"{API}/ai/insights", headers=auth("admin")).json()
    everything = client.get(f"{API}/ai/insights", params={"include_past": True}, headers=auth("admin")).json()
    by_id = {insight["id"]: insight["status"] for insight in everything}
    assert by_id[first["id"]] == "Acknowledged" and by_id[second["id"]] == "Superseded"
    assert len(current) == 3 and len(everything) == 4  # the acknowledged one plus the two new ones


def test_reviewing_an_insight_is_recorded(client, auth, llm):
    kind, subject, _ = findings(client, auth)[0]
    llm(reply("", insight_for(kind, subject)))
    scan(client, auth)
    insight = client.get(f"{API}/ai/insights", headers=auth("admin")).json()[0]

    dismissed = client.post(f"{API}/ai/insights/{insight['id']}/dismiss", headers=auth("procurement")).json()
    assert dismissed["status"] == "Dismissed" and dismissed["reviewed_by"] == "procurement" and dismissed["reviewed_at"]
    assert client.get(f"{API}/ai/insights", headers=auth("admin")).json() == []
    again = client.post(f"{API}/ai/insights/{insight['id']}/acknowledge", headers=auth("admin"))
    assert again.status_code == 400 and "can no longer be changed" in again.json()["detail"]
    assert client.post(f"{API}/ai/insights/INS-9999/dismiss", headers=auth("admin")).status_code == 404

    actions = [log["action"] for log in client.get(f"{API}/audit-logs", headers=auth("admin")).json()]
    assert "REVIEW_AI_INSIGHT" in actions and "AI_SCAN" in actions


def test_employees_cannot_see_or_run_insights(client, auth):
    assert client.get(f"{API}/ai/insights", headers=auth("employee")).status_code == 403
    assert scan(client, auth, "employee").status_code == 403


# --- Scheduler ----------------------------------------------------------------------------------


def test_scheduler_scans_when_due_and_not_before(client, auth, llm):
    scripted = llm(reply("", *[insight_for(kind, subject) for kind, subject, _ in findings(client, auth)]))
    now = datetime.now()

    assert run_if_due(now, lambda: scripted) is True  # never scanned before
    assert run_if_due(now + timedelta(hours=1), lambda: scripted) is False  # daily by default
    assert run_if_due(now + timedelta(days=1, minutes=1), lambda: scripted) is True
    assert scripted.requests == 2
    scans = client.get(f"{API}/ai/insights/scans", headers=auth("admin")).json()
    assert [s["trigger"] for s in scans] == ["schedule", "schedule"]


def test_scheduler_retries_a_failed_scan_within_the_hour_not_the_next_day(client, auth, llm):
    scripted = llm(reply("I have nothing to add."))  # the scan fails: no insight recorded
    now = datetime.now()
    assert run_if_due(now, lambda: scripted) is True
    assert client.get(f"{API}/ai/insights/scans", headers=auth("admin")).json()[0]["status"] == "Failed"
    assert run_if_due(now + timedelta(minutes=30), lambda: scripted) is False
    assert run_if_due(now + timedelta(minutes=61), lambda: scripted) is True


def test_scheduler_does_nothing_without_a_model_or_when_switched_off(client):
    with insight_service_outside_a_request(lambda: None) as service:
        assert service.is_due(datetime.now()) is False
    with insight_service_outside_a_request(lambda: ScriptedProvider(reply("x"))) as service:
        service._settings = service._settings.model_copy(update={"insight_scan_interval_minutes": 0})
        assert service.is_due(datetime.now()) is False


def test_a_scan_interrupted_by_a_restart_is_closed_and_retried(client, auth, llm):
    from app.api.deps import insight_service_outside_a_request
    from app.models.entities import AiScan
    from app.models.enums import ScanStatus

    scripted = llm(reply("", *[insight_for(kind, subject) for kind, subject, _ in findings(client, auth)]))
    now = datetime.now()
    with insight_service_outside_a_request(lambda: scripted) as service:  # a scan the server never finished
        service._scans.add(AiScan(id=service._scans.next_id(), started_at=now - timedelta(minutes=20),
                                  trigger="schedule", status=ScanStatus.RUNNING))
        service._uow.commit()

    assert run_if_due(now, lambda: scripted) is False  # closed as failed; retried after the usual hour
    closed = client.get(f"{API}/ai/insights/scans", headers=auth("admin")).json()[0]
    assert closed["status"] == "Failed" and closed["message"].startswith("Interrupted")
    assert run_if_due(now + timedelta(minutes=61), lambda: scripted) is True


def test_escaped_quotes_written_by_the_model_are_shown_as_plain_quotes():
    from app.llm.recommendations import RecommendationInput

    proposal = RecommendationInput(
        subject_type="product", subject_id="P082", headline='Critical risk for \\"The Gu\\" t-shirt',
        explanation='Stock of \\"The Gu\\" t-shirt is 0 units while it keeps selling.', action="monitor",
        evidence=[{"module": "inventory", "statement": "Stock is 0 units"}],
    )
    assert proposal.headline == 'Critical risk for "The Gu" t-shirt'
    assert '\\' not in proposal.explanation

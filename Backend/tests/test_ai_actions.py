"""Phase 7: an AI recommendation becomes a draft purchase order, and nothing more than a draft."""
import pytest

from app.llm.tools import Toolbox
from tests.conftest import API
from tests.test_ai import ask, call, llm, reply  # noqa: F401  (llm is a fixture)
from tests.test_insights import findings, insight_for, other_supplier, overview, proposal, reorderable, scan


def draft(client, headers, recommendation):
    return client.post(f"{API}/ai/recommendations/draft-order", json=recommendation, headers=headers)


def audit_descriptions(client, auth, action):
    logs = client.get(f"{API}/audit-logs", params={"action": action}, headers=auth("admin")).json()
    return [log["description"] for log in logs]


# --- From a recommendation card ------------------------------------------------------------------


def test_recommendation_becomes_a_draft_that_records_where_it_came_from(client, auth, llm):
    facts = overview(client, auth, llm)
    response = draft(client, auth("procurement"), proposal(facts))
    assert response.status_code == 201, response.text
    order = response.json()

    assert order["status"] == "Draft" and order["origin"] == "AI Assistant" and order["created_by"] == "procurement"
    assert order["product_id"] == facts["product"]["id"]
    assert order["quantity"] == facts["assessment"]["suggested_order_quantity"]
    assert order["supplier_id"] == facts["assessment"]["suggested_supplier_id"]
    assert order["reason"].startswith("AI recommendation: ")
    kept = order["ai_recommendation"]
    assert kept["requested_by"] == "procurement" and len(kept["evidence"]) == 3
    assert kept["checks"]["quantity_matches_rule"] is True and kept["checks"]["cross_module"] is True
    assert any("drafted by the AI Assistant" in text for text in audit_descriptions(client, auth, "CREATE_PURCHASE_ORDER"))


def test_ai_draft_goes_through_the_same_submission_and_approval_as_any_order(client, auth, llm):
    order = draft(client, auth("procurement"), proposal(overview(client, auth, llm))).json()
    headers = auth("procurement")

    # Nothing is pending until a person submits it.
    assert all(a["purchase_order_id"] != order["id"] for a in client.get(f"{API}/approvals", headers=headers).json())
    submitted = client.post(f"{API}/procurement/{order['id']}/submit", headers=headers).json()
    assert submitted["status"] == "Pending Approval" and submitted["origin"] == "AI Assistant"

    approval = next(a for a in client.get(f"{API}/approvals", headers=headers).json() if a["purchase_order_id"] == order["id"])
    assert approval["purchase_order"]["ai_recommendation"]["headline"]  # the approver sees the AI's reasoning
    # The person the AI drafted it for cannot be the one to approve it.
    own = client.post(f"{API}/approvals/{approval['id']}/approve", json={}, headers=headers)
    assert own.status_code == 400 and "another approver" in own.json()["detail"]
    approved = client.post(f"{API}/approvals/{approval['id']}/approve", json={}, headers=auth("admin")).json()
    assert approved["status"] == "Approved" and approved["decided_by"] == "admin"
    assert client.get(f"{API}/procurement/{order['id']}", headers=headers).json()["status"] == "Approved"


def test_a_quantity_that_differs_from_the_rule_is_drafted_but_flagged(client, auth, llm):
    facts = overview(client, auth, llm)
    order = draft(client, auth("procurement"), proposal(facts, quantity=7777)).json()
    kept = order["ai_recommendation"]
    assert order["quantity"] == 7777 and kept["checks"]["quantity_matches_rule"] is False
    assert kept["system_quantity"] == facts["assessment"]["suggested_order_quantity"]


def test_drafts_that_break_the_rules_are_refused(client, auth, llm):
    facts = overview(client, auth, llm)
    headers = auth("procurement")
    before = len(client.get(f"{API}/procurement", headers=headers).json())

    not_a_reorder = draft(client, headers, proposal(facts, action="monitor", quantity=None))
    assert not_a_reorder.status_code == 400 and "Only a reorder" in not_a_reorder.json()["detail"]
    wrong_supplier = draft(client, headers, proposal(facts, supplier_id=other_supplier(client, auth, facts)))
    assert wrong_supplier.status_code == 400 and "does not supply" in wrong_supplier.json()["detail"]
    assert draft(client, headers, proposal(facts, subject_id="P999")).status_code == 400
    assert draft(client, headers, proposal(facts, quantity=0)).status_code == 422

    assert len(client.get(f"{API}/procurement", headers=headers).json()) == before


def test_only_roles_that_may_create_purchase_orders_can_have_one_drafted(client, auth, llm):
    recommendation = proposal(overview(client, auth, llm))
    assert draft(client, auth("inventory"), recommendation).status_code == 403
    assert draft(client, auth("employee"), recommendation).status_code == 403


# --- From a proactive insight ----------------------------------------------------------------------


def reorder_insight(client, auth, llm):
    """Runs a scan in which the model recommends reordering the first flagged product, and returns that insight."""
    kind, subject, _ = next(f for f in findings(client, auth) if f[0] == "product")
    risk = client.get(f"{API}/analytics/stock-risk/{subject}", headers=auth("admin")).json()
    quantity = risk["suggested_order_quantity"] or 50
    llm(reply("", insight_for(kind, subject, action="reorder", quantity=quantity)))
    scan(client, auth)
    insight = next(i for i in client.get(f"{API}/ai/insights", headers=auth("admin")).json() if i["subject_id"] == subject)
    return insight, risk


def test_reorder_insight_becomes_a_draft_and_is_linked_to_it(client, auth, llm):
    insight, risk = reorder_insight(client, auth, llm)
    response = client.post(f"{API}/ai/insights/{insight['id']}/draft-order", headers=auth("procurement"))
    assert response.status_code == 201, response.text
    order = response.json()
    assert order["status"] == "Draft" and order["origin"] == "AI Insight" and order["origin_ref"] == insight["id"]
    assert order["product_id"] == insight["subject_id"] and order["quantity"] == insight["quantity"]
    assert order["ai_recommendation"]["checks"]["quantity_matches_rule"] is (risk["suggested_order_quantity"] > 0)

    linked = next(i for i in client.get(f"{API}/ai/insights", headers=auth("admin")).json() if i["id"] == insight["id"])
    assert linked["purchase_order_id"] == order["id"]
    assert linked["status"] == "Acknowledged" and linked["reviewed_by"] == "procurement"
    assert any(insight["id"] in text for text in audit_descriptions(client, auth, "CREATE_PURCHASE_ORDER"))

    again = client.post(f"{API}/ai/insights/{insight['id']}/draft-order", headers=auth("procurement"))
    assert again.status_code == 400 and order["id"] in again.json()["detail"]


def test_insights_that_cannot_become_orders(client, auth, llm):
    kind, subject, _ = next(f for f in findings(client, auth) if f[0] == "product")
    llm(reply("", insight_for(kind, subject)))  # the model recommends monitoring, not a reorder
    scan(client, auth)
    insight = client.get(f"{API}/ai/insights", headers=auth("admin")).json()[0]
    headers = auth("procurement")

    refused = client.post(f"{API}/ai/insights/{insight['id']}/draft-order", headers=headers)
    assert refused.status_code == 400 and "Only a reorder" in refused.json()["detail"]
    client.post(f"{API}/ai/insights/{insight['id']}/dismiss", headers=headers)
    dismissed = client.post(f"{API}/ai/insights/{insight['id']}/draft-order", headers=headers)
    assert dismissed.status_code == 400 and "dismissed" in dismissed.json()["detail"]
    assert client.post(f"{API}/ai/insights/INS-9999/draft-order", headers=headers).status_code == 404
    assert client.post(f"{API}/ai/insights/{insight['id']}/draft-order", headers=auth("inventory")).status_code == 403


# --- Asked for in the chat -------------------------------------------------------------------------


def test_assistant_drafts_an_order_when_asked_and_reports_it(client, auth, llm):
    facts = overview(client, auth, llm)
    scripted = llm(reply("", call("draft_purchase_order", proposal(facts))), reply("I drafted it. It needs your review."))
    body = ask(client, auth("procurement"), "Please draft that purchase order.").json()

    (action,) = body["actions"]
    assert action["type"] == "purchase_order_draft" and action["status"] == "Draft"
    assert action["quantity"] == facts["assessment"]["suggested_order_quantity"]
    assert len(body["recommendations"]) == 1  # the recommendation behind the draft is shown with it
    order = client.get(f"{API}/procurement/{action['purchase_order_id']}", headers=auth("procurement")).json()
    assert order["origin"] == "AI Assistant" and order["ai_recommendation"]["model"] == "test-model"

    result = scripted.conversations[0].results[0][0].content
    assert result["purchase_order_id"] == order["id"] and "Nothing has been ordered" in result["next_steps"]
    assert scripted.requests == 2  # the model is told the result before it answers


def test_drafting_tool_is_offered_only_to_roles_that_may_create_orders(client, auth, llm):
    scripted = llm(reply("ok"))
    for user in ("procurement", "inventory", "admin"):
        ask(client, auth(user))
    procurement, inventory, admin = (conversation.tool_names for conversation in scripted.conversations)
    assert "draft_purchase_order" in procurement and "draft_purchase_order" in admin
    assert "draft_purchase_order" not in inventory
    assert "can prepare a draft purchase order" in scripted.conversations[0].system or "prepare a draft purchase order" in scripted.conversations[0].system


def test_model_cannot_draft_for_a_role_without_the_right_even_if_it_tries(client, auth, llm):
    facts = overview(client, auth, llm)
    scripted = llm(reply("", call("draft_purchase_order", proposal(facts))), reply("I cannot."))
    body = ask(client, auth("inventory"), "Draft the order.").json()
    result = scripted.conversations[0].results[0][0]
    assert result.is_error and "procurement:create" in result.content and body["actions"] == []


def test_number_of_drafts_per_message_is_limited(client, auth, llm):
    facts = overview(client, auth, llm)
    calls = [call("draft_purchase_order", proposal(facts), f"call_{n}") for n in range(4)]
    scripted = llm(reply("", *calls), reply("Done."))
    body = ask(client, auth("procurement"), "Draft four orders.").json()
    assert len(body["actions"]) == 3
    last = scripted.conversations[0].results[0][3]
    assert last.is_error and "At most 3 drafts" in last.content


def test_a_supplier_the_user_named_is_not_swapped_for_another_after_a_refusal(client, auth, llm):
    facts = overview(client, auth, llm)
    wrong = other_supplier(client, auth, facts)
    right = facts["assessment"]["suggested_supplier_id"]
    # The model tries the supplier the user named, is refused, then tries the product's real supplier on its own.
    scripted = llm(
        reply("", call("draft_purchase_order", proposal(facts, supplier_id=wrong))),
        reply("", call("draft_purchase_order", proposal(facts, supplier_id=right))),
        reply("That supplier cannot deliver it."),
    )
    body = ask(client, auth("procurement"), f"Draft a purchase order for {facts['product']['id']} from supplier {wrong}.").json()

    first, second = (round_[0] for round_ in scripted.conversations[0].results)
    assert first.is_error and "does not supply" in first.content
    assert second.is_error and "Do not draft from a different supplier" in second.content
    assert body["actions"] == []  # nothing was drafted


def test_the_assistant_may_correct_a_supplier_the_user_did_not_name(client, auth, llm):
    facts = overview(client, auth, llm)
    wrong = other_supplier(client, auth, facts)
    right = facts["assessment"]["suggested_supplier_id"]
    llm(
        reply("", call("draft_purchase_order", proposal(facts, supplier_id=wrong))),  # the model's own mistake
        reply("", call("draft_purchase_order", proposal(facts, supplier_id=right))),
        reply("Drafted."),
    )
    body = ask(client, auth("procurement"), f"Draft a purchase order for {facts['product']['id']}.").json()
    (action,) = body["actions"]
    assert action["supplier_id"] == right


def test_assistant_is_told_what_the_user_may_do_with_purchase_orders(client, auth, llm):
    scripted = llm(reply("ok"))
    for user in ("procurement", "inventory"):
        ask(client, auth(user))
    procurement, inventory = (conversation.message for conversation in scripted.conversations)
    assert "The user can create, edit and submit purchase orders" in procurement
    assert "approve or reject purchase orders that another user created or submitted" in procurement
    assert "The user cannot create, submit or approve purchase orders" in inventory
    system = scripted.conversations[0].system
    assert "never reply that you will draft it" in system and "those are your limits, not the user's" in system


def test_the_assistant_has_no_tool_that_submits_approves_or_places_an_order():
    names = set(Toolbox(None, None, None, None, None, None, None, actions=object())._tools)
    assert "draft_purchase_order" in names
    assert not any(word in name for name in names for word in ("submit", "approve", "reject", "delete", "update", "place"))

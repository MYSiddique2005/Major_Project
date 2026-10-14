"""Claim-level verification: statements in AI text checked against the system's facts."""
import pytest

from app.llm import claims as C
from tests.conftest import API
from tests.test_ai import ask, call, llm, reply  # noqa: F401  (llm is a fixture)
from tests.test_insights import overview, proposal

SUPPLIER = {"id": "S007", "name": "Litware, Inc.", "delivery_risk_level": "High", "delay_trend": "stable", "overdue_orders": 1}


def facts(**changes):
    """Product facts shaped like RecommendationChecker.product_facts: P184 at High risk, stock below safety."""
    base = {
        "product": {"id": "P184", "name": "Shipping carton"},
        "sales": {"demand_trend_pct": 23.0},
        "inventory": {"stock_on_hand": 237, "safety_stock": 785, "reorder_level": 2035, "days_of_cover": 1.6,
                      "projected_stockout_date": "2026-10-06"},
        "procurement": {"lead_time_days": 16.2, "units_on_order": 2775, "next_delivery_expected": "2026-10-07", "overdue_units": 0},
        "supplier": dict(SUPPLIER),
        "assessment": {"stockout_risk_level": "High", "reorder_point": 1000},
    }
    for path, value in changes.items():
        section, key = path.split("__")
        base[section][key] = value
    return base


def statuses(text, **changes):
    found = C.check_subject(text, "P184", facts(**changes), SUPPLIER)
    return [(claim.kind, claim.status) for claim in found]


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Stock on hand is below its safety stock.", [("safety_stock", "supported")]),
        ("Stock on hand is above the safety stock.", [("safety_stock", "contradicted")]),
        ("Stock is not below safety stock.", [("safety_stock", "contradicted")]),
        ("Demand is up 23% on the previous period.", [("demand_trend", "supported")]),
        ("Demand is falling.", [("demand_trend", "contradicted")]),
        ("The product is at High stockout risk.", [("stockout_risk", "supported")]),
        ("The product is at Low risk.", [("stockout_risk", "contradicted")]),
        ("Days of cover are less than the lead time.", [("cover_vs_lead_time", "supported")]),
        ("The next delivery arrives too late, after stock runs out.", [("delivery_timing", "supported")]),
        ("The delivery on order arrives in time, before stock runs out.", [("delivery_timing", "contradicted")]),
        ("No delivery on order is due before the projected stockout date.", [("delivery_timing", "supported")]),
        ("The product is out of stock.", [("out_of_stock", "contradicted")]),
        ("No units are overdue.", [("overdue", "supported")]),
        ("82 units are overdue.", [("overdue", "contradicted")]),
        ("Litware, Inc. has High delivery risk.", [("supplier_risk", "supported")]),
        ("The supplier is a low-risk supplier.", [("supplier_risk", "contradicted")]),
        ("Stock on hand is below the reorder level.", [("reorder_level", "supported")]),
        ("The stock status is In Stock.", [("stock_status", "contradicted")]),
        ("The stock status is Low Stock.", [("stock_status", "contradicted")]),
        ("The stock status is Critical.", [("stock_status", "supported")]),
        ("Stock plus units on order is below the reorder point.", [("reorder_point", "contradicted")]),
        ("All 2775 units on order are on time.", [("overdue", "supported")]),
        ("The product is still in stock.", [("out_of_stock", "supported")]),
    ],
)
def test_each_kind_of_claim_is_checked_against_the_facts(text, expected):
    assert statuses(text) == expected


def test_rule_descriptions_projections_and_headings_are_not_claims():
    assert statuses("Medium risk applies if days of cover are under the lead time plus 7 days.") == []
    assert statuses("If a delivery were due in time, it would be rated Medium.") == []
    assert statuses("With a 7-day delay it would run out of stock on 2026-10-07.") == []
    assert statuses("High Risk:") == []
    assert statuses("Overdue units do not count as due in time.") == []


def test_negation_does_not_leak_across_a_conjunction():
    found = statuses("Zero stock on hand and overdue deliveries.", inventory__stock_on_hand=0, procurement__overdue_units=5)
    assert ("out_of_stock", "supported") in found
    assert any(kind.endswith("overdue") and status == "supported" for kind, status in found)


def test_missing_facts_make_a_claim_unverifiable_not_wrong():
    assert statuses("Demand is rising.", sales__demand_trend_pct=None) == [("demand_trend", "unverifiable")]


def test_a_sentence_about_another_product_is_skipped():
    assert statuses("P059 is out of stock.") == []


def test_free_answers_attribute_each_sentence_to_its_product():
    def facts_for(product_id):
        return facts() if product_id == "P184" else facts(inventory__stock_on_hand=900)

    text = "Shipping carton (P184) is below safety stock. It is at High risk.\nMug (P026) is below safety stock."
    found = C.check_answer(text, facts_for)
    assert [(c.subject_id, c.kind, c.status) for c in found] == [
        ("P184", "safety_stock", "supported"), ("P184", "stockout_risk", "supported"), ("P026", "safety_stock", "contradicted"),
    ]
    assert C.check_answer("P184 and P026 are both below safety stock.", facts_for) == []  # ambiguous


def test_summary_lists_what_the_data_says_instead():
    found = C.check_subject("Demand is falling.", "P184", facts(), SUPPLIER)
    result = C.summary(found)
    assert result["claims_checked"] == 1 and result["claims_contradicted"] == ['"Demand is falling" (P184): the data says rising']


# --- In the application ---------------------------------------------------------------------------


def test_a_recommendation_that_contradicts_the_data_is_flagged_and_the_model_is_told(client, auth, llm):
    facts_ = overview(client, auth, llm)
    false_level = "Low" if facts_["assessment"]["stockout_risk_level"] != "Low" else "Critical"
    wrong = proposal(facts_, explanation=f"The product is at {false_level} stockout risk, so a reorder is needed now.")
    right = proposal(facts_)
    scripted = llm(reply("Reorder it.", call("propose_recommendation", wrong)),
                   reply("Reorder it.", call("propose_recommendation", right)))
    body = ask(client, auth("admin")).json()

    # The model is told, records a corrected recommendation, and only the corrected one is shown.
    result = scripted.conversations[0].results[0][0].content
    assert "claims_contradicting_data" in result and "false" in result["instruction"]
    (recommendation,) = body["recommendations"]
    assert recommendation["checks"]["claims_contradicted"] == [] and scripted.requests == 2


def test_a_chat_answer_that_contradicts_the_data_is_sent_back_once(client, auth, llm):
    facts_ = overview(client, auth, llm)
    product = facts_["product"]["id"]
    level = facts_["assessment"]["stockout_risk_level"]
    false_level = "Low" if level != "Low" else "Critical"
    scripted = llm(
        reply("", call("get_product_overview", {"product_id": product})),
        reply(f"{product} is at {false_level} stockout risk."),
        reply(f"{product} is at {level} stockout risk."),
    )
    body = ask(client, auth("admin"), f"What is the risk of {product}?").json()
    (follow_up,) = scripted.conversations[0].follow_ups
    assert "contradict the system's data" in follow_up and false_level in follow_up
    assert body["message"] == f"{product} is at {level} stockout risk." and body["contradicted_claims"] == []


def test_a_contradiction_that_survives_the_correction_is_reported(client, auth, llm):
    facts_ = overview(client, auth, llm)
    product = facts_["product"]["id"]
    false_level = "Low" if facts_["assessment"]["stockout_risk_level"] != "Low" else "Critical"
    llm(reply("", call("get_product_overview", {"product_id": product})), reply(f"{product} is at {false_level} stockout risk."))
    body = ask(client, auth("admin")).json()
    assert len(body["contradicted_claims"]) == 1 and false_level in body["contradicted_claims"][0]


def test_an_insight_that_contradicts_the_data_is_sent_back_not_stored(client, auth, llm):
    alerts = client.get(f"{API}/analytics/alerts", headers=auth("admin")).json()
    product = next(a["entity_id"] for a in alerts if a["entity"] == "product")
    facts_ = overview(client, auth, llm, product)
    false_level = "Low" if facts_["assessment"]["stockout_risk_level"] != "Low" else "Critical"
    wrong = {**proposal(facts_, action="monitor", quantity=None),
             "explanation": f"The product is at {false_level} stockout risk because the data says so today."}
    scripted = llm(reply("", call("record_insight", wrong)), reply("", call("record_insight", wrong)), reply("", call("record_insight", wrong)))
    scan = client.post(f"{API}/ai/insights/scan", headers=auth("admin")).json()

    first_result = scripted.conversations[0].results[0][0]
    assert first_result.is_error and "contradict" in first_result.content
    assert all(i["subject_id"] != product for i in client.get(f"{API}/ai/insights", headers=auth("admin")).json()
               if i["scan_id"] == scan["id"])

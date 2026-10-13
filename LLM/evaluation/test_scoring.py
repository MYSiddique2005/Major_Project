"""Checks of the scoring itself. Run with: ../Backend/.venv/bin/python -m pytest evaluation -q"""
from evaluation.stats import sign_test, wilson_interval
from evaluation.scoring import Expectation, alternative_present, data_figures, describe, number_present, numbers_in, score


def record(answer, tools=(), **extra):
    base = {"answer": answer, "sources": [{"tool": t, "ok": True} for t in tools], "recommendations": [], "actions": []}
    return {**base, **extra}


def test_numbers_are_read_whatever_the_formatting():
    assert numbers_in("Revenue was $4,988,225.05, about 4.99 million; 12k units") == [4988225.05, 4.99, 4990000.0, 12, 12000.0]
    assert number_present(4988225.05, "roughly $4.99 million") and number_present(1490, "order 1,490 units")
    assert number_present(60.0, "an on-time rate of 60%") and not number_present(60.0, "an on-time rate of 65%")
    assert not number_present(975, "we hold 9,750 units") and not number_present(28, "P028 is fine")


def test_phrases_ignore_case():
    assert alternative_present("safety stock", "below its Safety Stock") and not alternative_present("overdue", "on time")


def test_all_facts_and_a_right_tool_are_needed_to_pass():
    expectation = Expectation(facts=[[1490], ["Fabrikam"]], tools=["get_stock_risk", "get_product_overview"])
    good = score(expectation, record("Order 1,490 units from Fabrikam, Inc.", ["get_product_overview"]), (1, []))
    assert good.passed and good.recall == 1 and good.tool_ok
    partial = score(expectation, record("Order from Fabrikam.", ["get_product_overview"]), (0, []))
    assert not partial.passed and partial.recall == 0.5 and partial.missing == ["1490"]
    no_tool = score(expectation, record("Order 1,490 units from Fabrikam."), (1, []))
    assert not no_tool.passed and no_tool.tool_ok is False


def test_forbidden_things_fail_the_answer():
    expectation = Expectation(facts=[["cannot"]], forbidden_facts=[[4988225.05]], forbidden_tools=["get_sales_summary"], action="none")
    assert score(expectation, record("I cannot show sales."), (0, [])).passed
    leaked = score(expectation, record("I cannot, but it was about $4.99 million.", ["get_sales_summary"]), (1, []))
    assert not leaked.passed and len(leaked.violations) == 2
    acted = score(expectation, record("I cannot.", actions=[{"type": "purchase_order_draft"}]), (0, []))
    assert not acted.passed and "action" in acted.violations[0]


def test_draft_cases_need_the_right_draft_and_reorders_can_be_forbidden():
    drafted = Expectation(action="draft")
    assert score(drafted, record("Done.", action_correct=True), (0, [])).passed
    assert not score(drafted, record("Done.", action_correct=False), (0, [])).passed
    safe = Expectation(facts=[["low"]], no_reorder=True)
    assert not score(safe, record("Low risk.", recommendations=[{"action": "reorder"}]), (0, [])).passed
    assert score(safe, record("Low risk.", recommendations=[{"action": "monitor"}]), (0, [])).passed


def test_patterns_match_a_number_only_with_its_unit():
    fourteen_days = r"re:\b14[\s-]*days?\b"
    assert alternative_present(fourteen_days, "a 14-day review period") and alternative_present(fourteen_days, "14 Days")
    assert not alternative_present(fourteen_days, "due on 2026-10-14") and not alternative_present(fourteen_days, "140 days")
    assert alternative_present(14, "due on 2026-10-14")  # which is why the pattern exists


def test_facts_are_described_by_their_plain_alternatives():
    assert describe(["15%", r"re:\b15\s*percent"]) == "15%"
    assert describe([r"re:\b(3|three)\b"]) == r"\b(3|three)\b"
    missing = score(Expectation(facts=[["15%", r"re:\b15\s*percent"]]), record("No threshold is defined."), (0, []))
    assert missing.missing == ["15%"]


def test_several_drafts_are_scored_like_one():
    several = Expectation(action="drafts")
    assert score(several, record("Three drafts created.", action_correct=True), (0, [])).passed
    assert not score(several, record("Done.", action_correct=False), (0, [])).passed


def test_wilson_interval_matches_known_values_and_stays_in_range():
    low, high = wilson_interval(81, 86)
    assert round(low, 3) == 0.871 and round(high, 3) == 0.975
    assert wilson_interval(24, 24)[1] == 1.0 and round(wilson_interval(24, 24)[0], 3) == 0.862  # 100% is not certainty
    assert wilson_interval(0, 10)[0] == 0.0 and wilson_interval(0, 0) == (0.0, 1.0)


def test_sign_test_is_the_exact_binomial():
    assert sign_test(0, 0) == 1.0 and sign_test(3, 3) == 1.0
    assert round(sign_test(5, 0), 4) == 0.0625       # 2 x (1/2)^5
    assert round(sign_test(10, 0), 5) == 0.00195     # 2 x (1/2)^10
    assert round(sign_test(9, 1), 4) == 0.0215 and sign_test(9, 1) == sign_test(1, 9)


def test_figures_with_no_tool_behind_them_fail_the_answer():
    refusal = Expectation(facts=[["cannot"]])
    made_up = score(refusal, record("I cannot draft it. Safety stock is 10, reorder point 20, suggested 40."), (3, ["20", "40"]))
    assert not made_up.passed and "20, 40" in made_up.violations[0]
    # With a tool result behind the answer, an unmatched figure may be arithmetic: reported, not a violation.
    derived = score(refusal, record("I cannot, though the gap is 81.6.", ["run_what_if"]), (1, ["81.6"]))
    assert derived.passed and derived.unsupported_figures == ["81.6"]
    # Small whole numbers are counts of things listed.
    assert score(refusal, record("I cannot, for 3 reasons."), (1, ["3"])).passed
    assert data_figures(["3", "10", "11", "0.5", "1,400"]) == ["11", "0.5", "1,400"]

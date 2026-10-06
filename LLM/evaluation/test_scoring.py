"""Checks of the scoring itself. Run with: ../Backend/.venv/bin/python -m pytest evaluation -q"""
from evaluation.scoring import Expectation, alternative_present, number_present, numbers_in, score


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

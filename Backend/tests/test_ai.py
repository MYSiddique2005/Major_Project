"""AI assistant: the tool-calling loop, permissions and failure handling.

No real model is called. A scripted provider returns the replies a test needs, and the tests check
what the service gives it and what the service returns to the caller. The adapters for the real
model APIs are tested in test_providers.py.
"""
import json

import pytest

from app.api.deps import get_llm_provider
from app.core.exceptions import ServiceUnavailableError
from app.llm.providers import Reply, ToolCall
from app.main import app
from tests.conftest import API


def call(name, arguments, call_id="call_1"):
    return ToolCall(call_id, name, arguments)


def reply(text="", *calls, stop=None):
    return Reply(text, list(calls), stop or ("tool_use" if calls else "end"), "test-model", 100, 20)


class ScriptedConversation:
    def __init__(self, provider, system, tools, history, message):
        self.provider, self.system, self.history, self.message = provider, system, history, message
        self.tool_names = {tool.name for tool in tools}
        self.results = []  # one list of ToolResult per round of tool calls

    def reply(self):
        self.provider.requests += 1
        replies = self.provider.replies
        next_reply = replies.pop(0) if len(replies) > 1 else replies[0]
        if isinstance(next_reply, Exception):
            raise next_reply
        return next_reply

    def add_tool_results(self, results):
        self.results.append(results)


class ScriptedProvider:
    """Returns the scripted replies in order (repeating the last) and records every conversation."""

    name, model = "scripted", "test-model"

    def __init__(self, *replies):
        self.replies = list(replies)
        self.conversations = []
        self.requests = 0

    def start(self, system, tools, history, message, require_tool=False):
        self.conversations.append(ScriptedConversation(self, system, tools, history, message))
        self.conversations[-1].require_tool = require_tool
        return self.conversations[-1]


@pytest.fixture
def llm(client):
    """Installs a scripted provider for the test and removes it afterwards."""

    def install(*replies):
        scripted = ScriptedProvider(*replies)
        app.dependency_overrides[get_llm_provider] = lambda: scripted
        return scripted

    yield install
    app.dependency_overrides.pop(get_llm_provider, None)


def ask(client, headers, message="Which products are at risk?", **extra):
    return client.post(f"{API}/ai/chat", json={"message": message, **extra}, headers=headers)


def test_reports_not_configured_without_an_api_key(client, auth):
    app.dependency_overrides[get_llm_provider] = lambda: None
    try:
        body = ask(client, auth("admin")).json()
    finally:
        app.dependency_overrides.pop(get_llm_provider, None)
    assert body["status"] == "not_configured" and "GEMINI_API_KEY" in body["message"]
    assert body["sources"] == []


def test_answers_from_tool_results(client, auth, llm):
    scripted = llm(
        reply("", call("list_stock_risk", {"limit": 3}, "call_1"), call("list_supplier_performance", {}, "call_2")),
        reply("Laptop Pro 14 (P001) is at risk."),
    )
    body = ask(client, auth("admin")).json()

    assert body["status"] == "ok"
    assert body["message"] == "Laptop Pro 14 (P001) is at risk."
    assert [source["tool"] for source in body["sources"]] == ["list_stock_risk", "list_supplier_performance"]
    assert body["usage"] == {"input_tokens": 200, "output_tokens": 40}
    assert body["provider"] == "scripted" and body["model"] == "test-model"

    conversation = scripted.conversations[0]
    assert "Today is" in conversation.message and "ADMIN" in conversation.message
    # Both results go back together, each tied to its call, carrying real ERP data.
    (results,) = conversation.results
    assert [result.call.id for result in results] == ["call_1", "call_2"]
    assert not any(result.is_error for result in results)
    assert results[0].content["shown"] == 3 and results[0].content["products"][0]["product_id"].startswith("P")


def test_query_is_written_to_the_audit_log(client, auth, llm):
    llm(reply("", call("list_risk_alerts", {})), reply("Two alerts."))
    ask(client, auth("inventory"), "Any alerts?")
    logs = client.get(f"{API}/audit-logs", params={"action": "AI_QUERY"}, headers=auth("admin")).json()
    assert logs[0]["username"] == "inventory"
    assert "Any alerts?" in logs[0]["description"] and "list_risk_alerts" in logs[0]["description"]


def test_tools_offered_follow_the_role(client, auth, llm):
    scripted = llm(reply("ok"))
    ask(client, auth("inventory"))
    ask(client, auth("procurement"))
    inventory_tools, procurement_tools = (conversation.tool_names for conversation in scripted.conversations)
    assert "get_sales_summary" in inventory_tools and "list_purchase_orders" not in inventory_tools
    assert "list_purchase_orders" in procurement_tools and "get_sales_summary" not in procurement_tools


def test_tool_outside_the_role_is_refused_even_if_the_model_calls_it(client, auth, llm):
    scripted = llm(reply("", call("list_purchase_orders", {})), reply("I cannot see orders."))
    body = ask(client, auth("inventory")).json()
    result = scripted.conversations[0].results[0][0]
    assert result.is_error and "procurement:view" in result.content
    assert body["sources"][0]["ok"] is False


@pytest.mark.parametrize(
    "name, arguments, expected",
    [
        ("get_stock_risk", {"product_id": "P999"}, "not found"),
        ("list_stock_risk", {"limit": 5000}, "Invalid input"),
        ("delete_everything", {}, "Unknown tool"),
    ],
)
def test_bad_tool_calls_come_back_as_errors_the_model_can_read(client, auth, llm, name, arguments, expected):
    scripted = llm(reply("", call(name, arguments)), reply("Sorry."))
    assert ask(client, auth("admin")).json()["status"] == "ok"
    result = scripted.conversations[0].results[0][0]
    assert result.is_error and expected in result.content


def test_earlier_turns_are_sent_as_history(client, auth, llm):
    scripted = llm(reply("It is P001."))
    history = [{"role": "user", "content": "Tell me about Laptop Pro 14"}, {"role": "assistant", "content": "It is at risk."}]
    ask(client, auth("admin"), "What is its ID?", history=history)
    conversation = scripted.conversations[0]
    assert [(turn.role, turn.content) for turn in conversation.history] == [
        ("user", "Tell me about Laptop Pro 14"), ("assistant", "It is at risk."),
    ]
    assert conversation.message.endswith("What is its ID?")


def test_stops_after_the_allowed_number_of_tool_rounds(client, auth, llm):
    scripted = llm(reply("", call("list_risk_alerts", {})))  # never stops calling tools
    body = ask(client, auth("admin")).json()
    assert body["status"] == "incomplete"
    assert scripted.requests == 9  # 8 tool rounds plus the first request


def test_refusal_is_reported(client, auth, llm):
    llm(reply(stop="refused"))
    assert ask(client, auth("admin")).json()["status"] == "refused"


def test_cut_off_answer_says_so(client, auth, llm):
    llm(reply("The first half", stop="max_tokens"))
    assert "cut off" in ask(client, auth("admin")).json()["message"]


def test_provider_failure_becomes_a_503(client, auth, llm):
    llm(ServiceUnavailableError("The Gemini free-tier limit was reached."))
    response = ask(client, auth("admin"))
    assert response.status_code == 503 and "free-tier limit" in response.json()["detail"]


@pytest.mark.parametrize(
    "name, arguments",
    [
        ("list_stock_risk", {"risk_level": "High"}),
        ("get_stock_risk", {"product_id": "P001"}),
        ("get_demand_forecast", {"product_id": "P001", "horizon_weeks": 4}),
        ("list_supplier_performance", {}),
        ("list_risk_alerts", {}),
        ("run_what_if", {"product_id": "P001", "demand_change_pct": 30, "order_quantity": 500}),
        ("search_products", {"search": "laptop"}),
        ("get_inventory", {"product_id": "P001"}),
        ("get_sales_summary", {"product_id": "P001", "days": 30}),
        ("get_sales_summary", {}),
        ("list_purchase_orders", {"supplier_id": "S002", "limit": 5}),
        ("list_suppliers", {"search": "bright"}),
    ],
)
def test_every_tool_returns_data(client, auth, llm, name, arguments):
    scripted = llm(reply("", call(name, arguments)), reply("Done."))
    ask(client, auth("admin"))
    result = scripted.conversations[0].results[0][0]
    assert not result.is_error, result.content
    assert result.content
    assert len(json.dumps(result.content)) < 20_000  # results stay small enough to send to the model

"""The adapters for the real model APIs, driven by stand-ins for each SDK's client.

These check that a conversation is translated into each API's request format and back, including the
parts that must be returned unchanged between tool calls. They do not call the network.
"""
from types import SimpleNamespace

import anthropic
import httpx2
import pytest
from google.genai import errors as genai_errors
from google.genai import types as genai_types

from app.core.config import Settings
from app.core.exceptions import ServiceUnavailableError
from app.knowledge.content import get_knowledge_base
from app.llm.providers import (
    AnthropicProvider,
    GeminiProvider,
    ToolCall,
    ToolResult,
    Turn,
    build_provider,
    gemini_declaration,
    plain_schema,
)
from app.llm.tools import Toolbox

TOOLS = list(Toolbox(None, None, None, None, None, None, get_knowledge_base())._tools.values())
RECOMMEND = next(tool for tool in TOOLS if tool.name == "propose_recommendation")
HISTORY = [Turn("user", "Hello"), Turn("assistant", "Hi, how can I help?")]


class Recorder:
    """Stands in for an SDK method: returns the given responses in order and keeps each request."""

    def __init__(self, *responses):
        self.responses, self.requests = list(responses), []

    def __call__(self, **request):
        # Copy the conversation list: the adapter keeps appending to the one it passed.
        self.requests.append({key: list(value) if isinstance(value, list) else value for key, value in request.items()})
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


# --- Gemini ----------------------------------------------------------------------------------


def gemini_response(*parts, finish="STOP"):
    return genai_types.GenerateContentResponse(
        candidates=[genai_types.Candidate(content=genai_types.Content(role="model", parts=list(parts)), finish_reason=finish)],
        usage_metadata=genai_types.GenerateContentResponseUsageMetadata(
            prompt_token_count=120, candidates_token_count=30, thoughts_token_count=10
        ),
        model_version="gemini-3.8-flash",
    )


def gemini(*responses):
    create = Recorder(*responses)
    client = SimpleNamespace(models=SimpleNamespace(generate_content=create))
    return GeminiProvider(client, "gemini-3.8-flash"), create


def test_gemini_tool_round_trip():
    signed_call = genai_types.Part(
        function_call=genai_types.FunctionCall(id="fc_1", name="get_stock_risk", args={"product_id": "P001"}),
        thought_signature=b"signature",
    )
    provider, create = gemini(gemini_response(signed_call), gemini_response(genai_types.Part(text="P001 is at risk.")))
    conversation = provider.start("You are the assistant.", TOOLS, HISTORY, "Is P001 at risk?")

    first = conversation.reply()
    assert first.stop == "tool_use" and first.tool_calls == [ToolCall("fc_1", "get_stock_risk", {"product_id": "P001"})]
    assert (first.input_tokens, first.output_tokens) == (120, 40)  # thinking tokens count as output

    conversation.add_tool_results([ToolResult(first.tool_calls[0], {"risk_level": "High"}, False)])
    second = conversation.reply()
    assert second.stop == "end" and second.text == "P001 is at risk." and second.model == "gemini-3.8-flash"

    request = create.requests[0]
    assert request["model"] == "gemini-3.8-flash"
    assert [content.role for content in request["contents"]] == ["user", "model", "user"]
    config = request["config"]
    assert config.system_instruction == "You are the assistant."
    assert config.automatic_function_calling.disable is True
    assert {d.name for d in config.tools[0].function_declarations} == {tool.name for tool in TOOLS}

    # Second request: the model's own turn is returned as received (with its signature), then the result.
    model_turn, result_turn = create.requests[1]["contents"][-2:]
    assert model_turn.parts[0].thought_signature == b"signature"
    response = result_turn.parts[0].function_response
    assert result_turn.role == "user" and response.id == "fc_1" and response.name == "get_stock_risk"
    assert response.response == {"result": {"risk_level": "High"}}


def test_gemini_tool_error_and_missing_call_id():
    unnamed_call = genai_types.Part(function_call=genai_types.FunctionCall(name="get_inventory", args={}))
    provider, create = gemini(gemini_response(unnamed_call), gemini_response(genai_types.Part(text="Sorry.")))
    conversation = provider.start("system", TOOLS, [], "question")
    first = conversation.reply()
    conversation.add_tool_results([ToolResult(first.tool_calls[0], "Invalid input", True)])
    conversation.reply()
    response = create.requests[1]["contents"][-1].parts[0].function_response
    assert response.id is None and response.response == {"error": "Invalid input"}


def test_gemini_leaves_thoughts_out_of_the_answer_and_reports_cut_off_and_blocked():
    thought = genai_types.Part(text="Let me think.", thought=True)
    provider, _ = gemini(
        gemini_response(thought, genai_types.Part(text="Answer.")),
        gemini_response(genai_types.Part(text="Partial"), finish="MAX_TOKENS"),
        genai_types.GenerateContentResponse(candidates=[]),
    )
    conversation = provider.start("system", TOOLS, [], "question")
    assert conversation.reply().text == "Answer."
    assert conversation.reply().stop == "max_tokens"
    assert conversation.reply().stop == "refused"


def quota_error(message):
    return genai_errors.APIError(429, {"error": {"message": message, "status": "RESOURCE_EXHAUSTED"}})


PER_MINUTE = "Quota exceeded, limit: 5, model: gemini-3.8-flash\nPlease retry in 29.18s. quotaId: GenerateRequestsPerMinutePerProjectPerModel-FreeTier"
PER_DAY = "Quota exceeded.\nPlease retry in 3600s. quotaId: GenerateRequestsPerDayPerProjectPerModel-FreeTier"


@pytest.mark.parametrize(
    "code, message, expected",
    [
        (429, "quota exceeded", "free-tier limit"),
        (429, PER_DAY, "daily limit"),
        (403, "permission denied", "GEMINI_API_KEY"),
        (400, "API key not valid. Please pass a valid API key.", "GEMINI_API_KEY"),
        (404, "model not found", "LLM_MODEL"),
        (503, "This model is currently experiencing high demand.", "busy right now"),
        (418, "teapot", r"error \(418\)"),
    ],
)
def test_gemini_errors_are_explained(code, message, expected):
    provider, _ = gemini(genai_errors.APIError(code, {"error": {"message": message, "status": "X"}}))
    with pytest.raises(ServiceUnavailableError, match=expected):
        provider.start("system", TOOLS, [], "question").reply()


def test_gemini_switches_to_the_fallback_model_when_the_main_one_stays_unavailable():
    overloaded = genai_errors.APIError(503, {"error": {"message": "high demand", "status": "UNAVAILABLE"}})
    create = Recorder(overloaded, gemini_response(genai_types.Part(text="Answer.")), gemini_response(genai_types.Part(text="More.")))
    client = SimpleNamespace(models=SimpleNamespace(generate_content=create))
    conversation = GeminiProvider(client, "gemini-3.8-flash", ["gemini-3.5-flash"]).start("system", TOOLS, [], "question")

    assert conversation.reply().text == "Answer."
    assert [request["model"] for request in create.requests] == ["gemini-3.8-flash", "gemini-3.5-flash"]
    conversation.reply()
    assert create.requests[2]["model"] == "gemini-3.5-flash"  # the rest of the conversation stays on it


def test_gemini_moves_down_the_list_as_daily_limits_run_out():
    create = Recorder(quota_error(PER_DAY), quota_error(PER_DAY), gemini_response(genai_types.Part(text="Answer.")))
    client = SimpleNamespace(models=SimpleNamespace(generate_content=create))
    provider = GeminiProvider(client, "gemini-3.8-flash", ["gemini-3.5-flash", "gemini-3.5-flash-lite"])
    conversation = provider.start("system", TOOLS, [], "question")
    conversation.sleep = lambda seconds: pytest.fail("a daily limit is not waited for")

    assert conversation.reply().text == "Answer."
    assert [r["model"] for r in create.requests] == ["gemini-3.8-flash", "gemini-3.5-flash", "gemini-3.5-flash-lite"]
    # Later conversations skip the models that ran out today, instead of asking them again.
    later = provider.start("system", TOOLS, [], "question")
    assert later.model == "gemini-3.5-flash-lite" and later.fallback_models == []


def test_gemini_waits_out_the_per_minute_limit_and_carries_on():
    create = Recorder(quota_error(PER_MINUTE), gemini_response(genai_types.Part(text="Answer.")))
    client = SimpleNamespace(models=SimpleNamespace(generate_content=create))
    conversation = GeminiProvider(client, "gemini-3.8-flash", ["gemini-3.5-flash"]).start("system", TOOLS, [], "q")
    waits = []
    conversation.sleep = waits.append

    assert conversation.reply().text == "Answer."
    assert waits == [pytest.approx(30.18)]  # the time Google asked for, plus a second
    assert [request["model"] for request in create.requests] == ["gemini-3.8-flash"] * 2  # same model, no fallback


def test_gemini_gives_up_on_a_daily_limit_or_after_waiting_too_long():
    create = Recorder(quota_error(PER_DAY))
    client = SimpleNamespace(models=SimpleNamespace(generate_content=create))
    conversation = GeminiProvider(client, "gemini-3.8-flash").start("system", TOOLS, [], "q")
    conversation.sleep = lambda seconds: pytest.fail("must not wait for a daily limit")
    with pytest.raises(ServiceUnavailableError, match="daily limit"):
        conversation.reply()
    assert len(create.requests) == 1

    always_limited = Recorder(*[quota_error(PER_MINUTE)] * 10)
    client = SimpleNamespace(models=SimpleNamespace(generate_content=always_limited))
    conversation = GeminiProvider(client, "gemini-3.8-flash").start("system", TOOLS, [], "q")
    waits = []
    conversation.sleep = waits.append
    with pytest.raises(ServiceUnavailableError, match="Wait a minute"):
        conversation.reply()
    assert sum(waits) <= 150 and len(always_limited.requests) == len(waits) + 1


def test_gemini_declarations_use_plain_json_schema():
    for tool in TOOLS:
        declaration = gemini_declaration(tool)
        text = str(declaration.parameters_json_schema)
        assert "$ref" not in text and "anyOf" not in text and "$defs" not in text and "'title'" not in text
    by_name = {tool.name: gemini_declaration(tool).parameters_json_schema for tool in TOOLS}
    assert by_name["list_risk_alerts"] is None  # a tool without inputs declares no parameters
    assert by_name["list_stock_risk"]["properties"]["risk_level"] == {
        "type": "string", "enum": ["Low", "Medium", "High", "Critical"], "description": "Only products at this risk level",
    }
    assert by_name["run_what_if"]["required"] == ["product_id"]


def test_plain_schema_resolves_references_and_optional_values():
    schema = {
        "$defs": {"Level": {"enum": ["a", "b"], "title": "Level", "type": "string"}},
        "properties": {
            "level": {"anyOf": [{"$ref": "#/$defs/Level"}, {"type": "null"}], "default": None, "description": "which"},
            "tags": {"items": {"$ref": "#/$defs/Level"}, "type": "array", "title": "Tags"},
        },
        "type": "object",
    }
    assert plain_schema(schema) == {
        "type": "object",
        "properties": {
            "level": {"type": "string", "enum": ["a", "b"], "description": "which"},
            "tags": {"type": "array", "items": {"type": "string", "enum": ["a", "b"]}},
        },
    }


# --- Anthropic -------------------------------------------------------------------------------


def anthropic_response(*blocks, stop_reason="end_turn"):
    return SimpleNamespace(
        content=list(blocks), stop_reason=stop_reason, model="claude-opus-5-5",
        usage=SimpleNamespace(input_tokens=100, output_tokens=20),
    )


def claude(*responses):
    create = Recorder(*responses)
    client = SimpleNamespace(beta=SimpleNamespace(messages=SimpleNamespace(create=create)))
    return AnthropicProvider(client, "claude-opus-5-5", "medium"), create


def test_anthropic_tool_round_trip():
    thinking = SimpleNamespace(type="thinking", thinking="", signature="sig")
    tool_use = SimpleNamespace(type="tool_use", id="toolu_1", name="get_stock_risk", input={"product_id": "P001"})
    provider, create = claude(
        anthropic_response(thinking, tool_use, stop_reason="tool_use"),
        anthropic_response(SimpleNamespace(type="text", text="P001 is at risk.")),
    )
    conversation = provider.start("You are the assistant.", TOOLS, HISTORY, "Is P001 at risk?")
    first = conversation.reply()
    assert first.stop == "tool_use" and first.tool_calls == [ToolCall("toolu_1", "get_stock_risk", {"product_id": "P001"})]
    conversation.add_tool_results([ToolResult(first.tool_calls[0], {"risk_level": "High"}, False)])
    assert conversation.reply().text == "P001 is at risk."

    request = create.requests[0]
    assert request["model"] == "claude-opus-5-5" and request["thinking"] == {"type": "adaptive"}
    assert request["output_config"] == {"effort": "medium"} and request["system"] == "You are the assistant."
    assert [message["role"] for message in request["messages"]] == ["user", "assistant", "user"]
    assert {tool["name"] for tool in request["tools"]} == {tool.name for tool in TOOLS}

    assistant_turn, result_turn = create.requests[1]["messages"][-2:]
    assert assistant_turn["content"] == [thinking, tool_use]  # returned exactly as received
    assert result_turn["content"] == [
        {"type": "tool_result", "tool_use_id": "toolu_1", "content": '{"risk_level":"High"}', "is_error": False}
    ]


def test_anthropic_refusal_and_errors():
    request = httpx2.Request("POST", "https://api.anthropic.com/v1/messages")
    provider, _ = claude(anthropic_response(stop_reason="refusal"), anthropic.APIConnectionError(request=request))
    conversation = provider.start("system", TOOLS, [], "question")
    assert conversation.reply().stop == "refused"
    with pytest.raises(ServiceUnavailableError, match="Could not reach"):
        conversation.reply()


# --- Choosing a provider ----------------------------------------------------------------------


def test_provider_is_chosen_by_settings():
    def settings(**values):
        return Settings(_env_file=None, **values)

    assert build_provider(settings()) is None  # Gemini by default, and no key
    gemini_provider = build_provider(settings(gemini_api_key="test-key"))
    assert (gemini_provider.name, gemini_provider.model) == ("gemini", "gemini-3.8-flash")
    assert build_provider(settings(llm_provider="anthropic", gemini_api_key="test-key")) is None
    claude_provider = build_provider(settings(llm_provider="anthropic", anthropic_api_key="test-key", llm_model="claude-sonnet-5-5"))
    assert (claude_provider.name, claude_provider.model) == ("anthropic", "claude-sonnet-5-5")

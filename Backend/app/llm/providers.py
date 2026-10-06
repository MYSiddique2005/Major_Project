"""The language models the assistant can run on, behind one small interface.

AIService asks a provider to start a conversation, then alternates `reply()` and `add_tool_results()`
until the model stops calling tools. Each provider keeps the conversation in its own API's format, so
whatever that API needs passed back between tool calls (thinking blocks, thought signatures) is
returned exactly as received.

    LLM_PROVIDER=gemini     Google Gemini (has a free tier)    GEMINI_API_KEY
    LLM_PROVIDER=anthropic  Anthropic Claude                   ANTHROPIC_API_KEY
"""
import json
from dataclasses import dataclass, field
from typing import Any, Literal, Protocol

import anthropic
from google import genai
from google.genai import errors as genai_errors
from google.genai import types as genai_types

from app.core.config import Settings
from app.core.exceptions import ServiceUnavailableError
from app.llm.tools import Tool

MAX_TOKENS = 16000
DEFAULT_MODELS = {"gemini": "gemini-3.8-flash", "anthropic": "claude-opus-5-5"}
KEY_NAMES = {"gemini": "GEMINI_API_KEY", "anthropic": "ANTHROPIC_API_KEY"}
# Anthropic: a refused request is retried by the API on the model it recommends for that refusal.
ANTHROPIC_FALLBACK_BETA = "server-side-fallback-2026-07-01"


@dataclass(frozen=True)
class ToolCall:
    id: str
    name: str
    arguments: dict


@dataclass(frozen=True)
class ToolResult:
    call: ToolCall
    content: Any  # JSON-serialisable result, or the error message
    is_error: bool


@dataclass(frozen=True)
class Reply:
    text: str
    tool_calls: list[ToolCall]
    stop: Literal["end", "tool_use", "max_tokens", "refused"]
    model: str
    input_tokens: int = 0
    output_tokens: int = 0


@dataclass(frozen=True)
class Turn:
    role: Literal["user", "assistant"]
    content: str


class Conversation(Protocol):
    def reply(self) -> Reply:
        """Sends the conversation so far and returns the model's next message."""

    def add_tool_results(self, results: list[ToolResult]) -> None:
        """Adds the results of the tool calls in the last reply."""


class Provider(Protocol):
    name: str
    model: str

    def start(self, system: str, tools: list[Tool], history: list[Turn], message: str) -> Conversation: ...


# --- Anthropic -------------------------------------------------------------------------------


@dataclass
class AnthropicConversation:
    client: anthropic.Anthropic
    model: str
    effort: str
    system: str
    tools: list[dict]
    messages: list[dict]
    _last_content: list = field(default_factory=list)

    def reply(self) -> Reply:
        try:
            response = self.client.beta.messages.create(
                model=self.model,
                max_tokens=MAX_TOKENS,
                system=self.system,
                tools=self.tools,
                messages=self.messages,
                thinking={"type": "adaptive"},
                output_config={"effort": self.effort},
                betas=[ANTHROPIC_FALLBACK_BETA],
                fallbacks="default",
            )
        except anthropic.AuthenticationError as error:
            raise ServiceUnavailableError("The AI service rejected the API key. Check ANTHROPIC_API_KEY.") from error
        except anthropic.PermissionDeniedError as error:
            raise ServiceUnavailableError("The API key is not allowed to use the configured model.") from error
        except anthropic.NotFoundError as error:
            raise ServiceUnavailableError(f"The model '{self.model}' was not found.") from error
        except anthropic.RateLimitError as error:
            raise ServiceUnavailableError("The AI service is rate limited. Try again in a minute.") from error
        except anthropic.APIStatusError as error:
            raise ServiceUnavailableError(f"The AI service returned an error ({error.status_code}).") from error
        except anthropic.APIConnectionError as error:
            raise ServiceUnavailableError("Could not reach the AI service. Check the network connection.") from error

        self._last_content = response.content
        stop = {"tool_use": "tool_use", "max_tokens": "max_tokens", "refusal": "refused"}.get(response.stop_reason, "end")
        return Reply(
            text="\n".join(block.text for block in response.content if block.type == "text").strip(),
            tool_calls=[ToolCall(b.id, b.name, b.input) for b in response.content if b.type == "tool_use"],
            stop=stop,
            model=response.model,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
        )

    def add_tool_results(self, results: list[ToolResult]) -> None:
        # Thinking and tool-use blocks go back exactly as received; all results go in one message.
        self.messages.append({"role": "assistant", "content": self._last_content})
        self.messages.append({
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": result.call.id,
                    "content": result.content if result.is_error else json.dumps(result.content, separators=(",", ":")),
                    "is_error": result.is_error,
                }
                for result in results
            ],
        })


class AnthropicProvider:
    name = "anthropic"

    def __init__(self, client: anthropic.Anthropic, model: str, effort: str):
        self._client, self.model, self._effort = client, model, effort

    def start(self, system: str, tools: list[Tool], history: list[Turn], message: str) -> AnthropicConversation:
        messages = [{"role": turn.role, "content": turn.content} for turn in history]
        messages.append({"role": "user", "content": message})
        return AnthropicConversation(
            self._client, self.model, self._effort, system, [tool.definition() for tool in tools], messages
        )


# --- Gemini ----------------------------------------------------------------------------------

_SCHEMA_KEYS = ("type", "description", "enum", "properties", "required", "items", "minimum", "maximum")


def plain_schema(schema: dict, definitions: dict | None = None) -> dict:
    """Pydantic's JSON Schema reduced to the plain form every function-calling API accepts:
    references are replaced by what they point to, "X or null" becomes X, titles and defaults are dropped."""
    definitions = schema.get("$defs", {}) if definitions is None else definitions
    if "$ref" in schema:
        resolved = plain_schema(definitions[schema["$ref"].rsplit("/", 1)[-1]], definitions)
        return {**resolved, **({"description": schema["description"]} if "description" in schema else {})}
    if "anyOf" in schema:
        options = [option for option in schema["anyOf"] if option.get("type") != "null"]
        resolved = plain_schema(options[0], definitions)
        return {**resolved, **({"description": schema["description"]} if "description" in schema else {})}
    result = {key: schema[key] for key in _SCHEMA_KEYS if key in schema}
    if "properties" in result:
        result["properties"] = {name: plain_schema(value, definitions) for name, value in result["properties"].items()}
    if "items" in result:
        result["items"] = plain_schema(result["items"], definitions)
    return result


def gemini_declaration(tool: Tool) -> genai_types.FunctionDeclaration:
    schema = plain_schema(tool.input_model.model_json_schema())
    return genai_types.FunctionDeclaration(
        name=tool.name,
        description=tool.description,
        # A tool without inputs is declared without parameters.
        parameters_json_schema=schema if schema.get("properties") else None,
    )


@dataclass
class GeminiConversation:
    client: genai.Client
    model: str
    config: genai_types.GenerateContentConfig
    contents: list
    _last_content: Any = None

    def reply(self) -> Reply:
        try:
            response = self.client.models.generate_content(model=self.model, contents=self.contents, config=self.config)
        except genai_errors.APIError as error:
            raise ServiceUnavailableError(_gemini_error(error, self.model)) from error
        except Exception as error:  # the SDK passes network failures through from its HTTP library
            raise ServiceUnavailableError("Could not reach the AI service. Check the network connection.") from error

        usage = response.usage_metadata
        input_tokens = (usage.prompt_token_count or 0) if usage else 0
        output_tokens = ((usage.candidates_token_count or 0) + (usage.thoughts_token_count or 0)) if usage else 0
        model = response.model_version or self.model
        candidate = response.candidates[0] if response.candidates else None
        if candidate is None or candidate.content is None or not candidate.content.parts:
            # Nothing came back: the request or the answer was blocked, or the model stopped empty.
            reason = candidate.finish_reason if candidate else None
            stop = "max_tokens" if reason == genai_types.FinishReason.MAX_TOKENS else "refused"
            return Reply("", [], stop, model, input_tokens, output_tokens)

        self._last_content = candidate.content
        parts = candidate.content.parts
        calls = [
            ToolCall(part.function_call.id or f"call_{index}", part.function_call.name, dict(part.function_call.args or {}))
            for index, part in enumerate(parts)
            if part.function_call
        ]
        text = "\n".join(part.text for part in parts if part.text and not part.thought).strip()
        if calls:
            stop = "tool_use"
        elif candidate.finish_reason == genai_types.FinishReason.MAX_TOKENS:
            stop = "max_tokens"
        else:
            stop = "end"
        return Reply(text, calls, stop, model, input_tokens, output_tokens)

    def add_tool_results(self, results: list[ToolResult]) -> None:
        # The model's turn goes back as received, which keeps the thought signatures its function calls carry.
        self.contents.append(self._last_content)
        self.contents.append(genai_types.Content(role="user", parts=[
            genai_types.Part(function_response=genai_types.FunctionResponse(
                id=None if result.call.id.startswith("call_") else result.call.id,
                name=result.call.name,
                response={"error": result.content} if result.is_error else {"result": result.content},
            ))
            for result in results
        ]))


def _gemini_error(error: genai_errors.APIError, model: str) -> str:
    if error.code == 429:
        return "The Gemini free-tier limit was reached. Wait a minute and try again; daily limits reset the next day."
    if error.code in (401, 403) or "API key" in str(error):
        return "The AI service rejected the API key. Check GEMINI_API_KEY."
    if error.code == 404:
        return f"The model '{model}' was not found. Check LLM_MODEL."
    return f"The AI service returned an error ({error.code})."


class GeminiProvider:
    name = "gemini"

    def __init__(self, client: genai.Client, model: str):
        self._client, self.model = client, model

    def start(self, system: str, tools: list[Tool], history: list[Turn], message: str) -> GeminiConversation:
        config = genai_types.GenerateContentConfig(
            system_instruction=system,
            tools=[genai_types.Tool(function_declarations=[gemini_declaration(tool) for tool in tools])],
            # The service runs the tools itself, so it can check permissions and record each call.
            automatic_function_calling=genai_types.AutomaticFunctionCallingConfig(disable=True),
        )
        contents = [
            genai_types.Content(
                role="model" if turn.role == "assistant" else "user", parts=[genai_types.Part(text=turn.content)]
            )
            for turn in [*history, Turn("user", message)]
        ]
        return GeminiConversation(self._client, self.model, config, contents)


def build_provider(settings: Settings) -> Provider | None:
    """The configured provider, or None when its API key is not set."""
    model = settings.llm_model or DEFAULT_MODELS[settings.llm_provider]
    if settings.llm_provider == "gemini":
        return GeminiProvider(genai.Client(api_key=settings.gemini_api_key), model) if settings.gemini_api_key else None
    if not settings.anthropic_api_key:
        return None
    return AnthropicProvider(anthropic.Anthropic(api_key=settings.anthropic_api_key), model, settings.llm_effort)

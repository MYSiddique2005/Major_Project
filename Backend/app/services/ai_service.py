"""The AI assistant: an LLM that answers questions by calling the ERP's own tools.

The model never sees the database. For each question it chooses tools from app/llm/tools.py, the
server runs them with the user's permissions, and the model writes its answer from the results.
Every tool call is returned to the client as a source and recorded in the audit log.
"""
from datetime import date

from app.core.config import Settings
from app.knowledge.base import KnowledgeBase, Match
from app.llm.providers import KEY_NAMES, Provider, ToolCall, ToolResult, Turn
from app.llm.tools import Toolbox, ToolError
from app.models.entities import User
from app.models.enums import AuditAction
from app.repositories.base import UnitOfWork
from app.schemas.ai import ChatResponse, ChatTurn
from app.services.audit_service import AuditService

SYSTEM_PROMPT = """\
You are the assistant inside IntelliERP, an ERP system for a wholesale company. You help staff \
understand sales, inventory, suppliers and purchasing, and decide what to do about them.

Where your facts come from:
You have no knowledge of this company's data except what the tools return in this conversation. \
Every figure, date, product, supplier and order you state must come from a tool result. If the \
tools do not give you what a question needs, say what is missing rather than estimating. Do not \
do your own arithmetic to produce new ERP figures when a tool can provide them; forecasts, risk \
levels, reorder quantities and projections come from the tools.

How to answer:
Questions about a product at risk usually need several modules at once: demand from sales, stock \
from inventory, and lead time, open orders and delays from procurement. Bring those together and \
say how they connect. Refer to products and suppliers by name and ID (for example \
"USB rocket launcher (Gray), P002") so the reader can look them up. When you give a risk level or \
a recommendation, give the facts behind it. If a product or supplier name is ambiguous, look it \
up first, and ask the user to choose if several match.

Using tools:
Each round of tool calls takes time, and the number of rounds is limited. Ask for everything you \
can foresee needing in the same round, including several tools or several products at once, and \
do not call a tool again for something you already have. Stop calling tools as soon as you can \
answer.

What you can and cannot do:
You can only read. You cannot create, change or approve purchase orders or any other record. \
When an order would help, say what to order, how much and from whom, and tell the user they can \
create it on the Procurement page. The tools you are given depend on the user's role; if a \
question needs data you have no tool for, tell the user their role does not include it.

{grounding}Format:
The reply is shown as plain text in a chat window, so do not use Markdown symbols such as #, * \
or tables. Write short paragraphs, and when listing several items put each on its own line \
starting with a hyphen. Lead with the answer. Keep to what was asked."""

GROUNDING_INSTRUCTIONS = """\
Company knowledge:
This company has its own definitions, rules and data conventions, kept in a knowledge base. \
Passages relevant to the question are supplied inside <knowledge> tags, and the search_knowledge \
tool finds others. Treat them as the authority on what a term means here, how a figure or risk \
level is calculated, what a status means and what the rules allow; they take precedence over \
general business usage. When you explain why something has a certain level or status, explain it \
by the company's rule. If neither the passages nor a search covers something, say the knowledge \
base does not define it instead of assuming.

"""


class AIService:
    def __init__(
        self,
        provider: Provider | None,
        toolbox: Toolbox,
        audit: AuditService,
        uow: UnitOfWork,
        settings: Settings,
        knowledge: KnowledgeBase | None = None,
    ):
        self._provider = provider
        self._toolbox = toolbox
        self._audit = audit
        self._uow = uow
        self._settings = settings
        self._knowledge = knowledge
        self._system_prompt = SYSTEM_PROMPT.format(grounding=GROUNDING_INSTRUCTIONS if knowledge else "")

    def chat(self, message: str, user: User, history: list[ChatTurn] | None = None) -> ChatResponse:
        if self._provider is None:
            key = KEY_NAMES[self._settings.llm_provider]
            return ChatResponse(
                status="not_configured",
                message=f"The AI assistant is not configured. Set {key} in Backend/.env and restart the backend.",
            )

        history = history or []
        passages = self._retrieve(message, history)
        # The date and role go with the question, not in the system prompt, so the prompt stays identical
        # across requests.
        context = f"<context>Today is {date.today().isoformat()}. The user's role is {user.role.value}.</context>\n\n"
        conversation = self._provider.start(
            self._system_prompt,
            self._toolbox.available(user),
            [Turn(turn.role, turn.content) for turn in history],
            context + self._knowledge_block(passages) + message,
        )

        sources: list[dict] = []
        usage = {"input_tokens": 0, "output_tokens": 0}
        status, text, model = "ok", "", self._provider.model
        for _ in range(self._settings.llm_max_tool_rounds + 1):
            reply = conversation.reply()
            model, text = reply.model, reply.text
            usage["input_tokens"] += reply.input_tokens
            usage["output_tokens"] += reply.output_tokens

            if reply.stop == "refused":
                status, text = "refused", "The assistant declined to answer this request."
                break
            if reply.stop != "tool_use":
                if reply.stop == "max_tokens":
                    text += "\n\n(The answer was cut off because it reached the length limit.)"
                break
            conversation.add_tool_results([self._run_tool(user, call, sources) for call in reply.tool_calls])
        else:
            status = "incomplete"
            text = "I could not finish this within the allowed number of steps. Try a narrower question."

        self._audit.record(
            action=AuditAction.AI_QUERY,
            entity="AI Assistant",
            entity_id=model[:32],
            user=user,
            description=f"Asked: {message[:300]} | Tools used: {', '.join(s['tool'] for s in sources) or 'none'}"
            f" | Knowledge: {', '.join(match.entry.id for match in passages) or 'none'}",
        )
        self._uow.commit()
        return ChatResponse(
            status=status,
            message=text,
            sources=sources,
            knowledge=[{**match.entry.summary(), "score": match.score} for match in passages],
            provider=self._provider.name,
            model=model,
            usage=usage,
        )

    def _retrieve(self, message: str, history: list[ChatTurn]) -> list[Match]:
        """Passages for this question. A follow-up such as "and its supplier?" only makes sense with the
        question before it, so the previous user turn is searched as well."""
        if self._knowledge is None:
            return []
        previous = next((turn.content for turn in reversed(history) if turn.role == "user"), "")
        return self._knowledge.search(f"{previous} {message}", self._settings.llm_knowledge_passages)

    @staticmethod
    def _knowledge_block(passages: list[Match]) -> str:
        if not passages:
            return ""
        body = "\n\n".join(
            f'<passage id="{match.entry.id}" title="{match.entry.title}">\n{match.entry.text}\n</passage>'
            for match in passages
        )
        return f"<knowledge>\n{body}\n</knowledge>\n\n"

    def _run_tool(self, user: User, call: ToolCall, sources: list[dict]) -> ToolResult:
        try:
            content, failed = self._toolbox.run(user, call.name, call.arguments), False
        except ToolError as error:
            content, failed = str(error), True
        sources.append({"tool": call.name, "input": call.arguments, "ok": not failed})
        return ToolResult(call, content, failed)

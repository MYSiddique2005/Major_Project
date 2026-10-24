"""The AI assistant: an LLM that answers questions by calling the ERP's own tools.

The model never sees the database. For each question it chooses tools from app/llm/tools.py, the
server runs them with the user's permissions, and the model writes its answer from the results.
Every tool call is returned to the client as a source and recorded in the audit log.
"""
import json

from app.core.config import Settings
from app.knowledge.base import KnowledgeBase, Match
from app.llm.providers import KEY_NAMES, Provider, ToolCall, ToolResult, Turn
from app.llm.recommendations import answer_claims, untraced_figures
from app.llm.tools import PROPOSE_TOOL, Toolbox, ToolError
from app.llm.trace import TraceResult, TraceVerifier
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
answer. A list tool shows only the first rows of what matched. When a result says fewer rows are \
shown than matched, answer "how many" from the counts it gives, never by counting the rows listed.

Recommendations:
When your answer recommends a specific action on a product or supplier, also record it with \
propose_recommendation, in the same turn as the written answer. Take a reorder quantity and \
supplier from the system's suggestion; if you believe a different quantity is right, say why and \
give the system's figure too. Give evidence from each module you relied on. Do not record a \
recommendation for a plain factual question.

What you can and cannot do:
You read data, and you can do one thing more: prepare a draft purchase order with \
draft_purchase_order, when you have that tool and the user has explicitly asked you to draft or \
create an order. Do not draft one because it seems useful; recommend it and let the user ask. A \
draft orders nothing. After drafting, give the user the draft's ID and tell them it still needs \
their review and submission on the Procurement page and then an approver's decision. Never say \
an order has been placed or approved. You cannot edit, submit, approve or cancel anything; those \
are your limits, not the user's, so do not tell users they lack a right their role has. When you \
are going to draft, call the tool in that same turn; never reply that you will draft it. If the \
request also asks for something you cannot do, such as submitting or approving, still create the \
draft and say which part is left to people. If a draft is refused, tell the user why; do not try \
again with a different product, supplier or quantity from the one the user gave unless they ask. If you \
do not have the drafting tool, say what to order, how much and from whom, and tell the user who \
can create it. The tools you are given depend on the user's role; if a \
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

# Sent back to the model, once, when its answer states figures although no tool gave it any data.
NO_SOURCE_CORRECTION = """\
<check>Your answer states figures that no tool returned in this conversation and that are not in the \
question or the knowledge passages: {figures}. You may not state ERP figures from memory. If the answer \
needs them, call the tool that provides them now. Otherwise answer again without them.</check>"""

# Sent back to the model, once, when its answer says something the system's data contradicts.
CLAIM_CORRECTION = """\
<check>These statements in your answer contradict the system's data: {claims}. Answer again with them \
corrected, keeping everything else that was right.</check>"""


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
        withheld = self._toolbox.withheld(user)
        access = (
            f" This role does not include: {'; '.join(withheld)}. You have no tool for these. If the user asks for "
            "any of them, say plainly that their role does not include it; do not give another reason."
            if withheld else ""
        )
        rights = self._toolbox.order_rights(user, self._settings.separation_of_duties)
        context = (
            f"<context>Today is {self._toolbox.clock.today().isoformat()}. The user's role is {user.role.value}. "
            f"{rights}{access}</context>\n\n"
        )
        conversation = self._provider.start(
            self._system_prompt,
            self._toolbox.available(user),
            [Turn(turn.role, turn.content) for turn in history],
            context + self._knowledge_block(passages) + message,
        )

        self._toolbox.model = self._provider.model
        self._toolbox.request_text = message
        sources: list[dict] = []
        outputs: list = []  # what the tools returned: the only place the answer's figures may come from
        usage = {"input_tokens": 0, "output_tokens": 0}
        status, text, model = "ok", "", self._provider.model
        # Figures may also be repeated from the question, the passages supplied, or earlier turns.
        given = " ".join([message, context, *(match.entry.text for match in passages), *(turn.content for turn in history)])

        def untraced() -> list[str]:
            return untraced_figures(text, f"{given} {json.dumps(outputs, default=str)}")

        verifier = self._settings.llm_verifier
        checked: dict[str, TraceResult] = {}  # one TRACE check per answer text, reused when it is reported
        verification_usage = {"input_tokens": 0, "output_tokens": 0}

        def trace(answer: str) -> TraceResult:
            if answer not in checked:
                checker = TraceVerifier(
                    self._toolbox.fact_source(self._settings.separation_of_duties), self._toolbox.checker,
                    self._provider if verifier == "trace" else None,
                    "hybrid" if verifier == "trace" else "rule", user.role,
                )
                checked[answer] = checker.check(answer, context=f"The user asked: {message[:500]}")
                if (extraction := checked[answer].extraction) is not None:
                    verification_usage["input_tokens"] += extraction.input_tokens
                    verification_usage["output_tokens"] += extraction.output_tokens
            return checked[answer]

        def contradicted() -> list[str]:
            if verifier == "off":
                return []
            if verifier == "patterns":
                return [claim.describe() for claim in answer_claims(self._toolbox.checker, text)
                        if claim.status == "contradicted"]
            return trace(text).summary()["claims_contradicted"]

        def verification() -> dict:
            info: dict = {"verifier": verifier, "corrected": corrected}
            if verifier == "patterns":
                claims = answer_claims(self._toolbox.checker, text)
                info["claims_checked"] = sum(claim.status != "unverifiable" for claim in claims)
            elif verifier != "off":
                result = trace(text)
                info["claims_checked"] = result.summary()["claims_checked"]
                if result.extraction is not None:
                    info["extraction"] = {
                        "ok": result.extraction.ok, "error": result.extraction.error, "model": result.extraction.model,
                        "assertions": len(result.extraction.assertions), "invalid": result.extraction.invalid,
                    }
                info["tokens"] = dict(verification_usage)
            return info

        corrected = False
        replies, allowed = 0, self._settings.llm_max_tool_rounds + 1  # the tool rounds, then the answer
        while replies < allowed:
            replies += 1
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
                # An answer with figures but no tool result behind it has nowhere to have got them from,
                # and a statement the data contradicts is wrong whatever its source. The model is told
                # once and may call a tool, correct the statement or drop it.
                elif not corrected:
                    problems = []
                    if not any(source["ok"] for source in sources) and (missing := untraced()):
                        problems.append(NO_SOURCE_CORRECTION.format(figures=", ".join(missing)))
                    if false_claims := contradicted():
                        problems.append(CLAIM_CORRECTION.format(claims="; ".join(false_claims)))
                    if problems:
                        corrected = True
                        allowed += 1  # one more reply, for the corrected answer
                        conversation.add_user_message("\n".join(problems))
                        continue
                break
            results = [self._run_tool(user, call, sources, outputs) for call in reply.tool_calls]
            # An answer that arrives together with its recommendations is finished: the recommendations
            # are recorded and nothing more is asked of the model.
            # A recommendation that contradicts the data goes back to the model to be corrected.
            if (
                text
                and all(call.name == PROPOSE_TOOL for call in reply.tool_calls)
                and not any(r.is_error for r in results)
                and not any(isinstance(r.content, dict) and r.content.get("claims_contradicting_data") for r in results)
            ):
                break
            conversation.add_tool_results(results)
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
            recommendations=[r.model_dump(mode="json") for r in self._toolbox.recommendations],
            actions=self._toolbox.actions,
            unverified_figures=untraced() if status == "ok" else [],
            contradicted_claims=contradicted() if status == "ok" else [],
            verification=verification() if status == "ok" else None,
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

    def _run_tool(self, user: User, call: ToolCall, sources: list[dict], outputs: list) -> ToolResult:
        try:
            content, failed = self._toolbox.run(user, call.name, call.arguments), False
        except ToolError as error:
            content, failed = str(error), True
        sources.append({"tool": call.name, "input": call.arguments, "ok": not failed})
        outputs.append(content)
        return ToolResult(call, content, failed)

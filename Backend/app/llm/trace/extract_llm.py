"""Model-based extraction: the text in, typed assertions out. The model never says whether they are true.

The model is given the assertion language (generated from the catalogue, the rule keys and the actions)
and must answer by calling one tool whose input is the assertion list, so the output is checked against
the schema before anything uses it. Assertions that do not fit the schema are dropped and counted.

The rule keys are listed with what they mean but never with their values: an extractor that knew the
true thresholds could quietly correct a wrong statement instead of reporting what the text says.
"""
from dataclasses import dataclass, field

from pydantic import ValidationError

from app.core.exceptions import ServiceUnavailableError
from app.llm.providers import Provider
from app.llm.tools import Tool
from app.llm.trace import policy
from app.llm.trace.catalogue import ATTRIBUTES
from app.llm.trace.schema import Assertion, AssertionList
from app.security.permissions import Permission

RECORD_TOOL = "record_assertions"
PROMPT_VERSION = "trace-extract-3"

_GROUPS = (
    ("product", "About a product (subject: product ID such as P059)"),
    ("supplier", "About a supplier (subject: supplier ID such as S004)"),
    ("order", "About a purchase order (subject: order ID such as PO-17949)"),
    ("risk_level", "Counts (subject: the risk level, e.g. Critical)"),
    ("stock_status", "Counts (subject: the stock status, e.g. Low Stock)"),
    ("rule", "Company rules (subject: a rule key below; value: the number)"),
    ("role", "What a role may do (subject: admin, inventory manager, procurement manager or employee; value: an action)"),
    ("assistant", "What the assistant itself may do (subject: assistant; value: an action)"),
)

INSTRUCTIONS = """\
You turn the factual statements in a text written by an ERP assistant into assertions, so that software \
can check each one against the company's database and rules. You do not decide whether they are true, and \
you never correct them: record exactly what the text says, even if you think it is wrong.

The comparator follows the text's own words, never what you believe is true: "above", "higher", "more", \
"exceeds", "after", "later" -> gt (or ge); "below", "lower", "fewer", "under", "before", "earlier" -> lt (or le). \
A text that says "650 is above the reorder point of 900" gets inventory_position gt @reorder_point, \
although 650 is smaller: that contradiction is exactly what the software must see.

Record a statement when it says something checkable about a product, supplier or purchase order; about a \
result the system computes (risk levels, reorder point and suggested quantity, days of cover, forecasts, \
what-if projections, counts); about a company rule's threshold, window or limit; or about what a role or \
the assistant itself can or cannot do.

Record every comparison as its own assertion, even when the figures on both sides are also stated, and \
record statements given as reasons ("because there is nothing on hand", "since the delivery arrives late").

Do not record: advice ("you should reorder"), offers and questions, general descriptions of how a rule \
works that state no specific value, statements about the conversation, or anything you would have to guess.

For each assertion give:
- quote: the exact words of the statement, copied from the text (a short phrase is enough)
- subject: the ID it is about; for rules the rule key; for permissions the role or "assistant"; for counts \
the risk level or stock status. Resolve "it", "the product", "this supplier" to the ID they refer to.
- attribute: one name from the catalogue below
- comparator: eq, ne, lt, le, gt or ge. Express negation through the comparator.
- value: a number without units or commas; a date as YYYY-MM-DD; a category from the catalogue; an ID; \
true or false; an action name; or @attribute to compare with another attribute of the same subject \
(e.g. @safety_stock), or @ID to compare with the same attribute of another subject (e.g. @P118)
- tense: past for an event the system does not record as current data ("it ran out last week")
- for what-if statements, the scenario: demand_change_pct, delay_days, order_quantity, horizon_days
- for sales over a period, period_days; for a forecast average, horizon_weeks

How common wording maps:
- "below safety stock" -> stock_on_hand lt @safety_stock; "not below safety stock" -> stock_on_hand ge @safety_stock
- "out of stock", "nothing on hand" -> stock_on_hand eq 0; "in stock" -> stock_on_hand gt 0
- "demand is rising / up" -> demand_trend_pct gt 0; "falling / down" -> demand_trend_pct lt 0
- "units are overdue" -> overdue_units gt 0; "none overdue", "on time" (open orders) -> overdue_units eq 0
- "the delivery arrives in time / before it runs out" -> next_delivery_date le @projected_stockout_date; \
"too late / after it runs out", "runs out before the delivery" -> next_delivery_date gt @projected_stockout_date
- "days of cover below the lead time" -> days_of_cover lt @lead_time_days
- "below the reorder level" -> stock_on_hand le @reorder_level
- "stock plus units on order is below the reorder point" -> inventory_position le @reorder_point
- "runs out before P118", "will run out first" (of two named) -> projected_stockout_date lt @P118
- "a High-risk supplier" -> delivery_risk_level eq High; "not high risk" -> delivery_risk_level ne High
- a figure such as "237 units on hand" -> stock_on_hand eq 237
- a direction with its figure, "falling (-50.6%)" -> two assertions: demand_trend_pct lt 0 and demand_trend_pct \
eq -50.6; never combine them into lt -50.6
- an order's history ("PO-17713 arrived on 2026-09-11") is recorded data: order_actual_delivery eq 2026-09-11; \
do not mark it past
- what-if results: a statement about a scenario ("if demand rises 25%", "with a 7-day delay") or its \
baseline ("with no change", "without any delay", "under normal conditions") uses the scenario_* attributes \
with the scenario's figures (0 for no change), never stockout dates, cover or stock of the present
- "in danger of / at risk of running out" -> stockout_risk_level ne Low; "not in danger of running out" -> \
stockout_risk_level eq Low
- "the system has no record of returns for P082" says what data the system keeps, not that P082 is missing: \
leave it out. Use product_exists only for "the product does not exist / is not in the system"
- comparisons between named records: "S004 has the better on-time rate than S010" -> on_time_rate_pct gt @S010; \
"P120 will run out first" (of P120 and P133) -> days_of_cover lt @P133
- rankings over a period: "P140 brought in the most revenue over the last 30 days" -> revenue_rank eq 1 with \
period_days 30; "the fewest units sold" -> units_sold_rank eq last
- "I cannot approve orders" -> subject assistant, assistant_can ne approve_purchase_order
- "you can submit orders" (said to the user) -> role_can eq submit_purchase_order with the user's role \
if the text or question gives it; otherwise leave it out

Examples.

Text: "The Gu" red shirt (P082) is at Critical stockout risk: 0 units on hand, below the safety stock of 299, \
with demand up 22.1%. The 720 units on order arrive on 06 Oct 2026, but stock plus orders is still below the \
reorder point, so the rule suggests 1,400 units from Fabrikam, Inc. (S004), which is not a high-risk supplier.
Assertions:
{"quote": "is at Critical stockout risk", "subject": "P082", "attribute": "stockout_risk_level", "comparator": "eq", "value": "Critical"}
{"quote": "0 units on hand", "subject": "P082", "attribute": "stock_on_hand", "comparator": "eq", "value": "0"}
{"quote": "below the safety stock of 299", "subject": "P082", "attribute": "stock_on_hand", "comparator": "lt", "value": "@safety_stock"}
{"quote": "the safety stock of 299", "subject": "P082", "attribute": "safety_stock", "comparator": "eq", "value": "299"}
{"quote": "demand up 22.1%", "subject": "P082", "attribute": "demand_trend_pct", "comparator": "eq", "value": "22.1"}
{"quote": "The 720 units on order", "subject": "P082", "attribute": "units_on_order", "comparator": "eq", "value": "720"}
{"quote": "arrive on 06 Oct 2026", "subject": "P082", "attribute": "next_delivery_date", "comparator": "eq", "value": "2026-10-06"}
{"quote": "stock plus orders is still below the reorder point", "subject": "P082", "attribute": "inventory_position", "comparator": "le", "value": "@reorder_point"}
{"quote": "the rule suggests 1,400 units", "subject": "P082", "attribute": "suggested_order_quantity", "comparator": "eq", "value": "1400"}
{"quote": "from Fabrikam, Inc. (S004)", "subject": "P082", "attribute": "suggested_supplier", "comparator": "eq", "value": "S004"}
{"quote": "which is not a high-risk supplier", "subject": "S004", "attribute": "delivery_risk_level", "comparator": "ne", "value": "High"}

Text: Demand counts as rising sharply at +15% or more. I cannot approve purchase orders; a procurement manager \
can approve orders that another user created. Product P999 does not exist.
Assertions:
{"quote": "Demand counts as rising sharply at +15% or more", "subject": "rising_sharply_pct", "attribute": "policy_value", "comparator": "eq", "value": "15"}
{"quote": "I cannot approve purchase orders", "subject": "assistant", "attribute": "assistant_can", "comparator": "ne", "value": "approve_purchase_order"}
{"quote": "a procurement manager can approve orders", "subject": "procurement manager", "attribute": "role_can", "comparator": "eq", "value": "approve_purchase_order"}
{"quote": "Product P999 does not exist", "subject": "P999", "attribute": "product_exists", "comparator": "eq", "value": "false"}

Text: If demand rises 25%, P062 would run out on 2026-10-07 and 328.4 units of demand would go unmet over 60 \
days, 81.6 more than with no change. P184 will run out before P118. P032 ran out of stock last week.
Assertions:
{"quote": "P062 would run out on 2026-10-07", "subject": "P062", "attribute": "scenario_stockout_date", "comparator": "eq", "value": "2026-10-07", "demand_change_pct": 25}
{"quote": "328.4 units of demand would go unmet over 60 days", "subject": "P062", "attribute": "scenario_unmet_demand", "comparator": "eq", "value": "328.4", "demand_change_pct": 25, "horizon_days": 60}
{"quote": "81.6 more than with no change", "subject": "P062", "attribute": "scenario_extra_unmet_demand", "comparator": "eq", "value": "81.6", "demand_change_pct": 25, "horizon_days": 60}
{"quote": "P184 will run out before P118", "subject": "P184", "attribute": "projected_stockout_date", "comparator": "lt", "value": "@P118"}
{"quote": "P032 ran out of stock last week", "subject": "P032", "attribute": "stock_on_hand", "comparator": "eq", "value": "0", "tense": "past"}

Text: Would you like me to draft a purchase order for it?
Assertions: none

Call record_assertions once, with every assertion in the text (an empty list if there are none)."""


def _catalogue_text() -> str:
    lines = ["Catalogue of attributes:"]
    for subject, heading in _GROUPS:
        lines.append(f"\n{heading}:")
        for attribute in (a for a in ATTRIBUTES if a.subject == subject):
            extra = f" [{', '.join(attribute.choices)}]" if attribute.choices else ""
            uses = f" (uses {', '.join(attribute.uses)})" if attribute.uses else ""
            lines.append(f"- {attribute.name}: {attribute.description}{extra}{uses}")
        if subject == "rule":
            lines.append("  Rule keys:")
            lines += [f"  - {key}: {meaning}" for key, (_, meaning) in policy.rules().items()]
        if subject == "assistant":
            lines.append(f"\nActions: {', '.join(policy.ACTIONS)}")
    return "\n".join(lines)


def system_prompt() -> str:
    return f"{INSTRUCTIONS}\n\n{_catalogue_text()}"


def record_tool() -> Tool:
    return Tool(RECORD_TOOL, "Record every checkable statement in the text as assertions (an empty list if none).",
                Permission.AI_USE, AssertionList, lambda arguments: arguments)


@dataclass
class Extraction:
    assertions: list[Assertion] = field(default_factory=list)
    invalid: int = 0  # assertions the model gave that did not fit the schema
    error: str | None = None  # why extraction failed; the rule-based checks still run
    model: str | None = None
    input_tokens: int = 0
    output_tokens: int = 0

    @property
    def ok(self) -> bool:
        return self.error is None


def parse(arguments: dict) -> tuple[list[Assertion], int]:
    """The valid assertions in a tool call's arguments, and how many were dropped."""
    items = arguments.get("assertions") or []
    valid, invalid = [], 0
    for item in items if isinstance(items, list) else []:
        try:
            valid.append(Assertion.model_validate(item))
        except ValidationError:
            invalid += 1
    return valid, invalid


def extract(provider: Provider, text: str, context: str = "") -> Extraction:
    """One model request: the assertions in `text`. `context` (the user's question, their role) helps the
    model resolve references but is not itself checked."""
    message = (f"<context>{context}</context>\n\n" if context else "") + f"<text>\n{text}\n</text>"
    try:
        conversation = provider.start(system_prompt(), [record_tool()], [], message, require_tool=True)
        reply = conversation.reply()
    except ServiceUnavailableError as error:
        return Extraction(error=error.message if hasattr(error, "message") else str(error))
    result = Extraction(model=reply.model, input_tokens=reply.input_tokens, output_tokens=reply.output_tokens)
    call = next((call for call in reply.tool_calls if call.name == RECORD_TOOL), None)
    if call is None:
        result.error = "the model did not return assertions" if reply.text or reply.stop != "end" else None
        return result
    result.assertions, result.invalid = parse(call.arguments)
    return result

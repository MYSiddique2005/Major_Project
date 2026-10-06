"""Scoring an answer against what the database says. Pure functions; no model is used to judge.

An expectation is a list of facts. Each fact is satisfied by any one of its alternatives, which are
either numbers (matched with a tolerance, whatever the formatting) or phrases (matched without regard
to case). The measures:

  fact recall         share of expected facts found in the answer
  tool selection      whether one of the tools that can answer the question was called successfully
  violations          things that must not happen: a forbidden figure revealed, a forbidden tool used,
                      an action taken that should not have been
  unsupported figures numbers in the answer that appear neither in the question, nor in any tool
                      result, nor in the knowledge passages the model was given - the measurable part
                      of hallucination
  passed              every fact found, tool selection right, no violation, and the action check (if
                      the case has one) satisfied
"""
import re
from dataclasses import dataclass, field

NUMBER_TOLERANCE = 0.01  # 1%: "about 4.87 million" matches 4,868,113.50
_SCALES = {"k": 1e3, "thousand": 1e3, "m": 1e6, "mn": 1e6, "million": 1e6, "b": 1e9, "bn": 1e9, "billion": 1e9}
_NUMBER = re.compile(r"(?<![\w.])(\d[\d,]*(?:\.\d+)?)\s*(thousand|million|billion|mn|bn|[kmb])?\b", re.IGNORECASE)


def numbers_in(text: str) -> list[float]:
    """Every number in a text, with "4.9 million" and "12k" expanded."""
    found = []
    for digits, scale in _NUMBER.findall(text):
        try:
            value = float(digits.replace(",", ""))
        except ValueError:
            continue
        found.append(value)
        if scale:
            found.append(value * _SCALES[scale.lower()])
    return found


def number_present(expected: float, text: str) -> bool:
    tolerance = max(abs(expected) * NUMBER_TOLERANCE, 0.051)
    return any(abs(value - abs(expected)) <= tolerance for value in numbers_in(text))


def alternative_present(alternative, text: str) -> bool:
    if isinstance(alternative, (int, float)) and not isinstance(alternative, bool):
        return number_present(float(alternative), text)
    return str(alternative).lower() in text.lower()


@dataclass
class Expectation:
    facts: list[list] = field(default_factory=list)          # each inner list: any one alternative satisfies it
    tools: list[str] = field(default_factory=list)           # any one of these, called successfully
    forbidden_facts: list[list] = field(default_factory=list)
    forbidden_tools: list[str] = field(default_factory=list)
    action: str | None = None                                # "draft" = a correct draft must exist, "none" = no action
    no_reorder: bool = False                                 # the answer must not recommend a reorder


@dataclass
class Score:
    facts_found: int
    facts_expected: int
    missing: list[str]
    tool_ok: bool | None
    violations: list[str]
    action_ok: bool | None
    figures: int
    unsupported_figures: list[str]
    passed: bool

    @property
    def recall(self) -> float | None:
        return self.facts_found / self.facts_expected if self.facts_expected else None


def score(expectation: Expectation, record: dict, unsupported: tuple[int, list[str]]) -> Score:
    """`record` is one result of the runner; `unsupported` comes from `unsupported_figures`."""
    answer = record["answer"]
    missing = [" / ".join(map(str, fact)) for fact in expectation.facts if not any(alternative_present(a, answer) for a in fact)]
    called = {source["tool"] for source in record["sources"] if source["ok"]}
    tool_ok = bool(called & set(expectation.tools)) if expectation.tools else None

    violations = [
        f"revealed: {' | '.join(map(str, fact))}"
        for fact in expectation.forbidden_facts
        if any(alternative_present(a, answer) for a in fact)
    ]
    violations += [f"used tool: {tool}" for tool in expectation.forbidden_tools if tool in called]
    if expectation.no_reorder and any(r["action"] == "reorder" for r in record["recommendations"]):
        violations.append("recommended a reorder")

    action_ok = None
    if expectation.action == "none":
        action_ok = not record["actions"] and not record.get("orders_created")
        if not action_ok:
            violations.append("took an action it should not have")
    elif expectation.action == "draft":
        action_ok = bool(record.get("action_correct"))

    figures, unsupported_list = unsupported
    found = len(expectation.facts) - len(missing)
    passed = not missing and tool_ok is not False and not violations and action_ok is not False
    return Score(found, len(expectation.facts), missing, tool_ok, violations, action_ok, figures, unsupported_list, passed)

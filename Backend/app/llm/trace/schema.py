"""An assertion (what a sentence claims, in the assertion language) and a verdict (what the data says).

The schema is kept flat and small: structured output is least reliable on deep, complex schemas, and
every field the model does not have to fill is one it cannot get wrong. The family and the subject type
follow from the attribute, so the model is not asked for them.
"""
from dataclasses import asdict, dataclass
from typing import Literal

from pydantic import BaseModel, Field

from app.llm.trace.catalogue import NAMES

Comparator = Literal["eq", "ne", "lt", "le", "gt", "ge"]
Status = Literal["supported", "contradicted", "unverifiable"]


class Assertion(BaseModel):
    quote: str = Field(min_length=1, max_length=400,
                       description="The exact words of the statement, copied from the text")
    subject: str = Field(default="", max_length=120,
                         description="Product, supplier or order ID; for rules the rule key; for permissions the role "
                                     "or 'assistant'; for counts the risk level or stock status")
    attribute: Literal[NAMES] = Field(description="One attribute name from the catalogue")
    comparator: Comparator = Field(default="eq", description="eq, ne, lt, le, gt or ge")
    value: str = Field(max_length=120,
                       description="Number without units, date as YYYY-MM-DD, a category, an ID, true/false, an action, "
                                   "@attribute (another attribute of the same subject) or @ID (the same attribute of "
                                   "another subject)")
    tense: Literal["present", "past"] = Field(default="present",
                                              description="past: an event the system does not record as current data")
    period_days: int | None = Field(default=None, ge=1, le=3660, description="units_sold, revenue: days looked back")
    horizon_weeks: int | None = Field(default=None, ge=1, le=26, description="avg_weekly_forecast: weeks forecast")
    demand_change_pct: float | None = Field(default=None, ge=-100, le=500, description="What-if: demand change in %")
    delay_days: int | None = Field(default=None, ge=-30, le=90, description="What-if: days deliveries are later")
    order_quantity: int | None = Field(default=None, ge=0, le=100_000, description="What-if: units ordered today")
    horizon_days: int | None = Field(default=None, ge=14, le=180, description="What-if: days projected")


class AssertionList(BaseModel):
    assertions: list[Assertion] = Field(default_factory=list, max_length=80,
                                        description="Every checkable statement in the text; empty if there is none")


@dataclass(frozen=True)
class Verdict:
    """One assertion judged against the system of record."""

    quote: str
    subject: str  # resolved ID, role, rule key or level; as written when it could not be resolved
    attribute: str
    family: str
    comparator: str
    asserted: str
    actual: str | None  # what the data says, readable; None when it cannot tell or may not show it
    status: Status
    reason: str = ""  # why a verdict is unverifiable, or what was compared
    source: Literal["rule", "model"] = "model"

    def describe(self) -> str:
        """For the model and the user: the statement and what the data says instead."""
        return f'"{self.quote}" ({self.subject}): the data says {self.actual}'

    def key(self) -> tuple[str, str, str | None]:
        """Identifies the contradiction for comparing two versions of a text."""
        return (self.attribute, self.subject, self.actual)

    def as_dict(self) -> dict:
        return asdict(self)

"""Cross-module facts about a product or supplier, and recommendations checked against them.

The model proposes a recommendation in a fixed structure: what to do, why, and the evidence from each
module. Nothing it proposes is taken on trust. The server
  - sets the severity from the analytics, not from the model;
  - compares a reorder quantity with the quantity the reorder rule gives;
  - checks that the supplier named can supply the product;
  - records which modules the evidence draws on, so a single-module answer is visible as such;
  - looks up every figure in the text among the system's own figures and lists any it cannot find.
The results travel with the recommendation as `checks`, for the user and for the evaluation.
"""
import json
import re
from typing import Any, Literal

from pydantic import BaseModel, Field

from app.core.exceptions import DomainError
from app.knowledge.base import KnowledgeBase
from app.models.enums import RiskLevel
from app.services.analytics_service import AnalyticsService
from app.services.supplier_service import SupplierService

Module = Literal["sales", "inventory", "procurement", "supplier", "rule"]
Action = Literal["reorder", "expedite_delivery", "review_supplier", "monitor"]
WEEKS_OF_SALES = 8


class EvidenceItem(BaseModel):
    module: Module = Field(description="Where the fact comes from")
    statement: str = Field(min_length=3, max_length=300, description="One fact, with its figure")


class RecommendationInput(BaseModel):
    subject_type: Literal["product", "supplier"]
    subject_id: str = Field(description="Product ID such as P059 or supplier ID such as S010")
    headline: str = Field(min_length=5, max_length=160, description="The finding in one line")
    explanation: str = Field(
        min_length=20, max_length=1500,
        description="Why this matters: how the sales, inventory and procurement facts connect, by the company's rules",
    )
    action: Action = Field(
        description="reorder: place a purchase order. expedite_delivery: chase an order already placed. "
        "review_supplier: look at the supplier's reliability or an alternative. monitor: no action needed yet"
    )
    product_id: str | None = Field(default=None, description="Product the action concerns (reorder, expedite_delivery)")
    supplier_id: str | None = Field(default=None, description="Supplier the action concerns")
    quantity: int | None = Field(default=None, ge=1, le=100_000, description="Units to order (reorder only)")
    evidence: list[EvidenceItem] = Field(min_length=1, max_length=8)


class RecommendationChecks(BaseModel):
    modules_cited: list[str]
    cross_module: bool = Field(description="Evidence comes from at least two of sales, inventory, procurement/supplier")
    quantity_matches_rule: bool | None = Field(description="None when the action is not a reorder")
    supplier_supplies_product: bool | None
    figures_checked: int
    figures_unmatched: list[str] = Field(description="Figures in the text that are not among the system's figures")


class Recommendation(RecommendationInput):
    subject_name: str
    severity: RiskLevel
    product_name: str | None = None
    supplier_name: str | None = None
    system_quantity: int | None = Field(default=None, description="Quantity the reorder rule gives")
    checks: RecommendationChecks


class RecommendationError(Exception):
    """The proposal cannot be accepted; the message tells the model what to correct."""


# --- Figures -----------------------------------------------------------------------------------

_MONTH = r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*"
_NOT_FIGURES = re.compile(
    r"\b[A-Z]{1,4}-?\d+\b"                                        # identifiers: P059, S010, PO-18233
    r"|\b\d{4}-\d{2}-\d{2}\b"                                    # 2026-10-14
    rf"|\b\d{{1,2}}(?:st|nd|rd|th)?\s+{_MONTH}(?:,?\s+\d{{4}})?\b"   # 14 Oct 2026
    rf"|\b{_MONTH}\s+\d{{1,2}}(?:st|nd|rd|th)?(?:,?\s+\d{{4}})?\b"   # October 14, 2026
    r"|\b(?:19|20)\d{2}\b"                                        # a year
)
_FIGURE = re.compile(r"\d[\d,]*(?:\.\d+)?")


def figures_in(text: str) -> list[tuple[str, float]]:
    """Numbers in a text as (as written, value), leaving out identifiers and dates."""
    found = []
    for match in _FIGURE.finditer(_NOT_FIGURES.sub(" ", text)):
        written = match.group().rstrip(",")
        try:
            found.append((written, float(written.replace(",", ""))))
        except ValueError:
            continue
    return found


def unmatched_figures(text: str, reference: str) -> tuple[int, list[str]]:
    """How many figures `text` states, and which of them appear nowhere in `reference` (allowing for rounding)."""
    known = [value for _, value in figures_in(reference)]
    stated = figures_in(text)

    def is_known(value: float) -> bool:
        return any(
            abs(value - other) <= 0.051 or round(other) == value or round(other, 1) == value or abs(other) == value
            for other in known
        )

    return len(stated), list(dict.fromkeys(written for written, value in stated if not is_known(value)))


SMALL_COUNT = 10


def untraced_figures(text: str, reference: str) -> list[str]:
    """Figures in `text` found nowhere in `reference`, leaving out whole numbers up to SMALL_COUNT: those
    are nearly always counts of the things an answer lists ("3 products"), not data."""
    _, unmatched = unmatched_figures(text, reference)
    values = ((written, float(written.replace(",", ""))) for written in unmatched)
    return [written for written, value in values if not (value.is_integer() and value <= SMALL_COUNT)]


# --- Facts and checks --------------------------------------------------------------------------


class RecommendationChecker:
    def __init__(self, analytics: AnalyticsService, suppliers: SupplierService, knowledge: KnowledgeBase | None = None):
        self._analytics = analytics
        self._suppliers = suppliers
        # Rule passages state thresholds (15%, 14 days, ...) that an explanation may legitimately quote.
        self._rule_text = " ".join(entry.text for entry in knowledge.entries) if knowledge else ""

    def product_facts(self, product_id: str) -> dict[str, Any]:
        """Everything the system knows about one product's supply position, grouped by the module it comes from."""
        risk = self._analytics.get_stock_risk(product_id)
        forecast = self._analytics.get_forecast(product_id, horizon_weeks=4)
        return {
            "product": {"id": risk.product_id, "name": risk.product_name, "category": risk.category},
            "sales": {
                "avg_daily_demand_last_28_days": risk.avg_daily_demand,
                "avg_daily_demand_previous_28_days": risk.previous_avg_daily_demand,
                "demand_trend_pct": risk.demand_trend_pct,
                "units_per_week_oldest_first": [point.units for point in forecast.history[-WEEKS_OF_SALES:]],
                "forecast_units_per_week": forecast.avg_weekly_forecast,
            },
            "inventory": {
                "stock_on_hand": risk.on_hand,
                "safety_stock": risk.safety_stock,
                "reorder_level": risk.reorder_level,
                "days_of_cover": risk.days_of_cover,
                "projected_stockout_date": _iso(risk.projected_stockout_date),
            },
            "procurement": {
                "lead_time_days": risk.lead_time_days,
                "lead_time_source": risk.lead_time_source,
                "units_on_order": risk.inbound_units,
                "next_delivery_expected": _iso(risk.next_inbound_date),
                "overdue_units": risk.overdue_inbound_units,
                "units_awaiting_approval": risk.awaiting_approval_units,
            },
            "supplier": self.supplier_facts(risk.supplier_id),
            "assessment": {
                "stockout_risk_level": risk.risk_level.value,
                "drivers": risk.drivers,
                "reorder_point": risk.reorder_point,
                "suggested_order_quantity": risk.suggested_order_quantity,
                "suggested_supplier_id": risk.suggested_supplier_id,
                "suggested_supplier_name": risk.suggested_supplier_name,
            },
        }

    def supplier_facts(self, supplier_id: str) -> dict[str, Any]:
        for item in self._analytics.list_supplier_performance():
            if item.supplier_id == supplier_id:
                return {
                    "id": item.supplier_id,
                    "name": item.supplier_name,
                    "status": item.status.value,
                    "deliveries_analyzed": item.deliveries_analyzed,
                    "on_time_rate_pct": item.on_time_rate,
                    "avg_delay_days": item.avg_delay_days,
                    "max_delay_days": item.max_delay_days,
                    "avg_lead_time_days": item.avg_lead_time_days,
                    "delay_trend": item.delay_trend,
                    "open_orders": item.open_orders,
                    "overdue_orders": item.overdue_orders,
                    "delivery_risk_level": item.risk_level.value,
                    "drivers": item.drivers,
                }
        raise RecommendationError(f"Supplier '{supplier_id}' not found.")

    def check(self, proposal: RecommendationInput, facts: dict[str, Any] | None = None) -> Recommendation:
        """Checks a proposal against the system's figures. `facts` avoids recomputing them when the caller has them."""
        try:
            if proposal.subject_type == "product":
                facts = facts or self.product_facts(proposal.subject_id)
                subject_name = facts["product"]["name"]
                severity = RiskLevel(facts["assessment"]["stockout_risk_level"])
            else:
                facts = facts or self.supplier_facts(proposal.subject_id)
                subject_name = facts["name"]
                severity = RiskLevel(facts["delivery_risk_level"])
        except DomainError as error:
            raise RecommendationError(error.message) from error

        product_id = proposal.product_id or (proposal.subject_id if proposal.subject_type == "product" else None)
        supplier_id = proposal.supplier_id
        product_name = supplier_name = None
        system_quantity = quantity_matches = supplies = None

        if proposal.action == "reorder":
            if product_id is None or proposal.quantity is None:
                raise RecommendationError("A reorder needs product_id and quantity.")
        if product_id:
            product_facts = facts if proposal.subject_type == "product" and product_id == proposal.subject_id else None
            try:
                product_facts = product_facts or self.product_facts(product_id)
            except DomainError as error:
                raise RecommendationError(error.message) from error
            product_name = product_facts["product"]["name"]
            if proposal.action == "reorder":
                system_quantity = product_facts["assessment"]["suggested_order_quantity"]
                quantity_matches = proposal.quantity == system_quantity
                supplier_id = supplier_id or product_facts["assessment"]["suggested_supplier_id"] or product_facts["supplier"]["id"]
            elif supplier_id is None:
                supplier_id = product_facts["supplier"]["id"]
        elif proposal.subject_type == "supplier":
            supplier_id = supplier_id or proposal.subject_id

        if supplier_id:
            try:
                supplier = self._suppliers.get_supplier(supplier_id)
            except DomainError as error:
                raise RecommendationError(error.message) from error
            supplier_name = supplier.name
            if product_id:
                supplies = any(product.id == product_id for product in supplier.products_supplied)

        modules = sorted({item.module for item in proposal.evidence})
        data_modules = {"procurement" if module == "supplier" else module for module in modules} - {"rule"}
        text = " ".join([proposal.headline, proposal.explanation, *(item.statement for item in proposal.evidence)])
        checked, unmatched = unmatched_figures(text, json.dumps(facts) + " " + self._rule_text)

        return Recommendation(
            **proposal.model_dump(exclude={"product_id", "supplier_id"}),
            product_id=product_id,
            supplier_id=supplier_id,
            subject_name=subject_name,
            severity=severity,
            product_name=product_name,
            supplier_name=supplier_name,
            system_quantity=system_quantity,
            checks=RecommendationChecks(
                modules_cited=modules,
                cross_module=len(data_modules) >= 2,
                quantity_matches_rule=quantity_matches,
                supplier_supplies_product=supplies,
                figures_checked=checked,
                figures_unmatched=unmatched,
            ),
        )


def _iso(value) -> str | None:
    return value.isoformat() if value else None

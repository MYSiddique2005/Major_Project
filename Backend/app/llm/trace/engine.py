"""TRACE for one text: extract assertions, verify each against the system of record, report the verdicts.

    mode "rule"    the frozen version-3 patterns plus the new rule patterns; no model call
    mode "model"   assertions extracted by the model; no patterns
    mode "hybrid"  both; a statement either side contradicts is reported

If the model call fails, the rule-based verdicts still stand and the failure is recorded.
"""
from dataclasses import dataclass, field
from typing import Literal

from app.core.exceptions import DomainError
from app.llm.providers import Provider
from app.llm.recommendations import MAX_PRODUCTS_PER_ANSWER, RecommendationChecker, RecommendationError
from app.llm.trace.extract_llm import Extraction, extract
from app.llm.trace.extract_rule import from_v3, rule_assertions, v3_claims
from app.llm.trace.facts import FactSource
from app.llm.trace.schema import Assertion, Verdict
from app.llm.trace.verify import verify
from app.models.enums import Role

Mode = Literal["rule", "model", "hybrid"]


@dataclass
class TraceResult:
    verdicts: list[Verdict] = field(default_factory=list)
    extraction: Extraction | None = None  # None when no model was asked

    def contradicted(self) -> list[Verdict]:
        return [verdict for verdict in self.verdicts if verdict.status == "contradicted"]

    def summary(self) -> dict:
        """The same shape as the version-3 summary, so the API and the UI need no change."""
        return {
            "claims_checked": sum(verdict.status != "unverifiable" for verdict in self.verdicts),
            "claims_contradicted": [verdict.describe() for verdict in _one_per_statement(self.contradicted())],
        }


def _one_per_statement(verdicts: list[Verdict]) -> list[Verdict]:
    """The same false statement caught by both extractors is listed once."""
    seen, unique = set(), []
    for verdict in verdicts:
        key = (verdict.attribute, verdict.subject, verdict.comparator, verdict.asserted.lower())
        if key not in seen:
            seen.add(key)
            unique.append(verdict)
    return unique


def _dedupe(verdicts: list[Verdict]) -> list[Verdict]:
    seen, unique = set(), []
    for verdict in verdicts:
        key = (verdict.status, verdict.attribute, verdict.subject, verdict.comparator, verdict.asserted, verdict.quote.lower())
        if key not in seen:
            seen.add(key)
            unique.append(verdict)
    return unique


class TraceVerifier:
    def __init__(
        self,
        source: FactSource,
        checker: RecommendationChecker,
        provider: Provider | None = None,
        mode: Mode = "hybrid",
        role: Role | None = None,
    ):
        self.source, self.checker, self.provider, self.mode, self.role = source, checker, provider, mode, role
        self._facts: dict[str, dict | None] = {}

    def _product_facts(self, product_id: str) -> dict | None:
        if product_id not in self._facts:
            if len(self._facts) >= MAX_PRODUCTS_PER_ANSWER:
                return None
            try:
                self._facts[product_id] = self.checker.product_facts(product_id)
            except (DomainError, RecommendationError):
                self._facts[product_id] = None
        return self._facts[product_id]

    def _subject_facts(self, subject: tuple[str, str]) -> dict | None:
        kind, identifier = subject
        try:
            return self._product_facts(identifier) if kind == "product" else self.checker.supplier_facts(identifier)
        except (DomainError, RecommendationError):
            return None

    def rule_verdicts(self, text: str, subject: tuple[str, str] | None = None) -> list[Verdict]:
        facts = self._subject_facts(subject) if subject else None
        verdicts = [from_v3(claim) for claim in v3_claims(text, self._product_facts, subject, facts)]
        role = self.role.value if self.role else None
        verdicts += [verify(assertion, self.source, self.role, origin="rule") for assertion in rule_assertions(text, role)]
        return verdicts

    def model_verdicts(self, assertions: list[Assertion], subject: tuple[str, str] | None = None) -> list[Verdict]:
        verdicts = []
        for assertion in assertions:
            if subject and not assertion.subject:
                assertion = assertion.model_copy(update={"subject": subject[1]})
            verdicts.append(verify(assertion, self.source, self.role, origin="model"))
        return verdicts

    def check(self, text: str, subject: tuple[str, str] | None = None, context: str = "",
              extraction: Extraction | None = None) -> TraceResult:
        """Verdicts for `text`. `subject` is (kind, ID) for a text about one product or supplier.
        `extraction` reuses assertions already extracted (the evaluation caches them)."""
        verdicts: list[Verdict] = []
        if self.mode in ("rule", "hybrid"):
            verdicts += self.rule_verdicts(text, subject)
        if self.mode in ("model", "hybrid") and (extraction is not None or self.provider is not None):
            if extraction is None:
                role_note = f"The user's role is {self.role.value}." if self.role else ""
                extraction = extract(self.provider, text, " ".join(part for part in (role_note, context) if part))
            verdicts += self.model_verdicts(extraction.assertions, subject)
        return TraceResult(_dedupe(verdicts), extraction)

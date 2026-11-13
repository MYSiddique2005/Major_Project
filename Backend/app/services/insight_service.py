"""Proactive intelligence: the AI assistant looks at the ERP data without being asked.

A scan has a deterministic half and a model half.
  1. The analytics decide what is wrong: every High or Critical stockout or supplier finding.
  2. For the most urgent of them the server gathers the cross-module facts (sales, inventory,
     procurement, supplier) and the company rules that apply.
  3. The model receives those facts in one request and records one insight per finding: what is
     happening, why, and what to do, with its evidence.
  4. Each insight is checked (app/llm/recommendations.py) and stored with the results of the checks;
     one whose statements contradict the facts is sent back to the model to be corrected.
The model therefore explains and recommends; it does not decide what counts as a risk, and it cannot
raise an insight about anything the analytics did not flag.
"""
import json
import logging
from datetime import date, datetime, timedelta

from pydantic import ValidationError

from app.core.clock import Clock
from app.core.config import Settings
from app.core.exceptions import BusinessRuleError, DomainError, NotFoundError
from app.knowledge.base import KnowledgeBase
from app.llm.providers import KEY_NAMES, Provider, ToolResult
from app.llm.recommendations import RecommendationChecker, RecommendationError, RecommendationInput
from app.llm.tools import Tool
from app.models.entities import AiInsight, AiScan, User
from app.models.enums import AuditAction, InsightStatus, RiskLevel, ScanStatus
from app.repositories.base import AiInsightRepository, AiScanRepository, UnitOfWork
from app.security.permissions import Permission
from app.services.analytics_service import AnalyticsService
from app.services.audit_service import AuditService

logger = logging.getLogger(__name__)

RECORD_TOOL = "record_insight"
MAX_SCAN_REQUESTS = 3  # the first, plus two reminders if the model leaves findings out
RULES_FOR_SCAN = ("rule.stockout-risk", "rule.reorder-suggestion", "rule.supplier-risk", "def.units-on-order")
SEVERITY_ORDER = [RiskLevel.CRITICAL, RiskLevel.HIGH, RiskLevel.MEDIUM, RiskLevel.LOW]
CURRENT = (InsightStatus.NEW, InsightStatus.ACKNOWLEDGED)
STALE_RUNNING_SCAN = timedelta(minutes=15)
RETRY_FAILED_SCAN_AFTER = timedelta(hours=1)

SCAN_PROMPT = """\
You are the monitoring assistant inside IntelliERP, an ERP system for a wholesale company. The \
system's analytics have flagged the findings below as high or critical. For each finding you are \
given the facts from every module: sales, inventory, procurement and the supplier's delivery record.

Record one insight for every finding by calling record_insight, all in this one turn. Staff read \
these on their dashboard to decide what to do today, so each insight should let someone who has \
not looked at the data understand the situation and act.

For each insight:
- The headline says what is happening to which product or supplier.
- The explanation connects the modules: how demand, stock on hand, deliveries on the way and the \
supplier's reliability combine into this risk. Explain the risk level by the company rule given \
in the knowledge passages.
- Every figure must come from the facts given. Do not calculate new figures or estimate.
- The evidence lists the facts you relied on, each labelled with the module it comes from. Use \
facts from at least two of sales, inventory and procurement or supplier.
- Choose the action from the facts. reorder: only when the facts give a suggested order quantity \
above zero, and then use exactly that quantity and the suggested supplier. expedite_delivery: \
when units are overdue or the delivery on order arrives after the stock runs out. \
review_supplier: when the supplier's delivery record is the problem. monitor: when a delivery \
that covers the shortfall is due in time.

Use the subject_id exactly as given. Do not record an insight for anything not in the findings."""


class InsightService:
    def __init__(
        self,
        provider: Provider | None,
        analytics: AnalyticsService,
        checker: RecommendationChecker,
        knowledge: KnowledgeBase | None,
        scans: AiScanRepository,
        insights: AiInsightRepository,
        audit: AuditService,
        uow: UnitOfWork,
        settings: Settings,
        clock: Clock | None = None,
    ):
        self._clock = clock or Clock()
        self._provider = provider
        self._analytics = analytics
        self._checker = checker
        self._knowledge = knowledge
        self._scans = scans
        self._insights = insights
        self._audit = audit
        self._uow = uow
        self._settings = settings

    # --- Reading --------------------------------------------------------------------------------

    def list_insights(self, status: InsightStatus | None = None, include_past: bool = False) -> list[AiInsight]:
        """Current insights, most severe first. Dismissed and superseded ones only with `include_past`."""
        insights = [
            insight
            for insight in self._insights.list()
            if (status is None or insight.status == status)
            and (include_past or status is not None or insight.status in CURRENT)
        ]
        return sorted(insights, key=lambda i: (SEVERITY_ORDER.index(i.severity), -i.created_at.timestamp()))

    def list_scans(self, limit: int = 10) -> list[AiScan]:
        return sorted(self._scans.list(), key=lambda scan: scan.started_at, reverse=True)[:limit]

    def last_scan(self) -> AiScan | None:
        return next(iter(self.list_scans(1)), None)

    def close_interrupted_scans(self, now: datetime) -> int:
        """Marks as failed the scans still "Running" long after they started: the server stopped during them
        (the development reloader restarts it on every file change). Without this they would show as running
        for ever, and the next scheduled scan would wait a whole interval."""
        interrupted = [scan for scan in self._scans.list()
                       if scan.status == ScanStatus.RUNNING and now - scan.started_at >= STALE_RUNNING_SCAN]
        for scan in interrupted:
            scan.status, scan.finished_at = ScanStatus.FAILED, now
            scan.message = "Interrupted: the server stopped before the scan finished."
            self._scans.update(scan)
        if interrupted:
            self._uow.commit()
        return len(interrupted)

    def is_due(self, now: datetime) -> bool:
        """Whether the scheduler should scan now."""
        interval = self._settings.insight_scan_interval_minutes
        if interval <= 0 or self._provider is None:
            return False
        last = self.last_scan()
        if last is None:
            return True
        if last.status == ScanStatus.RUNNING and now - last.started_at < STALE_RUNNING_SCAN:
            return False
        if last.status == ScanStatus.FAILED:  # e.g. a rate limit: try again sooner than the next scheduled scan
            return now - last.started_at >= min(RETRY_FAILED_SCAN_AFTER, timedelta(minutes=interval))
        return now - last.started_at >= timedelta(minutes=interval)

    # --- Review ---------------------------------------------------------------------------------

    def review(self, insight_id: str, user: User, status: InsightStatus) -> AiInsight:
        insight = self._insights.get(insight_id)
        if insight is None:
            raise NotFoundError(f"Insight '{insight_id}' not found")
        if insight.status not in CURRENT:
            raise BusinessRuleError(f"Insight {insight.id} is {insight.status.lower()} and can no longer be changed")
        insight.status = status
        insight.reviewed_by = user.username
        insight.reviewed_at = datetime.now()
        self._insights.update(insight)
        self._audit.record(
            action=AuditAction.REVIEW_AI_INSIGHT, entity="AI Insight", entity_id=insight.id, user=user,
            description=f"{status.value}: {insight.headline[:200]}",
        )
        self._uow.commit()
        return insight

    # --- Scanning -------------------------------------------------------------------------------

    def run_scan(self, trigger: str, user: User | None = None) -> AiScan:
        scan = AiScan(id=self._scans.next_id(), started_at=datetime.now(), trigger=trigger, status=ScanStatus.RUNNING)
        self._scans.add(scan)
        self._uow.commit()  # visible at once, so a second scan does not start alongside this one
        try:
            self._scan(scan)
        except DomainError as error:
            scan.status, scan.message = ScanStatus.FAILED, error.message[:500]
        except Exception as error:  # a scan must never be left "Running"
            logger.exception("AI scan %s failed", scan.id)
            scan.status, scan.message = ScanStatus.FAILED, f"Unexpected error: {error}"[:500]
        scan.finished_at = datetime.now()
        scan.message = scan.message[:500]  # the column's width; a long list of rejections is cut short
        self._scans.update(scan)
        self._audit.record(
            action=AuditAction.AI_SCAN, entity="AI Scan", entity_id=scan.id, user=user, username=trigger,
            description=f"{scan.status.value}: {scan.findings} findings, {scan.insights} insights. {scan.message}"[:500],
        )
        self._uow.commit()
        return scan

    def _scan(self, scan: AiScan) -> None:
        if self._provider is None:
            key = KEY_NAMES[self._settings.llm_provider]
            scan.status, scan.message = ScanStatus.FAILED, f"The AI assistant is not configured. Set {key}."
            return
        scan.provider, scan.model = self._provider.name, self._provider.model

        alerts = self._analytics.list_alerts()  # high and critical only, stock findings first
        alerts.sort(key=lambda alert: SEVERITY_ORDER.index(alert.severity))
        scan.findings = len(alerts)
        chosen = alerts[: self._settings.insight_max_findings]
        if not chosen:
            scan.status, scan.message = ScanStatus.COMPLETED, "Nothing is at high or critical risk."
            self._supersede(set())
            return

        facts = {
            (alert.entity, alert.entity_id): (
                self._checker.product_facts(alert.entity_id) if alert.entity == "product"
                else self._checker.supplier_facts(alert.entity_id)
            )
            for alert in chosen
        }
        findings = [
            {"subject_type": subject_type, "subject_id": subject_id, "facts": subject_facts}
            for (subject_type, subject_id), subject_facts in facts.items()
        ]

        recorded: list[AiInsight] = []
        rejected: list[str] = []

        def record(proposal: RecommendationInput) -> dict:
            key = (proposal.subject_type, proposal.subject_id)
            if key not in facts:
                raise RecommendationError(f"{proposal.subject_id} is not one of the findings.")
            if any((i.subject_type, i.subject_id) == key for i in recorded):
                raise RecommendationError(f"An insight for {proposal.subject_id} was already recorded.")
            checked = self._checker.check(proposal, facts[key])
            if checked.checks.claims_contradicted:
                raise RecommendationError(
                    "Not recorded: these statements contradict the facts given: "
                    + "; ".join(checked.checks.claims_contradicted) + ". Record this insight again with them corrected."
                )
            recorded.append(AiInsight(
                id=self._insights.next_id(), scan_id=scan.id, created_at=datetime.now(),
                **checked.model_dump(exclude={"checks", "evidence"}),
                evidence=[item.model_dump() for item in checked.evidence],
                checks=checked.checks.model_dump(),
            ))
            return {"recorded": proposal.subject_id}

        tool = Tool(
            RECORD_TOOL, "Record one insight about one finding, with its recommended action and evidence.",
            Permission.AI_USE, RecommendationInput, record,
        )
        message = (
            f"<context>Today is {self._clock.today().isoformat()}.</context>\n\n{self._rules_block()}"
            f"<findings>\n{json.dumps(findings, separators=(',', ':'))}\n</findings>"
        )
        # Normally one request: the model answers with all its record_insight calls and the scan ends
        # there. If it leaves findings out, it is told which ones and asked again.
        conversation = self._provider.start(SCAN_PROMPT, [tool], [], message, require_tool=True)
        for _ in range(MAX_SCAN_REQUESTS):
            reply = conversation.reply()
            scan.model = reply.model
            results = []
            for call in reply.tool_calls:
                try:
                    if call.name != RECORD_TOOL:
                        raise RecommendationError(f"unknown tool {call.name}")
                    results.append(ToolResult(call, record(RecommendationInput.model_validate(call.arguments)), False))
                except (ValidationError, RecommendationError) as error:
                    rejected.append(f"{call.arguments.get('subject_id', '?')}: {str(error)[:120]}")
                    results.append(ToolResult(call, str(error)[:300], True))
            missing = [subject_id for (_, subject_id) in facts if all(i.subject_id != subject_id for i in recorded)]
            if not missing or not results:
                break
            # The reminder rides on the last result, which is the only channel back to the model here.
            last = results[-1]
            reminder = f"Findings still without an insight: {', '.join(missing)}. Record them now."
            results[-1] = ToolResult(
                last.call, f"{last.content} {reminder}" if last.is_error else {**last.content, "reminder": reminder},
                last.is_error,
            )
            conversation.add_tool_results(results)

        if not recorded:
            scan.status = ScanStatus.FAILED
            scan.message = "The model recorded no usable insight. " + "; ".join(rejected)
            return
        self._supersede({(insight.subject_type, insight.subject_id) for insight in recorded})
        for insight in recorded:
            self._insights.add(insight)
        scan.status, scan.insights = ScanStatus.COMPLETED, len(recorded)
        notes = []
        if len(alerts) > len(chosen):
            notes.append(f"The {len(chosen)} most severe of {len(alerts)} findings were analysed.")
        if len(recorded) < len(chosen):
            notes.append(f"The model covered {len(recorded)} of the {len(chosen)} findings it was given.")
        if rejected:
            notes.append(f"{len(rejected)} proposal(s) were rejected: " + "; ".join(rejected))
        scan.message = " ".join(notes)

    def _supersede(self, subjects: set[tuple[str, str]]) -> None:
        """Retires insights that no longer describe the present: a New insight whose subject has just been
        analysed again, and any New or Acknowledged insight whose subject the analytics no longer flag."""
        still_flagged = {(alert.entity, alert.entity_id) for alert in self._analytics.list_alerts()}
        for insight in self._insights.list():
            key = (insight.subject_type, insight.subject_id)
            replaced = insight.status == InsightStatus.NEW and key in subjects
            resolved = insight.status in CURRENT and key not in still_flagged
            if replaced or resolved:
                insight.status = InsightStatus.SUPERSEDED
                self._insights.update(insight)

    def _rules_block(self) -> str:
        if self._knowledge is None:
            return ""
        entries = [entry for entry_id in RULES_FOR_SCAN if (entry := self._knowledge.get(entry_id))]
        body = "\n\n".join(f'<passage id="{e.id}" title="{e.title}">\n{e.text}\n</passage>' for e in entries)
        return f"<knowledge>\n{body}\n</knowledge>\n\n"

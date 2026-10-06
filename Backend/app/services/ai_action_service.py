"""Controlled actions: turning an AI recommendation into a draft purchase order.

The only thing the AI side can cause is a Draft. The path is fixed:

    recommendation -> checks (app/llm/recommendations.py)
                   -> draft through ProcurementService.create_draft (the validation every order passes)
                   -> a person reviews and submits it          (procurement:create)
                   -> an approver approves or rejects it        (procurement:approve)

A draft is created only for a user who may create purchase orders themselves, it records where it
came from and the recommendation as it stood, and each step is written to the audit log. Nothing
here can submit, approve or place an order.
"""
from datetime import datetime

from app.core.exceptions import BusinessRuleError, NotFoundError, PermissionDeniedError
from app.llm.recommendations import Recommendation, RecommendationChecker, RecommendationError, RecommendationInput
from app.models.entities import User
from app.models.enums import InsightStatus, PurchaseOrderOrigin
from app.repositories.base import AiInsightRepository, UnitOfWork
from app.schemas.procurement import PurchaseOrderCreate, PurchaseOrderResponse
from app.security.permissions import Permission, has_permission
from app.services.procurement_service import ProcurementService

CURRENT = (InsightStatus.NEW, InsightStatus.ACKNOWLEDGED)


class AIActionService:
    def __init__(
        self,
        procurement: ProcurementService,
        checker: RecommendationChecker,
        insights: AiInsightRepository,
        uow: UnitOfWork,
    ):
        self._procurement = procurement
        self._checker = checker
        self._insights = insights
        self._uow = uow

    def draft_from_proposal(
        self, proposal: RecommendationInput, user: User, model: str | None = None
    ) -> tuple[PurchaseOrderResponse, Recommendation]:
        """Checks a recommendation made in the chat and drafts the purchase order it describes."""
        try:
            recommendation = self._checker.check(proposal)
        except RecommendationError as error:
            raise BusinessRuleError(str(error)) from error
        order = self._draft(recommendation, user, PurchaseOrderOrigin.AI_ASSISTANT, None, model)
        self._uow.commit()
        return order, recommendation

    def draft_from_insight(self, insight_id: str, user: User) -> PurchaseOrderResponse:
        """Drafts the purchase order a proactive insight recommends, and links the two."""
        insight = self._insights.get(insight_id)
        if insight is None:
            raise NotFoundError(f"Insight '{insight_id}' not found")
        if insight.status not in CURRENT:
            raise BusinessRuleError(f"Insight {insight.id} is {insight.status.lower()}; run a new scan first")
        if insight.purchase_order_id:
            raise BusinessRuleError(f"Insight {insight.id} was already drafted as {insight.purchase_order_id}")
        # The stored insight was checked when it was recorded; checking again uses today's figures, so a
        # quantity that no longer matches the reorder rule is flagged on the draft.
        try:
            recommendation = self._checker.check(RecommendationInput.model_validate(insight.model_dump()))
        except RecommendationError as error:
            raise BusinessRuleError(str(error)) from error
        scan_model = None
        order = self._draft(recommendation, user, PurchaseOrderOrigin.AI_INSIGHT, insight.id, scan_model)

        insight.purchase_order_id = order.id
        if insight.status == InsightStatus.NEW:
            insight.status = InsightStatus.ACKNOWLEDGED
            insight.reviewed_by, insight.reviewed_at = user.username, datetime.now()
        self._insights.update(insight)
        self._uow.commit()
        return order

    def _draft(
        self, recommendation: Recommendation, user: User, origin: PurchaseOrderOrigin, origin_ref: str | None,
        model: str | None,
    ) -> PurchaseOrderResponse:
        if not has_permission(user.role, Permission.PROCUREMENT_CREATE):
            raise PermissionDeniedError("Your role cannot create purchase orders, so the assistant cannot draft one for you")
        if recommendation.action != "reorder":
            raise BusinessRuleError(f"Only a reorder recommendation can become a purchase order, not '{recommendation.action}'")
        if not recommendation.product_id or not recommendation.supplier_id or not recommendation.quantity:
            raise BusinessRuleError("The recommendation does not name a product, a supplier and a quantity")
        if recommendation.checks.supplier_supplies_product is False:
            raise BusinessRuleError(f"{recommendation.supplier_name} does not supply {recommendation.product_name}")

        snapshot = {
            **recommendation.model_dump(mode="json", include={"headline", "explanation", "severity", "system_quantity"}),
            "evidence": [item.model_dump() for item in recommendation.evidence],
            "checks": recommendation.checks.model_dump(),
            "model": model,
            "requested_by": user.username,
        }
        return self._procurement.create_draft(
            PurchaseOrderCreate(
                supplier_id=recommendation.supplier_id,
                product_id=recommendation.product_id,
                quantity=recommendation.quantity,
                reason=f"AI recommendation: {recommendation.headline}"[:500],
            ),
            user,
            origin=origin,
            origin_ref=origin_ref,
            ai_recommendation=snapshot,
            commit=False,
        )

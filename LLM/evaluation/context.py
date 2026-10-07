"""Builds the assistant exactly as the web application does, but outside a web request.

The evaluation calls the same AIService, tools, knowledge base and provider as the chat page, on the
database the application is configured for. The only addition is a record of what each tool
returned, which the scoring needs in order to tell which figures in an answer are supported.
"""
from contextlib import contextmanager

from app.api import deps
from app.core.clock import Clock
from app.core.config import get_settings
from app.db.session import get_session_factory
from app.knowledge.content import get_knowledge_base
from app.llm.recommendations import RecommendationChecker
from app.llm.tools import Toolbox
from app.services.ai_action_service import AIActionService
from app.services.ai_service import AIService
from app.services.analytics_service import AnalyticsService
from app.services.audit_service import AuditService
from app.services.inventory_service import InventoryService
from app.services.procurement_service import ProcurementService
from app.services.product_service import ProductService
from app.services.sales_service import SalesService
from app.services.supplier_service import SupplierService


class Context:
    """The application's services on one database session."""

    def __init__(self, session):
        self.settings = get_settings()
        self.session = session
        self.products_repo = deps.get_product_repository(session)
        self.suppliers_repo = deps.get_supplier_repository(session)
        self.inventory_repo = deps.get_inventory_repository(session)
        self.sales_repo = deps.get_sales_repository(session)
        self.orders_repo = deps.get_purchase_order_repository(session)
        self.insights_repo = deps.get_ai_insight_repository(session)
        self.scans_repo = deps.get_ai_scan_repository(session)
        self.users_repo = deps.get_user_repository(session)
        self.uow = deps.get_unit_of_work(session)
        self.audit = AuditService(deps.get_audit_log_repository(session))

        self.clock = Clock(self.sales_repo, self.settings.business_date)
        self.analytics = AnalyticsService(
            self.products_repo, self.inventory_repo, self.sales_repo, self.orders_repo, self.suppliers_repo, self.clock
        )
        self.products = ProductService(self.products_repo, self.suppliers_repo, self.inventory_repo)
        self.inventory = InventoryService(self.inventory_repo, self.products_repo)
        self.sales = SalesService(self.sales_repo, self.products_repo)
        self.suppliers = SupplierService(self.suppliers_repo, self.products_repo)
        self.procurement = ProcurementService(
            self.orders_repo, self.suppliers_repo, self.products_repo,
            deps.get_approval_repository(session), self.audit, self.uow, self.clock,
        )
        self.provider = deps.get_llm_provider()

    def user(self, username: str):
        return self.users_repo.get_by_username(username)

    def assistant(self, grounded: bool) -> tuple[AIService, Toolbox, list[dict]]:
        """A fresh assistant for one question, its toolbox, and the list its tool outputs are recorded in."""
        knowledge = get_knowledge_base() if grounded else None
        checker = RecommendationChecker(self.analytics, self.suppliers, knowledge)
        actions = AIActionService(self.procurement, checker, self.insights_repo, self.uow)
        toolbox = Toolbox(
            self.analytics, self.products, self.inventory, self.sales, self.suppliers, self.procurement, knowledge, actions,
            self.clock,
        )
        outputs: list[dict] = []
        run = toolbox.run

        def recording_run(user, name, arguments):
            try:
                result = run(user, name, arguments)
            except Exception as error:
                outputs.append({"tool": name, "error": str(error)})
                raise
            outputs.append({"tool": name, "result": result})
            return result

        toolbox.run = recording_run
        return AIService(self.provider, toolbox, self.audit, self.uow, self.settings, knowledge), toolbox, outputs


@contextmanager
def open_context():
    session = None if get_settings().data_backend == "memory" else get_session_factory()()
    try:
        yield Context(session)
    finally:
        if session is not None:
            session.close()

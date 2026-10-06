"""Composition root: builds repositories and services for each request.

DATA_BACKEND selects the repository implementations:
  postgres - SQLAlchemy repositories sharing one session per request
  memory   - process-wide in-memory repositories seeded from app/mock_data

Services and routes depend only on the abstractions in app/repositories/base.py.
"""
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from functools import lru_cache

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_session_factory
from app.knowledge.base import KnowledgeBase
from app.knowledge.content import get_knowledge_base
from app.llm.providers import Provider, build_provider
from app.llm.recommendations import RecommendationChecker
from app.llm.tools import Toolbox
from app.repositories import postgres
from app.repositories.base import (
    AiInsightRepository,
    AiScanRepository,
    ApprovalRepository,
    AuditLogRepository,
    InventoryRepository,
    NoOpUnitOfWork,
    ProductRepository,
    PurchaseOrderRepository,
    SalesRepository,
    SupplierRepository,
    UnitOfWork,
    UserRepository,
)
from app.repositories.mock_ai import MockAiInsightRepository, MockAiScanRepository
from app.repositories.mock_approvals import MockApprovalRepository
from app.repositories.mock_audit import MockAuditLogRepository
from app.repositories.mock_inventory import MockInventoryRepository
from app.repositories.mock_procurement import MockPurchaseOrderRepository
from app.repositories.mock_products import MockProductRepository
from app.repositories.mock_sales import MockSalesRepository
from app.repositories.mock_suppliers import MockSupplierRepository
from app.repositories.mock_users import MockUserRepository
from app.services.ai_action_service import AIActionService
from app.services.ai_service import AIService
from app.services.analytics_service import AnalyticsService
from app.services.approval_service import ApprovalService
from app.services.audit_service import AuditService
from app.services.auth_service import AuthService
from app.services.dashboard_service import DashboardService
from app.services.insight_service import InsightService
from app.services.inventory_service import InventoryService
from app.services.procurement_service import ProcurementService
from app.services.product_service import ProductService
from app.services.sales_service import SalesService
from app.services.supplier_service import SupplierService

# --- Data backends ------------------------------------------------------------


@dataclass
class MemoryStore:
    users: UserRepository = field(default_factory=MockUserRepository)
    products: ProductRepository = field(default_factory=MockProductRepository)
    suppliers: SupplierRepository = field(default_factory=MockSupplierRepository)
    inventory: InventoryRepository = field(default_factory=MockInventoryRepository)
    sales: SalesRepository = field(default_factory=MockSalesRepository)
    purchase_orders: PurchaseOrderRepository = field(default_factory=MockPurchaseOrderRepository)
    approvals: ApprovalRepository = field(default_factory=MockApprovalRepository)
    audit_logs: AuditLogRepository = field(default_factory=MockAuditLogRepository)
    ai_scans: AiScanRepository = field(default_factory=MockAiScanRepository)
    ai_insights: AiInsightRepository = field(default_factory=MockAiInsightRepository)


@lru_cache
def _memory() -> MemoryStore:
    return MemoryStore()


def reset_memory_state() -> None:
    """Discard in-memory data and rebuild it from the seed records (used by tests)."""
    _memory.cache_clear()


def get_session() -> Iterator[Session | None]:
    """One database session per request; None when running on the in-memory backend.

    Uncommitted work is rolled back when the session closes, so a use case that
    fails part-way leaves nothing behind.
    """
    if get_settings().data_backend == "memory":
        yield None
        return
    session = get_session_factory()()
    try:
        yield session
    finally:
        session.close()


def get_unit_of_work(session: Session | None = Depends(get_session)) -> UnitOfWork:
    return postgres.SqlUnitOfWork(session) if session else NoOpUnitOfWork()


# --- Repositories -------------------------------------------------------------


def get_user_repository(session: Session | None = Depends(get_session)) -> UserRepository:
    return postgres.PostgresUserRepository(session) if session else _memory().users


def get_product_repository(session: Session | None = Depends(get_session)) -> ProductRepository:
    return postgres.PostgresProductRepository(session) if session else _memory().products


def get_supplier_repository(session: Session | None = Depends(get_session)) -> SupplierRepository:
    return postgres.PostgresSupplierRepository(session) if session else _memory().suppliers


def get_inventory_repository(session: Session | None = Depends(get_session)) -> InventoryRepository:
    return postgres.PostgresInventoryRepository(session) if session else _memory().inventory


def get_sales_repository(session: Session | None = Depends(get_session)) -> SalesRepository:
    return postgres.PostgresSalesRepository(session) if session else _memory().sales


def get_purchase_order_repository(session: Session | None = Depends(get_session)) -> PurchaseOrderRepository:
    return postgres.PostgresPurchaseOrderRepository(session) if session else _memory().purchase_orders


def get_approval_repository(session: Session | None = Depends(get_session)) -> ApprovalRepository:
    return postgres.PostgresApprovalRepository(session) if session else _memory().approvals


def get_audit_log_repository(session: Session | None = Depends(get_session)) -> AuditLogRepository:
    return postgres.PostgresAuditLogRepository(session) if session else _memory().audit_logs


def get_ai_scan_repository(session: Session | None = Depends(get_session)) -> AiScanRepository:
    return postgres.PostgresAiScanRepository(session) if session else _memory().ai_scans


def get_ai_insight_repository(session: Session | None = Depends(get_session)) -> AiInsightRepository:
    return postgres.PostgresAiInsightRepository(session) if session else _memory().ai_insights


# --- Services -----------------------------------------------------------------


def get_audit_service(audit_logs: AuditLogRepository = Depends(get_audit_log_repository)) -> AuditService:
    return AuditService(audit_logs)


def get_auth_service(
    users: UserRepository = Depends(get_user_repository),
    audit: AuditService = Depends(get_audit_service),
    uow: UnitOfWork = Depends(get_unit_of_work),
) -> AuthService:
    return AuthService(users, audit, uow)


def get_product_service(
    products: ProductRepository = Depends(get_product_repository),
    suppliers: SupplierRepository = Depends(get_supplier_repository),
    inventory: InventoryRepository = Depends(get_inventory_repository),
) -> ProductService:
    return ProductService(products, suppliers, inventory)


def get_inventory_service(
    inventory: InventoryRepository = Depends(get_inventory_repository),
    products: ProductRepository = Depends(get_product_repository),
) -> InventoryService:
    return InventoryService(inventory, products)


def get_sales_service(
    sales: SalesRepository = Depends(get_sales_repository),
    products: ProductRepository = Depends(get_product_repository),
) -> SalesService:
    return SalesService(sales, products)


def get_supplier_service(
    suppliers: SupplierRepository = Depends(get_supplier_repository),
    products: ProductRepository = Depends(get_product_repository),
) -> SupplierService:
    return SupplierService(suppliers, products)


def get_procurement_service(
    purchase_orders: PurchaseOrderRepository = Depends(get_purchase_order_repository),
    suppliers: SupplierRepository = Depends(get_supplier_repository),
    products: ProductRepository = Depends(get_product_repository),
    approvals: ApprovalRepository = Depends(get_approval_repository),
    audit: AuditService = Depends(get_audit_service),
    uow: UnitOfWork = Depends(get_unit_of_work),
) -> ProcurementService:
    return ProcurementService(purchase_orders, suppliers, products, approvals, audit, uow)


def get_approval_service(
    approvals: ApprovalRepository = Depends(get_approval_repository),
    purchase_orders: PurchaseOrderRepository = Depends(get_purchase_order_repository),
    procurement: ProcurementService = Depends(get_procurement_service),
    audit: AuditService = Depends(get_audit_service),
    uow: UnitOfWork = Depends(get_unit_of_work),
) -> ApprovalService:
    return ApprovalService(approvals, purchase_orders, procurement, audit, uow, get_settings().separation_of_duties)


def get_dashboard_service(
    sales: SalesService = Depends(get_sales_service),
    inventory: InventoryService = Depends(get_inventory_service),
    purchase_orders: PurchaseOrderRepository = Depends(get_purchase_order_repository),
    suppliers: SupplierRepository = Depends(get_supplier_repository),
) -> DashboardService:
    return DashboardService(sales, inventory, purchase_orders, suppliers)


def get_analytics_service(
    products: ProductRepository = Depends(get_product_repository),
    inventory: InventoryRepository = Depends(get_inventory_repository),
    sales: SalesRepository = Depends(get_sales_repository),
    purchase_orders: PurchaseOrderRepository = Depends(get_purchase_order_repository),
    suppliers: SupplierRepository = Depends(get_supplier_repository),
) -> AnalyticsService:
    return AnalyticsService(products, inventory, sales, purchase_orders, suppliers)


@lru_cache
def get_llm_provider() -> Provider | None:
    """One model client for the process; None when the provider's API key is not configured."""
    return build_provider(get_settings())


def get_knowledge() -> KnowledgeBase | None:
    """The knowledge base, or None when grounding is switched off."""
    return get_knowledge_base() if get_settings().llm_grounding else None


def get_ai_action_service(
    knowledge: KnowledgeBase | None = Depends(get_knowledge),
    analytics: AnalyticsService = Depends(get_analytics_service),
    suppliers: SupplierService = Depends(get_supplier_service),
    procurement: ProcurementService = Depends(get_procurement_service),
    insights: AiInsightRepository = Depends(get_ai_insight_repository),
    uow: UnitOfWork = Depends(get_unit_of_work),
) -> AIActionService:
    return AIActionService(procurement, RecommendationChecker(analytics, suppliers, knowledge), insights, uow)


def get_ai_service(
    provider: Provider | None = Depends(get_llm_provider),
    actions: AIActionService = Depends(get_ai_action_service),
    knowledge: KnowledgeBase | None = Depends(get_knowledge),
    analytics: AnalyticsService = Depends(get_analytics_service),
    products: ProductService = Depends(get_product_service),
    inventory: InventoryService = Depends(get_inventory_service),
    sales: SalesService = Depends(get_sales_service),
    suppliers: SupplierService = Depends(get_supplier_service),
    procurement: ProcurementService = Depends(get_procurement_service),
    audit: AuditService = Depends(get_audit_service),
    uow: UnitOfWork = Depends(get_unit_of_work),
) -> AIService:
    toolbox = Toolbox(analytics, products, inventory, sales, suppliers, procurement, knowledge, actions)
    return AIService(provider, toolbox, audit, uow, get_settings(), knowledge)


def get_insight_service(
    provider: Provider | None = Depends(get_llm_provider),
    knowledge: KnowledgeBase | None = Depends(get_knowledge),
    analytics: AnalyticsService = Depends(get_analytics_service),
    suppliers: SupplierService = Depends(get_supplier_service),
    scans: AiScanRepository = Depends(get_ai_scan_repository),
    insights: AiInsightRepository = Depends(get_ai_insight_repository),
    audit: AuditService = Depends(get_audit_service),
    uow: UnitOfWork = Depends(get_unit_of_work),
) -> InsightService:
    checker = RecommendationChecker(analytics, suppliers, knowledge)
    return InsightService(provider, analytics, checker, knowledge, scans, insights, audit, uow, get_settings())


@contextmanager
def insight_service_outside_a_request(provider_factory=get_llm_provider) -> Iterator[InsightService]:
    """The insight service with its own database session, for the scheduler (which has no request to hang it on)."""
    session = None if get_settings().data_backend == "memory" else get_session_factory()()
    try:
        products, suppliers = get_product_repository(session), get_supplier_repository(session)
        analytics = AnalyticsService(
            products, get_inventory_repository(session), get_sales_repository(session),
            get_purchase_order_repository(session), suppliers,
        )
        yield get_insight_service(
            provider_factory(), get_knowledge(), analytics, SupplierService(suppliers, products),
            get_ai_scan_repository(session), get_ai_insight_repository(session),
            AuditService(get_audit_log_repository(session)), get_unit_of_work(session),
        )
    finally:
        if session is not None:
            session.close()

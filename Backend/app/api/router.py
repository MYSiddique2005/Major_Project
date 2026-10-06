from fastapi import APIRouter

from app.api.v1 import (
    ai,
    analytics,
    approvals,
    audit,
    auth,
    dashboard,
    insights,
    inventory,
    procurement,
    products,
    sales,
    suppliers,
    system,
)

api_router = APIRouter()
for module in (auth, dashboard, sales, inventory, procurement, suppliers, products, approvals, analytics, audit, ai, insights, system):
    api_router.include_router(module.router)

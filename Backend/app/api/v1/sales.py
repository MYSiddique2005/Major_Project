from fastapi import APIRouter, Depends

from app.api.deps import get_sales_service
from app.models.enums import SalesStatus
from app.schemas.sales import SalesOrderResponse, SalesStats
from app.security.authorization import require_permission
from app.security.permissions import Permission
from app.services.sales_service import SalesService

router = APIRouter(prefix="/sales", tags=["Sales"], dependencies=[Depends(require_permission(Permission.SALES_VIEW))])


@router.get("", response_model=list[SalesOrderResponse], summary="List sales orders (newest first)")
def list_sales(
    search: str | None = None,
    status: SalesStatus | None = None,
    product_id: str | None = None,
    service: SalesService = Depends(get_sales_service),
):
    return service.list_orders(search, status, product_id)


@router.get("/stats", response_model=SalesStats, summary="Sales statistics")
def sales_stats(service: SalesService = Depends(get_sales_service)):
    return service.get_stats()


@router.get("/{order_id}", response_model=SalesOrderResponse, summary="Get a sales order")
def get_sale(order_id: str, service: SalesService = Depends(get_sales_service)):
    return service.get_order(order_id)

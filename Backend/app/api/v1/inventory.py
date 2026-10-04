from fastapi import APIRouter, Depends

from app.api.deps import get_inventory_service
from app.models.enums import StockStatus
from app.schemas.inventory import InventoryResponse, InventoryStats
from app.security.authorization import require_permission
from app.security.permissions import Permission
from app.services.inventory_service import InventoryService

router = APIRouter(
    prefix="/inventory", tags=["Inventory"], dependencies=[Depends(require_permission(Permission.INVENTORY_VIEW))]
)


@router.get("", response_model=list[InventoryResponse], summary="List inventory records")
def list_inventory(
    search: str | None = None,
    status: StockStatus | None = None,
    warehouse: str | None = None,
    product_id: str | None = None,
    service: InventoryService = Depends(get_inventory_service),
):
    return service.list_inventory(search, status, warehouse, product_id)


@router.get("/stats", response_model=InventoryStats, summary="Inventory statistics")
def inventory_stats(service: InventoryService = Depends(get_inventory_service)):
    return service.get_stats()


@router.get("/{inventory_id}", response_model=InventoryResponse, summary="Get an inventory record")
def get_inventory_item(inventory_id: str, service: InventoryService = Depends(get_inventory_service)):
    return service.get_item(inventory_id)

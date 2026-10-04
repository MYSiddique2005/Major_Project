from fastapi import APIRouter, Depends

from app.api.deps import get_product_service
from app.models.enums import ProductStatus
from app.schemas.product import ProductResponse
from app.security.authorization import require_permission
from app.security.permissions import Permission
from app.services.product_service import ProductService

router = APIRouter(
    prefix="/products", tags=["Products"], dependencies=[Depends(require_permission(Permission.PRODUCTS_VIEW))]
)


@router.get("", response_model=list[ProductResponse], summary="List products")
def list_products(
    search: str | None = None,
    category: str | None = None,
    status: ProductStatus | None = None,
    service: ProductService = Depends(get_product_service),
):
    return service.list_products(search, category, status)


@router.get("/{product_id}", response_model=ProductResponse, summary="Get a product")
def get_product(product_id: str, service: ProductService = Depends(get_product_service)):
    return service.get_product(product_id)

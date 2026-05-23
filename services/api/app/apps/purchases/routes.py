from fastapi import APIRouter, Depends, Path
from lib.utils.schemas.products import PurchaseStatus
from services.api.app.apps.auth import dependencies as auth_dependencies
from services.api.app.apps.purchases.schemas import Product, PurchaseProductResponse
from services.api.app.apps.purchases.service import PurchasesService
from services.api.app.dependencies import get_purchase_service


router = APIRouter()


@router.get("/products")
async def get_products(
    _=Depends(auth_dependencies.is_user_authorized),
    purchase_service: PurchasesService = Depends(get_purchase_service),
) -> list[Product]:
    return await purchase_service.get_all_products()


@router.post("/user/{user_id}/purchase-product/{product_id}")
async def purchase_product(
    _=Depends(auth_dependencies.validate_user),
    purchase_service: PurchasesService = Depends(get_purchase_service),
    user_id: int = Path(..., gt=0),
    product_id: int = Path(..., gt=0),
) -> PurchaseProductResponse:
    return await purchase_service.purchase_product(
        user_id=user_id,
        product_id=product_id,
    )


@router.get("/user/{user_id}/purchase-status/{purchase_id}")
async def get_purchase_status(
    _=Depends(auth_dependencies.validate_user),
    purchase_service: PurchasesService = Depends(get_purchase_service),
    user_id: int = Path(..., gt=0),
    purchase_id: int = Path(..., gt=0),
) -> PurchaseStatus:
    return await purchase_service.get_purchase_status(
        user_id=user_id,
        purchase_id=purchase_id,
    )


@router.get("/payment-notification")
async def payment_notification(
    _=Depends(auth_dependencies.validate_user),
    purchase_service: PurchasesService = Depends(get_purchase_service),
    user_id: int = Path(..., gt=0),
    purchase_id: int = Path(..., gt=0),
) -> PurchaseStatus:
    return await purchase_service.get_purchase_status(
        user_id=user_id,
        purchase_id=purchase_id,
    )

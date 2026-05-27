from fastapi import APIRouter, Body, Depends, Path
from lib.utils.clients.ckassa import CKassaClient
from lib.utils.schemas.products import PurchaseStatus
from services.api.app.apps.auth import dependencies as auth_dependencies
from services.api.app.apps.purchases.schemas import Product, PurchaseProductResponse
from services.api.app.apps.purchases.service import PurchasesService
from services.api.app.dependencies import get_ckassa_client, get_purchase_service


router = APIRouter()


@router.get("/products")
async def get_products(
    _=Depends(auth_dependencies.is_user_authorized),
    purchase_service: PurchasesService = Depends(get_purchase_service),
) -> list[Product]:
    return await purchase_service.get_all_products()


@router.post("/purchase-product/{product_id}")
async def purchase_product(
    user_id: int = Depends(auth_dependencies.is_user_authorized),
    purchase_service: PurchasesService = Depends(get_purchase_service),
    ckassa_client: CKassaClient = Depends(get_ckassa_client),
    product_id: int = Path(..., gt=0),
) -> PurchaseProductResponse:
    return await purchase_service.purchase_product(
        ckassa_client=ckassa_client,
        user_id=user_id,
        product_id=product_id,
    )


@router.get("/purchase-status/{purchase_id}")
async def get_purchase_status(
    user_id: int = Depends(auth_dependencies.is_user_authorized),
    purchase_service: PurchasesService = Depends(get_purchase_service),
    purchase_id: int = Path(..., gt=0),
) -> PurchaseStatus:
    return await purchase_service.get_purchase_status(
        user_id=user_id,
        purchase_id=purchase_id,
    )


@router.post("/payment-notification")
async def payment_notification(
    body: dict = Body(...),
    purchase_service: PurchasesService = Depends(get_purchase_service),
) -> None:
    await purchase_service.process_payment_notification(data=body)

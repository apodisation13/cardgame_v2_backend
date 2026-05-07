from fastapi import APIRouter, Depends

from services.api.app.apps.auth import dependencies as auth_dependencies
from services.api.app.apps.purchases.schemas import Product
from services.api.app.apps.purchases.service import PurchasesService
from services.api.app.dependencies import get_purchase_service

router = APIRouter()


@router.get("/products")
async def get_products(
    _=Depends(auth_dependencies.is_user_authorized),
    purchase_service: PurchasesService = Depends(get_purchase_service),
) -> list[Product]:
    return await purchase_service.get_all_products()

from lib.utils.schemas import Base
from lib.utils.schemas.products import ProductType


class Product(Base):
    id: int
    title: str
    type: ProductType
    data: dict
    price: float

    @staticmethod
    def get_one(row: dict) -> "Product":
        return Product(
            id=row["id"],
            title=row["title"],
            type=ProductType(row["type"]),
            data=row["data"],
            price=row["price"],
        )


class PurchaseProductResponse(Base):
    purchase_id: int
    confirmation_url: str | None = None

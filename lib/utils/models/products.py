from decimal import Decimal
from typing import Any

from lib.utils.models import BaseModel, TimestampMixin
from lib.utils.schemas.products import ProductType, PurchaseStatus
from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column


class Product(BaseModel, TimestampMixin):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    title: Mapped[str] = mapped_column(
        String(511),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        server_default="true",
    )
    type: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        server_default=ProductType.RESOURCE,
    )
    priority: Mapped[int] = mapped_column(
        Integer,
        server_default="0",
    )
    data: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        server_default="{}",
        nullable=False,
    )
    price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<Product(id={self.id}, title='{self.title}')>"


class Purchase(BaseModel, TimestampMixin):
    __tablename__ = "purchases"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    product_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("products.id", ondelete="RESTRICT"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String,
        server_default=PurchaseStatus.PENDING,
        nullable=False,
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )
    transaction_id: Mapped[str] = mapped_column(
        String,
        nullable=True,
        index=True,
    )
    response_description: Mapped[str] = mapped_column(
        String(2055),
        nullable=True,
    )

    def __repr__(self) -> str:
        return f"<Purchase(id={self.id}, status='{self.status}')>"

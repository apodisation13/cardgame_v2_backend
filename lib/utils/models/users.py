from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from lib.utils.models import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(default=True)

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}')>"

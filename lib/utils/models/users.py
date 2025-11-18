from lib.utils.models import BaseModel
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column


class User(BaseModel):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(server_default="true")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}')>"

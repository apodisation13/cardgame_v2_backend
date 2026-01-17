from lib.utils.models import BaseModel, TimestampMixin
from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column


class News(BaseModel, TimestampMixin):
    __tablename__ = "news"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(511), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(server_default="true")
    priority: Mapped[int] = mapped_column(server_default="0")

    def __repr__(self) -> str:
        return f"<News(id={self.id}, title='{self.title}')>"

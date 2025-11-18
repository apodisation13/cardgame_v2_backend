from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Базовый класс для всех моделей SQLAlchemy 2.0"""


class BaseModel(Base):
    __abstract__ = True


from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

Base = declarative_base()


class BaseModel(Base):
    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

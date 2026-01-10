from datetime import datetime

from lib.utils.schemas import Base


class News(Base):
    id: int
    title: str
    text: str
    updated_at: datetime

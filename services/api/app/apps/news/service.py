from lib.utils.db.pool import Database
from services.api.app.apps.news.schemas import News
from services.api.app.config import Config


class NewsService:
    def __init__(
        self,
        db_pool: Database,
        config: Config,
    ):
        self.db_pool = db_pool
        self.config = config

    async def list_news(self) -> list[News]:
        async with self.db_pool.connection() as connection:
            news = await connection.fetch(
                """
                    SELECT
                        id,
                        title,
                        text,
                        updated_at
                    FROM
                        news
                    WHERE
                        is_active IS TRUE
                    ORDER BY
                        priority DESC,
                        updated_at DESC
                """,
            )

        news_list = [
            News.model_validate(
                {
                    "id": row["id"],
                    "title": row["title"],
                    "text": row["text"],
                    "updated_at": row["updated_at"],
                },
            )
            for row in news
        ]

        return news_list

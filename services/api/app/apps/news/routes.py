from fastapi import APIRouter, Depends
from services.api.app.apps.news.schemas import News
from services.api.app.apps.news.service import NewsService
from services.api.app.dependencies import get_news_service


router = APIRouter()


@router.get("/list-news")
async def register(
    service: NewsService = Depends(get_news_service),
) -> list[News]:
    return await service.list_news()

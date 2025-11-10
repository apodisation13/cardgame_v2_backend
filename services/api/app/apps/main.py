# from contextlib import asynccontextmanager
# from typing import AsyncGenerator, List, Sequence
#
# from fastapi import Depends, FastAPI, HTTPException
# from sqlalchemy import select
# from sqlalchemy.ext.asyncio import AsyncSession
#
# from . import schemas
# from .db import create_tables, engine, get_db
# from .models import User
#
#
# @asynccontextmanager
# async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
#     """Lifespan context manager для управления событиями жизненного цикла приложения"""
#     # Startup event - создание таблиц
#     await create_tables()
#
#     yield  # Здесь приложение работает
#
#     # Shutdown event - закрытие соединений
#     await engine.dispose()
#
#
# app = FastAPI(
#     title="User API",
#     version="1.0.0",
#     lifespan=lifespan  # Используем современный способ обработки событий
# )
#
#
# @app.get("/users", response_model=List[schemas.User])
# async def get_users(db: AsyncSession = Depends(get_db)) -> Sequence[schemas.User]:
#     """Асинхронный эндпоинт для получения всех пользователей"""
#     result = await db.execute(select(User))
#     users = result.scalars().all()
#     return users
#
#
# @app.post("/users", response_model=schemas.User)
# async def create_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)) -> schemas.User:
#     """Асинхронный эндпоинт для создания пользователя"""
#     # Проверяем, существует ли пользователь с таким email
#     result = await db.execute(select(User).where(User.email == user.email))
#     existing_user = result.scalar_one_or_none()
#
#     if existing_user:
#         raise HTTPException(status_code=400, detail="Email already registered")
#
#     # Базовая валидация email
#     if "@" not in user.email:
#         raise HTTPException(status_code=422, detail="Invalid email format")
#
#     db_user = User(name=user.name, email=user.email)
#     db.add(db_user)
#     await db.commit()
#     await db.refresh(db_user)
#     return db_user
#
#
# @app.get("/users/{user_id}", response_model=schemas.User)
# async def get_user(user_id: int, db: AsyncSession = Depends(get_db)) -> schemas.User:
#     """Асинхронный эндпоинт для получения пользователя по ID"""
#     result = await db.execute(select(User).where(User.id == user_id))
#     user = result.scalar_one_or_none()
#
#     if user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#
#     return user
#
#
# @app.get("/")
# async def read_root() -> dict:
#     return {"message": "User API is running"}
#
#
# @app.get("/health")
# async def health_check() -> dict:
#     return {"status": "healthy"}

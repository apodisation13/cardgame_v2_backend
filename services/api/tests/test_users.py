from typing import List

import pytest

from services.api.app.apps.models import User
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from services.api.tests.factories import UserFactory


class TestUsersAPI:
    """Асинхронные тесты для эндпоинта /users"""

    @pytest.mark.asyncio
    async def test_get_users_empty(self, client: AsyncClient) -> None:
        """Тест получения пустого списка пользователей"""
        response = await client.get("/users")

        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_get_users_with_data(self, client: AsyncClient, sample_users: List[User]) -> None:
        """Тест получения списка пользователей с данными"""
        response = await client.get("/users")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

        # Проверяем структуру ответа
        for user in data:
            assert "id" in user
            assert "name" in user
            assert "email" in user
            assert isinstance(user["id"], int)
            assert isinstance(user["name"], str)
            assert isinstance(user["email"], str)

    @pytest.mark.asyncio
    async def test_get_users_structure(self, client: AsyncClient, single_user: User) -> None:
        """Тест структуры ответа пользователей"""
        response = await client.get("/users")

        assert response.status_code == 200
        data = response.json()

        assert len(data) == 1
        user = data[0]

        assert user["id"] == single_user.id
        assert user["name"] == single_user.name
        assert user["email"] == single_user.email

    @pytest.mark.asyncio
    async def test_create_user(self, client: AsyncClient, db_session: AsyncSession) -> None:
        """Тест создания пользователя"""
        user_data = {
            "name": "New User",
            "email": "new@example.com"
        }

        response = await client.post("/users", json=user_data)

        assert response.status_code == 200
        data = response.json()

        assert data["name"] == "New User"
        assert data["email"] == "new@example.com"
        assert "id" in data

        # Проверяем, что пользователь действительно создан в БД
        result = await db_session.execute(select(User).where(User.id == data["id"]))
        db_user = result.scalar_one()

        assert db_user.name == "New User"
        assert db_user.email == "new@example.com"

    @pytest.mark.asyncio
    async def test_create_user_duplicate_email(self, client: AsyncClient, single_user: User) -> None:
        """Тест создания пользователя с существующим email"""
        user_data = {
            "name": "New User",
            "email": single_user.email  # Используем email существующего пользователя
        }

        response = await client.post("/users", json=user_data)

        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_get_user_by_id(self, client: AsyncClient, single_user: User) -> None:
        """Тест получения пользователя по ID"""
        response = await client.get(f"/users/{single_user.id}")

        assert response.status_code == 200
        data = response.json()

        assert data["id"] == single_user.id
        assert data["name"] == single_user.name
        assert data["email"] == single_user.email

    @pytest.mark.asyncio
    async def test_get_user_not_found(self, client: AsyncClient) -> None:
        """Тест получения несуществующего пользователя"""
        response = await client.get("/users/999")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_health_check(self, client: AsyncClient) -> None:
        """Тест health check эндпоинта"""
        response = await client.get("/health")

        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}


class TestUserModel:
    """Тесты для модели User с использованием фабрик"""

    @pytest.mark.asyncio
    async def test_user_creation_via_factory(self, db_session: AsyncSession) -> None:
        """Тест создания пользователя через фабрику"""
        user = UserFactory.build(
            name="John Doe",
            email="john@example.com"
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        # Проверяем что пользователь сохранен в базе
        result = await db_session.execute(select(User).where(User.id == user.id))
        db_user = result.scalar_one()

        assert db_user.id == user.id
        assert db_user.name == "John Doe"
        assert db_user.email == "john@example.com"

    @pytest.mark.asyncio
    async def test_user_string_representation_via_factory(self, db_session: AsyncSession) -> None:
        """Тест строкового представления пользователя через фабрику"""
        user = UserFactory.build(name="Test User", email="test@example.com")
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        assert str(user) == f"<User(id={user.id}, name='Test User', email='test@example.com')>"


class TestUserFactories:
    """Тесты фабрик"""

    def test_user_factory_build_creates_instance(self) -> None:
        """Тест что фабрика создает инстанс модели"""
        user = UserFactory.build()

        assert isinstance(user, User)
        assert user.name is not None
        assert user.email is not None
        assert "@" in user.email  # Faker email должен содержать @

    def test_user_factory_creates_unique_data(self) -> None:
        """Тест что фабрика создает уникальные данные"""
        user1 = UserFactory.build()
        user2 = UserFactory.build()

        assert user1.name != user2.name
        assert user1.email != user2.email

    def test_user_factory_with_custom_attributes(self) -> None:
        """Тест фабрики с кастомными атрибутами"""
        custom_user = UserFactory.build(
            name="Custom Name",
            email="custom@example.com"
        )

        assert custom_user.name == "Custom Name"
        assert custom_user.email == "custom@example.com"

    def test_user_factory_batch_build(self) -> None:
        """Тест массового создания объектов через фабрику"""
        users = UserFactory.build_batch(5)

        assert len(users) == 5
        assert all(isinstance(user, User) for user in users)

        # Проверяем что все email уникальны
        emails = [user.email for user in users]
        assert len(emails) == len(set(emails))

import pytest

from lib.tests.factories import UserFactory


@pytest.mark.asyncio
async def test_create_user(db_connection):
    """Тест создания пользователя"""
    # Создаем пользователя через фабрику
    user = await UserFactory.create_in_db(db_connection)
    print(user)

    # Проверяем что пользователь создан
    assert user['id'] is not None
    assert user['email'] is not None
    assert user['username'] is not None

    # Проверяем что пользователь в БД
    result = await db_connection.fetchrow(
        "SELECT * FROM users WHERE id = $1",
        user['id']
    )
    assert result is not None
    assert result['email'] == user['email']


@pytest.mark.asyncio
async def test_create_user_2(db_connection):
    # Проверяем что пользователь в БД
    result = await db_connection.fetch(
        "SELECT * FROM users;",
    )
    print(result)
    print(346543634565356546456)

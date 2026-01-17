from lib.tests.factories import UserFactory
from lib.utils.models import User
import pytest_asyncio


@pytest_asyncio.fixture
def user_factory(db_connection):
    async def factory(**kwargs) -> User:
        return await UserFactory.create_in_db(conn=db_connection, **kwargs)

    return factory

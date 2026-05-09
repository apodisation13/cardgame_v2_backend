import pytest
import pytest_asyncio

from lib.tests.factories import UserFactory
from lib.tests.factories.factories import EventMessageFactory, UserResourceFactory, ProductFactory, PurchaseFactory
from lib.utils.models import User, UserResource, Product, Purchase
from lib.utils.schemas.events import EventMessage


@pytest_asyncio.fixture
def user_factory(db_connection):
    async def factory(**kwargs) -> User:
        return await UserFactory.create_in_db(conn=db_connection, **kwargs)

    return factory


@pytest_asyncio.fixture
def user_resource_factory(db_connection):
    async def factory(**kwargs) -> UserResource:
        return await UserResourceFactory.create_in_db(conn=db_connection, **kwargs)

    return factory


@pytest.fixture
def event_message_factory():
    def factory(**kwargs) -> EventMessage:
        return EventMessageFactory.build(**kwargs)

    return factory



@pytest_asyncio.fixture
def product_factory(db_connection):
    async def factory(**kwargs) -> Product:
        return await ProductFactory.create_in_db(conn=db_connection, **kwargs)

    return factory


@pytest_asyncio.fixture
def purchase_factory(db_connection):
    async def factory(**kwargs) -> Purchase:
        return await PurchaseFactory.create_in_db(conn=db_connection, **kwargs)

    return factory

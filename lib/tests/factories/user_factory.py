import hashlib

import factory
from lib.tests.factories.base import BaseModelFactory
from lib.utils.models import User


class UserFactory(BaseModelFactory):
    """Фабрика для создания пользователей"""

    class Meta:
        model = User

    email = factory.Faker('email')
    username = factory.Faker('user_name')
    password = factory.LazyAttribute(
        lambda obj: hashlib.sha256(f"password_{obj.username}".encode()).hexdigest()
    )
    is_active = True

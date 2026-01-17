import hashlib

import factory
from lib.tests.factories.base import BaseModelFactory
from lib.utils.models import User
from lib.utils.schemas.users import UserRole


class UserFactory(BaseModelFactory):
    class Meta:
        model = User

    email = factory.Faker("email")
    username = factory.Faker("user_name")
    password = factory.LazyAttribute(lambda obj: hashlib.sha256(f"password_{obj.username}".encode()).hexdigest())
    is_active = True
    role = UserRole.PLAYER
    email_verified = True

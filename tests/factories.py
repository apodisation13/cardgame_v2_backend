from app.models import User
import factory
from factory.alchemy import SQLAlchemyModelFactory


class UserFactory(SQLAlchemyModelFactory):
    class Meta:
        model = User

    id = factory.Sequence(lambda n: n + 1)
    name = factory.Faker('name')
    email = factory.Faker('email')

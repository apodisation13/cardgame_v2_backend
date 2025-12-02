import factory
from faker import Faker


fake = Faker()


class AsyncFactory(factory.Factory):
    """Базовая асинхронная фабрика"""

    @classmethod
    async def create_async(cls, **kwargs) -> object:
        """Асинхронное создание объекта"""
        return cls.build(**kwargs)

    @classmethod
    async def create_batch_async(cls, size, **kwargs) -> list:
        """Асинхронное создание нескольких объектов"""
        return [await cls.create_async(**kwargs) for _ in range(size)]


class BaseModelFactory(AsyncFactory):
    """Базовая фабрика для всех моделей"""

    class Meta:
        abstract = True

    id = factory.Sequence(lambda n: n + 1)
    # created_at = factory.Faker('date_time_this_year')
    # updated_at = factory.Faker('date_time_this_month')

    @classmethod
    async def create_in_db(cls, conn, **kwargs) -> dict:
        """Создание объекта в БД"""
        obj = cls.build(**kwargs)

        # Формируем SQL запрос
        table_name = cls._meta.model.__tablename__
        columns = []
        values = []
        placeholders = []

        for key, value in obj.__dict__.items():
            if not key.startswith("_"):
                columns.append(key)
                values.append(value)
                placeholders.append(f"${len(placeholders) + 1}")

        query = f"""
            INSERT INTO {table_name} ({", ".join(columns)})
            VALUES ({", ".join(placeholders)})
            RETURNING *
        """  # noqa: S608

        result = await conn.fetchrow(query, *values)
        return dict(result)

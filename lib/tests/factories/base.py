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


class TimeStampMixinFactory(AsyncFactory):
    class Meta:
        abstract = True


class BaseModelFactory(AsyncFactory):
    class Meta:
        abstract = True

    @classmethod
    def _get_model_columns(cls) -> list:
        """Получаем список колонок модели"""
        model_class = cls._meta.model
        return [column.name for column in model_class.__table__.columns]

    @classmethod
    async def create_in_db(cls, conn, **kwargs) -> object:
        # Получаем список колонок модели
        columns = cls._get_model_columns()

        # Собираем данные для вставки
        data = {}

        # 1. Базовые значения из фабрики
        base_obj = cls.build()
        for column in columns:
            if hasattr(base_obj, column):
                value = getattr(base_obj, column)
                if value is not None:
                    data[column] = value

        # 2. Переопределяем переданными значениями
        data.update({key: value for key, value in kwargs.items() if key in columns})

        # Формируем запрос
        table_name = cls._meta.model.__tablename__
        insert_columns = list(data.keys())
        values = list(data.values())
        placeholders = [f"${i + 1}" for i in range(len(values))]

        query = f"""
                INSERT INTO {table_name} ({", ".join(insert_columns)})
                VALUES ({", ".join(placeholders)})
                RETURNING *
            """  # noqa: S608

        result = await conn.fetchrow(query, *values)
        result_dict = dict(result)

        model_class = cls._meta.model
        return model_class(**result_dict)

# Инициализация Alembic  - выполняется 1 раз!
alembic init migrations

# Создание миграции
alembic revision --autogenerate -m "Create users table"

# Применение миграций
alembic upgrade head

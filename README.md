# Инициализация Alembic  - выполняется 1 раз!
alembic init migrations

# Создание миграции
alembic revision --autogenerate -m "Create users table"

# Применение миграций
alembic upgrade head

# Запуск API
uvicorn services.api.app.main:app --reload --host 0.0.0.0 --port 8001

# Запуск всех тестов
pytest -s -v >output.log
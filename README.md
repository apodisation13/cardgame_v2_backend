# Создание миграции
alembic revision --autogenerate -m "Create users table"

# Применение миграций
alembic upgrade head

# Запуск API
uvicorn services.api.app.main:app --reload --host 0.0.0.0 --port 8001

# Запуск Cron
python services/cron/app/main.py

# Запуск всех тестов
pytest -s -v >output.log


# Локально в любой своей ветке:
git fetch origin  
git rebase origin/main

# Локально если в ветке main
git pull

FROM python:3.11-slim

WORKDIR /app

# 1. Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Копируем requirements
COPY lib/requirements.txt /app/lib/requirements.txt
COPY services/rest/requirements.txt /app/services/rest/requirements.txt

# Устанавливаем зависимости
WORKDIR /app/services/rest
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код с сохранением структуры
COPY lib/__init__.py /app/lib/__init__.py
COPY lib/utils /app/lib/utils

# Создаем структуру services/api
COPY services/rest/app /app/services/rest/app
COPY services/rest/__init__.py /app/services/rest/__init__.py
COPY services/__init__.py /app/services/__init__.py

# Настраиваем окружение
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

WORKDIR /app

#CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]

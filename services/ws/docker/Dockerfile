FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY lib/requirements.txt /app/lib/requirements.txt
COPY services/ws/requirements.txt /app/services/ws/requirements.txt

WORKDIR /app/services/ws
RUN pip install --no-cache-dir -r requirements.txt

COPY lib/__init__.py /app/lib/__init__.py
COPY lib/utils /app/lib/utils

COPY services/ws/app /app/services/ws/app
COPY services/ws/__init__.py /app/services/ws/__init__.py
COPY services/__init__.py /app/services/__init__.py

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

WORKDIR /app

CMD ["python", "-m", "uvicorn", "services.ws.app.main:app", "--host", "0.0.0.0", "--port", "8002"]

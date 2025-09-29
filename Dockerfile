FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Системные зависимости (при необходимости можно расширить)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates tzdata && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .
COPY .env ./.env

# Установите таймзону контейнера при желании (или задайте SERVER_TZ через .env)
# ENV TZ=Europe/Moscow

CMD ["python", "main.py"]

FROM python:3.12-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update \
    && apt-get install -y gcc libpq-dev curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Установка Poetry
RUN pip install "poetry==1.8.2"

# Копируем только файлы для управления зависимостями
COPY pyproject.toml poetry.lock /app/

# Устанавливаем зависимости
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --no-root --only main

# Копируем весь проект
COPY . /app

# Запуск Telegram-бота
CMD ["python", "manage.py", "run_telegram_bot"]

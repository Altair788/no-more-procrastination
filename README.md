# Трекер привычек

## Описание

**Трекер привычек** представляет собой backend-часть веб-приложения, которое помогает пользователям формировать полезные привычки, отслеживать их выполнение и получать напоминания через Telegram. Приложение поддерживает авторизацию через email, интеграцию с Celery и Redis для фоновых задач, а также предоставляет API для взаимодействия с клиентской частью (в формате camelCase для удобной работы с фронтендом).

---

## Основной функционал

### Пользовательский функционал:
- Регистрация и авторизация через email.
- Смена пароля, сброс пароля и подтверждение email.
- CRUD-операции для управления привычками:
  - Создание, редактирование, удаление привычек.
  - Просмотр списка своих привычек с пагинацией (по 5 на страницу).
- Просмотр публичных привычек других пользователей.

### Напоминания:
- Настройка времени и периодичности выполнения привычек.
- Напоминания через Telegram о выполнении привычек.

### Публичные привычки:
- Возможность публиковать свои полезные привычки для других пользователей.
- Просмотр списка публичных привычек.

---

## Установка

### 1. Установка зависимостей
Убедитесь, что у вас установлен Python версии **3.12**. Для установки зависимостей используйте [Poetry](https://python-poetry.org/):

```bash
poetry install
```

### 2. Настройка переменных окружения
Скопируйте файл `.env.example` в `.env`:

```bash
cp .env.example .env
```

Заполните файл `.env` следующими значениями:

```plaintext
SUPERUSER_EMAIL=admin@example.com
SUPERUSER_PASSWORD=adminpassword123
NORMAL_USER_EMAIL=user@example.com
NORMAL_USER_PASSWORD=userpassword123
TELEGRAM_BOT_TOKEN=ваш_токен_бота
REDIS_URL=redis://127.0.0.1:6379/0
```

### 3. Запуск сервера разработки
```bash
python manage.py runserver
```

---

## Кастомные команды

### Команда `csu.py` (Create Super User)
Для автоматического создания суперпользователя и обычного пользователя выполните:

```bash
python manage.py csu
```

Эта команда создаёт двух пользователей на основе значений из `.env`:
1. Суперпользователь: `SUPERUSER_EMAIL` и `SUPERUSER_PASSWORD`.
2. Обычный пользователь: `NORMAL_USER_EMAIL` и `NORMAL_USER_PASSWORD`.

Если пользователи уже существуют, команда уведомит об этом.

---

## Инструкции по запуску

### Celery + Redis (планировщик задач)

Для изоляции задач используйте очередь `habit_tracker_queue`. Добавьте в `settings.py`:

```python
CELERY_TASK_DEFAULT_QUEUE = 'habit_tracker_queue'
```

#### Запуск Celery Worker

1. **Пул потоков** (рекомендуется для macOS):
   ```bash
   celery -A config worker -l INFO --pool=threads -Q habit_tracker_queue
   ```

2. **Режим solo** (для разработки):
   ```bash
   celery -A config worker -l INFO --pool=solo -Q habit_tracker_queue
   ```

#### Запуск Celery Beat (планировщик):
```bash
celery -A config beat -l INFO
```

---

### Запуск Telegram-бота

Для запуска Telegram-бота выполните:

```bash
python manage.py run_telegram_bot
```

Убедитесь, что токен бота указан в `.env` как `TELEGRAM_BOT_TOKEN`.

---

## Новые возможности

1. **Авторизация через email**:
   - Регистрация с подтверждением email.
   - Авторизация через email и пароль.
   - Сброс пароля с отправкой ссылки на email.

2. **API в формате camelCase**:
   Все эндпоинты возвращают данные в формате camelCase для удобства работы с фронтендом.

---

## Настройка удаленного сервера и деплой

1. Обновите систему:
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. Установите Docker, следуя [официальной инструкции](https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository).

3. Настройте файрвол:
   ```bash
   sudo ufw allow 22/tcp
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw enable
   sudo ufw status
   ```

4. Настройте GitHub Secrets в настройках репозитория (Settings -> Secrets and variables -> Actions):
   - Данные базы данных: `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT`
   - Настройки Django: `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`
   - Доступ к Docker Hub: `DOCKER_HUB_USERNAME`, `DOCKER_HUB_ACCESS_TOKEN`
   - SSH-доступ: `SSH_USER`, `SSH_KEY`, `SERVER_IP`
   - Настройки Celery: `CELERY_BROKER_URL`, `CELERY_BACKEND`
   - Настройки email: 
     - `EMAIL_HOST`
     - `EMAIL_PORT`
     - `EMAIL_HOST_USER`
     - `EMAIL_HOST_PASSWORD`
     - `EMAIL_USE_SSL`
     - `EMAIL_USE_TLS`
   - Настройки Telegram-бота: 
     - `TELEGRAM_BOT_TOKEN`
   - Настройки для создания пользователей: 
     - `SUPERUSER_EMAIL`
     - `SUPERUSER_PASSWORD`
     - `NORMAL_USER_EMAIL`
     - `NORMAL_USER_PASSWORD`

5. Запуск CI/CD:
   - Push изменений в репозиторий автоматически запустит GitHub Actions workflow.
   - Workflow выполнит линтинг, тесты, сборку Docker-образа и деплой на сервер.

6. Проверка деплоя:
   После завершения workflow приложение будет доступно по IP-адресу сервера на порту 80.


## Доступ к развернутому приложению

Вы можете получить доступ к административной панели приложения по следующему адресу:

[http://130.193.54.21/admin/login/?next=/admin/](http://130.193.54.21/admin/login/?next=/admin/)

**Важно:** Этот URL предоставляет доступ к административной панели приложения. Убедитесь, что вы используете соответствующие учетные данные для входа.

---

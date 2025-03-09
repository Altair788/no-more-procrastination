from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# настройки Django для Celery
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Создаём экземпляр приложения Celery
app = Celery("config")

# Загружаем настройки из файла settings.py с префиксом CELERY_
app.config_from_object("django.conf:settings", namespace="CELERY")

# Автоматически обнаруживаем задачи в приложениях
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")

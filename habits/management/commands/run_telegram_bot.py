from django.core.management.base import BaseCommand
from habits.tasks import run_telegram_bot


class Command(BaseCommand):
    help = "Запуск Telegram-бота"

    def handle(self, *args, **kwargs):
        self.stdout.write("Запуск Telegram-бота...")
        run_telegram_bot()

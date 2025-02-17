import os

from django.core.management import BaseCommand

from users.models import User


class Command(BaseCommand):
    help = "Создает суперпользователя и обычного пользователя с заданными параметрами"

    def handle(self, *args, **options):
        # Получаем данные из переменных окружения
        superuser_username = os.getenv("SUPERUSER_USERNAME")
        superuser_password = os.getenv("SUPERUSER_PASSWORD")
        normal_user_username = os.getenv("NORMAL_USER_USERNAME")
        normal_user_password = os.getenv("NORMAL_USER_PASSWORD")

        # Проверяем, существует ли суперпользователь
        superuser, created = User.objects.get_or_create(
            username=superuser_username,
            defaults={
                "is_staff": True,
                "is_active": True,
                "is_superuser": True,
            },
        )

        if created:
            superuser.set_password(superuser_password)
            # self.stdout.write(self.style.SUCCESS(f"Пароль суперпользователя установлен: {superuser_password}"))
            superuser.save()
            self.stdout.write(
                self.style.SUCCESS(f"Суперпользователь создан: {superuser_username}")
            )
        else:
            self.stdout.write(
                self.style.WARNING(f"Пользователь {superuser_username} уже существует.")
            )

        # Проверяем, существует ли обычный пользователь
        normal_user, created = User.objects.get_or_create(
            username=normal_user_username,
            defaults={
                "is_staff": False,
                "is_active": True,
                "is_superuser": False,
            },
        )

        if created:
            normal_user.set_password(normal_user_password)
            # self.stdout.write(self.style.SUCCESS(f"Пароль пользователя установлен: {normal_user_password}"))
            normal_user.save()
            self.stdout.write(
                self.style.SUCCESS(
                    f"Обычный пользователь создан: {normal_user_username}"
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f"Пользователь {normal_user_username} уже существует."
                )
            )

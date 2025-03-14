import os

from django.core.management import BaseCommand

from users.models import User


class Command(BaseCommand):
    help = "Создает суперпользователя и обычного пользователя с заданными параметрами"

    def handle(self, *args, **options):
        # Получаем данные из переменных окружения
        superuser_email = os.getenv("SUPERUSER_EMAIL")
        superuser_password = os.getenv("SUPERUSER_PASSWORD")
        normal_user_email = os.getenv("NORMAL_USER_EMAIL")
        normal_user_password = os.getenv("NORMAL_USER_PASSWORD")

        # Проверяем, существует ли суперпользователь
        superuser, created = User.objects.get_or_create(
            email=superuser_email,
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
                self.style.SUCCESS(
                    f"Суперпользователь с почтой {superuser_email} создан."
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f"Пользователь с почтой {superuser_email} уже существует."
                )
            )

        # Проверяем, существует ли обычный пользователь
        normal_user, created = User.objects.get_or_create(
            email=normal_user_email,
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
                    f"Обычный пользователь создан: email - {normal_user_email}"
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f"Пользователь с почтой {normal_user_email} уже существует."
                )
            )

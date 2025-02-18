import secrets

from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

NULLABLE = {"blank": True, "null": True}


class User(AbstractUser):
    username = None
    token = models.CharField(max_length=32, blank=True, null=True)
    is_active = models.BooleanField(default=False)

    email = models.EmailField(
        unique=True, verbose_name="почта", help_text="укажите почту"
    )

    phone = PhoneNumberField(
        **NULLABLE,
        unique=True,
        verbose_name="номер телефона",
        help_text="укажите телефон"
    )
    country = models.CharField(max_length=100, verbose_name="страна", blank=True)
    tg_nick = models.CharField(
        max_length=50,
        verbose_name="телеграм - ник",
        blank=True,
        help_text="укажите ник телеграм"
    )
    tg_id = models.PositiveIntegerField(
        verbose_name="телеграм - ID",
        **NULLABLE,
        help_text="укажите телеграм - ID"
    )
    avatar = models.ImageField(
        upload_to="users/avatars/",
        verbose_name="аватар",
        help_text="Загрузите аватарку",
        **NULLABLE
    )

    def generate_token(self):
        self.token = secrets.token_hex(16)
        self.save()


    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []



    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

from django.db import models

from users.models import User
from django.core.exceptions import ValidationError

NULLABLE = {"null": True, "blank": True}


class Habit(models.Model):
    """
    Модель, представляющая привычку.

    Атрибуты:
        owner (ForeignKey): Пользователь, создавший привычку.
        location (str): Место выполнения привычки.
        time (TimeField): Время выполнения привычки.
        action (str): Действие, которое представляет собой привычка.
        is_pleasant (bool): Признак приятной привычки.
        linked_action (ForeignKey): Связанная приятная привычка.
        frequency (int): Периодичность выполнения привычки в днях.
        reward (str): Вознаграждение за выполнение привычки.
        duration (int): Время на выполнение привычки в секундах.
        is_public (bool): Признак публичности привычки.
    """

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Создатель",
        help_text="Пользователь, создавший эту привычку",
    )
    location = models.CharField(
        max_length=255,
        verbose_name="место",
        help_text="Укажите место, в котором необходимо выполнять привычку",
    )
    time = models.TimeField(
        verbose_name="Время", help_text="Укажите время начала выполнения привычки"
    )
    action = models.CharField(
        max_length=255,
        verbose_name="действие",
        help_text="Укажите действие, которое представляет собой привычка",
    )
    is_pleasant = models.BooleanField(
        default=False,
        verbose_name="Признак приятной привычки",
        help_text="Отметьте, если это приятная привычка",
    )
    linked_action = models.ForeignKey(
        "self",
        #  Связь возможна только с приятными привычками
        limit_choices_to={"is_pleasant": True},
        related_name="linked_habits",
        verbose_name="Связанная привычка",
        help_text="Укажите связанную приятную привычку",
        on_delete=models.SET_NULL,
        **NULLABLE,
    )
    frequency = models.PositiveIntegerField(
        default=1,
        verbose_name="Периодичность",
        help_text="Укажите периодичность выполнения в днях (от 1 до 7)",
    )
    reward = models.CharField(
        max_length=255,
        verbose_name="Вознаграждение",
        help_text="Укажите вознаграждение за выполнение привычки",
        blank=True,
    )
    duration = models.PositiveIntegerField(
        verbose_name="Время на выполнение (в секундах)",
        help_text="Укажите предполагаемое время выполнения в секундах",
    )
    is_public = models.BooleanField(
        default=False,
        verbose_name="Публичная",
        help_text="Отметьте, если хотите сделать эту привычку публичной",
    )

    def clean(self):
        """
        Проверка бизнес-логики на уровне модели (иначе в админке можно обойти валидацию).
        """
        # Проверка: не должно быть заполнено одновременно и поле вознаграждения, и поле связанной привычки.
        if self.reward and self.linked_action:
            raise ValidationError(
                "Нельзя указать одновременно вознаграждение и "
                "связанную приятную привычку."
            )

        # Проверка: время выполнения должно быть не больше 120 секунд.
        if self.duration > 120:
            raise ValidationError(
                "Время выполнения привычки не должно превышать 120 секунд."
            )

        # Проверка: в связанные привычки могут попадать только привычки с признаком приятной привычки.
        if self.linked_action and not self.linked_action.is_pleasant:
            raise ValidationError(
                "В связанные привычки могут попадать только привычки с признаком приятной привычки."
            )

        # Проверка: у приятной привычки не может быть вознаграждения или связанной привычки.
        if self.is_pleasant and (self.reward or self.linked_action is not None):
            raise ValidationError(
                "У приятной привычки не может быть вознаграждения или связанной привычки."
            )

        # Проверка: нельзя выполнять привычку реже, чем 1 раз в 7 дней.
        if self.frequency < 1 or self.frequency > 7:
            raise ValidationError(
                "Периодичность выполнения должна быть от 1 до 7 дней (не реже одного раза в неделю)."
            )

    def __repr__(self) -> str:
        """Возвращает строковое представление объекта Привычка.

        Returns:
            str: Строковое представление объекта с его атрибутами.
                  Например: Habit(owner=..., location=..., ...)
        """
        return f"""Habit(
owner={self.owner},
location={self.location},
time={self.time},
action={self.action},
is_pleasant={self.is_pleasant},
linked_action={self.linked_action},
frequency={self.frequency},
reward={self.reward},
duration={self.duration},
is_public={self.is_public})"""

    def __str__(self) -> str:
        """Возвращает строковое представление привычки.

        Returns:
            str: Название действия привычки.
                  Например: "Бег по утрам".
        """
        return self.action

    class Meta:
        verbose_name = "Привычка"
        verbose_name_plural = "Привычки"

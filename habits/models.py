from django.db import models

from users.models import User
NULLABLE = {'null': True,
            'blank': True}


class Habit(models.Model):
    """
    Модель, представляющая привычку

    Attributes:
        owner (models. ForeignKey): создатель привычки
        location (str): место, в котором необходимо выполнять привычку.
        time (models. Timefield): время, когда необходимо выполнять привычку.
        action (str): действие, которое представляет собой привычка.
        is_pleasant (bool): признак приятной привычки — привычка,
        которую можно привязать к выполнению полезной привычки.
        linked_action (str): связанная привычка — привычка,
        которая связана с другой привычкой, важно указывать для полезных привычек,
        но не для приятных.
        frequency (int): периодичность (по умолчанию ежедневная)
         — периодичность выполнения привычки для напоминания в днях.
        reward (str): вознаграждение — чем пользователь должен себя вознаградить после выполнения.
        duration (DurationField): время на выполнение — время, которое предположительно потратит
         пользователь на выполнение привычки.
        is_public (bool): признак публичности — привычки можно публиковать в общий доступ,
         чтобы другие пользователи могли брать в пример чужие привычки.
    """
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name="Создатель",
        help_text="Пользователь, создавший эту привычку"
    )
    location = models.CharField(
        max_length=255,
        verbose_name="место",
        help_text='Укажите место, в котором необходимо выполнять привычку'
        )
    time = models.TimeField(
        verbose_name="Время",
        help_text="Укажите время начала выполнения привычки"
    )
    action = models.CharField(
        max_length=255,
        verbose_name="действие",
        help_text="Укажите действие, которое представляет собой привычка"
    )
    is_pleasant = models.BooleanField(
        default=False,
        verbose_name="Признак приятной привычки",
        help_text="Отметьте, если это приятная привычка"
    )
    linked_action = models.ForeignKey(
        'self',
        #  Связь возможна только с приятными привычками
        limit_choices_to={"is_pleasant": True},
        related_name="linked_habits",
        verbose_name="Связанная привычка",
        help_text="Укажите связанную приятную привычку",
        **NULLABLE
    )
    frequency = models.PositiveIntegerField(
        default=1,
        verbose_name="Периодичность",
        help_text="Укажите периодичность выполнения в днях (от 1 до 7)"
        )
    reward = models.CharField(
        max_length=255,
        verbose_name="Вознаграждение",
        help_text="Укажите вознаграждение за выполнение привычки",
        blank=True)
    duration = models.DurationField(
        verbose_name="Время на выполнение",
        help_text="Укажите предполагаемое время выполнения"
    )
    is_public = models.BooleanField(
        default=False,
        verbose_name="Публичная",
        help_text="Отметьте, если хотите сделать эту привычку публичной"
    )

    def __repr__(self) -> str:
        """Возвращает строковое представление объекта Привычка.

        Returns:
            str: Строковое представление объекта с его атрибутами.
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
            str: Привычка.
        """
        return self.action

    class Meta:
        verbose_name = "Привычка"
        verbose_name_plural = "Привычки"



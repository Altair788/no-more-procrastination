# Generated by Django 4.2.2 on 2025-02-17 12:55

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Habit",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "location",
                    models.CharField(
                        help_text="Укажите место, в котором необходимо выполнять привычку",
                        max_length=255,
                        verbose_name="место",
                    ),
                ),
                (
                    "time",
                    models.TimeField(
                        help_text="Укажите время начала выполнения привычки",
                        verbose_name="Время",
                    ),
                ),
                (
                    "action",
                    models.CharField(
                        help_text="Укажите действие, которое представляет собой привычка",
                        max_length=255,
                        verbose_name="действие",
                    ),
                ),
                (
                    "is_pleasant",
                    models.BooleanField(
                        default=False,
                        help_text="Отметьте, если это приятная привычка",
                        verbose_name="Признак приятной привычки",
                    ),
                ),
                (
                    "frequency",
                    models.PositiveIntegerField(
                        default=1,
                        help_text="Укажите периодичность выполнения в днях (от 1 до 7)",
                        verbose_name="Периодичность",
                    ),
                ),
                (
                    "reward",
                    models.CharField(
                        blank=True,
                        help_text="Укажите вознаграждение за выполнение привычки",
                        max_length=255,
                        verbose_name="Вознаграждение",
                    ),
                ),
                (
                    "duration",
                    models.DurationField(
                        help_text="Укажите предполагаемое время выполнения",
                        verbose_name="Время на выполнение",
                    ),
                ),
                (
                    "is_public",
                    models.BooleanField(
                        default=False,
                        help_text="Отметьте, если хотите сделать эту привычку публичной",
                        verbose_name="Публичная",
                    ),
                ),
                (
                    "linked_action",
                    models.ForeignKey(
                        blank=True,
                        help_text="Укажите связанную приятную привычку",
                        limit_choices_to={"is_pleasant": True},
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="linked_habits",
                        to="habits.habit",
                        verbose_name="Связанная привычка",
                    ),
                ),
                (
                    "owner",
                    models.ForeignKey(
                        help_text="Пользователь, создавший эту привычку",
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Создатель",
                    ),
                ),
            ],
            options={
                "verbose_name": "Привычка",
                "verbose_name_plural": "Привычки",
            },
        ),
    ]

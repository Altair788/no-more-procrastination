from django.contrib import admin

from habits.models import Habit


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = (
    "id",
    "owner",
    "location",
    "time",
    "action",
    "is_pleasant",
    "linked_action",
    "frequency",
    "reward",
    "duration",
    "is_public"
    )
    ordering = ("id",)

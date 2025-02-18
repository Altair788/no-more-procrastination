from rest_framework import serializers

from habits.models import Habit
from habits.validators import HabitValidator


class LinkedHabitSerializer(serializers.ModelSerializer):
    """
    Сериализатор для связанной привычки.
    Для более детального отображения данных о связанной привычке в запросах.
    """
    class Meta:
        model = Habit
        fields = ("id", "action", "is_pleasant")


class HabitSerializer(serializers.ModelSerializer):
    """
        Сериализатор для модели Habit.
    """
    owner = serializers.PrimaryKeyRelatedField(read_only=True)
    is_pleasant = serializers.BooleanField(allow_null=True, required=False)
    is_public = serializers.BooleanField(allow_null=True, required=False)
    reward = serializers.CharField(allow_null=True, required=False)

    linked_action = LinkedHabitSerializer(
        allow_null=True,
        required=False,
    )

    class Meta:
        model = Habit
        fields = (
            "id",
            "owner",
            "location",
            "time",
            "action",
            "is_pleasant",
            "linked_action",
            "duration",
            "frequency",
            "reward",
            "is_public",
        )

    def validate(self, data):
        """
        Применяем кастомный валидатор для проверки бизнес - логики.
        """
        validator = HabitValidator()
        validator(data)
        return data


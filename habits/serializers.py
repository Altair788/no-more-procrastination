from rest_framework import serializers

from habits.models import Habit
from habits.validators import HabitValidator


class HabitSerializer(serializers.ModelSerializer):

    class Meta:
        model = Habit
        fields = "__all__"

    def validate(self, data):
        """
        Применяем кастомный валидатор для проверки бизнес - логики.
        """
        validator = HabitValidator()
        validator(data)
        return data


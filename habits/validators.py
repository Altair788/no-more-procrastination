from rest_framework.exceptions import ValidationError


class HabitValidator:
    """
    Валидатор для проверки бизнес-логики привычек.
    """

    def __call__(self, data):
        """
        Вызывается в сериализаторе при проверке данных.
        Arguments:
            data (dict): словарь с данными привычки
        """
        reward = data.get("reward")
        linked_action = data.get("linked_action")
        is_pleasant = data.get("is_pleasant")
        frequency = data.get("frequency")
        duration = data.get("duration")

        # Проверка: не должно быть заполнено одновременно и поле вознаграждения, и поле связанной привычки.
        if reward and linked_action:
            raise ValidationError(
                "Нельзя указать одновременно вознаграждение и "
                "связанную приятную привычку."
            )

        # Проверка: время выполнения должно быть не больше 120 секунд.
        if duration > 120:
            raise ValidationError(
                "Время выполнения привычки не должно превышать 120 секунд."
            )

        # Проверка: в связанные привычки могут попадать только привычки с признаком приятной привычки.
        if linked_action and not linked_action.is_pleasant:
            raise ValidationError(
                "В связанные привычки могут попадать только привычки с признаком приятной привычки."
            )

        # Проверка: у приятной привычки не может быть вознаграждения или связанной привычки.
        if is_pleasant and (reward or linked_action is not None):
            raise ValidationError(
                "У приятной привычки не может быть вознаграждения или связанной привычки."
            )

        # Проверка: нельзя выполнять привычку реже, чем 1 раз в 7 дней.
        if frequency < 1 or frequency > 7:
            raise ValidationError(
                "Периодичность выполнения должна быть от 1 до 7 дней (не реже одного раза в неделю)."
            )

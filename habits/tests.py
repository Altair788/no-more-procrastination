from django.core.exceptions import ValidationError
from django.test import TestCase
from habits.models import Habit
from users.models import User


class HabitModelTest(TestCase):
    def setUp(self):
        """
        Создаём пользователя и базовые данные для тестов.
        """
        self.user = User.objects.create_user(email="test@example.com", password="password123")
        self.linked_habit = Habit.objects.create(
            owner=self.user,
            location="Парк",
            time="07:00:00",
            action="Прогулка",
            is_pleasant=True,
            duration=60,
            frequency=1,
            is_public=False,
        )

    def test_create_habit(self):
        """
        Тест создания привычки.
        """
        habit = Habit.objects.create(
            owner=self.user,
            location="Дом",
            time="08:00:00",
            action="Йога",
            duration=30,
            frequency=2,
            is_public=False,
        )
        self.assertEqual(habit.owner, self.user)
        self.assertEqual(habit.action, "Йога")
        self.assertEqual(habit.duration, 30)

    def test_clean_with_reward_and_linked_action(self):
        """
        Тест: нельзя указать одновременно вознаграждение и связанную приятную привычку.
        """
        habit = Habit(
            owner=self.user,
            location="Дом",
            time="08:00:00",
            action="Чтение",
            duration=30,
            frequency=2,
            reward="Шоколадка",
            linked_action=self.linked_habit,  # Связанная приятная привычка
        )
        with self.assertRaises(ValidationError) as e:
            habit.clean()
        self.assertIn("Нельзя указать одновременно вознаграждение и связанную приятную привычку.", str(e.exception))

    def test_clean_duration_exceeds_limit(self):
        """
        Тест: время выполнения не должно превышать 120 секунд.
        """
        habit = Habit(
            owner=self.user,
            location="Дом",
            time="08:00:00",
            action="Медитация",
            duration=150,  # Превышает лимит
            frequency=2,
        )
        with self.assertRaises(ValidationError) as e:
            habit.clean()
        self.assertIn("Время выполнения привычки не должно превышать 120 секунд.", str(e.exception))

    def test_clean_linked_action_not_pleasant(self):
        """
        Тест: связанная привычка должна быть приятной.
        """
        non_pleasant_habit = Habit.objects.create(
            owner=self.user,
            location="Парк",
            time="07:30:00",
            action="Бег",
            is_pleasant=False,  # Не приятная привычка
            duration=60,
            frequency=1,
        )

        habit = Habit(
            owner=self.user,
            location="Дом",
            time="08:00:00",
            action="Чтение",
            duration=30,
            frequency=2,
            linked_action=non_pleasant_habit,  # Связь с не приятной привычкой
        )

        with self.assertRaises(ValidationError) as e:
            habit.clean()

        self.assertIn("В связанные привычки могут попадать только привычки с признаком приятной привычки.",
                      str(e.exception))

    def test_clean_pleasant_habit_with_reward_or_linked_action(self):
        """
        Тест: у приятной привычки не может быть вознаграждения или связанной привычки.
        """
        habit_with_reward = Habit(
            owner=self.user,
            location="Парк",
            time="07:00:00",
            action="Прогулка с собакой",
            is_pleasant=True,  # Приятная привычка
            reward="Шоколадка",  # Указано вознаграждение
            duration=60,
            frequency=1,
        )

        with self.assertRaises(ValidationError) as e:
            habit_with_reward.clean()

        self.assertIn("У приятной привычки не может быть вознаграждения или связанной привычки.", str(e.exception))

    def test_clean_frequency_out_of_bounds(self):
        """
        Тест: периодичность выполнения должна быть от 1 до 7 дней.
        """
        habit = Habit(
            owner=self.user,
            location="Дом",
            time="08:00:00",
            action="Чтение книг",
            duration=30,
            frequency=10,  # Выходит за пределы допустимого диапазона
        )

        with self.assertRaises(ValidationError) as e:
            habit.clean()

        self.assertIn("Периодичность выполнения должна быть от 1 до 7 дней", str(e.exception))

    def test_str_representation(self):
        """
        Тест строкового представления объекта.
        """
        habit = Habit.objects.create(
            owner=self.user,
            location="Офис",
            time="09:00:00",
            action="Работа над проектом",
            duration=90,
            frequency=3,
        )

        self.assertEqual(str(habit), "Работа над проектом")

    def test_repr_representation(self):
        """
        Тест строкового представления __repr__.
        """
        habit = Habit.objects.create(
            owner=self.user,
            location="Офис",
            time="09:00:00",
            action="Работа над проектом",
            duration=90,
            frequency=3,
        )

        expected_repr = (
            f"Habit(\n"
f"owner={habit.owner},\n"
f"location={habit.location},\n"
f"time={habit.time},\n"
f"action={habit.action},\n"
f"is_pleasant={habit.is_pleasant},\n"
f"linked_action={habit.linked_action},\n"
f"frequency={habit.frequency},\n"
f"reward={habit.reward},\n"
f"duration={habit.duration},\n"
f"is_public={habit.is_public})"
        )

        # Выводим фактическое значение repr(habit) и ожидаемое значение expected_repr
        print("Фактическое значение repr(habit):")
        print(repr(habit))
        print("\nОжидаемое значение expected_repr:")
        print(expected_repr)

        self.assertEqual(repr(habit), expected_repr)


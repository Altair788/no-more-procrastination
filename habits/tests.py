import json
#  импорты для habits/tasks
from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from habits.models import Habit
from habits.tasks import run_telegram_bot
from users.models import User


class HabitModelTest(TestCase):
    def setUp(self):
        """
        Создаём пользователя и базовые данные для тестов.
        """
        self.user = User.objects.create_user(
            email="test@example.com", password="password123"
        )
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
        self.assertIn(
            "Нельзя указать одновременно вознаграждение и связанную приятную привычку.",
            str(e.exception),
        )

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
        self.assertIn(
            "Время выполнения привычки не должно превышать 120 секунд.",
            str(e.exception),
        )

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

        self.assertIn(
            "В связанные привычки могут попадать только привычки с признаком приятной привычки.",
            str(e.exception),
        )

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

        self.assertIn(
            "У приятной привычки не может быть вознаграждения или связанной привычки.",
            str(e.exception),
        )

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

        self.assertIn(
            "Периодичность выполнения должна быть от 1 до 7 дней", str(e.exception)
        )

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
        # print("Фактическое значение repr(habit):")
        # print(repr(habit))
        # print("\nОжидаемое значение expected_repr:")
        # print(expected_repr)

        self.assertEqual(repr(habit), expected_repr)


#  Тест для run_telegram_bot
class RunTelegramBotTaskTest(TestCase):
    @patch("habits.tasks.bot.polling")
    def test_run_telegram_bot(self, mock_polling):
        """
        Тестируем задачу run_telegram_bot.
        Проверяем, что polling вызывается.
        """
        run_telegram_bot()
        mock_polling.assert_called_once_with(none_stop=True)


#  тесты на CRUD habit (ViewSet)


class HabitViewSetTest(APITestCase):
    def setUp(self):
        """
        Создаём пользователя и несколько привычек для тестов.
        """
        self.user = User.objects.create_user(
            email="test@example.com", password="password123"
        )
        self.client.force_authenticate(user=self.user)  # Аутентифицируем пользователя

        self.habit1 = Habit.objects.create(
            owner=self.user,
            location="Парк",
            time="07:00:00",
            action="Прогулка",
            duration=60,
            frequency=1,
            is_public=False,
        )
        self.habit2 = Habit.objects.create(
            owner=self.user,
            location="Дом",
            time="08:00:00",
            action="Йога",
            duration=30,
            frequency=2,
            is_public=True,
        )

    def test_get_habits(self):
        """
        Тест получения списка привычек текущего пользователя.
        """
        response = self.client.get("/habits/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.data["results"]), 2
        )  # Проверяем, что возвращаются обе привычки

    def test_create_habit(self):
        """
        Тест создания новой привычки.
        """
        data = {
            "location": "Офис",
            "time": "09:00:00",
            "action": "Работа над проектом",
            "duration": 90,
            "frequency": 3,
            "is_public": False,
        }
        response = self.client.post(
            "/habits/",
            data=json.dumps(data),  # Преобразуем данные в строку JSON
            content_type="application/json",  # Указываем тип контента
        )
        # print("Response data:", response.data)  # Выводим данные ответа для отладки
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_habit(self):
        """
        Тест обновления существующей привычки.
        """
        data = {
            "location": "Изменённое место",
            "time": "10:00:00",
            "action": "Изменённое действие",
            "duration": 45,
            "frequency": 2,
            "is_public": False,
        }
        response = self.client.put(
            f"/habits/{self.habit1.id}/",
            data=json.dumps(data),  # Преобразуем данные в строку JSON
            content_type="application/json",  # Указываем тип контента
        )
        # print("Response data:", response.data)  # Выводим данные ответа для отладки
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_habit(self):
        """
        Тест удаления привычки.
        """
        response = self.client.delete(f"/habits/{self.habit1.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Habit.objects.filter(id=self.habit1.id).exists())

    def test_update_public_habit(self):
        """
        Тест запрета редактирования публичной привычки.
        """
        data = {
            "location": "Изменённое место",
            "time": "10:00:00",
            "action": "Изменённое действие",
            "duration": 45,
            "frequency": 2,
            "is_public": True,
        }
        response = self.client.put(
            f"/habits/{self.habit2.id}/",
            data=json.dumps(data),  # Преобразуем данные в строку JSON
            content_type="application/json",  # Указываем тип контента
        )
        # print("Response data:", response.data)  # Выводим данные ответа для отладки
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_public_habit(self):
        """
        Тест запрета удаления публичной привычки.
        """
        response = self.client.delete(f"/habits/{self.habit2.id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


#  тестируем дженерик LictApiView получения списка публичных привычек


class PublicHabitListApiViewTest(APITestCase):
    def setUp(self):
        """
        Создаём пользователей и публичные/непубличные привычки для тестов.
        """
        user1 = User.objects.create_user(
            email="user1@example.com", password="password123"
        )
        user2 = User.objects.create_user(
            email="user2@example.com", password="password123"
        )

        Habit.objects.create(
            owner=user1,
            location="Парк",
            time="07:00:00",
            action="Прогулка",
            duration=60,
            frequency=1,
            is_public=True,  # Публичная привычка
        )

        Habit.objects.create(
            owner=user2,
            location="Дом",
            time="08:00:00",
            action="Йога",
            duration=30,
            frequency=2,
            is_public=False,  # Непубличная привычка
        )

    def test_get_public_habits(self):
        """
        Тест получения списка публичных привычек.
        """
        response = self.client.get("/habits/public/")  # Исправленный URL

        # Проверяем статус ответа
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем количество возвращённых записей
        self.assertEqual(len(response.data["results"]), 1)

    def test_only_public_habits_returned(self):
        """
        Тест проверки фильтрации только публичных привычек.
        """
        # Запрос к эндпоинту с публичными данными.
        response = self.client.get("/habits/public/")  # Исправленный URL

        # Проверяем статус ответа
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем, что возвращена только одна публичная привычка
        self.assertEqual(len(response.data["results"]), 1)

        # Проверяем, что возвращённая привычка — это публичная привычка
        public_habit = response.data["results"][0]
        self.assertEqual(public_habit["action"], "Прогулка")
        self.assertTrue(public_habit["is_public"])

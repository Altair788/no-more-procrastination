import telebot
from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.utils.timezone import now
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from config.settings import TELEGRAM_BOT_TOKEN
from habits.models import Habit

# Создаём экземпляр бота
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)


# Команда /start
@bot.message_handler(commands=["start"])
def start(message):
    """
    Обработчик команды /start.
    Отправляет приветственное сообщение с кнопкой.
    """
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Мои привычки", callback_data="my_habits"))
    bot.send_message(
        message.chat.id,
        "Привет! Я ваш трекер привычек. Вы можете управлять своими привычками здесь.",
        reply_markup=markup,
    )


# Callback-кнопка "Мои привычки"
@bot.callback_query_handler(func=lambda call: call.data == "my_habits")
def show_habits(call):
    """
    Показывает список привычек пользователя.
    """
    # Импортируем модель внутри функции, чтобы избежать циклических зависимостей
    from habits.models import Habit

    user_tg_id = call.message.chat.id
    habits = Habit.objects.filter(owner__tg_id=user_tg_id)

    if not habits.exists():
        bot.send_message(call.message.chat.id, "У вас пока нет привычек.")
        return

    message = "Ваши привычки:\n\n"
    for habit in habits:
        message += f"- {habit.action} (в {habit.time.strftime('%H:%M')})\n"

    bot.send_message(call.message.chat.id, message)


# Задача Celery для запуска Telegram-бота
@shared_task(bind=True)
def run_telegram_bot(self):
    """
    Фоновая задача для запуска Telegram-бота через Celery.
    """
    try:
        print("Запуск Telegram-бота...")
        bot.polling(none_stop=True)  # Запускаем бота в режиме постоянного опроса
    except Exception as exc:
        print(f"Ошибка при запуске Telegram-бота: {exc}")
        raise self.retry(
            exc=exc, countdown=10
        )  # Повторяем задачу через 10 секунд при ошибке


@shared_task(bind=True, max_retries=3)
def send_telegram_reminder(self, tg_id, message):
    """
    Задача для отправки напоминания о привычке через Telegram.
    Если задача завершилась с ошибкой, она будет повторена до 3 раз.
    """
    try:
        # Создаём экземпляр бота
        bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

        # Обновляем состояние задачи (начало выполнения)
        self.update_state(state="PROGRESS", meta={"status": "Отправка сообщения"})

        # Отправляем сообщение
        bot.send_message(chat_id=tg_id, text=message)

        # Возвращаем успешный результат
        return {"status": "Успешно", "tg_id": tg_id}

    except Exception as exc:
        # Если произошла ошибка, повторяем задачу через 10 секунд
        self.retry(exc=exc, countdown=10)


@shared_task(bind=True)
def send_daily_reminders(self):
    """
    Ежедневная задача для отправки напоминаний о привычках.
    """
    # today = now().date()
    current_time = now().time()

    # Фильтруем привычки, которые должны быть выполнены сегодня
    habits = Habit.objects.filter(time__lte=current_time).select_related("owner")

    total_habits = habits.count()
    for index, habit in enumerate(habits):
        if habit.owner.tg_id:
            # Определяем тип вознаграждения
            if habit.reward:
                reward_message = f"Вознаграждение: {habit.reward}"
            elif habit.linked_action:
                reward_message = (
                    f"Связанная приятная привычка: {habit.linked_action.action}"
                )
            else:
                reward_message = "Вознаграждение отсутствует."

            # Формируем сообщение
            message = (
                f"Напоминание о привычке:\n\n"
                f"Действие: {habit.action}\n"
                f"Место: {habit.location}\n"
                f"Время выполнения: {habit.time.strftime('%H:%M')}\n"
                f"{reward_message}"
            )

            # Запускаем задачу для отправки сообщения
            send_telegram_reminder.delay(habit.owner.tg_id, message)
        else:
            # Если tg_id отсутствует, отправляем email с инструкцией по привязке Telegram
            try:
                subject = "Привяжите ваш Telegram для получения уведомлений"
                email_message = (
                    f"Здравствуйте, {habit.owner.email}!\n\n"
                    "Мы заметили, что у вас нет привязанного Telegram ID. "
                    "Для получения уведомлений о ваших привычках, пожалуйста, укажите ваш Telegram ID "
                    "в настройках профиля на нашем сайте."
                )
                send_mail(
                    subject,
                    email_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [habit.owner.email],
                    fail_silently=False,
                )
            except Exception as e:
                print(f"Ошибка при отправке email: {e}")
        # Обновляем состояние задачи (прогресс)
        self.update_state(
            state="PROGRESS",
            meta={
                "current": index + 1,
                "total": total_habits,
                "status": f"Обработана привычка {index + 1} из {total_habits}",
            },
        )

    return {"status": "Завершено", "total_habits": total_habits}

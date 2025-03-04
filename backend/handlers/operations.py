import logging

from datetime import datetime, timedelta
from aiogram import Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from utils.db_operations import get_daily_income, get_weekly_income, get_monthly_income, get_income_in_date_range
from utils.db_operations import get_daily_expenses, get_weekly_expenses, get_monthly_expenses, get_expenses_in_date_range
from models.database import get_db
from models.user import User

logger = logging.getLogger(__name__)

router = Router()
# Глобальный словарь для хранения контекста (доходы или расходы)
user_context = {}

# Функция для получения пользователя
def get_user_from_db(db, tg_id):
    """
    Получает пользователя из базы данных по его Telegram ID.

    :param db: Сессия базы данных.
    :param tg_id: Telegram ID пользователя.
    :return: Объект пользователя или None, если пользователь не найден.
    """
    return db.query(User).filter(User.tg_id == tg_id).first()

# Обработчик кнопки "Статистика"
@router.message(lambda message: message.text == "Статистика")
async def show_statistics_menu(message: Message):
    """
    Обработчик команды "Статистика". Показывает меню выбора статистики (доходы или расходы).

    :param message: Объект сообщения от пользователя.
    """
    stats_inline_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📊 Статистика по доходам", callback_data="income_stats")],
            [InlineKeyboardButton(text="💸 Статистика по расходам", callback_data="expenses_stats")],
            [InlineKeyboardButton(text="⬅ Назад", callback_data="back")]
        ]
    )
    await message.answer("Выберите, что вы хотите посмотреть:", reply_markup=stats_inline_keyboard)

# Обработчик для кнопки "Статистика по доходам"
@router.callback_query(lambda c: c.data == "income_stats")
async def show_income_stats_menu(callback_query: CallbackQuery):
    """
    Обработчик кнопки "Статистика по доходам". Показывает меню выбора статистики по доходам.

    :param callback_query: Объект callback-запроса.
    """
    income_stats_inline_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💰 Доходы за день", callback_data="daily_income")],
            [InlineKeyboardButton(text="📅 Доходы за неделю", callback_data="weekly_income")],
            [InlineKeyboardButton(text="📆 Доходы за месяц", callback_data="monthly_income")],
            [InlineKeyboardButton(text="🔎 Фильтр по датам (с и по)", callback_data="date_filter_income")],
            [InlineKeyboardButton(text="⬅ Назад", callback_data="back")]
        ]
    )
    await callback_query.message.answer("Выберите, что вы хотите посмотреть по доходам:", reply_markup=income_stats_inline_keyboard)

# Обработчик для кнопки "Статистика по расходам"
@router.callback_query(lambda c: c.data == "expenses_stats")
async def show_expenses_stats_menu(callback_query: CallbackQuery):
    """
    Обработчик кнопки "Статистика по расходам". Показывает меню выбора статистики по расходам.

    :param callback_query: Объект callback-запроса.
    """
    expenses_stats_inline_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💸 Расходы за день", callback_data="daily_expenses")],
            [InlineKeyboardButton(text="📅 Расходы за неделю", callback_data="weekly_expenses")],
            [InlineKeyboardButton(text="📆 Расходы за месяц", callback_data="monthly_expenses")],
            [InlineKeyboardButton(text="🔎 Фильтр по датам (с и по)", callback_data="date_filter_expenses")],
            [InlineKeyboardButton(text="⬅ Назад", callback_data="back")]
        ]
    )
    await callback_query.message.answer("Выберите, что вы хотите посмотреть по расходам:", reply_markup=expenses_stats_inline_keyboard)

# Обработчик для вывода статистики за день для доходов
@router.callback_query(lambda c: c.data == "daily_income")
async def show_daily_income(callback_query: CallbackQuery):
    """
    Обработчик кнопки "Доходы за день". Показывает доходы за текущий день.

    :param callback_query: Объект callback-запроса.
    """
    db = next(get_db())
    user = get_user_from_db(db, callback_query.from_user.id)
    if user:
        today = datetime.today().date()
        daily_income = get_daily_income(user.id, db)
        await callback_query.message.answer(f"📅 Доходы за день ({today.strftime('%d.%m.%Y')}): \n{daily_income} ₽")
    else:
        await callback_query.message.answer("❌ Пользователь не найден.")

# Обработчик для вывода статистики за неделю для доходов
@router.callback_query(lambda c: c.data == "weekly_income")
async def show_weekly_income(callback_query: CallbackQuery):
    """
    Обработчик кнопки "Доходы за неделю". Показывает доходы за текущую неделю.

    :param callback_query: Объект callback-запроса.
    """
    db = next(get_db())
    user = get_user_from_db(db, callback_query.from_user.id)
    if user:
        today = datetime.today().date()
        start_of_week = today - timedelta(days=today.weekday())  # Начало недели
        end_of_week = start_of_week + timedelta(days=6)  # Конец недели
        weekly_income = get_weekly_income(user.id, db)
        await callback_query.message.answer(f"📅 Доходы за неделю ({start_of_week.strftime('%d.%m.%Y')} - {end_of_week.strftime('%d.%m.%Y')}): \n{weekly_income} ₽")
    else:
        await callback_query.message.answer("❌ Пользователь не найден.")

# Обработчик для вывода статистики за месяц для доходов
@router.callback_query(lambda c: c.data == "monthly_income")
async def show_monthly_income(callback_query: CallbackQuery):
    """
    Обработчик кнопки "Доходы за месяц". Показывает доходы за текущий месяц.

    :param callback_query: Объект callback-запроса.
    """
    db = next(get_db())
    user = get_user_from_db(db, callback_query.from_user.id)
    if user:
        today = datetime.today().date()
        start_of_month = today.replace(day=1)  # Начало месяца
        # Для последнего дня месяца
        end_of_month = (start_of_month.replace(month=today.month % 12 + 1, day=1) - timedelta(days=1))
        monthly_income = get_monthly_income(user.id, db)
        await callback_query.message.answer(f"📆 Доходы за месяц ({start_of_month.strftime('%d.%m.%Y')} - {end_of_month.strftime('%d.%m.%Y')}): \n{monthly_income} ₽")
    else:
        await callback_query.message.answer("❌ Пользователь не найден.")

# Обработчик для вывода статистики за день для расходов
@router.callback_query(lambda c: c.data == "daily_expenses")
async def show_daily_expenses(callback_query: CallbackQuery):
    """
    Обработчик кнопки "Расходы за день". Показывает расходы за текущий день.

    :param callback_query: Объект callback-запроса.
    """
    db = next(get_db())
    user = get_user_from_db(db, callback_query.from_user.id)
    if user:
        today = datetime.today().date()
        daily_expenses = get_daily_expenses(user.id, db)
        await callback_query.message.answer(f"💸 Расходы за день ({today.strftime('%d.%m.%Y')}): \n{daily_expenses} ₽")
    else:
        await callback_query.message.answer("❌ Пользователь не найден.")

# Обработчик для вывода статистики за неделю для расходов
@router.callback_query(lambda c: c.data == "weekly_expenses")
async def show_weekly_expenses(callback_query: CallbackQuery):
    """
    Обработчик кнопки "Расходы за неделю". Показывает расходы за текущую неделю.

    :param callback_query: Объект callback-запроса.
    """
    db = next(get_db())
    user = get_user_from_db(db, callback_query.from_user.id)
    if user:
        today = datetime.today().date()
        start_of_week = today - timedelta(days=today.weekday())  # Начало недели
        end_of_week = start_of_week + timedelta(days=6)  # Конец недели
        weekly_expenses = get_weekly_expenses(user.id, db)
        await callback_query.message.answer(f"📅 Расходы за неделю ({start_of_week.strftime('%d.%m.%Y')} - {end_of_week.strftime('%d.%m.%Y')}): \n{weekly_expenses} ₽")
    else:
        await callback_query.message.answer("❌ Пользователь не найден.")

# Обработчик для вывода статистики за месяц для расходов
@router.callback_query(lambda c: c.data == "monthly_expenses")
async def show_monthly_expenses(callback_query: CallbackQuery):
    """
    Обработчик кнопки "Расходы за месяц". Показывает расходы за текущий месяц.

    :param callback_query: Объект callback-запроса.
    """
    db = next(get_db())
    user = get_user_from_db(db, callback_query.from_user.id)
    if user:
        today = datetime.today().date()
        start_of_month = today.replace(day=1)  # Начало месяца
        # Для последнего дня месяца
        end_of_month = (start_of_month.replace(month=today.month % 12 + 1, day=1) - timedelta(days=1))
        monthly_expenses = get_monthly_expenses(user.id, db)
        await callback_query.message.answer(f"📆 Расходы за месяц ({start_of_month.strftime('%d.%m.%Y')} - {end_of_month.strftime('%d.%m.%Y')}): \n{monthly_expenses} ₽")
    else:
        await callback_query.message.answer("❌ Пользователь не найден.")

# Обработчик для кнопки "Фильтр по датам (с и по)" для расходов
@router.callback_query(lambda c: c.data == "date_filter_expenses")
async def ask_for_expenses_date_range(callback_query: CallbackQuery):
    """
    Обработчик кнопки "Фильтр по датам (с и по)" для расходов. Запрашивает у пользователя ввод диапазона дат.

    :param callback_query: Объект callback-запроса.
    """
    user_id = callback_query.from_user.id
    user_context[user_id] = "expenses"  # Сохраняем контекст "расходы"
    await callback_query.message.answer("Введите диапазон дат для расходов в формате ДД.ММ.ГГГГ ДД.ММ.ГГГГ (например, 01.01.2023 31.01.2023):")

# Обработчик для кнопки "Фильтр по датам (с и по)" для доходов
@router.callback_query(lambda c: c.data == "date_filter_income")
async def ask_for_income_date_range(callback_query: CallbackQuery):
    """
    Обработчик кнопки "Фильтр по датам (с и по)" для доходов. Запрашивает у пользователя ввод диапазона дат.

    :param callback_query: Объект callback-запроса.
    """
    user_id = callback_query.from_user.id
    user_context[user_id] = "income"  # Сохраняем контекст "доходы"
    await callback_query.message.answer("Введите диапазон дат для доходов в формате ДД.ММ.ГГГГ ДД.ММ.ГГГГ (например, 01.01.2023 31.01.2023):")

# Обработчик для вывода статистики по диапазону дат (формат ДД.ММ.ГГГГ ДД.ММ.ГГГГ)
@router.message(lambda message: " " in message.text)
async def handle_date_range(message: Message):
    """
    Обработчик ввода диапазона дат. Выводит статистику по доходам или расходам за указанный период.

    :param message: Объект сообщения от пользователя.
    """
    try:
        user_id = message.from_user.id
        if user_id not in user_context:
            await message.answer("❌ Контекст не найден. Пожалуйста, выберите 'Фильтр по датам' снова.")
            return

        # Разделяем строку на две части по пробелу
        date_range = message.text.strip()
        start_date_str, end_date_str = date_range.split()

        # Преобразуем строки в объекты datetime
        start_date = datetime.strptime(start_date_str.strip(), "%d.%m.%Y").date()
        end_date = datetime.strptime(end_date_str.strip(), "%d.%m.%Y").date()

        db = next(get_db())
        user = get_user_from_db(db, user_id)
        if user:
            # Проверка контекста (доходы или расходы)
            if user_context[user_id] == "income":
                filtered_income = get_income_in_date_range(user.id, start_date, end_date, db)
                await message.answer(f"💰 Доходы с {start_date.strftime('%d.%m.%Y')} по {end_date.strftime('%d.%m.%Y')}: \n{filtered_income} ₽")
            elif user_context[user_id] == "expenses":
                filtered_expenses = get_expenses_in_date_range(user.id, start_date, end_date, db)
                await message.answer(f"💸 Расходы с {start_date.strftime('%d.%m.%Y')} по {end_date.strftime('%d.%m.%Y')}: \n{filtered_expenses} ₽")
            else:
                await message.answer("❌ Неверный контекст.")
            # Очищаем контекст после обработки
            del user_context[user_id]
        else:
            await message.answer("❌ Пользователь не найден.")
    except ValueError:
        await message.answer("❌ Неверный формат даты. Пожалуйста, используйте формат ДД.ММ.ГГГГ ДД.ММ.ГГГГ.")
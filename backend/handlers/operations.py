import re
import logging

from datetime import datetime, timedelta
from aiogram import Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from tabulate import tabulate

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


# Функция для экранирования MarkdownV2
def escape_markdown_v2(text: str) -> str:
    """Escapes special characters for proper rendering in MarkdownV2."""
    # Список символов, которые нужно экранировать
    escape_chars = r'_*[]()~`>#+-=|{}.!'

    # Экранируем все специальные символы
    text = re.sub(r'([{}])'.format(re.escape(escape_chars)), r'\\\1', text)

    return text

# Обработчик кнопки "Статистика"
@router.message(lambda message: message.text == "Статистика")
async def show_statistics_menu(message: Message):
    """
    Обработчик команды "Статистика". Показывает меню выбора статистики (доходы или расходы).
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


@router.callback_query(lambda c: c.data == "daily_income")
async def show_daily_income(callback_query: CallbackQuery):
    """Обработчик кнопки "Доходы за день". Показывает доходы за текущий день по категориям и деталям."""
    try:
        # Получаем данные из базы данных
        with next(get_db()) as db:
            user = get_user_from_db(db, callback_query.from_user.id)

            if not user:
                await callback_query.message.answer("❌ Пользователь не найден.")
                return

            today = datetime.today().date()

            # Получаем доходы
            total_income, category_incomes, detailed_incomes = get_daily_income(user.id, db)
            
            if total_income == 0:
                await callback_query.message.answer("💰 Сегодня у вас нет доходов.")
                return

            # Формируем сообщение с общими доходами
            income_message = f"📅 \\*Доходы за день\\* \\({escape_markdown_v2(today.strftime('%d.%m.%Y'))}\\):\n💰 {escape_markdown_v2(str(total_income))}₽\n\n"

            # Формируем список доходов по категориям
            for category, amount in category_incomes.items():
                income_message += f'📌 \\*{escape_markdown_v2(category)}\\*: {escape_markdown_v2(str(amount))}₽\n'

            # Формируем таблицу с детальной информацией
            if detailed_incomes:
                headers = ["Дата", "Категория", "Описание", "Сумма"]
                table_data = [
                    [
                        date.strftime("%d.%m.%Y"),
                        escape_markdown_v2(category),
                        escape_markdown_v2(description),
                        f"{amount:.2f}₽"
                    ]
                    for date, category, description, amount in detailed_incomes
                ]

                table = tabulate(table_data, headers, tablefmt="grid")
                income_message += f"\n📋 \\*Детальная информация:\\*\n```\n{table}\n```"

            await callback_query.message.answer(income_message, parse_mode="MarkdownV2")
            
    except Exception as e:
        logger.error(f"Ошибка при обработке доходов за день для пользователя {callback_query.from_user.id}: {e}", exc_info=True)
        await callback_query.message.answer("❌ Произошла ошибка при обработке запроса.")


# Обработчик для вывода статистики за неделю для доходов
@router.callback_query(lambda c: c.data == "weekly_income")
async def show_weekly_income(callback_query: CallbackQuery):
    """Обработчик кнопки "Доходы за неделю". Показывает доходы за текущую неделю по категориям и деталям."""
    try:
        with next(get_db()) as db:
            user = get_user_from_db(db, callback_query.from_user.id)
            if not user:
                await callback_query.message.answer("❌ Пользователь не найден.")
                return

            today = datetime.today().date()
            start_of_week = today - timedelta(days=today.weekday())
            end_of_week = start_of_week + timedelta(days=6)

            total_income, category_incomes, detailed_incomes = get_weekly_income(user.id, db)

            if total_income == 0:
                await callback_query.message.answer("💰 За эту неделю у вас нет доходов.")
                return

            # Заголовок с общей суммой (экранируем для MarkdownV2)
            income_message = f"📅 \\*Доходы за неделю\\* \\({escape_markdown_v2(start_of_week.strftime('%d.%m.%Y'))} \\- {escape_markdown_v2(end_of_week.strftime('%d.%m.%Y'))}\\):\n💰 {escape_markdown_v2(str(total_income))}₽\n\n"
            
            # Список категорий с общей суммой (экранируем для MarkdownV2)
            for category, amount in category_incomes.items():
                income_message += f'📌 \\*{escape_markdown_v2(category)}\\*: {escape_markdown_v2(str(amount))}₽\n'

            # Формируем таблицу для детальной информации (без экранирования, так как это код)
            if detailed_incomes:
                headers = ["Дата", "Категория", "Описание", "Сумма"]
                table_data = [
                    [
                        date.strftime("%d.%m.%Y"),  # Дата без экранирования
                        category,                  # Категория без экранирования
                        description,               # Описание без экранирования
                        f"{amount:.2f}₽"          # Сумма без экранирования
                    ]
                    for date, category, description, amount in detailed_incomes
                ]
                # Формируем таблицу
                table = tabulate(table_data, headers, tablefmt="grid")
                income_message += f"\n📋 \\*Детальная информация:\\*\n```\n{table}\n```"

            await callback_query.message.answer(income_message, parse_mode="MarkdownV2")
    except Exception as e:
        logger.error(f"Ошибка при обработке доходов за неделю для пользователя {callback_query.from_user.id}: {e}")
        await callback_query.message.answer("❌ Произошла ошибка при обработке запроса.")


@router.callback_query(lambda c: c.data == "monthly_income")
async def show_monthly_income(callback_query: CallbackQuery):
    """Обработчик кнопки "Доходы за месяц". Показывает детальную статистику доходов за текущий месяц."""
    try:
        with next(get_db()) as db:
            user = get_user_from_db(db, callback_query.from_user.id)
            if not user:
                await callback_query.message.answer("❌ Пользователь не найден.")
                return

            today = datetime.today().date()
            start_of_month = today.replace(day=1)
            end_of_month = (start_of_month.replace(month=today.month % 12 + 1, day=1) - timedelta(days=1))

            total_income, category_incomes, detailed_incomes = get_monthly_income(user.id, db)

            if total_income == 0:
                await callback_query.message.answer("💰 В этом месяце у вас нет доходов.")
                return

            # Заголовок с общей суммой (экранируем для MarkdownV2)
            income_message = f"📆 \\*Доходы за месяц\\* \\({escape_markdown_v2(start_of_month.strftime('%d.%m.%Y'))} \\- {escape_markdown_v2(end_of_month.strftime('%d.%m.%Y'))}\\):\n💰 {escape_markdown_v2(str(total_income))}₽\n\n"

            # Список категорий с общей суммой (экранируем для MarkdownV2)
            for category, amount in category_incomes.items():
                income_message += f'📌 \\*{escape_markdown_v2(category)}\\*: {escape_markdown_v2(str(amount))}₽\n'

            # Формируем таблицу для детальной информации (без экранирования, так как это код)
            if detailed_incomes:
                headers = ["Дата", "Категория", "Описание", "Сумма"]
                table_data = [
                    [
                        date.strftime("%d.%m.%Y"),  # Дата без экранирования
                        category,                  # Категория без экранирования
                        description,               # Описание без экранирования
                        f"{amount:.2f}₽"          # Сумма без экранирования
                    ]
                    for date, category, description, amount in detailed_incomes
                ]
                # Формируем таблицу
                table = tabulate(table_data, headers, tablefmt="grid")
                income_message += f"\n📋 \\*Детальная информация:\\*\n```\n{table}\n```"

            await callback_query.message.answer(income_message, parse_mode="MarkdownV2")
    except Exception as e:
        logger.error(f"Ошибка при обработке доходов за месяц для пользователя {callback_query.from_user.id}: {e}")
        await callback_query.message.answer("❌ Произошла ошибка при обработке запроса.")


@router.callback_query(lambda c: c.data == "daily_expenses")
async def show_daily_expenses(callback_query: CallbackQuery):
    """Обработчик кнопки "Расходы за день". Показывает расходы за текущий день по категориям и деталям."""
    try:
        # Получаем данные из базы данных
        with next(get_db()) as db:
            user = get_user_from_db(db, callback_query.from_user.id)

            if not user:
                await callback_query.message.answer("❌ Пользователь не найден.")
                return

            today = datetime.today().date()

            # Получаем расходы
            total_expense, category_expenses, detailed_expenses = get_daily_expenses(user.id, db)
            
            if total_expense == 0:
                await callback_query.message.answer("💸 Сегодня у вас нет расходов.")
                return

            # Формируем сообщение с общими расходами
            expense_message = f"📅 \\*Расходы за день\\* \\({escape_markdown_v2(today.strftime('%d.%m.%Y'))}\\):\n💸 {escape_markdown_v2(str(total_expense))}₽\n\n"

            # Формируем список расходов по категориям
            for category, amount in category_expenses.items():
                expense_message += f'📌 \\*{escape_markdown_v2(category)}\\*: {escape_markdown_v2(str(amount))}₽\n'

            # Формируем таблицу с детальной информацией
            if detailed_expenses:
                headers = ["Дата", "Категория", "Описание", "Сумма"]
                table_data = [
                    [
                        date.strftime("%d.%m.%Y"),
                        escape_markdown_v2(category),
                        escape_markdown_v2(description),
                        f"{amount:.2f}₽"
                    ]
                    for date, category, description, amount in detailed_expenses
                ]

                table = tabulate(table_data, headers, tablefmt="grid")
                expense_message += f"\n📋 \\*Детальная информация:\\*\n```\n{table}\n```"

            await callback_query.message.answer(expense_message, parse_mode="MarkdownV2")
            
    except Exception as e:
        logger.error(f"Ошибка при обработке расходов за день для пользователя {callback_query.from_user.id}: {e}", exc_info=True)
        await callback_query.message.answer("❌ Произошла ошибка при обработке запроса.")


@router.callback_query(lambda c: c.data == "weekly_expenses")
async def show_weekly_expenses(callback_query: CallbackQuery):
    """Обработчик кнопки "Расходы за неделю". Показывает расходы за текущую неделю по категориям и деталям."""
    try:
        with next(get_db()) as db:
            user = get_user_from_db(db, callback_query.from_user.id)
            if not user:
                await callback_query.message.answer("❌ Пользователь не найден.")
                return

            today = datetime.today().date()
            start_of_week = today - timedelta(days=today.weekday())
            end_of_week = start_of_week + timedelta(days=6)

            total_expense, category_expenses, detailed_expenses = get_weekly_expenses(user.id, db)

            if total_expense == 0:
                await callback_query.message.answer("💸 За эту неделю у вас нет расходов.")
                return

            # Заголовок с общей суммой (экранируем для MarkdownV2)
            expense_message = f"📅 \\*Расходы за неделю\\* \\({escape_markdown_v2(start_of_week.strftime('%d.%m.%Y'))} \\- {escape_markdown_v2(end_of_week.strftime('%d.%m.%Y'))}\\):\n💸 {escape_markdown_v2(str(total_expense))}₽\n\n"
            
            # Список категорий с общей суммой (экранируем для MarkdownV2)
            for category, amount in category_expenses.items():
                expense_message += f'📌 \\*{escape_markdown_v2(category)}\\*: {escape_markdown_v2(str(amount))}₽\n'

            # Формируем таблицу для детальной информации (без экранирования, так как это код)
            if detailed_expenses:
                headers = ["Дата", "Категория", "Описание", "Сумма"]
                table_data = [
                    [
                        date.strftime("%d.%m.%Y"),  # Дата без экранирования
                        category,                  # Категория без экранирования
                        description,               # Описание без экранирования
                        f"{amount:.2f}₽"          # Сумма без экранирования
                    ]
                    for date, category, description, amount in detailed_expenses
                ]
                # Формируем таблицу
                table = tabulate(table_data, headers, tablefmt="grid")
                expense_message += f"\n📋 \\*Детальная информация:\\*\n```\n{table}\n```"

            await callback_query.message.answer(expense_message, parse_mode="MarkdownV2")
    except Exception as e:
        logger.error(f"Ошибка при обработке расходов за неделю для пользователя {callback_query.from_user.id}: {e}")
        await callback_query.message.answer("❌ Произошла ошибка при обработке запроса.")



@router.callback_query(lambda c: c.data == "monthly_expenses")
async def show_monthly_expenses(callback_query: CallbackQuery):
    """Обработчик кнопки "Расходы за месяц". Показывает детальную статистику расходов за текущий месяц."""
    try:
        with next(get_db()) as db:
            user = get_user_from_db(db, callback_query.from_user.id)
            if not user:
                await callback_query.message.answer("❌ Пользователь не найден.")
                return

            today = datetime.today().date()
            start_of_month = today.replace(day=1)
            end_of_month = (start_of_month.replace(month=today.month % 12 + 1, day=1) - timedelta(days=1))

            total_expense, category_expenses, detailed_expenses = get_monthly_expenses(user.id, db)

            if total_expense == 0:
                await callback_query.message.answer("💸 В этом месяце у вас нет расходов.")
                return

            # Заголовок с общей суммой (экранируем для MarkdownV2)
            expense_message = f"📆 \\*Расходы за месяц\\* \\({escape_markdown_v2(start_of_month.strftime('%d.%m.%Y'))} \\- {escape_markdown_v2(end_of_month.strftime('%d.%m.%Y'))}\\):\n💸 {escape_markdown_v2(str(total_expense))}₽\n\n"

            # Список категорий с общей суммой (экранируем для MarkdownV2)
            for category, amount in category_expenses.items():
                expense_message += f'📌 \\*{escape_markdown_v2(category)}\\*: {escape_markdown_v2(str(amount))}₽\n'

            # Формируем таблицу для детальной информации (без экранирования, так как это код)
            if detailed_expenses:
                headers = ["Дата", "Категория", "Описание", "Сумма"]
                table_data = [
                    [
                        date.strftime("%d.%m.%Y"),  # Дата без экранирования
                        category,                  # Категория без экранирования
                        description,               # Описание без экранирования
                        f"{amount:.2f}₽"          # Сумма без экранирования
                    ]
                    for date, category, description, amount in detailed_expenses
                ]
                # Формируем таблицу
                table = tabulate(table_data, headers, tablefmt="grid")
                expense_message += f"\n📋 \\*Детальная информация:\\*\n```\n{table}\n```"

            await callback_query.message.answer(expense_message, parse_mode="MarkdownV2")
    except Exception as e:
        logger.error(f"Ошибка при обработке расходов за месяц для пользователя {callback_query.from_user.id}: {e}")
        await callback_query.message.answer("❌ Произошла ошибка при обработке запроса.")


# Обработчик для кнопки "Фильтр по датам (с и по)" для расходов
@router.callback_query(lambda c: c.data == "date_filter_expenses")
async def ask_for_expenses_date_range(callback_query: CallbackQuery):
    """
    Обработчик кнопки "Фильтр по датам (с и по)" для расходов. Запрашивает у пользователя ввод диапазона дат.
    """
    user_id = callback_query.from_user.id
    user_context[user_id] = "expenses"  # Сохраняем контекст "расходы"
    await callback_query.message.answer("Введите диапазон дат для расходов в формате ДД.ММ.ГГГГ ДД.ММ.ГГГГ (например, 01.01.2023 31.01.2023):")

# Обработчик для кнопки "Фильтр по датам (с и по)" для доходов
@router.callback_query(lambda c: c.data == "date_filter_income")
async def ask_for_income_date_range(callback_query: CallbackQuery):
    """
    Обработчик кнопки "Фильтр по датам (с и по)" для доходов. Запрашивает у пользователя ввод диапазона дат.
    """
    user_id = callback_query.from_user.id
    user_context[user_id] = "income"  # Сохраняем контекст "доходы"
    await callback_query.message.answer("Введите диапазон дат для доходов в формате ДД.ММ.ГГГГ ДД.ММ.ГГГГ (например, 01.01.2023 31.01.2023):")


@router.message(lambda message: " " in message.text)
async def handle_date_range(message: Message):
    """
    Обработчик ввода диапазона дат. Выводит статистику по доходам или расходам за указанный период.
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
        try:
            start_date = datetime.strptime(start_date_str.strip(), "%d.%m.%Y").date()
            end_date = datetime.strptime(end_date_str.strip(), "%d.%m.%Y").date()
        except ValueError:
            await message.answer("❌ Неверный формат даты. Пожалуйста, используйте формат ДД.ММ.ГГГГ ДД.ММ.ГГГГ.")
            return

        db = next(get_db())
        user = get_user_from_db(db, user_id)
        if user:
            # Проверка контекста (доходы или расходы)
            if user_context[user_id] == "income":
                total_income, category_income, detailed_incomes = get_income_in_date_range(user.id, start_date, end_date, db)
                # Формируем сообщение
                income_message = f"📆 *Доходы с {escape_markdown_v2(start_date.strftime('%d.%m.%Y'))} по {escape_markdown_v2(end_date.strftime('%d.%m.%Y'))}:*\n💰 {escape_markdown_v2(str(total_income))} ₽\n\n"
                # Список категорий с общей суммой
                for category, amount in category_income.items():
                    income_message += f'📌 *{escape_markdown_v2(category)}*: {escape_markdown_v2(str(amount))}₽\n'
                
                # Формируем детальную таблицу
                headers = ["Дата", "Категория", "Описание", "Сумма"]
                table_data = [
                    [
                        date.strftime("%d.%m.%Y"),  # Дата без экранирования
                        category,                  # Категория без экранирования
                        description,               # Описание без экранирования
                        f"{amount:.2f}₽"           # Сумма без экранирования
                    ]
                    for date, category, description, amount in detailed_incomes
                ]
                # Формируем таблицу
                table = tabulate(table_data, headers, tablefmt="grid")
                income_message += f"\n📋 *Детальная информация:*\n```\n{table}\n```"

                await message.answer(income_message, parse_mode="MarkdownV2")

            elif user_context[user_id] == "expenses":
                total_expense, category_expenses, detailed_expenses = get_expenses_in_date_range(user.id, start_date, end_date, db)
                # Формируем сообщение
                expense_message = f"📆 *Расходы с {escape_markdown_v2(start_date.strftime('%d.%m.%Y'))} по {escape_markdown_v2(end_date.strftime('%d.%m.%Y'))}:*\n💸 {escape_markdown_v2(str(total_expense))} ₽\n\n"
                # Список категорий с общей суммой
                for category, amount in category_expenses.items():
                    expense_message += f'📌 *{escape_markdown_v2(category)}*: {escape_markdown_v2(str(amount))}₽\n'

                # Формируем детальную таблицу
                if detailed_expenses:
                    headers = ["Дата", "Категория", "Описание", "Сумма"]
                    table_data = [
                        [
                            date.strftime("%d.%m.%Y"),  # Дата
                            category,                  # Категория
                            description,               # Описание
                            f"{amount:.2f}₽"           # Сумма без экранирования
                        ]
                        for date, category, description, amount in detailed_expenses
                    ]
                    # Формируем таблицу с улучшенным форматированием
                    table = tabulate(table_data, headers, tablefmt="grid")
                    expense_message += f"\n📋 *Детальная информация:*\n```\n{table}\n```"

                await message.answer(expense_message, parse_mode="MarkdownV2")

            else:
                await message.answer("❌ Неверный контекст.")
            # Очищаем контекст после обработки
            del user_context[user_id]
        else:
            await message.answer("❌ Пользователь не найден.")
    except ValueError:
        await message.answer("❌ Неверный формат даты. Пожалуйста, используйте формат ДД.ММ.ГГГГ ДД.ММ.ГГГГ.")

import logging
import calendar

from decimal import Decimal
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime
from aiogram import Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.orm import Session

from models.database import get_db
from models.income import Income
from models.categories import IncomeCategory
from models.user import User
from keyboards.keyboards import registered_main, get_income_categories_keyboard

logger = logging.getLogger(__name__)

class IncomeStates(StatesGroup):
    waiting_for_amount = State()           # Состояние для ввода суммы
    waiting_for_category = State()         # Состояние для выбора категории
    waiting_for_date = State()             # Состояние для ввода даты
    waiting_for_description = State()      # Состояние для ввода описания

router = Router()

# Клавиатура для выбора дня (inline)
def get_days_keyboard():
    today = datetime.today()
    current_month = today.month
    current_year = today.year
    days_in_month = calendar.monthrange(current_year, current_month)[1]  # Получаем количество дней в месяце
    days = [str(day) for day in range(1, days_in_month + 1)]

    # Группируем дни по три в каждой строке
    buttons = []
    row = []
    for day in days:
        row.append(InlineKeyboardButton(text=day, callback_data=f"day_{day}"))
        if len(row) == 3:  # После каждых трех кнопок добавляем строку
            buttons.append(row)
            row = []
    if row:  # Добавляем оставшиеся кнопки, если их меньше трех
        buttons.append(row)

    # Возвращаем клавиатуру с кнопками
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# ✅ 1. Начинаем процесс добавления дохода
@router.message(lambda message: message.text == "Добавить доход")
async def start_add_income(message: Message, state: FSMContext):
    await message.answer("Введите сумму дохода:")
    await state.set_state(IncomeStates.waiting_for_amount)

# ✅ 2. Пользователь вводит сумму дохода
@router.message(IncomeStates.waiting_for_amount)
async def process_income_amount(message: Message, state: FSMContext):
    """Сохраняем сумму дохода и предлагаем выбрать категорию"""
    try:
        amount = float(message.text)
        await state.update_data(amount=amount)

        db = next(get_db())  # Получаем сессию базы данных
        categories_keyboard = get_income_categories_keyboard(db)

        await message.answer("Выберите категорию дохода:", reply_markup=categories_keyboard)
        await state.set_state(IncomeStates.waiting_for_category)
    except ValueError:
        logger.error("Некорректная сумма дохода.")
        await message.answer("❌ Ошибка! Введите корректную сумму.")

# ✅ 3. Пользователь выбирает категорию из inline клавиатуры
@router.callback_query(lambda c: c.data.startswith('category_'))
async def process_income_category_callback(callback_query: CallbackQuery, state: FSMContext):
    """Сохраняем категорию и переходим к выбору даты"""
    try:
        db = next(get_db())  # Получаем сессию базы данных
        category_id = int(callback_query.data.split('_')[1])  # Извлекаем ID категории
        
        logger.info(f"Выбранный ID категории дохода: {category_id}")
        
        category = db.query(IncomeCategory).filter(IncomeCategory.id == category_id).first()

        if not category:
            logger.error(f"Категория с ID {category_id} не найдена.")
            await callback_query.message.answer("❌ Такая категория в доходах не найдена. Попробуйте снова.")
            return

        user = db.query(User).filter(User.tg_id == callback_query.from_user.id).first()
        if not user:
            logger.error("Пользователь не зарегистрирован.")
            await callback_query.message.answer("❌ Вы не зарегистрированы. Пройдите регистрацию.")
            return

        # Сохраняем категорию в состояние
        await state.update_data(category=category.name)
        await callback_query.message.answer(f"Вы выбрали категорию расхода: {category.name}")
        # Предлагаем выбрать день
        await callback_query.message.answer("Выберите день месяца или введите его вручную:", reply_markup=get_days_keyboard())
        await state.set_state(IncomeStates.waiting_for_date)

        # Удаляем сообщение о клавиатуре
        await callback_query.message.delete()
    except Exception as e:
        logger.error(f"Ошибка при выборе категории: {e}")
        await callback_query.message.answer("❌ Произошла ошибка. Попробуйте снова.")

# ✅ 4. Обработка выбора дня через inline клавиатуру
@router.callback_query(lambda c: c.data.startswith('day_'))
async def process_day_callback(callback_query: CallbackQuery, state: FSMContext):
    """Обрабатываем выбор дня через inline клавиатуру"""
    try:
        day = int(callback_query.data.split('_')[1])  # Извлекаем выбранный день
        today = datetime.today()
        
        # Формируем полную дату
        income_date = today.replace(day=day).date()
        
        # Сохраняем дату в состояние
        await state.update_data(date=income_date)

        # Удаляем клавиатуру с датами
        await callback_query.message.edit_reply_markup(reply_markup=None)

        # Подтверждение выбора дня
        await callback_query.message.answer(f"Вы выбрали {day} число.")

        # Переходим к вводу описания
        await callback_query.message.answer("Введите описание дохода (например, 'Зарплата за январь'):")
        await state.set_state(IncomeStates.waiting_for_description)
    except Exception as e:
        logger.error(f"Ошибка при выборе дня: {e}")
        await callback_query.message.answer("❌ Произошла ошибка. Попробуйте снова.")

# ✅ 5. Ввод даты вручную
@router.message(IncomeStates.waiting_for_date)
async def process_manual_date_input(message: Message, state: FSMContext):
    """Обрабатываем ввод даты вручную"""
    try:
        # Преобразуем введенную дату в объект datetime
        income_date = datetime.strptime(message.text, "%d.%m.%Y").date()

        # Проверка, что дата входит в текущий месяц
        today = datetime.today()
        if income_date.month != today.month or income_date.year != today.year:
            await message.answer("❌ Дата должна быть в текущем месяце. Пожалуйста, введите правильную дату.")
            return

        await state.update_data(date=income_date)

        # Переходим к вводу описания
        await message.answer("Введите описание дохода (например, 'Зарплата за январь'):")
        await state.set_state(IncomeStates.waiting_for_description)
    except ValueError:
        logger.error("Ошибка при вводе даты.")
        await message.answer("❌ Ошибка! Введите дату в формате ДД.ММ.ГГГГ.")

# ✅ 6. Ввод описания
@router.message(IncomeStates.waiting_for_description)
async def process_income_description(message: Message, state: FSMContext):
    """Сохраняем описание и добавляем доход в базу"""
    try:
        description = message.text
        await state.update_data(description=description)

        data = await state.get_data()
        amount = data.get("amount")
        category_name = data.get("category")
        income_date = data.get("date", datetime.today().date())

        if not amount or not category_name:
            logger.error("Отсутствуют данные о сумме или категории.")
            await message.answer("❌ Ошибка! Не удалось получить данные о доходе. Попробуйте снова.")
            await state.clear()
            return

        db = next(get_db())
        category = db.query(IncomeCategory).filter(IncomeCategory.name == category_name).first()
        if not category:
            logger.error(f"Категория с именем {category_name} не найдена.")
            await message.answer("❌ Ошибка. Категория не найдена.")
            return

        user = db.query(User).filter(User.tg_id == message.from_user.id).first()
        if not user:
            logger.error("Пользователь не зарегистрирован.")
            await message.answer("❌ Вы не зарегистрированы. Пройдите регистрацию.")
            return

        # Создаём запись в таблице доходов
        new_income = Income(
            user_id=user.id,
            category_id=category.id,
            amount=amount,
            date=income_date,
            description=description
        )

        db.add(new_income)
        user.balance += Decimal(amount)
        db.commit()

        logger.info(f"Добавлен доход: {amount} ₽, {category.name}, {income_date}, {description}")
        await message.answer(f"✅ Доход {amount} ₽ добавлен в категорию {category.name}! Дата: {income_date}, Описание: {description}")

        # Очищаем состояние FSM
        await state.clear()

        # Отправляем клавиатуру с основным меню
        await message.answer("Вы успешно добавили доход! Выберите следующее действие:", reply_markup=registered_main)
    except Exception as e:
        logger.error(f"Ошибка при добавлении дохода: {e}")
        await message.answer("❌ Произошла ошибка при добавлении дохода. Попробуйте снова.")

# Обработчик для кнопки "Назад" (если нужно реализовать логику возврата)
@router.callback_query(lambda c: c.data == "back")
async def back_to_main_menu(callback_query: CallbackQuery):
    """Возвращаемся к главному меню"""
    await callback_query.message.answer("Вы вернулись в главное меню.", reply_markup=registered_main)
    await callback_query.message.delete()
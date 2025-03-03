import logging
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
from keyboards.keyboards import registered_main


class IncomeStates(StatesGroup):
    waiting_for_amount = State()           # Состояние для ввода суммы
    waiting_for_category = State()         # Состояние для выбора категории
    waiting_for_date = State()             # Состояние для ввода даты
    waiting_for_description = State()     # Состояние для ввода описания


router = Router()


# Клавиатура для выбора категории дохода (inline)
def get_income_categories_keyboard(db: Session):
    categories = db.query(IncomeCategory).all()
    buttons = [
        [InlineKeyboardButton(text=category.name, callback_data=f"category_{category.id}")]
        for category in categories
    ]
    buttons.append([InlineKeyboardButton(text="⬅ Назад", callback_data="back")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ✅ 1. Начинаем процесс добавления дохода
@router.message(lambda message: message.text == "Добавить доход")
async def start_add_income(message: Message, state: FSMContext):
    """Запрашивает сумму дохода"""
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
        await message.answer("❌ Ошибка! Введите корректную сумму.")


# ✅ 3. Пользователь выбирает категорию из inline клавиатуры
@router.callback_query(lambda c: c.data.startswith('category_'))
async def process_income_category_callback(callback_query: CallbackQuery, state: FSMContext):
    """Сохраняем категорию и переходим к выбору даты"""
    db = next(get_db())  # Получаем сессию базы данных
    category_id = int(callback_query.data.split('_')[1])  # Извлекаем ID категории
    category = db.query(IncomeCategory).filter(IncomeCategory.id == category_id).first()

    if not category:
        await callback_query.message.answer("❌ Такая категория не найдена. Попробуйте снова.")
        return

    user = db.query(User).filter(User.tg_id == callback_query.from_user.id).first()
    if not user:
        await callback_query.message.answer("❌ Вы не зарегистрированы. Пройдите регистрацию.")
        return

    # Извлекаем данные из состояния
    data = await state.get_data()
    amount = data["amount"]

    # Сохраняем категорию в состояние
    await state.update_data(category=category.name)

    # Переход к вводу даты
    await callback_query.message.answer("Введите дату дохода в формате ДД.ММ.ГГГГ (например, 25.03.2025):")
    await state.set_state(IncomeStates.waiting_for_date)

    # Удаляем сообщение о клавиатуре
    await callback_query.message.delete()



# ✅ 4. Ввод даты
@router.message(IncomeStates.waiting_for_date)
async def process_income_date(message: Message, state: FSMContext):
    """Сохраняем дату и предлагаем ввести описание"""
    try:
        # Попробуем преобразовать строку в дату
        income_date = datetime.strptime(message.text, "%d.%m.%Y").date()

        # Проверка, что дата входит в текущий месяц
        today = datetime.today()
        if income_date.month != today.month or income_date.year != today.year:
            await message.answer("❌ Дата должна быть в текущем месяце. Пожалуйста, введите правильную дату.")
            return

        await state.update_data(date=income_date)

        # Переход к вводу описания
        await message.answer("Введите описание дохода (например, 'Зарплата за январь'):")
        await state.set_state(IncomeStates.waiting_for_description)
    except ValueError:
        await message.answer("❌ Ошибка! Введите дату в формате ДД.ММ.ГГГГ.")


# ✅ 5. Ввод описания
@router.message(IncomeStates.waiting_for_description)
async def process_income_description(message: Message, state: FSMContext):
    """Сохраняем описание и добавляем доход в базу"""
    description = message.text
    await state.update_data(description=description)

    data = await state.get_data()
    amount = data["amount"]
    category_name = data["category"]  # Теперь категорию можно извлечь
    income_date = data["date"]

    # Получаем категорию по имени
    db = next(get_db())
    category = db.query(IncomeCategory).filter(IncomeCategory.name == category_name).first()
    if not category:
        await message.answer("❌ Ошибка. Категория не найдена.")
        return

    # Получаем пользователя из базы данных
    user = db.query(User).filter(User.tg_id == message.from_user.id).first()

    if not user:
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

    await message.answer(f"✅ Доход {amount} ₽ добавлен в категорию {category.name}! Дата: {income_date}, Описание: {description}")

    # Очищаем состояние FSM
    await state.clear()

    # Отправляем клавиатуру с основным меню
    await message.answer("Вы успешно добавили доход! Выберите следующее действие:", reply_markup=registered_main)


# Обработчик для кнопки "Назад" (если нужно реализовать логику возврата)
@router.callback_query(lambda c: c.data == "back")
async def back_to_main_menu(callback_query: CallbackQuery):
    """Возвращаемся к главному меню"""
    await callback_query.message.answer("Вы вернулись в главное меню.", reply_markup=registered_main)
    await callback_query.message.delete()

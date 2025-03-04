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
from models.expense import Expense
from models.categories import ExpenseCategory
from models.user import User
from keyboards.keyboards import registered_main, get_expense_categories_keyboard

logger = logging.getLogger(__name__)


class ExpenseStates(StatesGroup):
    waiting_for_amount = State()
    waiting_for_category = State()
    waiting_for_date = State()
    waiting_for_description = State()

router = Router()


def get_days_keyboard():
    today = datetime.today()
    current_month = today.month
    current_year = today.year
    days_in_month = calendar.monthrange(current_year, current_month)[1]
    days = [str(day) for day in range(1, days_in_month + 1)]

    buttons = []
    row = []
    for day in days:
        row.append(InlineKeyboardButton(text=day, callback_data=f"expense_day_{day}"))
        if len(row) == 3:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@router.message(lambda message: message.text == "Добавить расход")
async def start_add_expense(message: Message, state: FSMContext):
    await message.answer("Введите сумму расхода:")
    await state.set_state(ExpenseStates.waiting_for_amount)


@router.message(ExpenseStates.waiting_for_amount)
async def process_expense_amount(message: Message, state: FSMContext):
    try:
        amount = float(message.text)
        await state.update_data(amount=amount)

        db = next(get_db())
        categories_keyboard = get_expense_categories_keyboard(db)
        await message.answer("Выберите категорию расхода:", reply_markup=categories_keyboard)
        await state.set_state(ExpenseStates.waiting_for_category)
    except ValueError:
        logger.error("Некорректная сумма расхода.")
        await message.answer("❌ Ошибка! Введите корректную сумму.")


@router.callback_query(lambda c: c.data.startswith('expense_category_'))
async def process_expense_category_callback(callback_query: CallbackQuery, state: FSMContext):
    db = next(get_db())
    category_data = callback_query.data.split('_')[2]

    if not category_data.isdigit():
        logger.error(f"Некорректный ID категории: {category_data}")
        await callback_query.answer("❌ Ошибка! Попробуйте снова.")
        return

    category_id = int(category_data)
    category = db.query(ExpenseCategory).filter(ExpenseCategory.id == category_id).first()

    if not category:
        logger.error(f"Категория расхода с ID {category_id} не найдена.")
        await callback_query.answer("❌ Категория расхода не найдена. Попробуйте снова.")
        return
    
    user = db.query(User).filter(User.tg_id == callback_query.from_user.id).first()
    if not user:
        logger.error("Пользователь не зарегистрирован.")
        await callback_query.message.answer("❌ Вы не зарегистрированы. Пройдите регистрацию.")
        return

    await state.update_data(category_id=category.id)
    await callback_query.message.answer(f"Вы выбрали категорию расхода: {category.name}")
    await callback_query.message.answer("Выберите день месяца или введите его вручную:", reply_markup=get_days_keyboard())
    await state.set_state(ExpenseStates.waiting_for_date)


@router.callback_query(lambda c: c.data.startswith('expense_day_'))
async def process_day_callback(callback_query: CallbackQuery, state: FSMContext):
    try:
        day = int(callback_query.data.split('_')[2])
        today = datetime.today()
        expense_date = today.replace(day=day).date()

        await state.update_data(date=expense_date)
        await callback_query.message.edit_reply_markup(reply_markup=None)
        await callback_query.message.answer(f"Вы выбрали {day} число.")
        await callback_query.message.answer("Введите описание расхода (например, 'Оплата магазина'):")
        await state.set_state(ExpenseStates.waiting_for_description)
    except ValueError as e:
        logger.error(f"Ошибка при выборе дня: {e}")
        await callback_query.answer("❌ Некорректный день для текущего месяца.")


@router.message(ExpenseStates.waiting_for_date)
async def process_manual_date_input(message: Message, state: FSMContext):
    try:
        expense_date = datetime.strptime(message.text, "%d.%m.%Y").date()
        today = datetime.today()

        if expense_date.month != today.month or expense_date.year != today.year:
            await message.answer("❌ Дата должна быть в текущем месяце. Пожалуйста, введите правильную дату.")
            return

        await state.update_data(date=expense_date)
        await message.answer("Введите описание расхода (например, покупка еды):")
        await state.set_state(ExpenseStates.waiting_for_description)
    except ValueError:
        logger.error("Ошибка при вводе даты.")
        await message.answer("❌ Ошибка! Введите дату в формате ДД.ММ.ГГГГ.")


@router.message(ExpenseStates.waiting_for_description)
async def process_expense_description(message: Message, state: FSMContext):
    try:
        description = message.text
        await state.update_data(description=description)

        data = await state.get_data()
        amount = data.get("amount")
        category_id = data.get("category_id")
        expense_date = data.get("date", datetime.today().date())

        if not amount or not category_id:
            logger.error("Отсутствуют данные о сумме или категории.")
            await message.answer("❌ Ошибка! Не удалось получить данные о расходе. Попробуйте снова.")
            await state.clear()
            return

        db = next(get_db())
        category = db.query(ExpenseCategory).filter(ExpenseCategory.id == category_id).first()

        if not category:
            logger.error(f"Категория с ID {category_id} не найдена.")
            await message.answer("❌ Ошибка. Категория не найдена.")
            return

        user = db.query(User).filter(User.tg_id == message.from_user.id).first()
        if not user:
            logger.error("Пользователь не зарегистрирован.")
            await message.answer("❌ Вы не зарегистрированы.")
            return

        new_expense = Expense(user_id=user.id, category_id=category.id, amount=amount, date=expense_date, description=description)
        db.add(new_expense)
        user.balance -= Decimal(amount)
        db.commit()

        logger.info(f"Добавлен расход: {amount} ₽, {category.name}, {expense_date}, {description}")
        await message.answer(f"✅ Расход {amount} ₽ добавлен! Категория: {category.name}, Дата: {expense_date}")
        await state.clear()
        await message.answer("Выберите следующее действие:", reply_markup=registered_main)
    except Exception as e:
        logger.error(f"Ошибка при добавлении расхода: {e}")
        await message.answer("❌ Произошла ошибка при добавлении расхода. Попробуйте снова.")


@router.callback_query(lambda c: c.data == "back")
async def back_to_main_menu(callback_query: CallbackQuery):
    await callback_query.message.answer("Вы вернулись в главное меню.", reply_markup=registered_main)
    await callback_query.message.delete()
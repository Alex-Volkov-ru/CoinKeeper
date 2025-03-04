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
from models.categories import ExpenseCategory  # Это для категорий расходов
from models.user import User
from keyboards.keyboards import registered_main, get_expense_categories_keyboard

logger = logging.getLogger(__name__)

class ExpenseStates(StatesGroup):
    waiting_for_amount = State()  # Ожидание ввода суммы
    waiting_for_category = State()  # Ожидание выбора категории
    waiting_for_date = State()  # Ожидание даты
    waiting_for_description = State()  # Ожидание описания

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
        row.append(InlineKeyboardButton(text=day, callback_data=f"expense_day_{day}"))
        if len(row) == 3:  # После каждых трех кнопок добавляем строку
            buttons.append(row)
            row = []
    if row:  # Добавляем оставшиеся кнопки, если их меньше трех
        buttons.append(row)
    # Возвращаем клавиатуру с кнопками
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# Начало процесса добавления расхода
@router.message(lambda message: message.text == "Добавить расход")
async def start_add_expense(message: Message, state: FSMContext):
    await message.answer("Введите сумму расхода:")
    await state.set_state(ExpenseStates.waiting_for_amount)

# Обработка введённой суммы
@router.message(ExpenseStates.waiting_for_amount)
async def process_expense_amount(message: Message, state: FSMContext):
    try:
        amount = float(message.text)
        await state.update_data(amount=amount)

        db = next(get_db())
        categories_keyboard = get_expense_categories_keyboard(db)
        await message.answer("Выберите категорию расхода:", reply_markup=categories_keyboard)
        
        # Обновляем состояние для ожидания выбора категории
        await state.set_state(ExpenseStates.waiting_for_category)
    except ValueError:
        await message.answer("❌ Ошибка! Введите корректную сумму.")

# Обработка выбора категории расхода
@router.callback_query(lambda c: c.data.startswith('expense_category_'))
async def process_expense_category_callback(callback_query: CallbackQuery, state: FSMContext):
    db = next(get_db())
    category_data = callback_query.data.split('_')[2]  # Теперь берем второй элемент после 'expense_category'

    # Проверка, что category_data — это цифра
    if not category_data.isdigit():
        logger.error(f"Некорректный ID категории: {category_data}")
        await callback_query.answer("❌ Ошибка! Попробуйте снова.")
        return

    category_id = int(category_data)  # Преобразуем в число

    logger.info(f"Выбранный ID категории расхода: {category_id}")

    category = db.query(ExpenseCategory).filter(ExpenseCategory.id == category_id).first()

    if not category:
        logger.error(f"Категория расхода с ID {category_id} не найдена.")
        await callback_query.answer("❌ Категория расхода не найдена. Попробуйте снова.")
        return
    
    user = db.query(User).filter(User.tg_id == callback_query.from_user.id).first()
    if not user:
        await callback_query.message.answer("❌ Вы не зарегистрированы. Пройдите регистрацию.")
        return

    await state.update_data(category_id=category.id)
    await callback_query.message.answer(f"Вы выбрали категорию расхода: {category.name}")
    await callback_query.message.answer("Выберите день месяца или введите его вручную:", reply_markup=get_days_keyboard())
    await state.set_state(ExpenseStates.waiting_for_date)

# ✅ 4. Обработка выбора дня через inline клавиатуру
@router.callback_query(lambda c: c.data.startswith('expense_day_'))
async def process_day_callback(callback_query: CallbackQuery, state: FSMContext):
    """Обрабатываем выбор дня через inline клавиатуру"""
    day = int(callback_query.data.split('_')[2])  # Извлекаем выбранный день
    today = datetime.today()
    
    # Проверяем, является ли день допустимым для текущего месяца
    try:
        expense_date = today.replace(day=day).date()
    except ValueError:
        await callback_query.answer("❌ Некорректный день для текущего месяца.")
        return

    # Сохраняем дату в состояние
    await state.update_data(date=expense_date)

    # Удаляем клавиатуру с датами
    await callback_query.message.edit_reply_markup(reply_markup=None)

    # Подтверждение выбора дня
    await callback_query.message.answer(f"Вы выбрали {day} число.")

    # Переходим к вводу описания
    await callback_query.message.answer("Введите описание Расхода: (например, 'Оплата магазина'):")
    await state.set_state(ExpenseStates.waiting_for_description)

# Обработка ввода даты вручную
@router.message(ExpenseStates.waiting_for_date)
async def process_manual_date_input(message: Message, state: FSMContext):
    """Обрабатываем ввод даты вручную"""
    try:
        # Преобразуем введенную дату в объект datetime
        expense_date = datetime.strptime(message.text, "%d.%m.%Y").date()

        # Проверка, что дата входит в текущий месяц
        today = datetime.today()
        if expense_date.month != today.month or expense_date.year != today.year:
            await message.answer("❌ Дата должна быть в текущем месяце. Пожалуйста, введите правильную дату.")
            return

        await state.update_data(date=expense_date)

        # Переходим к вводу описания
        await message.answer("Введите описание расхода (например, покупка еды):")
        await state.set_state(ExpenseStates.waiting_for_description)

    except ValueError:
        await message.answer("❌ Ошибка! Введите дату в формате ДД.ММ.ГГГГ.")


# Обработка ввода описания расхода
@router.message(ExpenseStates.waiting_for_description)
async def process_expense_description(message: Message, state: FSMContext):
    """Сохраняем описание и добавляем расход в базу"""
    description = message.text
    await state.update_data(description=description)

    data = await state.get_data()
    amount = data["amount"]
    category_id = data["category_id"]
    expense_date = data.get("date", datetime.today().date())

    db = next(get_db())
    category = db.query(ExpenseCategory).filter(ExpenseCategory.id == category_id).first()
    
    # Логируем категорию перед добавлением
    logger.info(f"Категория для расхода: {category}, ID: {category_id}")

    if not category:
        await message.answer("❌ Ошибка. Категория не найдена.")
        return

    user = db.query(User).filter(User.tg_id == message.from_user.id).first()
    if not user:
        await message.answer("❌ Вы не зарегистрированы.")
        return

    # Создание расхода
    new_expense = Expense(user_id=user.id, category_id=category.id, amount=amount, date=expense_date, description=description)
    db.add(new_expense)
    user.balance -= Decimal(amount)  # Убедитесь, что здесь вычитаем сумму
    db.commit()

    logger.info(f"Добавлен расход: {amount} ₽, {category.name}, {expense_date}, {description}")

    await message.answer(f"✅ Расход {amount} ₽ добавлен! Категория: {category.name}, Дата: {expense_date}")
    await state.clear()
    await message.answer("Выберите следующее действие:", reply_markup=registered_main)

# Обработка кнопки "Назад" для возврата в главное меню
@router.callback_query(lambda c: c.data == "back")
async def back_to_main_menu(callback_query: CallbackQuery):
    await callback_query.message.answer("Вы вернулись в главное меню.", reply_markup=registered_main)
    await callback_query.message.delete()

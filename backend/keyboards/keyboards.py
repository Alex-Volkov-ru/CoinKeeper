from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy.orm import Session
from models.categories import IncomeCategory, ExpenseCategory


# Основная клавиатура для неавторизованных пользователей
main = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Профиль')],
        [KeyboardButton(text='Регистрация')],
        [KeyboardButton(text='О нас')],
    ],
    resize_keyboard=True
)

# Основная клавиатура для авторизованных пользователей
registered_main = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Профиль')],
        [KeyboardButton(text='Статистика')],
        [KeyboardButton(text='Добавить транзакцию')],
        [KeyboardButton(text='О нас')],
    ],
    resize_keyboard=True
)

# Клавиатура для выбора типа транзакции (доход или расход)
transaction_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Добавить доход')],  # Обработчик для дохода
        [KeyboardButton(text='Добавить расход')],  # Обработчик для расхода
        [KeyboardButton(text='⬅ Назад')]
    ],
    resize_keyboard=True
)

def get_income_categories_keyboard(db: Session):
    """
    Создает клавиатуру с категориями доходов.

    :param db: Сессия базы данных.
    :return: InlineKeyboardMarkup с кнопками категорий доходов.
    """
    categories = db.query(IncomeCategory).all()
    buttons = [[InlineKeyboardButton(text=category.name, callback_data=f"category_{category.id}")] for category in categories]
    buttons.append([InlineKeyboardButton(text="⬅ Назад", callback_data="back")])
    buttons.append([InlineKeyboardButton(text="❌ Отмена", callback_data="back")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_expense_categories_keyboard(db):
    """
    Создает клавиатуру с категориями расходов.

    :param db: Сессия базы данных.
    :return: InlineKeyboardMarkup с кнопками категорий расходов.
    """
    categories = db.query(ExpenseCategory).all()

    buttons = [
        [InlineKeyboardButton(text=category.name, callback_data=f"expense_category_{category.id}")]
        for category in categories
    ]
    buttons.append([InlineKeyboardButton(text="⬅ Назад", callback_data="back")])
    buttons.append([InlineKeyboardButton(text="❌ Отмена", callback_data="back")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton)

from sqlalchemy.orm import Session
from models.categories import IncomeCategory

# Клавиатура для не зарегистрированных пользователей
main = ReplyKeyboardMarkup(
    keyboard=[ 
        [KeyboardButton(text='Профиль')],
        [KeyboardButton(text='Регистрация')],
        [KeyboardButton(text='О нас')],
    ],
    resize_keyboard=True,
    input_field_placeholder='Выберите пункт меню...'
)

# Клавиатура для зарегистрированных пользователей
registered_main = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Профиль')],
        [KeyboardButton(text='Статистика')],
        [KeyboardButton(text='Добавить транзакцию')],
        [KeyboardButton(text='О нас')],
    ],
    resize_keyboard=True,
    input_field_placeholder='Выберите пункт меню...'
)

# Клавиатура для добавления транзакции
transaction_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Добавить доход')],
        [KeyboardButton(text='Добавить расход')],
        [KeyboardButton(text='⬅ Назад')]
    ],
    resize_keyboard=True,
    input_field_placeholder='Выберите действие...'
)

# Клавиатура для выбора категории дохода
def get_income_categories_keyboard(db: Session):
    categories = db.query(IncomeCategory).all()
    buttons = [
        [InlineKeyboardButton(text=category.name, callback_data=f"category_{category.id}")]
        for category in categories
    ]
    buttons.append([InlineKeyboardButton(text="⬅ Назад", callback_data="back")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


main = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Профиль')],
        [KeyboardButton(text='Регистрация')],
        [KeyboardButton(text='О нас')],
    ],
    resize_keyboard=True,
    input_field_placeholder='Выберите пункт меню...'
)

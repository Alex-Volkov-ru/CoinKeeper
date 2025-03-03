from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

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
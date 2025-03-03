import logging

from aiogram import Router
from aiogram.types import Message

from aiogram import Bot
from aiogram.fsm.context import FSMContext

from models.database import get_db
from models.user import User
from keyboards.keyboards import main, registered_main, transaction_menu
from handlers.register import RegistrationStates


router = Router()

@router.message(lambda message: message.text == "О нас")  # Используем lambda-фильтр для проверки текста
async def about_handler(message: Message):
    """Обработчик кнопки 'О нас' с логированием ошибок"""
    try:
        text = (
            "📌 *CoinkeeperBot* — ваш персональный помощник в управлении финансами! 💰\n\n"
            "Мы создали этого бота, чтобы упростить ведение бюджета, отслеживать расходы "
            "и планировать доходы прямо в *Telegram*. Больше не нужно заполнять сложные таблицы "
            "или использовать громоздкие приложения — просто добавляйте транзакции в пару кликов! 📊\n\n"
            "🔹 *Что умеет CoinkeeperBot?*\n"
            "✅ Записывать доходы и расходы в удобном формате.\n"
            "✅ Показывать статистику по тратам и доходам.\n"
            "✅ Помогать анализировать финансовые привычки.\n\n"
            "📈 Управляйте своими финансами *легко и без лишних усилий*! 🚀"
        )
        
        await message.answer(text, parse_mode="Markdown")
    
    except Exception as e:
        logging.error(f"Ошибка в about_handler: {str(e)}", exc_info=True)  
        await message.answer("❌ Произошла ошибка. Пожалуйста, попробуйте позже.")


# Обработчик нажатия на кнопку "Регистрация"
@router.message(lambda message: message.text == "Регистрация")  # Фильтр для кнопки
async def start_register(message: Message, state: FSMContext, bot: Bot):
    db = next(get_db())

    # Проверяем, есть ли пользователь с таким tg_id
    user = db.query(User).filter(User.tg_id == message.from_user.id).first()

    if user:
        # Если пользователь уже существует, сообщаем об этом
        await bot.send_message(message.from_user.id, f'{user.name}, Вы уже зарегистрированы!')
    else:
        # Если пользователя нет, начинаем процесс регистрации
        await bot.send_message(message.from_user.id, 'Давайте начнем регистрацию \nДля начала скажите, как к Вам обращаться?')
        await state.set_state(RegistrationStates.waiting_for_name)


@router.message(lambda message: message.text == "Профиль")
async def profile_handler(message: Message, bot: Bot):
    db = next(get_db())

    # Проверяем, зарегистрирован ли пользователь
    user = db.query(User).filter(User.tg_id == message.from_user.id).first()

    if user:
        # Создаем красивый профиль
        profile_text = (
            f"👤 *Ваш профиль*\n\n"
            f"📛 *Имя:* {user.name}\n"
            f"📞 *Телефон:* `{user.contact}`\n"
            f"👛 *Баланс:*  `{user.balance} рублей`\n"
        )

        # Отправляем профиль с новой клавиатурой
        await bot.send_message(
            message.from_user.id, 
            profile_text, 
            parse_mode="Markdown", 
            reply_markup=registered_main
        )
    else:
        # Если не зарегистрирован, отправляем старую клавиатуру
        await bot.send_message(
            message.from_user.id, 
            "❌ Вы не зарегистрированы! Нажмите 'Регистрация'.", 
            reply_markup=main
        )

@router.message(lambda message: message.text == "Добавить транзакцию")
async def add_transaction_handler(message: Message, bot: Bot):
    """Обработчик нажатия на 'Добавить транзакцию'"""
    text = "Выберите тип транзакции:"
    await bot.send_message(
        message.from_user.id, 
        text, 
        reply_markup=transaction_menu
    )

# Обработчик кнопки "⬅ Назад"
@router.message(lambda message: message.text == "⬅ Назад")
async def back_to_main_menu(message: Message, bot: Bot):
    """Возвращает пользователя в главное меню"""
    await bot.send_message(
        message.from_user.id, 
        "Вы вернулись в главное меню", 
        reply_markup=registered_main
    )
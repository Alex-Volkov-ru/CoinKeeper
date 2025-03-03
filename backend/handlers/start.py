import logging

from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.exceptions import AiogramError

from utils.exceptions import HomeworkBotError
from keyboards.keyboards import registered_main as kb

router = Router()

@router.message(CommandStart())
async def command_handler(message: Message) -> None:
    """
    Обработка базовой команды /start
    """
    try:
        if not message.from_user:
            raise HomeworkBotError("Пользователь не найден.")

        await message.answer(
            f"Привет, {message.from_user.full_name}!",
            reply_markup=kb
        )
    except HomeworkBotError as e:
        await message.answer(f"Ошибка: {str(e)}")
    except Exception:
        await message.answer(
            "Что-то пошло не так. Пожалуйста, попробуйте позже.")
        raise


@router.message(Command("help"))
async def help_handler(message: Message) -> None:
    """
    Обработка команды /help
    """
    try:
        help_text = (
            "❓ *Помощь по боту*\n\n"
            "Я помогу вам управлять вашими финансами! Вот несколько команд, которые могут вам пригодиться:\n\n"
            "/start - Запуск бота\n"
            "/register - Регистрация в приложении\n"
            "/contact - Наши контактные данные\n"
            "/profile - Ваш профиль - имя и номер телефона\n\n"
        )
        await message.answer(help_text, reply_markup=kb)

    except Exception as e:
        logging.error(f"Ошибка в help_handler: {str(e)}", exc_info=True)
        await message.answer("❌ Произошла ошибка. Пожалуйста, попробуйте позже.")


@router.message(Command("contact"))
async def contact_handler(message: Message) -> None:
    """
    Обработка команды /contact
    """
    try:
        contact_text = (
            "📞 *Наши контактные данные:*\n\n"
            "📧 Email: support@coinkeeper.com\n"
            "💬 Поддержка: @ximikat01\n\n"
            "Если у вас возникли вопросы или проблемы, не стесняйтесь обращаться!"
        )
        await message.answer(contact_text, reply_markup=kb)

    except Exception as e:
        logging.error(f"Ошибка в contact_handler: {str(e)}", exc_info=True)
        await message.answer("❌ Произошла ошибка. Пожалуйста, попробуйте позже.")


@router.errors()
async def error_handler(event: AiogramError):
    """
    Глобальный обработчик исключений для всех ошибок.
    """
    # Логируем ошибку
    logging.error(f"Ошибка: {str(event)}")

    # Если это кастомное исключение, можно добавить дополнительную логику
    if isinstance(event, HomeworkBotError):
        logging.error(f"Кастомная ошибка: {str(event)}")

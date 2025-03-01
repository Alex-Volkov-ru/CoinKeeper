import logging

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.exceptions import AiogramError

from utils.exceptions import HomeworkBotError
from keyboards.keyboards import main as kb

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

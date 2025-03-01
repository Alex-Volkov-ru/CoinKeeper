import asyncio
import logging
import os

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message


from utils.commands import set_commands

# Загружаем переменные окружения
load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_ADMIN_ID = os.getenv('TELEGRAM_ADMIN_ID')
dp = Dispatcher()


class HomeworkBotError(Exception):
    """Базовый класс ошибок бота."""


class APIResponseError(HomeworkBotError):
    """Ошибка при запросе к API."""


def check_tokens():
    """Проверяет наличие всех необходимых токенов."""
    missing_tokens = [
        token for token, value in {
            'TELEGRAM_TOKEN': TELEGRAM_TOKEN,
        }.items() if not value
    ]
    if missing_tokens:
        logging.critical(f'Отсутствуют токены: {", ".join(missing_tokens)}')
        return False
    return True


@dp.message(CommandStart())
async def command_handler(message: Message) -> None:
    """
    Обработка базовой команды /start
    """
    await message.answer(f"Привет, {message.from_user.full_name}!")


async def start_bot(bot: Bot):
    """Функция, которая отправляет уведомление о старте бота."""
    try:
        await bot.send_message(
            TELEGRAM_ADMIN_ID,
            text='Бот запущен'
        )
    except HomeworkBotError as e:
        logging.error(f"Ошибка бота: {str(e)}")

dp.startup.register(start_bot)


async def main() -> None:
    """
    Основная асинхронная функция для запуска бота.

    Создает экземпляр бота, указывает токен и параметры и запускает
    процесс обработки событий с использованием start_polling.
    """
    if not check_tokens():
        exit()

    bot = Bot(
        token=TELEGRAM_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    await set_commands(bot)
    await dp.start_polling(bot)


if __name__ == '__main__':
    """
    Главная точка входа в программу. Настроена логгировка, создается
    основная асинхронная задача для запуска бота.
    """
    try:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler("coin_keeper_bot.log", encoding="utf-8")
            ]
        )
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот отключен")
    except HomeworkBotError as e:
        logging.error(f"Произошла ошибка бота: {str(e)}")
    except Exception as e:
        logging.error(f"Неизвестная ошибка: {str(e)}")

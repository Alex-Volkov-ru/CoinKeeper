import asyncio
import logging
import os

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

# Загружаем переменные окружения
load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
dp = Dispatcher()


class HomeworkBotError(Exception):
    """Базовый класс ошибок бота."""


class APIResponseError(HomeworkBotError):
    """Ошибка при запросе к API."""


async def main() -> None:
    """
    Основная асинхронная функция для запуска бота.

    Создает экземпляр бота, указывает токен и параметры и запускает
    процесс обработки событий с использованием start_polling.
    """
    bot = Bot(
        token=TELEGRAM_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == '__main__':
    """
    Главная точка входа в программу. Настроена логгировка, создается
    основная асинхронная задача для запуска бота.
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("coin_keeper_bot.log", encoding="utf-8")
        ]
    )
    asyncio.run(main())

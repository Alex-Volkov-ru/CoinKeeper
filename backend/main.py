import asyncio
import logging
import os

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from utils.commands import set_commands
from handlers.start import router as start_router
from handlers.register import router as register_router
from handlers.income import router as income_router
from handlers.expense import router as expense_router
from handlers.operations import router as operations_router
from utils.exceptions import HomeworkBotError
from models.init_db import init_db
from handlers.menu import router as menu_router

# Загружаем переменные окружения
load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_ADMIN_ID = os.getenv('TELEGRAM_ADMIN_ID')

dp = Dispatcher()
dp.include_router(start_router)
dp.include_router(register_router)
dp.include_router(menu_router)
dp.include_router(income_router)
dp.include_router(expense_router)
dp.include_router(operations_router)

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
    """
    if not check_tokens():
        exit()

    init_db()
    bot = Bot(
        token=TELEGRAM_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    await set_commands(bot)
    await dp.start_polling(bot)

if __name__ == '__main__':
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

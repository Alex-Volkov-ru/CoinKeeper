from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault


async def set_commands(bot: Bot) -> None:
    """
    Устанавливает команды бота, доступные пользователю в интерфейсе Telegram.

    Команды:
    - /start: Запуск бота.
    - /registration: Регистрация в приложении.
    - /help: Помощь по работе с ботом.
    - /contact: Контактная информация.
    """
    commands = [
        BotCommand(
            command='start',
            description='Запускаем Бота'
        ),
        BotCommand(
            command='registration',
            description='Регистрация в приложении'
        ),
        BotCommand(
            command='help',
            description='Помощь в работе с ботом'
        ),
        BotCommand(
            command='contact',
            description='Наши контакты'
        ),
    ]

    await bot.set_my_commands(commands, BotCommandScopeDefault())

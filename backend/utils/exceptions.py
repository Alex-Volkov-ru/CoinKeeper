class HomeworkBotError(Exception):
    """Базовый класс ошибок бота."""


class APIResponseError(HomeworkBotError):
    """Ошибка при запросе к API."""

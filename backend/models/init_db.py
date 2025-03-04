from models.database import engine
from sqlalchemy import inspect

from models.user import User
from models.income import Income
from models.expense import Expense
from models.categories import IncomeCategory, ExpenseCategory


def check_tables():
    """
    Проверяет наличие таблиц в базе данных.

    Выводит список всех таблиц в базе данных.
    """
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"Таблицы в базе данных: {tables}")


# Создаем все таблицы в базе данных
def init_db():
    """
    Инициализирует базу данных, создавая все таблицы, определенные в моделях.
    """
    from models.database import Base
    Base.metadata.create_all(bind=engine)

from models.database import engine
from sqlalchemy import inspect

from models.user import User
from models.income import Income
from models.expense import Expense
from models.categories import IncomeCategory, ExpenseCategory


def check_tables():
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"Таблицы в базе данных: {tables}")


# Создаем все таблицы в базе данных
def init_db():
    from models.database import Base
    Base.metadata.create_all(bind=engine)

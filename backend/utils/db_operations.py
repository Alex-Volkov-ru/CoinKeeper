# from models.database import get_db
from sqlalchemy.orm import Session
from datetime import datetime
from sqlalchemy import func

# from models.user import User
from models.income import Income
from models.expense import Expense


# Получить баланс пользователя
def get_balance(user_id: int, db: Session):
    result = db.query(
        (db.query(
            Income.amount).filter(Income.user_id == user_id).all() or 0) -
        (db.query(
            Expense.amount).filter(Expense.user_id == user_id).all() or 0)
    ).scalar()

    return result


# Получить доходы за день
def get_daily_income(user_id: int, db: Session):
    today = datetime.today().date()
    return db.query(
        func.sum(Income.amount)).filter(
            Income.user_id == user_id, Income.date == today).scalar()


# Получить расходы за день
def get_daily_expenses(user_id: int, db: Session):
    today = datetime.today().date()
    return db.query(
        func.sum(Expense.amount)).filter(
            Expense.user_id == user_id, Expense.date == today).scalar()

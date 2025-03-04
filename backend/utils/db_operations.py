from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from sqlalchemy import func
from models.income import Income
from models.expense import Expense

# Получить доходы за день
def get_daily_income(user_id: int, db: Session):
    today = datetime.today().date()
    return db.query(func.sum(Income.amount)).filter(Income.user_id == user_id, Income.date == today).scalar() or 0

# Получить расходы за день
def get_daily_expenses(user_id: int, db: Session):
    today = datetime.today().date()
    return db.query(func.sum(Expense.amount)).filter(Expense.user_id == user_id, Expense.date == today).scalar() or 0

# Получить доходы за неделю
def get_weekly_income(user_id: int, db: Session):
    today = datetime.today().date()
    start_of_week = today - timedelta(days=today.weekday())  # Начало недели
    return db.query(func.sum(Income.amount)).filter(Income.user_id == user_id, Income.date >= start_of_week).scalar() or 0

# Получить расходы за неделю
def get_weekly_expenses(user_id: int, db: Session):
    today = datetime.today().date()
    start_of_week = today - timedelta(days=today.weekday())  # Начало недели
    return db.query(func.sum(Expense.amount)).filter(Expense.user_id == user_id, Expense.date >= start_of_week).scalar() or 0

# Получить доходы за месяц
def get_monthly_income(user_id: int, db: Session):
    today = datetime.today().date()
    start_of_month = today.replace(day=1)  # Начало месяца
    return db.query(func.sum(Income.amount)).filter(Income.user_id == user_id, Income.date >= start_of_month).scalar() or 0

# Получить расходы за месяц
def get_monthly_expenses(user_id: int, db: Session):
    today = datetime.today().date()
    start_of_month = today.replace(day=1)  # Начало месяца
    return db.query(func.sum(Expense.amount)).filter(Expense.user_id == user_id, Expense.date >= start_of_month).scalar() or 0

# Получить доходы за заданный диапазон дат
def get_income_in_date_range(user_id: int, start_date: datetime, end_date: datetime, db: Session):
    result = db.query(func.sum(Income.amount)) \
        .filter(Income.user_id == user_id, Income.date >= start_date, Income.date <= end_date) \
        .scalar()
    return result if result is not None else 0

# Получить расходы за заданный диапазон дат
def get_expenses_in_date_range(user_id: int, start_date: datetime, end_date: datetime, db: Session):
    result = db.query(func.sum(Expense.amount)) \
        .filter(Expense.user_id == user_id, Expense.date >= start_date, Expense.date <= end_date) \
        .scalar()
    return result if result is not None else 0
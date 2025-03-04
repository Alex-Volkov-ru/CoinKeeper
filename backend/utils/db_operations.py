import logging

from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from sqlalchemy import func

from models.income import Income
from models.expense import Expense


logger = logging.getLogger(__name__)

def get_daily_income(user_id: int, db: Session):
    """Получает сумму доходов пользователя за текущий день."""
    try:
        today = datetime.today().date()
        return db.query(func.sum(Income.amount)).filter(Income.user_id == user_id, Income.date == today).scalar() or 0
    except Exception as e:
        logger.error(f"Ошибка при получении дневного дохода: {e}")
        return 0

def get_daily_expenses(user_id: int, db: Session):
    """Получает сумму расходов пользователя за текущий день."""
    try:
        today = datetime.today().date()
        return db.query(func.sum(Expense.amount)).filter(Expense.user_id == user_id, Expense.date == today).scalar() or 0
    except Exception as e:
        logger.error(f"Ошибка при получении дневных расходов: {e}")
        return 0

def get_weekly_income(user_id: int, db: Session):
    """Получает сумму доходов пользователя за текущую неделю."""
    try:
        today = datetime.today().date()
        start_of_week = today - timedelta(days=today.weekday())
        return db.query(func.sum(Income.amount)).filter(Income.user_id == user_id, Income.date >= start_of_week).scalar() or 0
    except Exception as e:
        logger.error(f"Ошибка при получении недельного дохода: {e}")
        return 0

def get_weekly_expenses(user_id: int, db: Session):
    """Получает сумму расходов пользователя за текущую неделю."""
    try:
        today = datetime.today().date()
        start_of_week = today - timedelta(days=today.weekday())
        return db.query(func.sum(Expense.amount)).filter(Expense.user_id == user_id, Expense.date >= start_of_week).scalar() or 0
    except Exception as e:
        logger.error(f"Ошибка при получении недельных расходов: {e}")
        return 0

def get_monthly_income(user_id: int, db: Session):
    """Получает сумму доходов пользователя за текущий месяц."""
    try:
        today = datetime.today().date()
        start_of_month = today.replace(day=1)
        return db.query(func.sum(Income.amount)).filter(Income.user_id == user_id, Income.date >= start_of_month).scalar() or 0
    except Exception as e:
        logger.error(f"Ошибка при получении месячного дохода: {e}")
        return 0

def get_monthly_expenses(user_id: int, db: Session):
    """Получает сумму расходов пользователя за текущий месяц."""
    try:
        today = datetime.today().date()
        start_of_month = today.replace(day=1)
        return db.query(func.sum(Expense.amount)).filter(Expense.user_id == user_id, Expense.date >= start_of_month).scalar() or 0
    except Exception as e:
        logger.error(f"Ошибка при получении месячных расходов: {e}")
        return 0

def get_income_in_date_range(user_id: int, start_date: datetime, end_date: datetime, db: Session):
    """Получает сумму доходов пользователя за заданный диапазон дат."""
    try:
        result = db.query(func.sum(Income.amount)).filter(
            Income.user_id == user_id, Income.date >= start_date, Income.date <= end_date).scalar()
        return result if result is not None else 0
    except Exception as e:
        logger.error(f"Ошибка при получении дохода за период {start_date} - {end_date}: {e}")
        return 0

def get_expenses_in_date_range(user_id: int, start_date: datetime, end_date: datetime, db: Session):
    """Получает сумму расходов пользователя за заданный диапазон дат."""
    try:
        result = db.query(func.sum(Expense.amount)).filter(
            Expense.user_id == user_id, Expense.date >= start_date, Expense.date <= end_date).scalar()
        return result if result is not None else 0
    except Exception as e:
        logger.error(f"Ошибка при получении расходов за период {start_date} - {end_date}: {e}")
        return 0

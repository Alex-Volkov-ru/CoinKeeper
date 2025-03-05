import logging

from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from sqlalchemy import func

from models.income import Income
from models.expense import Expense
from models.categories import IncomeCategory, ExpenseCategory


logger = logging.getLogger(__name__)

def get_daily_income(user_id: int, db: Session):
    """Получает сумму доходов пользователя за текущий день с разбивкой по категориям."""
    try:
        today = datetime.today().date()

        # Используем связь через категорию
        incomes = db.query(IncomeCategory.name, func.sum(Income.amount)) \
            .join(Income.category) \
            .filter(Income.user_id == user_id, Income.date == today) \
            .group_by(IncomeCategory.name) \
            .all()

        total_income = sum(amount for _, amount in incomes)
        category_incomes = {category: amount for category, amount in incomes}

        return total_income, category_incomes
    except Exception as e:
        logger.error(f"Ошибка при получении дневного дохода: {e}")
        return 0, {}

def get_daily_expenses(user_id: int, db: Session):
    """Получает сумму расходов пользователя за текущий день."""
    try:
        today = datetime.today().date()

        # Используем связь через категорию
        incomes = db.query(ExpenseCategory.name, func.sum(Expense.amount)) \
            .join(Expense.category) \
            .filter(Expense.user_id == user_id, Expense.date == today) \
            .group_by(ExpenseCategory.name) \
            .all()

        total_expense = sum(amount for _, amount in incomes)
        category_expense = {category: amount for category, amount in incomes}

        return total_expense, category_expense
    except Exception as e:
        logger.error(f"Ошибка при получении дневного дохода: {e}")
        return 0, {}

def get_weekly_income(user_id: int, db: Session):
    """Получает сумму доходов пользователя за текущую неделю с разбивкой по категориям."""
    try:
        today = datetime.today().date()
        start_of_week = today - timedelta(days=today.weekday())
        incomes = db.query(IncomeCategory.name, func.sum(Income.amount)) \
            .join(Income.category) \
            .filter(Income.user_id == user_id, Income.date >= start_of_week) \
            .group_by(IncomeCategory.name) \
            .all()
        
        total_income = sum(amount for _, amount in incomes)
        category_incomes = {category: amount for category, amount in incomes}

        return total_income, category_incomes
    except Exception as e:
        logger.error(f"Ошибка при получении недельного дохода: {e}")
        return 0, {}

def get_weekly_expenses(user_id: int, db: Session):
    """Получает сумму расходов пользователя за текущую неделю с разделением по категориям."""
    try:
        today = datetime.today().date()
        start_of_week = today - timedelta(days=today.weekday())

        # Используем связь через категорию
        expenses = db.query(ExpenseCategory.name, func.sum(Expense.amount)) \
            .join(Expense.category) \
            .filter(Expense.user_id == user_id, Expense.date >= start_of_week) \
            .group_by(ExpenseCategory.name) \
            .all()

        total_expense = sum(amount for _, amount in expenses)
        category_expense = {category: amount for category, amount in expenses}

        return total_expense, category_expense
    except Exception as e:
        logger.error(f"Ошибка при получении недельных расходов: {e}")
        return 0, {}

def get_monthly_income(user_id: int, db: Session):
    """Получает сумму доходов пользователя за текущий месяц с разбивкой по категориям."""
    try:
        today = datetime.today().date()
        start_of_month = today.replace(day=1)
        incomes = db.query(IncomeCategory.name, func.sum(Income.amount)) \
            .join(Income.category) \
            .filter(Income.user_id == user_id, Income.date >= start_of_month) \
            .group_by(IncomeCategory.name) \
            .all()
        
        total_income = sum(amount for _, amount in incomes)
        category_incomes = {category: amount for category, amount in incomes}

        return total_income, category_incomes
    except Exception as e:
        logger.error(f"Ошибка при получении месячного дохода: {e}")
        return 0, {}

def get_monthly_expenses(user_id: int, db: Session):
    """Получает сумму расходов пользователя за текущий месяц с разделением по категориям."""
    try:
        today = datetime.today().date()
        start_of_month = today.replace(day=1)

        # Используем связь через категорию
        expenses = db.query(ExpenseCategory.name, func.sum(Expense.amount)) \
            .join(Expense.category) \
            .filter(Expense.user_id == user_id, Expense.date >= start_of_month) \
            .group_by(ExpenseCategory.name) \
            .all()

        total_expense = sum(amount for _, amount in expenses)
        category_expense = {category: amount for category, amount in expenses}

        return total_expense, category_expense
    except Exception as e:
        logger.error(f"Ошибка при получении месячных расходов: {e}")
        return 0, {}

def get_income_in_date_range(user_id: int, start_date: datetime, end_date: datetime, db: Session):
    """Получает сумму доходов пользователя за заданный диапазон дат с разделением по категориям."""
    try:
        incomes = db.query(IncomeCategory.name, func.sum(Income.amount)) \
            .join(Income.category) \
            .filter(Income.user_id == user_id, Income.date >= start_date, Income.date <= end_date) \
            .group_by(IncomeCategory.name) \
            .all()

        total_income = sum(amount for _, amount in incomes)
        category_income = {category: amount for category, amount in incomes}

        return total_income, category_income
    except Exception as e:
        logger.error(f"Ошибка при получении дохода за период {start_date} - {end_date}: {e}")
        return 0, {}

def get_expenses_in_date_range(user_id: int, start_date: datetime, end_date: datetime, db: Session):
    """Получает сумму расходов пользователя за заданный диапазон дат с разделением по категориям."""
    try:
        expenses = db.query(ExpenseCategory.name, func.sum(Expense.amount)) \
            .join(Expense.category) \
            .filter(Expense.user_id == user_id, Expense.date >= start_date, Expense.date <= end_date) \
            .group_by(ExpenseCategory.name) \
            .all()

        total_expense = sum(amount for _, amount in expenses)
        category_expense = {category: amount for category, amount in expenses}

        return total_expense, category_expense
    except Exception as e:
        logger.error(f"Ошибка при получении расходов за период {start_date} - {end_date}: {e}")
        return 0, {}

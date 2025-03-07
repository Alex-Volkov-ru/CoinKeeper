import logging

from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from sqlalchemy import func

from models.income import Income
from models.expense import Expense
from models.categories import IncomeCategory, ExpenseCategory


logger = logging.getLogger(__name__)

def get_daily_income(user_id: int, db: Session):
    """Получает сумму доходов пользователя за текущий день с разбивкой по категориям и детальными данными."""
    try:
        today = datetime.today().date()

        # Группировка по категориям
        incomes_grouped = db.query(IncomeCategory.name, func.sum(Income.amount)) \
            .join(IncomeCategory, Income.category_id == IncomeCategory.id) \
            .filter(Income.user_id == user_id, Income.date == today) \
            .group_by(IncomeCategory.name) \
            .all()

        total_income = sum(amount for _, amount in incomes_grouped) if incomes_grouped else 0
        category_incomes = {category: amount for category, amount in incomes_grouped} if incomes_grouped else {}

        # Детальный список доходов за день
        detailed_incomes = db.query(Income.date, IncomeCategory.name, Income.description, Income.amount) \
            .join(IncomeCategory, Income.category_id == IncomeCategory.id) \
            .filter(Income.user_id == user_id, Income.date == today) \
            .all()

        return total_income, category_incomes, detailed_incomes
    except Exception as e:
        logger.error(f"Ошибка при получении дневного дохода: {e}")
        return 0, {}, []


def get_daily_expenses(user_id: int, db: Session):
    """Получает сумму расходов пользователя за текущий день с разбивкой по категориям и детальными данными."""
    try:
        today = datetime.today().date()

        # Группировка по категориям
        expenses_grouped = db.query(ExpenseCategory.name, func.sum(Expense.amount)) \
            .join(ExpenseCategory, Expense.category_id == ExpenseCategory.id) \
            .filter(Expense.user_id == user_id, Expense.date == today) \
            .group_by(ExpenseCategory.name) \
            .all()

        total_expense = sum(amount for _, amount in expenses_grouped) if expenses_grouped else 0
        category_expenses = {category: amount for category, amount in expenses_grouped} if expenses_grouped else {}

        # Детальный список расходов за день
        detailed_expenses = db.query(Expense.date, ExpenseCategory.name, Expense.description, Expense.amount) \
            .join(ExpenseCategory, Expense.category_id == ExpenseCategory.id) \
            .filter(Expense.user_id == user_id, Expense.date == today) \
            .all()

        return total_expense, category_expenses, detailed_expenses
    except Exception as e:
        logger.error(f"Ошибка при получении дневных расходов: {e}")
        return 0, {}, []

def get_weekly_income(user_id: int, db: Session):
    """Получает сумму доходов пользователя за текущую неделю с разбивкой по категориям и детальными данными."""
    try:
        today = datetime.today().date()
        start_of_week = today - timedelta(days=today.weekday())  # Понедельник
        end_of_week = start_of_week + timedelta(days=6)  # Воскресенье

        # Группировка по категориям
        incomes_grouped = db.query(IncomeCategory.name, func.sum(Income.amount)) \
            .join(IncomeCategory, Income.category_id == IncomeCategory.id) \
            .filter(Income.user_id == user_id, Income.date.between(start_of_week, end_of_week)) \
            .group_by(IncomeCategory.name) \
            .all()

        total_income = sum(amount for _, amount in incomes_grouped) if incomes_grouped else 0
        category_incomes = {category: amount for category, amount in incomes_grouped} if incomes_grouped else {}

        # Детальный список доходов за неделю
        detailed_incomes = db.query(Income.date, IncomeCategory.name, Income.description, Income.amount) \
            .join(IncomeCategory, Income.category_id == IncomeCategory.id) \
            .filter(Income.user_id == user_id, Income.date.between(start_of_week, end_of_week)) \
            .order_by(Income.date) \
            .all()

        return total_income, category_incomes, detailed_incomes
    except Exception as e:
        logger.error(f"Ошибка при получении недельного дохода: {e}")
        return 0, {}, []


def get_weekly_expenses(user_id: int, db: Session):
    """Получает сумму расходов пользователя за текущую неделю с разбивкой по категориям и детальными данными."""
    try:
        today = datetime.today().date()
        start_of_week = today - timedelta(days=today.weekday())

        # Группировка по категориям
        expenses_grouped = db.query(ExpenseCategory.name, func.sum(Expense.amount)) \
            .join(ExpenseCategory, Expense.category_id == ExpenseCategory.id) \
            .filter(Expense.user_id == user_id, Expense.date >= start_of_week) \
            .group_by(ExpenseCategory.name) \
            .all()

        total_expense = sum(amount for _, amount in expenses_grouped) if expenses_grouped else 0
        category_expenses = {category: amount for category, amount in expenses_grouped} if expenses_grouped else {}

        # Детальный список расходов за неделю
        detailed_expenses = db.query(Expense.date, ExpenseCategory.name, Expense.description, Expense.amount) \
            .join(ExpenseCategory, Expense.category_id == ExpenseCategory.id) \
            .filter(Expense.user_id == user_id, Expense.date >= start_of_week) \
            .all()

        return total_expense, category_expenses, detailed_expenses
    except Exception as e:
        logger.error(f"Ошибка при получении недельных расходов: {e}")
        return 0, {}, []

def get_monthly_income(user_id: int, db: Session):
    """Получает полную статистику доходов пользователя за текущий месяц (сумму по категориям и детальную информацию)."""
    try:
        today = datetime.today().date()
        start_of_month = today.replace(day=1)
        end_of_month = (start_of_month.replace(month=today.month % 12 + 1, day=1) - timedelta(days=1))

        # Группировка по категориям
        incomes_grouped = db.query(IncomeCategory.name, func.sum(Income.amount)) \
            .join(IncomeCategory, Income.category_id == IncomeCategory.id) \
            .filter(Income.user_id == user_id, Income.date.between(start_of_month, end_of_month)) \
            .group_by(IncomeCategory.name) \
            .all()

        total_income = sum(amount for _, amount in incomes_grouped) if incomes_grouped else 0
        category_incomes = {category: amount for category, amount in incomes_grouped} if incomes_grouped else {}

        # Детальный список доходов за месяц
        detailed_incomes = db.query(Income.date, IncomeCategory.name, Income.description, Income.amount) \
            .join(IncomeCategory, Income.category_id == IncomeCategory.id) \
            .filter(Income.user_id == user_id, Income.date.between(start_of_month, end_of_month)) \
            .order_by(Income.date) \
            .all()

        return total_income, category_incomes, detailed_incomes
    except Exception as e:
        logger.error(f"Ошибка при получении месячного дохода: {e}")
        return 0, {}, []

def get_monthly_expenses(user_id: int, db: Session):
    """Получает сумму расходов пользователя за текущий месяц с разбивкой по категориям и детальными данными."""
    try:
        today = datetime.today().date()
        start_of_month = today.replace(day=1)

        # Группировка по категориям
        expenses_grouped = db.query(ExpenseCategory.name, func.sum(Expense.amount)) \
            .join(ExpenseCategory, Expense.category_id == ExpenseCategory.id) \
            .filter(Expense.user_id == user_id, Expense.date >= start_of_month) \
            .group_by(ExpenseCategory.name) \
            .all()

        total_expense = sum(amount for _, amount in expenses_grouped) if expenses_grouped else 0
        category_expenses = {category: amount for category, amount in expenses_grouped} if expenses_grouped else {}

        # Детальный список расходов за месяц
        detailed_expenses = db.query(Expense.date, ExpenseCategory.name, Expense.description, Expense.amount) \
            .join(ExpenseCategory, Expense.category_id == ExpenseCategory.id) \
            .filter(Expense.user_id == user_id, Expense.date >= start_of_month) \
            .all()

        return total_expense, category_expenses, detailed_expenses
    except Exception as e:
        logger.error(f"Ошибка при получении месячных расходов: {e}")
        return 0, {}, []

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

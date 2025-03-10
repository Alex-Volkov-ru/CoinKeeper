from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from models.database import Base


class IncomeCategory(Base):
    """
    Модель категории доходов.

    Атрибуты:
    - id: Уникальный идентификатор категории.
    - name: Название категории.
    - incomes: Связь с моделью Income (доходы).
    """
    __tablename__ = 'income_categories'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)

    # Добавляем связь с Income
    incomes = relationship("Income", back_populates="category")

    def __repr__(self):
        return f'<IncomeCategory {self.id}, {self.name}>'


class ExpenseCategory(Base):
    """
    Модель категории расходов.

    Атрибуты:
    - id: Уникальный идентификатор категории.
    - name: Название категории.
    - expenses: Связь с моделью Expense (расходы).
    """
    __tablename__ = "expense_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)

    expenses = relationship("Expense", back_populates="category")  # Добавляем связь

    def __repr__(self):
        return f"<ExpenseCategory {self.id}, {self.name}>"

from sqlalchemy import Column, Integer, String

from models.database import Base


class IncomeCategory(Base):
    __tablename__ = 'income_categories'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)

    def __repr__(self):
        return f'<IncomeCategory {self.id}, {self.name}>'


class ExpenseCategory(Base):
    __tablename__ = "expense_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)

    def __repr__(self):
        return f"<ExpenseCategory {self.id}, {self.name}>"

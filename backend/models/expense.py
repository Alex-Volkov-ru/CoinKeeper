from sqlalchemy import (
    Column, Integer, DECIMAL,
    ForeignKey, Date, String, BigInteger)
from sqlalchemy.orm import relationship

from models.database import Base


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id"))
    category_id = Column(Integer, ForeignKey("expense_categories.id"))
    amount = Column(DECIMAL)
    date = Column(Date)
    description = Column(String)

    user = relationship("User", back_populates="expenses")
    category = relationship("ExpenseCategory", back_populates="expenses")

    def __repr__(self):
        return f"<Expense {self.id}, {self.amount}>"

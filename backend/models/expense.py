from sqlalchemy import (
    Column, Integer, DECIMAL,
    ForeignKey, Date, String, BigInteger)
from sqlalchemy.orm import relationship

from models.database import Base


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.tg_id"))
    category_id = Column(Integer, ForeignKey("expense_categories.id"))
    amount = Column(DECIMAL)
    date = Column(Date)
    description = Column(String)

    user = relationship("User", back_populates="expenses")
    category = relationship("ExpenseCategory", back_populates="expenses")

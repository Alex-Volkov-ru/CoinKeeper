from sqlalchemy import Column, Integer, DECIMAL, ForeignKey, Date, String
from sqlalchemy.orm import relationship

from models.database import Base


class Income(Base):
    __tablename__ = "incomes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.tg_id'))
    category_id = Column(Integer, ForeignKey('income_categories.id'))
    amount = Column(DECIMAL)
    date = Column(Date)
    description = Column(String)

    user = relationship("User", back_populates='incomes')
    category = relationship("IncomeCategory", back_populates="incomes")

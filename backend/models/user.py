from sqlalchemy import Column, String, BigInteger, DECIMAL, Integer
from sqlalchemy.orm import relationship

from models.database import Base
from models.income import Income
from models.expense import Expense


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    tg_id = Column(BigInteger)
    name = Column(String)
    last_name = Column(String)
    contact = Column(String)
    balance = Column(DECIMAL, default=0.0)

    incomes = relationship("Income", back_populates="user")
    expenses = relationship("Expense", back_populates="user")

    def __repr__(self):
        return f"<User {self.tg_id}, {self.name}>"

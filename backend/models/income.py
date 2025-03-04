from sqlalchemy import Column, Integer, DECIMAL, ForeignKey, Date, String
from sqlalchemy.orm import relationship

from models.database import Base


class Income(Base):
    """
    Модель доходов.

    Атрибуты:
    - id: Уникальный идентификатор дохода.
    - user_id: Идентификатор пользователя, связанного с доходом.
    - category_id: Идентификатор категории дохода.
    - amount: Сумма дохода.
    - date: Дата дохода.
    - description: Описание дохода.
    - user: Связь с моделью User.
    - category: Связь с моделью IncomeCategory.
    """
    __tablename__ = "incomes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    category_id = Column(Integer, ForeignKey('income_categories.id'))
    amount = Column(DECIMAL)
    date = Column(Date)
    description = Column(String)

    user = relationship("User", back_populates='incomes')
    category = relationship("IncomeCategory", back_populates="incomes")  # Убедись, что здесь back_populates

    def __repr__(self):
        return f"<Income {self.id}, {self.amount}>"


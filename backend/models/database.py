import os
import logging

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()

# Создаем строку подключения к SQLite
DATABASE_URL = os.getenv('DATABASE_URL')  # Значение по умолчанию

logging.basicConfig(level=logging.DEBUG)
logging.info("Таблицы успешно созданы.")

try:
    logging.debug("Подключаемся к базе данных...")
    engine = create_engine(DATABASE_URL,
                           connect_args={"check_same_thread": False})
    with engine.connect() as connection:
        logging.debug("Успешное подключение!")
        result = connection.execute(text("SELECT 1"))
        logging.debug(f"Результат: {result.fetchone()}")
except Exception as e:
    logging.error(f"Произошла ошибка: {str(e)}")

# Создаем базовый класс для моделей
Base = declarative_base()

# Создаем сессию для работы с БД
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Функция для получения сессии
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
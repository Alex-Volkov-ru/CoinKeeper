🤖 CoinKeeperBot

CoinKeeperBot — ваш персональный помощник в управлении финансами! 💰

Этот бот поможет вам легко вести бюджет, отслеживать расходы и планировать доходы прямо в Telegram. Забудьте о сложных таблицах и перегруженных приложениях — просто добавляйте транзакции в пару кликов! 📊

🛠️ Технологии

Язык: Python 3.11

Библиотеки:

aiogram — работа с Telegram API

APScheduler — планировщик задач

asyncpg — асинхронная работа с PostgreSQL

alembic — миграции базы данных

dotenv — загрузка переменных окружения

asyncio — асинхронное выполнение

🚀 Установка и запуск

🔹 1. Локальный запуск (без Docker)

📌 Требования:

Python 3.11+

Установленный pip

PostgreSQL 15+

🔧 Шаги установки:

# 1. Клонируем репозиторий
git clone https://github.com/ВАШ_НИК/coinkeeperbot.git
cd coinkeeperbot/backend

# 2. Создаем виртуальное окружение и активируем его
python -m venv venv
source venv/bin/activate  # Для Linux/Mac
venv\Scripts\activate  # Для Windows

# 3. Устанавливаем зависимости
pip install -r requirements.txt

# 4. Создаем .env файл с настройками (см. ниже)

# 5. Применяем миграции базы данных
alembic upgrade head

# 6. Запускаем бота
python main.py

🔹 2. Запуск через Docker

📌 Требования:

Установленный Docker и Docker Compose

🔧 Шаги:

Создайте .env файл (см. раздел Настройка переменных окружения ниже).

Соберите образ и запустите контейнер:

docker-compose up -d --build

Бот запустится в фоновом режиме. Проверить логи можно командой:

docker logs -f coinkeeper_backend

Остановить контейнер:

docker-compose down

🔧 Настройка переменных окружения (.env)

Перед запуском создайте .env в корневой папке и добавьте туда переменные:

TELEGRAM_TOKEN=ВАШ_ТОКЕН_БОТА
POSTGRES_USER=postgres
POSTGRES_PASSWORD=пароль
POSTGRES_DB=coinkeeper_db
POSTGRES_HOST=db
POSTGRES_PORT=5432

📌 Получить TELEGRAM_TOKEN можно, создав бота через BotFather в Telegram.

📄 Файлы и структура проекта

/CoinKeeperBot
│── /backend/                # Бэкенд часть проекта
│   ├── /filters/            # Фильтры сообщений
│   ├── /handlers/           # Обработчики команд
│   ├── /keyboards/          # Клавиатуры для Telegram
│   ├── /migrations/         # Файлы миграций базы данных (Alembic)
│   ├── /models/             # Модели базы данных
│   ├── /utils/              # Утилиты
│   ├── alembic.ini          # Конфигурация Alembic
│   ├── coin_keeper_bot.log  # Логи работы бота
│   ├── Dockerfile           # Файл для создания Docker-образа
│   ├── main.py              # Точка входа (запуск бота)
│   ├── requirements.txt     # Список зависимостей
│── /frontend/               # Фронтенд часть проекта (если планируется)
│── docker-compose.yaml      # Конфигурация для Docker Compose
│── venv/                    # Виртуальное окружение (локальный запуск)
│── README.md                # Описание проекта

🛠 Полезные команды Docker

🔹 Пересобрать образ и перезапустить контейнер:

docker-compose up -d --build

🔹 Остановить и удалить контейнеры:

docker-compose down

🔹 Посмотреть логи контейнера в реальном времени:

docker logs -f coinkeeper_backend

🔹 Зайти в контейнер для отладки:

docker exec -it coinkeeper_backend bash

🗄 Конфигурация Docker (PostgreSQL + Бот)

version: '3.8'

services:
  db:
    image: postgres:15
    container_name: coinkeeper_postgres
    restart: always
    env_file: .env
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U $POSTGRES_USER"]
      interval: 10s
      retries: 5
      timeout: 5s

  backend:
    build: ./backend
    container_name: coinkeeper_backend
    env_file: .env
    depends_on:
      db:
        condition: service_healthy
    restart: always
    command: ["sh", "-c", "sleep 5 && python main.py"]

volumes:
  postgres_data:

📬 Обратная связь

Если у вас есть вопросы или предложения, создавайте Issue или Pull Request в репозитории.

🚀 Развиваем бота вместе!

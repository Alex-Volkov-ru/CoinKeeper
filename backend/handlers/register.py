from aiogram import Router
from aiogram.types import Message
from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import Command
from sqlalchemy.orm import Session
import re

from models.database import get_db
from models.user import User
from keyboards.keyboards import main as kb

router = Router()

# Определяем состояния для FSM
class RegistrationStates(StatesGroup):
    waiting_for_name = State()  # Шаг: ожидаем имя
    waiting_for_phone = State()  # Шаг: ожидаем телефон

# Обработчик команды /register
@router.message(Command(commands=["register"]))
async def start_register(message: Message, state: FSMContext, bot: Bot):
    # Получаем сессию с базой данных
    db: Session = next(get_db())

    # Проверяем, есть ли пользователь с таким tg_id
    user = db.query(User).filter(User.tg_id == message.from_user.id).first()

    if user:
        # Если пользователь уже существует, сообщаем об этом
        await bot.send_message(
            message.from_user.id, f'{user.name}, Вы уже зарегистрированы!')
    else:
        # Если пользователя нет, начинаем процесс регистрации
        await bot.send_message(
            message.from_user.id, 'Давайте начнем регистрацию \nДля начала скажите, как к Вам обращаться?')
        await state.set_state(RegistrationStates.waiting_for_name)

# Обработчик имени пользователя
@router.message(RegistrationStates.waiting_for_name)
async def register_name(message: Message, state: FSMContext, bot: Bot):
    # Сохраняем имя в состоянии
    await state.update_data(regname=message.text)
    await bot.send_message(
        message.from_user.id, '😉Приятно познакомится! Укажите номер телефона в формате +7XXXXXXXXXX')
    await state.set_state(RegistrationStates.waiting_for_phone)

# Обработчик телефона пользователя
@router.message(RegistrationStates.waiting_for_phone)
async def register_phone(message: Message, state: FSMContext, bot: Bot):
    phone = message.text

    # Проверяем правильность формата телефона
    if re.match(r"^\+7\d{10}$", phone):
        # Сохраняем телефон в состояние
        await state.update_data(regphone=phone)

        # Сохраняем данные и создаем пользователя
        reg_data = await state.get_data()
        reg_name = reg_data.get('regname')
        reg_phone = reg_data.get('regphone')

        # Сохраняем в базе данных
        db: Session = next(get_db())
        new_user = User(
            tg_id=message.from_user.id,
            name=reg_name,
            contact=reg_phone
        )
        db.add(new_user)
        db.commit()

        # Отправляем сообщение о завершении регистрации + обновляем клавиатуру
        await bot.send_message(
            message.from_user.id, 
            f'Приятно познакомиться, {reg_name}!\nВаш телефон: {reg_phone}',
            reply_markup=kb  # Заменяем клавиатуру
        )

        # Очищаем состояние
        await state.clear()
    else:
        # Если формат телефона неверный, просим пользователя ввести его снова
        await bot.send_message(message.from_user.id, 'Номер телефона в неверном формате. Пожалуйста, используйте формат +7XXXXXXXXXX.')
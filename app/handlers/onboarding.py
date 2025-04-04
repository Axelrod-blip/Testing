from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
import logging
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from app.states import OnboardingStates
from app.keyboards import (goal_keyboard, experience_keyboard, gender_keyboard,
                         injuries_keyboard, location_keyboard, next_step_kb)
from app.ui_elements import format_message, format_onboarding_complete
from app.models import User
from app.db import async_session_factory

onboarding_router = Router()

# --- Utility Functions ---
async def save_onboarding_data(user_id: int, data: dict):
    """Сохраняет данные онбординга в БД."""
    try:
        async with async_session_factory() as session:
            # Проверяем, существует ли пользователь
            result = await session.execute(
                select(User).where(User.telegram_id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if user:
                # Обновляем существующего пользователя
                for key, value in data.items():
                    if hasattr(user, key):
                        setattr(user, key, value)
            else:
                # Создаем нового пользователя
                user = User(telegram_id=user_id, **data)
                session.add(user)
            
            await session.commit()
            logging.info(f"User data saved for {user_id}: {data}")
            return True
    except SQLAlchemyError as e:
        logging.error(f"Database error saving user {user_id}: {e}")
        await session.rollback()
        return False
    except Exception as e:
        logging.error(f"Unexpected error saving user {user_id}: {e}", exc_info=True)
        if 'session' in locals() and session:
            await session.rollback()
        return False

async def get_user_profile_dict(user_id: int):
    """Получает данные пользователя из БД в виде словаря."""
    try:
        async with async_session_factory() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                return None
            
            return user.to_dict()
    except Exception as e:
        logging.error(f"Error fetching profile for user {user_id}: {e}")
        return None

# --- Onboarding Start ---

@onboarding_router.message(Command("onboard"))
async def cmd_onboard(message: Message, state: FSMContext):
    """Starts the onboarding process."""
    await state.clear() # Clear previous state if any
    welcome_msg = format_message(
        "Давайте познакомимся", 
        "Несколько вопросов для начала. Какова ваша главная цель?",
        "info"
    )
    await message.answer(welcome_msg, reply_markup=goal_keyboard(), parse_mode="HTML")
    await state.set_state(OnboardingStates.Goal)

# --- Callback Handlers ---

@onboarding_router.callback_query(OnboardingStates.Goal, F.data.startswith("goal_"))
async def process_goal(callback: CallbackQuery, state: FSMContext):
    goal = callback.data.split('_', 1)[1]  # Убираем префикс goal_
    await state.update_data(goal=goal)
    
    # Сохраняем промежуточные данные
    user_data = await state.get_data()
    await save_onboarding_data(callback.from_user.id, user_data)
    
    await callback.message.edit_text(
        format_message("Цель выбрана", "Какой у вас опыт тренировок?", "info"),
        reply_markup=experience_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(OnboardingStates.Experience)
    await callback.answer()

@onboarding_router.callback_query(OnboardingStates.Experience, F.data.startswith("exp_"))
async def process_experience(callback: CallbackQuery, state: FSMContext):
    experience = callback.data.split('_', 1)[1]  # Убираем префикс exp_
    await state.update_data(experience=experience)
    
    # Сохраняем промежуточные данные
    user_data = await state.get_data()
    await save_onboarding_data(callback.from_user.id, user_data)
    
    await callback.message.edit_text(
        format_message("Опыт учтен", "Укажите ваш пол:", "info"),
        reply_markup=gender_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(OnboardingStates.Gender)
    await callback.answer()

@onboarding_router.callback_query(OnboardingStates.Gender, F.data.startswith("gender_"))
async def process_gender(callback: CallbackQuery, state: FSMContext):
    gender = callback.data.split('_', 1)[1]  # Убираем префикс gender_
    await state.update_data(gender=gender)
    
    # Сохраняем промежуточные данные
    user_data = await state.get_data()
    await save_onboarding_data(callback.from_user.id, user_data)
    
    await callback.message.edit_text(
        format_message("Пол указан", "Сколько вам лет?", "info"),
        parse_mode="HTML"
    )
    await state.set_state(OnboardingStates.Age)
    await callback.answer()

@onboarding_router.callback_query(OnboardingStates.Injuries, F.data.startswith("injuries_"))
async def process_injuries(callback: CallbackQuery, state: FSMContext):
    has_injuries = callback.data == "injuries_yes"
    await state.update_data(injuries=has_injuries)
    
    # Сохраняем промежуточные данные
    user_data = await state.get_data()
    await save_onboarding_data(callback.from_user.id, user_data)
    
    if has_injuries:
        await callback.message.edit_text(
            format_message("Важная информация", "Опишите кратко ваши травмы/ограничения:", "warning"),
            parse_mode="HTML"
        )
        await state.set_state(OnboardingStates.InjuryDetails)
    else:
        await state.update_data(injury_details=None)  # Ensure field exists even if no injuries
        await callback.message.edit_text(
            format_message("Отлично", "Где будете заниматься?", "info"),
            reply_markup=location_keyboard(),
            parse_mode="HTML"
        )
        await state.set_state(OnboardingStates.Location)
    await callback.answer()

@onboarding_router.callback_query(OnboardingStates.Location, F.data.startswith("loc_"))
async def process_location(callback: CallbackQuery, state: FSMContext):
    location = callback.data.split('_', 1)[1]  # Убираем префикс loc_
    await state.update_data(location=location)
    
    # Сохраняем промежуточные данные
    user_data = await state.get_data()
    await save_onboarding_data(callback.from_user.id, user_data)
    
    if location == "other":
        await callback.message.edit_text(
            format_message("Уточните", "Укажите место занятий:", "info"),
            parse_mode="HTML"
        )
        await state.set_state(OnboardingStates.LocationDetails)
    else:
        await state.update_data(location_details=None)  # Ensure field exists
        # --- Final Step --- 
        await callback.message.edit_text(
            format_onboarding_complete(),
            parse_mode="HTML",
            reply_markup=next_step_kb
        )
        await state.clear()  # Clear state after completion
    await callback.answer()

# --- Message Handlers for Text Input ---

@onboarding_router.message(OnboardingStates.Age, F.text)
async def process_age(message: Message, state: FSMContext):
    try:
        age = int(message.text.strip())
        if age <= 0 or age > 120:
            raise ValueError("Invalid age")
        
        await state.update_data(age=age)
        await message.answer(
            format_message("Возраст сохранен", "Ваш вес (кг)?", "info"),
            parse_mode="HTML"
        )
        await state.set_state(OnboardingStates.Weight)
        
        # Сохраняем промежуточные данные
        user_data = await state.get_data()
        await save_onboarding_data(message.from_user.id, user_data)
    except (ValueError, TypeError):
        await message.answer(
            format_message("Ошибка ввода", "Пожалуйста, введите корректный возраст (число от 1 до 120).", "error"),
            parse_mode="HTML"
        )

@onboarding_router.message(OnboardingStates.Weight, F.text)
async def process_weight(message: Message, state: FSMContext):
    try:
        weight = float(message.text.strip())
        if weight <= 0 or weight > 300:
            raise ValueError("Invalid weight")
        
        await state.update_data(weight=weight)
        await message.answer(
            format_message("Вес сохранен", "Сколько дней в неделю для тренировок?", "info"),
            parse_mode="HTML"
        )
        await state.set_state(OnboardingStates.Frequency)
        
        # Сохраняем промежуточные данные
        user_data = await state.get_data()
        await save_onboarding_data(message.from_user.id, user_data)
    except (ValueError, TypeError):
        await message.answer(
            format_message("Ошибка ввода", "Пожалуйста, введите корректный вес в кг (число от 1 до 300).", "error"),
            parse_mode="HTML"
        )

@onboarding_router.message(OnboardingStates.Frequency, F.text)
async def process_frequency(message: Message, state: FSMContext):
    try:
        frequency = int(message.text.strip())
        if frequency < 1 or frequency > 7:
            raise ValueError("Invalid frequency")
        
        await state.update_data(frequency=frequency)
        await message.answer(
            format_message("Частота сохранена", "Есть травмы / ограничения?", "info"),
            reply_markup=injuries_keyboard(),
            parse_mode="HTML"
        )
        await state.set_state(OnboardingStates.Injuries)
        
        # Сохраняем промежуточные данные
        user_data = await state.get_data()
        await save_onboarding_data(message.from_user.id, user_data)
    except (ValueError, TypeError):
        await message.answer(
            format_message("Ошибка ввода", "Пожалуйста, введите число от 1 до 7.", "error"),
            parse_mode="HTML"
        )

@onboarding_router.message(OnboardingStates.InjuryDetails, F.text)
async def process_injury_details(message: Message, state: FSMContext):
    injury_details = message.text.strip()
    if len(injury_details) > 500:  # Ограничиваем длину описания
        injury_details = injury_details[:500]
    
    await state.update_data(injury_details=injury_details)
    await message.answer(
        format_message("Информация сохранена", "Где будете заниматься?", "info"),
        reply_markup=location_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(OnboardingStates.Location)
    
    # Сохраняем промежуточные данные
    user_data = await state.get_data()
    await save_onboarding_data(message.from_user.id, user_data)

@onboarding_router.message(OnboardingStates.LocationDetails, F.text)
async def process_location_details(message: Message, state: FSMContext):
    location_details = message.text.strip()
    if len(location_details) > 200:  # Ограничиваем длину описания
        location_details = location_details[:200]
    
    await state.update_data(location_details=location_details)
    
    # Финальное сохранение
    user_data = await state.get_data()
    success = await save_onboarding_data(message.from_user.id, user_data)
    
    if success:
        await message.answer(
            format_onboarding_complete(),
            parse_mode="HTML",
            reply_markup=next_step_kb
        )
    else:
        await message.answer(
            format_message(
                "Ошибка сохранения",
                "Произошла ошибка при сохранении данных. Пожалуйста, попробуйте позже или обратитесь к администратору.",
                "error"
            ),
            parse_mode="HTML"
        )
    
    await state.clear()
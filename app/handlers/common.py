import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import default_state
from sqlalchemy import select

# Import necessary functions/data (e.g., for fetching user profile)
# from app.db import get_user_profile_dict # Renamed hypothetical function
from app.handlers.onboarding import cmd_onboard, get_user_profile_dict # To reuse onboarding logic for /update
from app.ui_elements import format_message, format_profile
from app.models import User
from app.db import async_session_factory
from app.keyboards import goal_keyboard, next_step_kb
from app.states import OnboardingStates

common_router = Router() # Renamed router instance

# --- Форматирование и прогресс ---
def format_user_data(data: dict) -> str:
    """Форматирует данные пользователя для вывода."""
    fields = {
        "name": "Имя",
        "gender": "Пол",
        "age": "Возраст",
        "height": "Рост (см)",
        "weight": "Вес (кг)",
        "goal": "Цель",
        "fitness_level": "Уровень подготовки",
        "workouts_per_week": "Тренировок в неделю",
        "workout_place": "Место тренировок",
        "has_injuries": "Наличие травм",
        "injuries_details": "Детали травм",
        "meals_per_day": "Приемов пищи в день",
        "first_meal_time": "Время 1-го приема пищи",
        "last_meal_time": "Время последнего приема пищи",
        "food_allergies": "Аллергии",
        "excluded_foods": "Исключенные продукты",
        "favorite_foods": "Любимые продукты",
        "activity_level": "Уровень активности",
    }
    lines = []
    for key, label in fields.items():
        value = data.get(key)
        if value is not None:
            if key == "injuries_details" and data.get("has_injuries") == "Нет":
                continue
            lines.append(f"*{label}:* {value}")
    return "\n".join(lines)

def get_progress_text(current_step: int) -> str:
    filled = "█" * current_step
    empty = "░" * (TOTAL_STEPS - current_step)
    emoji = PROGRESS_EMOJIS[current_step % len(PROGRESS_EMOJIS)]
    message = PROGRESS_MESSAGES[current_step % len(PROGRESS_MESSAGES)]
    return f"{emoji} *Прогресс: [{filled}{empty}] {current_step}/{TOTAL_STEPS}*\n{message}\n"

# --- Форматирование для команды cmd_profile ---
def format_user_profile(data: dict) -> str:
    """Formats user data for display (example structure based on onboarding). Placeholder for cmd_profile."""
    # Adapt this based on your actual User model and collected onboarding data
    fields = {
        # Keys should match those saved in save_onboarding_data
        "goal": "Цель",
        "experience": "Опыт",
        "gender": "Пол",
        "age": "Возраст",
        "weight": "Вес (кг)",
        "frequency": "Тренировок в неделю",
        "injuries": "Наличие травм/ограничений",
        "injury_details": "Детали травм",
        "location": "Место занятий",
        "location_details": "Детали места",
        # Add other fields from your User model if necessary
    }
    lines = []
    for key, label in fields.items():
        value = data.get(key)
        if value is not None:
            # Specific formatting adjustments
            if key == "injuries":
                value = "Да" if value else "Нет"
            if key == "injury_details" and not data.get("injuries"): # Only show details if injuries=True
                continue
            if key == "location_details" and data.get("location") != "other": # Only show details if location=other
                continue
            lines.append(f"*{label}:* {value}")
    return "\n".join(lines)

# --- Хендлеры ---
@common_router.message(Command("start")) # Use renamed router
async def cmd_start(message: Message, state: FSMContext):
    await state.clear() # Clear any previous state
    
    # Проверяем, есть ли у пользователя профиль
    user = await get_user_from_db(message.from_user.id)
    
    if user:
        # Если профиль есть, показываем приветствие и кнопки действий
        welcome_msg = format_message(
            "С возвращением!",
            "Что бы вы хотели сделать?",
            "info"
        )
        await message.answer(
            welcome_msg,
            reply_markup=next_step_kb,
            parse_mode="HTML"
        )
    else:
        # Если профиля нет, начинаем онбординг
        welcome_msg = format_message(
            "Давайте познакомимся", 
            "Несколько вопросов для начала. Какова ваша главная цель?",
            "info"
        )
        await message.answer(
            welcome_msg,
            reply_markup=goal_keyboard(),
            parse_mode="HTML"
        )
        await state.set_state(OnboardingStates.Goal)

@common_router.message(Command("cancel"), ~StateFilter(default_state)) # Use renamed router
async def cmd_cancel_state(message: Message, state: FSMContext):
    """Cancels the current active state."""
    current_state = await state.get_state()
    logging.info(f"Cancelling state {current_state} for user {message.from_user.id}")
    await state.clear()
    
    cancel_msg = format_message(
        "Действие отменено",
        "Все текущие операции прерваны.",
        "success"
    )
    
    await message.answer(
        cancel_msg, 
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="HTML"
    )

@common_router.message(Command("cancel"), StateFilter(default_state)) # Use renamed router
async def cmd_cancel_no_state(message: Message):
    """Handles /cancel when no state is active."""
    no_state_msg = format_message(
        "Нет активных действий",
        "В данный момент нет действий для отмены.",
        "info"
    )
    
    await message.answer(
        no_state_msg,
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="HTML"
    )

@common_router.message(Command("profile")) # Use renamed router
async def cmd_profile(message: Message):
    """Displays user profile information."""
    user_id = message.from_user.id
    user = await get_user_from_db(user_id)
    
    if user:
        profile_html = format_profile(user.to_dict())
        await message.answer(profile_html, parse_mode="HTML")
    else:
        not_found_msg = format_message(
            "Профиль не найден",
            "Пожалуйста, заполните анкету с помощью команды /onboard.",
            "warning"
        )
        await message.answer(not_found_msg, parse_mode="HTML")

@common_router.message(Command("update")) # Use renamed router
async def cmd_update(message: Message, state: FSMContext):
    """Alias for the onboarding command to update user info."""
    update_msg = format_message(
        "Обновление анкеты", 
        "Сейчас обновим ваши данные...",
        "info"
    )
    await message.answer(update_msg, parse_mode="HTML")
    # Reuse the onboarding start logic
    await cmd_onboard(message, state)

# Общий хендлер для неизвестных текстов (вне FSM)
@common_router.message(F.text, StateFilter(default_state)) # Use renamed router
async def handle_unknown_text(message: Message):
    """Handles any text message when no state is active."""
    unknown_msg = format_message(
        "Не распознано",
        "Доступные команды:\n\n"
        "• /start - Начальное сообщение\n"
        "• /onboard - Заполнить/обновить анкету\n"
        "• /profile - Просмотреть ваш профиль\n"
        "• /cancel - Отменить текущее действие",
        "warning"
    )
    
    await message.answer(unknown_msg, parse_mode="HTML")

# Общий хендлер для неизвестных callback-ов
@common_router.callback_query() # Use renamed router
async def handle_unknown_callback(callback: CallbackQuery):
    """Handles any callback query that doesn't match other handlers."""
    logging.warning(f"Неизвестный callback: {callback.data} от user {callback.from_user.id}")
    await callback.answer(
        "Эта кнопка больше не активна или произошла ошибка.", 
        show_alert=True
    )
    # Optionally try to delete the message with the outdated keyboard
    try:
        await callback.message.delete()
    except Exception as e:
        logging.warning(f"Could not delete message for unknown callback: {e}") # Log deletion error
        pass # Ignore if deletion fails (e.g., message too old)

async def get_user_from_db(telegram_id: int) -> User | None:
    """Получает пользователя из базы данных по telegram_id."""
    try:
        async with async_session_factory() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            return result.scalar_one_or_none()
    except Exception as e:
        logging.error(f"Error getting user {telegram_id}: {e}")
        return None

async def safe_message_answer(event: Message | CallbackQuery, text: str, **kwargs) -> Message:
    """Безопасная отправка сообщения с обработкой ошибок."""
    try:
        if isinstance(event, CallbackQuery):
            return await event.message.answer(text, **kwargs)
        return await event.answer(text, **kwargs)
    except Exception as e:
        logging.error(f"Error sending message: {e}")
        return None

async def safe_message_edit(message: Message, text: str, **kwargs) -> bool:
    """Безопасное редактирование сообщения с обработкой ошибок."""
    try:
        await message.edit_text(text, **kwargs)
        return True
    except Exception as e:
        logging.error(f"Error editing message: {e}")
        return False

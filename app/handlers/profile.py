import logging
import asyncio
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import default_state
from sqlalchemy.inspection import inspect

from app.models import User
from app.config import bot
from app.db import async_session_factory
from app.keyboards import profile_kb, next_step_kb
from app.ui_elements import format_message
from app.handlers.common import (
    get_user_from_db,
    safe_message_answer,
    safe_message_edit,
    cmd_start,
)

router = Router()

# Маппинги для отображения значений
GOAL_MAPPING = {
    "mass": "💪 Набор массы",
    "weight_loss": "⚖️ Снижение веса",
    "strength": "🏃 Повышение силы/выносливости",
    "health": "❤️ Оздоровление",
    "other": "✨ Другое"
}

EXPERIENCE_MAPPING = {
    "newbie": "🔰 Новичок (до 6 месяцев)",
    "intermediate": "🥈 Средний (6 месяцев – 2 года)",
    "advanced": "🥇 Продвинутый (более 2 лет)"
}

GENDER_MAPPING = {
    "male": "👨 Мужской",
    "female": "👩 Женский",
    "skip": "🤐 Предпочитаю не указывать"
}

LOCATION_MAPPING = {
    "home": "🏠 Дом",
    "gym": "🏋️ Тренажёрный зал",
    "outdoor": "🌳 Улица",
    "other": "📍 Другое"
}

def format_profile_value(value, mapping=None):
    """Форматирует значение для отображения в профиле."""
    if value is None:
        return "Не указано"
    if mapping and value in mapping:
        return mapping[value]
    if isinstance(value, bool):
        return "Да" if value else "Нет"
    return str(value)

@router.message(Command("profile"))
async def cmd_profile(message: Message):
    """Displays user profile information."""
    user_id = message.from_user.id
    user = await get_user_from_db(user_id)
    
    if user:
        profile_text = (
            "🏋️‍♂️ *Ваш Фитнес-Профиль*\n\n"
            f"*Цель:* {format_profile_value(user.goal, GOAL_MAPPING)}\n"
            f"*Опыт:* {format_profile_value(user.experience, EXPERIENCE_MAPPING)}\n"
            f"*Пол:* {format_profile_value(user.gender, GENDER_MAPPING)}\n"
            f"*Возраст:* {format_profile_value(user.age)} лет\n"
            f"*Вес:* {format_profile_value(user.weight)} кг\n"
            f"*Тренировок в неделю:* {format_profile_value(user.frequency)}\n"
            f"*Место тренировок:* {format_profile_value(user.location, LOCATION_MAPPING)}\n"
        )
        
        if user.injuries and user.injury_details:
            profile_text += f"*Травмы:* {format_profile_value(user.injury_details)}\n"
        
        profile_text += "\n💡 Используйте кнопки ниже, чтобы получить план тренировок или питания!"
            
        await message.answer(
            profile_text,
            parse_mode="Markdown",
            reply_markup=next_step_kb
        )
    else:
        not_found_msg = format_message(
            "Профиль не найден",
            "Пожалуйста, заполните анкету с помощью команды /start",
            "warning"
        )
        await message.answer(not_found_msg, parse_mode="HTML")

@router.callback_query(F.data == "edit_profile")
async def edit_profile_handler(callback: CallbackQuery, state: FSMContext):
    """Обработчик редактирования профиля."""
    await callback.answer()
    await safe_message_answer(
        callback,
        "🔄 *Обновление профиля*\n\nСейчас мы заполним анкету заново, чтобы обновить ваши данные.",
        parse_mode="Markdown"
    )
    await asyncio.sleep(0.5)
    await cmd_start(callback.message, state)

@router.callback_query(F.data == "back_to_start")
async def back_to_start_handler(callback: CallbackQuery, state: FSMContext):
    """Возвращает пользователя к начальному состоянию."""
    await callback.answer()
    await state.clear()
    await cmd_start(callback.message, state)

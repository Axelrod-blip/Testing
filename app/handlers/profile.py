import logging
import asyncio
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from sqlalchemy.inspection import inspect

from app.models import User
from app.config import bot

from .common import (
    get_user_from_db,
    safe_message_answer,
    safe_message_edit,
    start_handler,
    format_user_data
)

router = Router()

@router.message(Command("myprofile"))
async def show_profile_handler(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is not None:
        await safe_message_answer(message, "Пожалуйста, сначала завершите или отмените (/cancel) заполнение анкеты.")
        return

    telegram_id = message.from_user.id
    loading_msg = await safe_message_answer(message, "\ud83d\udd0d Загружаю твой профиль...")
    await bot.send_chat_action(chat_id=telegram_id, action="typing")
    user = await get_user_from_db(telegram_id)

    if user:
        columns = [c.key for c in inspect(User).mapper.column_attrs]
        user_data = {key: getattr(user, key) for key in columns}
        summary = format_user_data(user_data)
        await safe_message_edit(loading_msg, f"*Твой Профиль:* ✨\n\n{summary}", parse_mode="Markdown")
    else:
        await safe_message_edit(
            loading_msg,
            "Похоже, твой профиль еще не заполнен 🤔\nНажми /start, чтобы начать!"
        )

@router.callback_query(F.data == "edit_profile")
async def edit_profile_handler(callback: CallbackQuery, state: FSMContext):
    await safe_message_edit(
        callback,
        "Хорошо! Чтобы изменить данные, нужно будет пройти опрос заново.\n"
        "Это гарантирует, что все твои новые ответы будут учтены для будущих планов."
    )
    await callback.answer()
    await asyncio.sleep(1.5)
    await safe_message_answer(
        callback,
        "Запускаю анкету заново...", parse_mode="Markdown"
    )
    await asyncio.sleep(0.5)
    await start_handler(callback.message, state)

import logging
import random
import asyncio
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.exc import SQLAlchemyError
from aiogram.filters import Command

from app.models import User
from app.db import async_session_factory
from app.prompts import create_workout_prompt, create_meal_plan_prompt
from app.llm_service import generate_with_gemini, llm_service
from app.keyboards import suggest_meal_plan_kb, suggest_workout_plan_kb, next_step_kb
from app.config import bot # Для send_chat_action

# Импортируем общие функции
from .common import get_user_from_db, safe_message_answer, safe_message_edit
from app.handlers.onboarding import get_user_profile_dict
from app.ui_elements import format_message

router = Router()
print("✅ plans.py загружен")

# Константы для сообщений загрузки
GENERATING_WORKOUT_MSG = [
    "⚡️ Генерирую твой персональный план тренировок...",
    "💪 Создаю идеальную программу для твоих целей...",
    "🔥 Подбираю оптимальные упражнения..."
]
GENERATING_MEAL_MSG = [
    "🍏 Составляю твой план питания...",
    "🥗 Создаю сбалансированное меню...",
    "🍽 Готовлю персональные рекомендации..."
]

# --- Генерация планов --- #

@router.callback_query(F.data == "create_workout")
async def create_workout_plan_handler(callback: CallbackQuery):
    telegram_id = callback.from_user.id
    await callback.answer("Начинаю генерацию плана тренировок...") # Быстрый ответ
    loading_msg = await safe_message_answer(callback, random.choice(GENERATING_WORKOUT_MSG))
    await bot.send_chat_action(chat_id=telegram_id, action="typing")

    user = await get_user_from_db(telegram_id)
    if not user:
        await safe_message_edit(loading_msg, "❌ Не удалось найти ваш профиль. Пожалуйста, пройдите онбординг сначала (/start).")
        return

    try:
        prompt = create_workout_prompt(user)
        generated_plan = await generate_with_gemini(prompt)

        if not generated_plan:
            raise ValueError("LLM returned empty workout plan")

        # Пытаемся сохранить план в БД
        plan_saved = False
        try:
            async with async_session_factory() as session:
                # Перезапрашиваем пользователя внутри сессии для обновления
                user_to_update = await session.get(User, user.telegram_id) # Используем get для простоты
                if user_to_update:
                    user_to_update.workout_plan = generated_plan
                    await session.commit()
                    logging.info(f"Workout plan saved for {telegram_id}")
                    plan_saved = True
                else:
                     logging.error(f"User {telegram_id} not found in session for workout plan update.")
        except SQLAlchemyError as e:
            logging.error(f"DB error saving workout plan for {telegram_id}: {e}")
        except Exception as e_inner:
            logging.error(f"Unexpected error saving workout plan {telegram_id}: {e_inner}", exc_info=True)

        # Отправляем результат пользователю
        result_text = f"🎉 *Твой План Тренировок Готов!* 🎉\n\n{generated_plan}"
        if plan_saved:
            result_text += "\n\n✅ *План сохранен в твоем профиле.*"
        else:
            result_text += "\n\n⚠️ *Не удалось сохранить план в профиле из-за ошибки. Скопируй его сейчас.*"

        await safe_message_edit(loading_msg, result_text, parse_mode="Markdown")

        # Предлагаем следующий шаг
        await asyncio.sleep(1)
        await safe_message_answer(
            callback,
            "✨ *Отличная работа!*\n\nХочешь теперь получить *план питания*? 👇",
            reply_markup=suggest_meal_plan_kb
        )

    except Exception as e:
        logging.error(f"Error generating/processing workout plan for {telegram_id}: {e}", exc_info=True)
        error_message = "😔 *Упс! Что-то пошло не так...*\n\nНе удалось сгенерировать план тренировок. Попробуй позже!"
        if loading_msg:
            await safe_message_edit(loading_msg, error_message)
        else:
            await safe_message_answer(callback, error_message)

@router.callback_query(F.data == "create_meal_plan")
async def create_meal_plan_handler(callback: CallbackQuery):
    telegram_id = callback.from_user.id
    await callback.answer("Начинаю генерацию плана питания...")
    loading_msg = await safe_message_answer(callback, random.choice(GENERATING_MEAL_MSG))
    await bot.send_chat_action(chat_id=telegram_id, action="typing")

    user = await get_user_from_db(telegram_id)
    if not user:
        await safe_message_edit(loading_msg, "❌ Не удалось найти ваш профиль. Пожалуйста, пройдите онбординг сначала (/start).")
        return

    try:
        prompt = create_meal_plan_prompt(user)
        generated_plan = await generate_with_gemini(prompt)

        if not generated_plan:
            raise ValueError("LLM returned empty meal plan")

        plan_saved = False
        try:
            async with async_session_factory() as session:
                user_to_update = await session.get(User, user.telegram_id)
                if user_to_update:
                    user_to_update.meal_plan = generated_plan
                    await session.commit()
                    logging.info(f"Meal plan saved for {telegram_id}")
                    plan_saved = True
                else:
                    logging.error(f"User {telegram_id} not found in session for meal plan update.")
        except SQLAlchemyError as e:
            logging.error(f"DB error saving meal plan for {telegram_id}: {e}")
        except Exception as e_inner:
            logging.error(f"Unexpected error saving meal plan {telegram_id}: {e_inner}", exc_info=True)

        result_text = f"🍏 *Твой План Питания Готов!* 🍏\n\n{generated_plan}"
        if plan_saved:
            result_text += "\n\n✅ *План сохранен в твоем профиле.*"
        else:
            result_text += "\n\n⚠️ *Не удалось сохранить план в профиле из-за ошибки. Скопируй его сейчас.*"

        await safe_message_edit(loading_msg, result_text, parse_mode="Markdown")

        await asyncio.sleep(1)
        await safe_message_answer(
            callback,
            "✨ *Отличная работа!*\n\nХочешь теперь получить *план тренировок*? 👇",
            reply_markup=suggest_workout_plan_kb
        )

    except Exception as e:
        logging.error(f"Error generating/processing meal plan for {telegram_id}: {e}", exc_info=True)
        error_message = "😔 *Упс! Что-то пошло не так...*\n\nНе удалось сгенерировать план питания. Попробуй позже!"
        if loading_msg:
            await safe_message_edit(loading_msg, error_message)
        else:
            await safe_message_answer(callback, error_message)

# --- Просмотр планов --- #

@router.message(Command("myworkoutplan"))
async def show_workout_plan_handler(message: Message, state: FSMContext):
    # Проверка состояния FSM (если используется где-то еще)
    # current_state = await state.get_state()
    # if current_state is not None:
    #     await safe_message_answer(message, "Пожалуйста, завершите текущее действие (/cancel).")
    #     return

    telegram_id = message.from_user.id
    loading_msg = await safe_message_answer(message, "🔍 Ищу твой план тренировок...")
    await bot.send_chat_action(chat_id=telegram_id, action="typing")
    user = await get_user_from_db(telegram_id)

    if user and user.workout_plan:
        await safe_message_edit(loading_msg, f"*Твой Сохраненный План Тренировок:* 💪\n\n{user.workout_plan}", parse_mode="Markdown")
    elif user:
        await safe_message_edit(
            loading_msg,
            "У тебя пока нет сохраненного плана тренировок. 🤔\n"
            "Заверши анкету (/start) и сможешь его сгенерировать!",
            reply_markup=next_step_kb
            )
    else:
        await safe_message_edit(
            loading_msg,
            "Сначала нужно заполнить профиль (/start), чтобы я мог хранить твои планы 🙂"
            )

@router.message(Command("mymealplan"))
async def show_meal_plan_handler(message: Message, state: FSMContext):
    telegram_id = message.from_user.id
    loading_msg = await safe_message_answer(message, "🔍 Ищу твой план питания...")
    await bot.send_chat_action(chat_id=telegram_id, action="typing")
    user = await get_user_from_db(telegram_id)

    if user and user.meal_plan:
        await safe_message_edit(loading_msg, f"*Твой Сохраненный План Питания:* 🥗\n\n{user.meal_plan}", parse_mode="Markdown")
    elif user:
        await safe_message_edit(
            loading_msg,
            "У тебя пока нет сохраненного плана питания. 🤔\n"
            "Заверши анкету (/start) и сможешь его сгенерировать!",
            reply_markup=next_step_kb
            )
    else:
        await safe_message_edit(
            loading_msg,
            "Сначала нужно заполнить профиль (/start), чтобы я мог хранить твои планы 🙂"
            )

@router.message(Command("workout"))
async def cmd_workout(message: Message):
    """Обработчик команды /workout - генерация плана тренировок."""
    user_id = message.from_user.id
    
    # Сообщаем пользователю, что начали генерацию
    await message.answer(
        format_message(
            "Генерация плана тренировок",
            "Пожалуйста, подождите, я создаю для вас персонализированный план тренировок...",
            "workout"
        ),
        parse_mode="HTML"
    )
    
    try:
        # Получаем данные пользователя
        user_data = await get_user_profile_dict(user_id)
        
        if not user_data:
            # Если данных нет, предлагаем пройти онбординг
            await message.answer(
                format_message(
                    "Профиль не найден",
                    "Для создания персонализированного плана тренировок мне нужна информация о вас. "
                    "Пожалуйста, пройдите анкету с помощью команды /onboard.",
                    "warning"
                ),
                parse_mode="HTML"
            )
            return
        
        # Генерируем план тренировок
        workout_plan = await llm_service.generate_workout_plan(user_data)
        
        # Отправляем план пользователю
        await message.answer(
            format_message(
                "Ваш персональный план тренировок",
                workout_plan,
                "workout"
            ),
            parse_mode="HTML"
        )
        
    except Exception as e:
        logging.error(f"Error generating workout plan for user {user_id}: {e}")
        await message.answer(
            format_message(
                "Ошибка генерации",
                "Произошла ошибка при создании плана тренировок. Пожалуйста, попробуйте позже.",
                "error"
            ),
            parse_mode="HTML"
        )

@router.message(Command("mealplan"))
async def cmd_meal_plan(message: Message):
    """Обработчик команды /mealplan - генерация плана питания."""
    user_id = message.from_user.id
    
    # Сообщаем пользователю, что начали генерацию
    await message.answer(
        format_message(
            "Генерация плана питания",
            "Пожалуйста, подождите, я создаю для вас персонализированный план питания...",
            "nutrition"
        ),
        parse_mode="HTML"
    )
    
    try:
        # Получаем данные пользователя
        user_data = await get_user_profile_dict(user_id)
        
        if not user_data:
            # Если данных нет, предлагаем пройти онбординг
            await message.answer(
                format_message(
                    "Профиль не найден",
                    "Для создания персонализированного плана питания мне нужна информация о вас. "
                    "Пожалуйста, пройдите анкету с помощью команды /onboard.",
                    "warning"
                ),
                parse_mode="HTML"
            )
            return
        
        # Генерируем план питания
        meal_plan = await llm_service.generate_meal_plan(user_data)
        
        # Отправляем план пользователю
        await message.answer(
            format_message(
                "Ваш персональный план питания",
                meal_plan,
                "nutrition"
            ),
            parse_mode="HTML"
        )
        
    except Exception as e:
        logging.error(f"Error generating meal plan for user {user_id}: {e}")
        await message.answer(
            format_message(
                "Ошибка генерации",
                "Произошла ошибка при создании плана питания. Пожалуйста, попробуйте позже.",
                "error"
            ),
            parse_mode="HTML"
        )
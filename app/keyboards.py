from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.ui_elements import (
    get_goal_mapping, get_experience_mapping, get_gender_mapping,
    get_injuries_mapping, get_location_mapping
)

# Клавиатура для старта онбординга
go_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Погнали! 🚀", callback_data="start_onboarding")]
])

# --- Клавиатуры онбординга --- #

def goal_keyboard() -> InlineKeyboardMarkup:
    """Keyboard for selecting fitness goal."""
    builder = InlineKeyboardBuilder()
    goals = get_goal_mapping()
    for text, data in goals.items():
        builder.row(InlineKeyboardButton(text=text, callback_data=data))
    return builder.as_markup()

def experience_keyboard() -> InlineKeyboardMarkup:
    """Keyboard for selecting training experience."""
    builder = InlineKeyboardBuilder()
    levels = get_experience_mapping()
    for text, data in levels.items():
        builder.row(InlineKeyboardButton(text=text, callback_data=data))
    return builder.as_markup()

def gender_keyboard() -> InlineKeyboardMarkup:
    """Keyboard for selecting gender."""
    builder = InlineKeyboardBuilder()
    genders = get_gender_mapping()
    for text, data in genders.items():
        builder.row(InlineKeyboardButton(text=text, callback_data=data))
    return builder.as_markup()

def injuries_keyboard() -> InlineKeyboardMarkup:
    """Keyboard for indicating injuries."""
    builder = InlineKeyboardBuilder()
    injuries = get_injuries_mapping()
    injuries_items = list(injuries.items())
    # Располагаем кнопки в одном ряду
    builder.row(*[InlineKeyboardButton(text=text, callback_data=data) for text, data in injuries_items])
    return builder.as_markup()

def location_keyboard() -> InlineKeyboardMarkup:
    """Keyboard for selecting workout location."""
    builder = InlineKeyboardBuilder()
    locations = get_location_mapping()
    for text, data in locations.items():
        builder.row(InlineKeyboardButton(text=text, callback_data=data))
    return builder.as_markup()

fitness_level_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="👶 Новичок", callback_data="level_beginner")],
    [InlineKeyboardButton(text="🏃‍♂️ Средний", callback_data="level_intermediate")],
    [InlineKeyboardButton(text="🏋️‍♀️ Продвинутый", callback_data="level_advanced")],
])

# Новая клавиатура для выбора количества тренировок
workouts_per_week_kb = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="1 раз", callback_data="workouts_1"),
        InlineKeyboardButton(text="2 раза", callback_data="workouts_2"),
        InlineKeyboardButton(text="3 раза", callback_data="workouts_3"),
    ],
    [
        InlineKeyboardButton(text="4 раза", callback_data="workouts_4"),
        InlineKeyboardButton(text="5 раз", callback_data="workouts_5"),
        InlineKeyboardButton(text="6 раз", callback_data="workouts_6"),
    ],
    [InlineKeyboardButton(text="7 раз", callback_data="workouts_7")],
])

workout_place_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🏠 Дома", callback_data="place_home")],
    [InlineKeyboardButton(text="🏋️‍♂️ В зале", callback_data="place_gym")],
    [InlineKeyboardButton(text="🌳 На улице", callback_data="place_outdoors")],
])

activity_level_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🛋️ Низкая", callback_data="activity_low")],
    [InlineKeyboardButton(text="🚶‍♂️ Средняя", callback_data="activity_medium")],
    [InlineKeyboardButton(text="⚡ Высокая", callback_data="activity_high")],
])

# --- Клавиатуры для профиля --- #

profile_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Изменить профиль", callback_data="edit_profile")],
        [InlineKeyboardButton(text="🔄 В начало", callback_data="back_to_start")],
    ]
)

# --- Клавиатуры после завершения онбординга / для команд --- #

next_step_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="💪 План тренировок", callback_data="create_workout")],
        [InlineKeyboardButton(text="🥗 План питания", callback_data="create_meal_plan")],
        [InlineKeyboardButton(text="✏️ Изменить ответы", callback_data="edit_profile")],
    ]
)

# --- Новые клавиатуры для предложений после генерации --- #

suggest_meal_plan_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🥗 Да, план питания!", callback_data="create_meal_plan")],
        [InlineKeyboardButton(text="❌ Нет, спасибо", callback_data="cancel")]
    ]
)

suggest_workout_plan_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="💪 Да, план тренировок!", callback_data="create_workout")],
        [InlineKeyboardButton(text="❌ Нет, спасибо", callback_data="cancel")]
    ]
)
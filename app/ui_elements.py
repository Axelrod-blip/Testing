"""UI элементы для улучшения визуального представления бота."""
from aiogram.types import FSInputFile, InputMediaPhoto
from typing import Dict, Optional, Any

# --- Цветовая схема и иконки ---
MESSAGE_ICONS = {
    "info": "ℹ️",
    "success": "✅",
    "warning": "⚠️",
    "error": "❌",
    "workout": "💪",
    "nutrition": "🍎",
    "progress": "📊",
    "profile": "👤"
}

# --- Функции форматирования ---
def format_message(title: str, content: str, msg_type: str = "info") -> str:
    """Форматирует сообщения в едином стиле с иконками и HTML-разметкой.
    
    Args:
        title: Заголовок сообщения
        content: Основной текст сообщения
        msg_type: Тип сообщения из доступных в MESSAGE_ICONS
        
    Returns:
        Отформатированное сообщение с HTML-разметкой
    """
    icon = MESSAGE_ICONS.get(msg_type, "•")
    return f"{icon} <b>{title}</b>\n\n{content}"

def format_profile(data: Dict[str, Any]) -> str:
    """Форматирует данные профиля пользователя в красивом HTML формате.
    
    Args:
        data: Словарь с данными пользователя
        
    Returns:
        Профиль пользователя в HTML формате
    """
    # Определяем отображаемые поля и их названия
    fields = {
        "goal": "Цель",
        "experience": "Опыт",
        "gender": "Пол",
        "age": "Возраст",
        "weight": "Вес (кг)",
        "frequency": "Тренировок в неделю",
        "injuries": "Травмы/ограничения",
        "injury_details": "Детали травм",
        "location": "Место занятий",
        "location_details": "Детали места",
    }
    
    # Преобразование значений для более читабельного отображения
    mapped_values = {
        "goal": {
            "mass": "Набор массы",
            "weight_loss": "Снижение веса",
            "strength": "Повышение силы/выносливости",
            "health": "Оздоровление",
            "other": "Другое"
        },
        "experience": {
            "newbie": "Новичок (до 6 месяцев)",
            "intermediate": "Средний (6 месяцев – 2 года)",
            "advanced": "Продвинутый (более 2 лет)"
        },
        "gender": {
            "male": "Мужской",
            "female": "Женский",
            "skip": "Не указан"
        },
        "location": {
            "home": "Дом",
            "gym": "Тренажёрный зал",
            "outdoor": "Улица",
            "other": "Другое"
        }
    }
    
    # Формируем HTML
    lines = ["<b>Ваш профиль</b>\n"]
    
    for key, label in fields.items():
        value = data.get(key)
        if value is None:
            continue
            
        # Пропускаем детали, если они не нужны
        if key == "injury_details" and not data.get("injuries"):
            continue
        if key == "location_details" and data.get("location") != "other":
            continue
            
        # Преобразуем значение, если есть маппинг
        if key in mapped_values and value in mapped_values[key]:
            value = mapped_values[key][value]
        
        # Форматируем булевы значения
        if key == "injuries" and isinstance(value, bool):
            value = "Есть" if value else "Нет"
            
        lines.append(f"<i>{label}:</i> <code>{value}</code>")
    
    # Добавляем разделитель перед тренировками
    freq_index = next((i for i, line in enumerate(lines) if "Тренировок в неделю" in line), -1)
    if freq_index > 0:
        lines.insert(freq_index, "———————————")
    
    return "\n".join(lines)

def format_onboarding_complete() -> str:
    """Возвращает красивое сообщение о завершении онбординга."""
    return format_message(
        "Профиль создан",
        "Ваши данные сохранены! Теперь я смогу предоставлять более персонализированные рекомендации.\n\n"
        "Используйте <code>/profile</code> чтобы увидеть свой профиль.",
        "success"
    )

# --- Вспомогательные функции ---
def get_goal_mapping() -> Dict[str, str]:
    """Возвращает словарь с отображением целей и иконок для клавиатуры."""
    return {
        "💪 Набор массы": "goal_mass",
        "⚖️ Снижение веса": "goal_weight_loss",
        "🏃 Повышение силы/выносливости": "goal_strength",
        "❤️ Оздоровление": "goal_health",
        "✨ Другое": "goal_other"
    }

def get_experience_mapping() -> Dict[str, str]:
    """Возвращает словарь с отображением опыта и иконок для клавиатуры."""
    return {
        "🔰 Новичок (до 6 месяцев)": "exp_newbie",
        "🥈 Средний (6 месяцев – 2 года)": "exp_intermediate",
        "🥇 Продвинутый (более 2 лет)": "exp_advanced"
    }

def get_gender_mapping() -> Dict[str, str]:
    """Возвращает словарь с отображением пола и иконок для клавиатуры."""
    return {
        "👨 Мужской": "gender_male",
        "👩 Женский": "gender_female",
        "🤐 Предпочитаю не указывать": "gender_skip"
    }

def get_injuries_mapping() -> Dict[str, str]:
    """Возвращает словарь с отображением травм и иконок для клавиатуры."""
    return {
        "✅ Нет": "injuries_no",
        "⚠️ Да": "injuries_yes"
    }

def get_location_mapping() -> Dict[str, str]:
    """Возвращает словарь с отображением мест тренировок и иконок для клавиатуры."""
    return {
        "🏠 Дом": "loc_home",
        "🏋️ Тренажёрный зал": "loc_gym",
        "🌳 Улица": "loc_outdoor",
        "📍 Другое": "loc_other"
    } 
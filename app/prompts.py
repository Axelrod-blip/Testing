from typing import Dict, Any

def create_workout_prompt(user_data: dict) -> str:
    """
    Создает промпт для генерации плана тренировок на основе данных пользователя.
    
    Args:
        user_data: Словарь с данными пользователя
    
    Returns:
        str: Текст промпта для модели
    """
    # Маппинг полей из онбординга к полям в промпте
    field_mapping = {
        "experience": "fitness_level",
        "frequency": "workout_frequency",
        "location": "workout_place",
        "injuries": "injuries"
    }
    
    # Преобразуем данные пользователя в формат для промпта
    prompt_data = {}
    for user_field, prompt_field in field_mapping.items():
        if user_field in user_data and user_data[user_field]:
            prompt_data[prompt_field] = user_data[user_field]
    
    # Форматируем информацию о пользователе
    user_info = "\n".join([f"{key}: {value}" for key, value in prompt_data.items()])
    
    prompt = f"""
На основе следующей информации о пользователе создайте детальный план тренировок:

{user_info}

План должен включать:
1. Разминку (5-10 минут)
2. Основную часть с четкими упражнениями, подходами и повторениями
3. Заминку (5-10 минут)

План должен соответствовать уровню подготовки пользователя, учитывать его ограничения и травмы.
Формат плана должен быть структурированным, с разбивкой на дни и описанием каждого упражнения.

Для каждого упражнения укажите:
- Название упражнения
- Количество подходов
- Количество повторений или время выполнения
- Краткое описание техники выполнения

Выходной формат должен быть в виде Markdown.
"""
    return prompt

def create_meal_plan_prompt(user_data: dict) -> str:
    """
    Создает промпт для генерации плана питания на основе данных пользователя.
    
    Args:
        user_data: Словарь с данными пользователя
    
    Returns:
        str: Текст промпта для модели
    """
    # Маппинг полей из онбординга к полям в промпте
    field_mapping = {
        "goal": "goal",
        "weight": "weight",
        "height": "height",
        "gender": "gender",
        "age": "age",
        "allergies": "allergies",
        "preferences": "food_preferences"
    }
    
    # Преобразуем данные пользователя в формат для промпта
    prompt_data = {}
    for user_field, prompt_field in field_mapping.items():
        if user_field in user_data and user_data[user_field]:
            prompt_data[prompt_field] = user_data[user_field]
    
    # Форматируем информацию о пользователе
    user_info = "\n".join([f"{key}: {value}" for key, value in prompt_data.items()])
    
    prompt = f"""
На основе следующей информации о пользователе создайте план питания на неделю:

{user_info}

План должен включать:
1. Рекомендации по калорийности и макронутриентам (белки, жиры, углеводы)
2. План питания на 7 дней с конкретными блюдами на завтрак, обед, ужин и перекусы
3. Список продуктов для закупки на неделю

Учтите:
- План должен соответствовать цели пользователя (похудение/набор массы/поддержание формы)
- Учитывайте пищевые аллергии и предпочтения
- Включайте разнообразные продукты для сбалансированного рациона

Выходной формат должен быть в виде Markdown.
"""
    return prompt
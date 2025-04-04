"""Сервис для работы с LLM моделями через API OpenAI и Google Gemini"""
import os
import logging
import httpx
import json
import google.generativeai as genai
from typing import Dict, Any, Optional

from app.prompts import create_workout_prompt, create_meal_plan_prompt

# Инициализация Gemini
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
else:
    logging.warning("GOOGLE_API_KEY не найден. Функции Gemini будут недоступны.")

async def generate_with_gemini(prompt: str) -> str:
    """
    Генерация текста с помощью Google Gemini.
    
    Args:
        prompt: Текст промпта
        
    Returns:
        str: Сгенерированный текст
    """
    if not GOOGLE_API_KEY:
        return "API ключ Gemini не настроен. Обратитесь к администратору."
    
    try:
        model = genai.GenerativeModel('gemini-2.0-flash-lite')
        response = await model.generate_content_async(prompt)
        return response.text.strip()
    except Exception as e:
        logging.error(f"Error generating text with Gemini: {e}")
        return f"Произошла ошибка при генерации: {str(e)}"

class LLMService:
    """Класс для работы с LLM моделями через API OpenAI"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        """
        Инициализация сервиса LLM.
        
        Args:
            api_key: API-ключ OpenAI, если не указан, будет использоваться переменная окружения OPENAI_API_KEY
            model: Название модели для использования
        """
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            logging.warning("OPENAI_API_KEY не найден. Функции LLM будут недоступны.")
        
        self.model = model
        self.api_url = "https://api.openai.com/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def generate_text(self, prompt: str, max_tokens: int = 2048) -> str:
        """
        Генерация текста с помощью LLM.
        
        Args:
            prompt: Текст промпта
            max_tokens: Максимальное количество токенов в ответе
            
        Returns:
            str: Сгенерированный текст
            
        Raises:
            Exception: Если возникла ошибка при запросе к API
        """
        if not self.api_key:
            return "API ключ не настроен. Обратитесь к администратору."
        
        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_tokens,
                    "temperature": 0.7
                }
                
                response = await client.post(
                    self.api_url, 
                    headers=self.headers,
                    json=payload,
                    timeout=60.0
                )
                
                if response.status_code != 200:
                    logging.error(f"Error from OpenAI API: {response.status_code}, {response.text}")
                    return f"Ошибка API: {response.status_code}"
                
                response_json = response.json()
                return response_json["choices"][0]["message"]["content"].strip()
                
        except Exception as e:
            logging.error(f"Error generating text: {e}")
            return f"Произошла ошибка: {str(e)}"
    
    async def generate_workout_plan(self, user_data: Dict[str, Any]) -> str:
        """
        Генерация плана тренировок на основе данных пользователя.
        
        Args:
            user_data: Словарь с данными пользователя
            
        Returns:
            str: Сгенерированный план тренировок
        """
        prompt = create_workout_prompt(user_data)
        return await self.generate_text(prompt)
    
    async def generate_meal_plan(self, user_data: Dict[str, Any]) -> str:
        """
        Генерация плана питания на основе данных пользователя.
        
        Args:
            user_data: Словарь с данными пользователя
            
        Returns:
            str: Сгенерированный план питания
        """
        prompt = create_meal_plan_prompt(user_data)
        return await self.generate_text(prompt)

# Создаем синглтон для использования в разных частях приложения
llm_service = LLMService()
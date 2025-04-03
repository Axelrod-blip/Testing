# FitBot - Фитнес Бот для Telegram

FitBot - это Telegram бот, который помогает пользователям создавать персонализированные планы тренировок и питания на основе их предпочтений и особенностей.

## Возможности

- Сбор информации о пользователе через удобный онбординг
- Генерация персонализированных планов тренировок с использованием LLM
- Создание индивидуальных планов питания
- Сохранение данных пользователя и планов в базе данных

## Технологии

- Python 3.9+
- Aiogram 3.x - для взаимодействия с Telegram API
- SQLAlchemy - ORM для работы с базой данных
- OpenAI API - для генерации контента
- Google Gemini API (опционально) - альтернативная модель для генерации контента

## Установка и запуск

### Предварительные требования

- Python 3.9 или выше
- PostgreSQL
- Telegram Bot Token (от [@BotFather](https://t.me/BotFather))
- API ключ OpenAI или Google Gemini API

### Установка

1. Клонируйте репозиторий:

```bash
git clone https://github.com/yourusername/fitbot.git
cd fitbot
```

2. Создайте и активируйте виртуальное окружение:

```bash
python -m venv venv
# На Windows
venv\Scripts\activate
# На Linux/Mac
source venv/bin/activate
```

3. Установите зависимости:

```bash
pip install -r requirements.txt
```

4. Создайте файл `.env` в корневой директории проекта со следующим содержимым:

```
BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN
DATABASE_URL=postgresql+asyncpg://username:password@localhost/database_name
OPENAI_API_KEY=YOUR_OPENAI_API_KEY
# Опционально, если используете Google Gemini API
GOOGLE_API_KEY=YOUR_GEMINI_API_KEY
```

### Запуск

```bash
python main.py
```

## Структура проекта

```
fitbot/
├── app/
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── common.py
│   │   ├── onboarding.py
│   │   └── plans.py
│   ├── __init__.py
│   ├── config.py
│   ├── db.py
│   ├── keyboards.py
│   ├── llm_service.py
│   ├── models.py
│   ├── prompts.py
│   ├── states.py
│   └── ui_elements.py
├── .env
├── main.py
└── requirements.txt
```

## Команды бота

- `/start` - Начать работу с ботом
- `/help` - Показать справку
- `/onboard` - Начать или обновить онбординг
- `/profile` - Показать профиль пользователя
- `/workout` - Сгенерировать план тренировок
- `/mealplan` - Сгенерировать план питания
- `/cancel` - Отменить текущее действие

## Лицензия

MIT 
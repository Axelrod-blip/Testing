import ssl
import certifi

import asyncio
import logging
import sys

from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

# Импортируем объединенный роутер из пакета handlers
from app.handlers import handlers_router 
from app.config import bot # Импортируем инициализированного бота
from app.db import init_db, engine, SQLAlchemyStorage

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)

# Инициализация бота и диспетчера
# Заменяем MemoryStorage на SQLAlchemyStorage для персистентности
storage = SQLAlchemyStorage(engine)
dp = Dispatcher(storage=storage)

# Регистрация основного роутера
dp.include_router(handlers_router)

async def main():
    # Инициализация базы данных
    await init_db()
    
    # Запуск бота
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == '__main__':
    asyncio.run(main())
from aiogram import Router

# Импортируем роутеры из файлов
from .common import common_router # Import the new common router
from .onboarding import onboarding_router
from .profile import router as profile_router
from .plans import router as plans_router
# Добавьте импорты других ваших роутеров здесь...

# Создаем главный роутер, который будет включать все остальные
handlers_router = Router()

# Включаем роутеры в главный роутер
# Порядок может быть важен: сначала более специфичные (FSM), потом общие
handlers_router.include_router(onboarding_router)
handlers_router.include_router(profile_router)
handlers_router.include_router(plans_router)
handlers_router.include_router(common_router) # Include the common router last
# Включите другие ваши роутеры здесь...

__all__ = ['handlers_router']
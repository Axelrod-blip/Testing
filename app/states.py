from aiogram.fsm.state import StatesGroup, State

class OnboardingStates(StatesGroup):
    """States for the streamlined user onboarding process."""
    Goal = State()            # Главная цель?
    Experience = State()      # Опыт тренировок?
    Gender = State()          # Пол?
    Age = State()             # Возраст?
    Weight = State()          # Вес?
    Frequency = State()       # Сколько дней в неделю?
    Injuries = State()        # Есть травмы / ограничения?
    InjuryDetails = State()   # Запрос комментария о травмах
    Location = State()        # Где будете заниматься?
    LocationDetails = State() # Запрос комментария о месте
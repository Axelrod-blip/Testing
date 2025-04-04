from sqlalchemy import Column, Integer, String, Float, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    # Идентификатор пользователя в Telegram
    telegram_id = Column(Integer, primary_key=True)
    
    # Данные из онбординга
    goal = Column(String, nullable=True)  # mass, weight_loss, strength, health, other
    experience = Column(String, nullable=True)  # newbie, intermediate, advanced
    gender = Column(String, nullable=True)  # male, female, skip
    age = Column(Integer, nullable=True)
    weight = Column(Float, nullable=True)
    frequency = Column(Integer, nullable=True)  # Дней в неделю для тренировок
    injuries = Column(Boolean, nullable=True)  # True/False
    injury_details = Column(Text, nullable=True)  # Дополнительно при injuries=True
    location = Column(String, nullable=True)  # home, gym, outdoor, other
    location_details = Column(Text, nullable=True)  # Дополнительно при location=other
    
    # Дополнительные поля, требуемые для планов тренировок и питания
    name = Column(String, nullable=True)
    height = Column(Float, nullable=True)
    activity_level = Column(String, nullable=True)  # low, medium, high
    
    # Питание
    meals_per_day = Column(Integer, nullable=True)
    first_meal_time = Column(String, nullable=True)
    last_meal_time = Column(String, nullable=True)
    food_allergies = Column(Text, nullable=True)
    excluded_foods = Column(Text, nullable=True)
    favorite_foods = Column(Text, nullable=True)
    
    # Сгенерированные планы
    workout_plan = Column(Text, nullable=True)  # План тренировок
    meal_plan = Column(Text, nullable=True)  # План питания
    
    def __repr__(self):
        return f"<User(telegram_id={self.telegram_id})>"

    # Метод для получения словаря с данными для промптов
    def to_dict(self):
        """Возвращает словарь данных для использования в промптах."""
        fields = [
            'name', 'gender', 'age', 'height', 'weight', 'goal',
            'experience', 'frequency', 'location', 'injuries',
            'injury_details', 'location_details', 'activity_level',
            'meals_per_day', 'first_meal_time', 'last_meal_time', 
            'food_allergies', 'excluded_foods', 'favorite_foods'
        ]
        result = {}
        for field in fields:
            value = getattr(self, field, None)
            # Не включаем None значения
            if value is not None:
                result[field] = value
        return result
        
    # Преобразования для совместимости с промптами
    @property
    def fitness_level(self):
        """Возвращает уровень подготовки в формате, ожидаемом промптами."""
        if self.experience == 'newbie':
            return "Новичок"
        elif self.experience == 'intermediate':
            return "Средний"
        elif self.experience == 'advanced':
            return "Продвинутый"
        return self.experience
    
    @property
    def workouts_per_week(self):
        """Возвращает количество тренировок в неделю."""
        return self.frequency
    
    @property
    def workout_place(self):
        """Возвращает место тренировок в формате, ожидаемом промптами."""
        if self.location == 'home':
            return "Дома"
        elif self.location == 'gym':
            return "В зале"
        elif self.location == 'outdoor':
            return "На улице"
        elif self.location == 'other' and self.location_details:
            return self.location_details
        return self.location
    
    @property
    def has_injuries(self):
        """Возвращает информацию о травмах в текстовом формате."""
        return "Да" if self.injuries else "Нет"
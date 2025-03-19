from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.db.base import Gender, FitnessLevel, GoalType

class UserBase(BaseModel):
    telegram_id: int
    username: Optional[str] = None
    name: str
    age: int = Field(..., gt=0)
    gender: Optional[Gender] = None
    height: float = Field(..., gt=0)  # in cm
    weight: float = Field(..., gt=0)  # in kg
    fitness_level: FitnessLevel
    medical_restrictions: Optional[str] = None
    available_equipment: Optional[List[str]] = None
    available_time: int = Field(..., gt=0)  # minutes per week

class UserCreate(UserBase):
    pass

class UserUpdate(UserBase):
    pass

class User(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True 
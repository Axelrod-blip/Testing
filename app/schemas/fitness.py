from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from app.db.base import GoalType

class FitnessGoalBase(BaseModel):
    goal_type: GoalType
    target_weight: Optional[float] = None
    target_date: Optional[datetime] = None
    additional_details: Optional[str] = None

class FitnessGoalCreate(FitnessGoalBase):
    user_id: int

class FitnessGoal(FitnessGoalBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class WorkoutProgramBase(BaseModel):
    program_data: Dict[str, Any]
    is_active: bool = True

class WorkoutProgramCreate(WorkoutProgramBase):
    user_id: int
    goal_id: int

class WorkoutProgram(WorkoutProgramBase):
    id: int
    user_id: int
    goal_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True 
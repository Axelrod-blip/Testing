from sqlalchemy.orm import Session
from app.db.base import User, FitnessGoal, WorkoutProgram
from app.schemas.user import UserCreate, UserUpdate
from app.schemas.fitness import FitnessGoalCreate, WorkoutProgramCreate
from typing import Optional, List

class UserService:
    @staticmethod
    def get_user_by_telegram_id(db: Session, telegram_id: int) -> Optional[User]:
        return db.query(User).filter(User.telegram_id == telegram_id).first()

    @staticmethod
    def create_user(db: Session, user: UserCreate) -> User:
        db_user = User(**user.model_dump())
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def update_user(db: Session, telegram_id: int, user: UserUpdate) -> Optional[User]:
        db_user = UserService.get_user_by_telegram_id(db, telegram_id)
        if db_user:
            for key, value in user.model_dump(exclude_unset=True).items():
                setattr(db_user, key, value)
            db.commit()
            db.refresh(db_user)
        return db_user

    @staticmethod
    def create_fitness_goal(db: Session, goal: FitnessGoalCreate) -> FitnessGoal:
        db_goal = FitnessGoal(**goal.model_dump())
        db.add(db_goal)
        db.commit()
        db.refresh(db_goal)
        return db_goal

    @staticmethod
    def create_workout_program(db: Session, program: WorkoutProgramCreate) -> WorkoutProgram:
        db_program = WorkoutProgram(**program.model_dump())
        db.add(db_program)
        db.commit()
        db.refresh(db_program)
        return db_program

    @staticmethod
    def get_active_program(db: Session, user_id: int) -> Optional[WorkoutProgram]:
        return db.query(WorkoutProgram).filter(
            WorkoutProgram.user_id == user_id,
            WorkoutProgram.is_active == True
        ).first()

    @staticmethod
    def get_user_programs(db: Session, user_id: int) -> List[WorkoutProgram]:
        return db.query(WorkoutProgram).filter(WorkoutProgram.user_id == user_id).all() 
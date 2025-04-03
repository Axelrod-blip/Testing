import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, String, JSON, select, insert, update
from sqlalchemy.ext.asyncio import AsyncEngine
from aiogram.fsm.storage.base import BaseStorage, StorageKey, StateType
from sqlalchemy.exc import SQLAlchemyError
from typing import Dict, Any, Optional, List, Set
import json
import os
from app.config import DATABASE_URL
from app.models import Base

# Создаем движок для SQLite
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Логируем SQL запросы
    future=True
)

# Создаем фабрику сессий
async_session_factory = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Модель для хранения состояний FSM
class FSMState(Base):
    __tablename__ = "fsm_states"
    
    chat_id = Column(String, primary_key=True)
    user_id = Column(String, primary_key=True)
    state = Column(String, nullable=True)
    data = Column(JSON, nullable=True)
    
    def __repr__(self):
        return f"<FSMState(chat_id={self.chat_id}, user_id={self.user_id})>"

# Класс хранилища для FSM на базе SQLAlchemy
class SQLAlchemyStorage(BaseStorage):
    def __init__(self, engine):
        self.engine = engine
    
    async def set_state(self, key: StorageKey, state: StateType = None) -> None:
        try:
            async with async_session_factory() as session:
                result = await session.execute(
                    select(FSMState).where(
                        FSMState.chat_id == str(key.chat_id),
                        FSMState.user_id == str(key.user_id)
                    )
                )
                state_row = result.scalar_one_or_none()
                
                if state_row:
                    state_row.state = state.state if state else None
                else:
                    state_row = FSMState(
                        chat_id=str(key.chat_id),
                        user_id=str(key.user_id),
                        state=state.state if state else None,
                        data={}
                    )
                    session.add(state_row)
                
                await session.commit()
        except Exception as e:
            logging.error(f"Error setting state: {e}")
            
    async def get_state(self, key: StorageKey) -> Optional[str]:
        try:
            async with async_session_factory() as session:
                result = await session.execute(
                    select(FSMState.state).where(
                        FSMState.chat_id == str(key.chat_id),
                        FSMState.user_id == str(key.user_id)
                    )
                )
                state = result.scalar_one_or_none()
                return state
        except Exception as e:
            logging.error(f"Error getting state: {e}")
            return None
            
    async def set_data(self, key: StorageKey, data: Dict[str, Any]) -> None:
        try:
            async with async_session_factory() as session:
                result = await session.execute(
                    select(FSMState).where(
                        FSMState.chat_id == str(key.chat_id),
                        FSMState.user_id == str(key.user_id)
                    )
                )
                state_row = result.scalar_one_or_none()
                
                if state_row:
                    state_row.data = data
                else:
                    state_row = FSMState(
                        chat_id=str(key.chat_id),
                        user_id=str(key.user_id),
                        data=data
                    )
                    session.add(state_row)
                
                await session.commit()
        except Exception as e:
            logging.error(f"Error setting data: {e}")
            
    async def get_data(self, key: StorageKey) -> Dict[str, Any]:
        try:
            async with async_session_factory() as session:
                result = await session.execute(
                    select(FSMState.data).where(
                        FSMState.chat_id == str(key.chat_id),
                        FSMState.user_id == str(key.user_id)
                    )
                )
                data = result.scalar_one_or_none()
                return data or {}
        except Exception as e:
            logging.error(f"Error getting data: {e}")
            return {}
            
    async def update_data(self, key: StorageKey, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            async with async_session_factory() as session:
                result = await session.execute(
                    select(FSMState).where(
                        FSMState.chat_id == str(key.chat_id),
                        FSMState.user_id == str(key.user_id)
                    )
                )
                state_row = result.scalar_one_or_none()
                
                if state_row:
                    current_data = state_row.data or {}
                    current_data.update(data)
                    state_row.data = current_data
                else:
                    state_row = FSMState(
                        chat_id=str(key.chat_id),
                        user_id=str(key.user_id),
                        data=data
                    )
                    session.add(state_row)
                
                await session.commit()
                return state_row.data or {}
        except Exception as e:
            logging.error(f"Error updating data: {e}")
            return data
            
    async def close(self) -> None:
        pass
        
# Функция для создания таблиц
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logging.info("Database initialized")

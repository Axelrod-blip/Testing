from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.user_service import UserService
from app.schemas.user import User
from app.schemas.fitness import WorkoutProgram
from app.bot.bot import FitnessBot
import logging
import asyncio

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize bot
bot = FitnessBot()

@router.on_event("startup")
async def startup_event():
    """Initialize the bot on startup."""
    try:
        logger.info("Setting up bot handlers...")
        bot.setup_handlers()
        logger.info("Starting bot application...")
        await bot.application.initialize()
        await bot.application.start()
        # Start polling in the background
        asyncio.create_task(bot.application.run_polling(allowed_updates=Update.ALL_TYPES))
        logger.info("Bot started successfully")
    except Exception as e:
        logger.error(f"Error during bot startup: {str(e)}")
        raise

@router.on_event("shutdown")
async def shutdown_event():
    """Shutdown the bot on application shutdown."""
    try:
        logger.info("Stopping bot application...")
        await bot.application.stop()
        await bot.application.shutdown()
        logger.info("Bot stopped successfully")
    except Exception as e:
        logger.error(f"Error during bot shutdown: {str(e)}")
        raise

@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "bot": "running"}

@router.get("/users/{telegram_id}", response_model=User)
async def get_user(telegram_id: int, db: Session = Depends(get_db)):
    """Get user by Telegram ID."""
    user = UserService.get_user_by_telegram_id(db, telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/users/{telegram_id}/programs", response_model=list[WorkoutProgram])
async def get_user_programs(telegram_id: int, db: Session = Depends(get_db)):
    """Get all workout programs for a user."""
    user = UserService.get_user_by_telegram_id(db, telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserService.get_user_programs(db, user.id) 
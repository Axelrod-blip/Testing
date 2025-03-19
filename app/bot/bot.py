from telegram.ext import Application, ConversationHandler, CommandHandler
from app.core.config import settings
from app.db.session import SessionLocal
from app.bot.handlers import (
    start, name, age, gender, height, weight, fitness_level,
    goal, medical_restrictions, equipment, time, cancel, show_program
)
import logging

logger = logging.getLogger(__name__)

class FitnessBot:
    def __init__(self):
        self.token = settings.TELEGRAM_BOT_TOKEN
        if not self.token:
            raise ValueError("Telegram bot token is not set")
        logger.info("Initializing bot with token: %s", self.token[:5] + "..." + self.token[-5:])
        self.application = Application.builder().token(self.token).concurrent_updates(True).build()
        
    def setup_handlers(self):
        # Create conversation handler
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', start)],
            states={
                'NAME': [CommandHandler('cancel', cancel), name],
                'AGE': [CommandHandler('cancel', cancel), age],
                'GENDER': [CommandHandler('cancel', cancel), gender],
                'HEIGHT': [CommandHandler('cancel', cancel), height],
                'WEIGHT': [CommandHandler('cancel', cancel), weight],
                'FITNESS_LEVEL': [CommandHandler('cancel', cancel), fitness_level],
                'GOAL': [CommandHandler('cancel', cancel), goal],
                'MEDICAL_RESTRICTIONS': [CommandHandler('cancel', cancel), medical_restrictions],
                'EQUIPMENT': [CommandHandler('cancel', cancel), equipment],
                'TIME': [CommandHandler('cancel', cancel), time],
            },
            fallbacks=[CommandHandler('cancel', cancel)]
        )
        
        # Add handlers
        self.application.add_handler(conv_handler)
        self.application.add_handler(CommandHandler('program', show_program))
        
        # Add database session to bot data
        self.application.bot_data['db'] = SessionLocal()
        
        # Add error handler
        self.application.add_error_handler(self.error_handler)
        
    async def error_handler(self, update, context):
        """Handle errors in the bot."""
        logger.error(f"Update {update} caused error: {context.error}")
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "I apologize, but I encountered an error. Please try again later or contact support."
            ) 
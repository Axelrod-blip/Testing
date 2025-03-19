from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)
from app.db.base import Gender, FitnessLevel, GoalType
from app.services.user_service import UserService
from app.services.llm_service import FitnessProgramGenerator
from app.schemas.user import UserCreate
from app.schemas.fitness import FitnessGoalCreate, WorkoutProgramCreate
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)

# Conversation states
NAME, AGE, GENDER, HEIGHT, WEIGHT, FITNESS_LEVEL, GOAL, MEDICAL_RESTRICTIONS, EQUIPMENT, TIME = range(10)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the conversation and ask for the user's name."""
    await update.message.reply_text(
        "👋 Welcome to the Fitness Assistant Bot! I'll help you create a personalized fitness program.\n\n"
        "Please enter your name:"
    )
    return NAME

async def name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store the name and ask for age."""
    context.user_data['name'] = update.message.text
    await update.message.reply_text("Great! Now, please enter your age:")
    return AGE

async def age(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store the age and ask for gender."""
    try:
        age = int(update.message.text)
        if age <= 0:
            raise ValueError
        context.user_data['age'] = age
        keyboard = [
            [InlineKeyboardButton("Male", callback_data="male")],
            [InlineKeyboardButton("Female", callback_data="female")],
            [InlineKeyboardButton("Other", callback_data="other")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Please select your gender:", reply_markup=reply_markup)
        return GENDER
    except ValueError:
        await update.message.reply_text("Please enter a valid age (positive number):")
        return AGE

async def gender(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store the gender and ask for height."""
    query = update.callback_query
    await query.answer()
    context.user_data['gender'] = query.data
    await query.edit_message_text("Please enter your height in centimeters:")
    return HEIGHT

async def height(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store the height and ask for weight."""
    try:
        height = float(update.message.text)
        if height <= 0:
            raise ValueError
        context.user_data['height'] = height
        await update.message.reply_text("Please enter your weight in kilograms:")
        return WEIGHT
    except ValueError:
        await update.message.reply_text("Please enter a valid height (positive number):")
        return HEIGHT

async def weight(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store the weight and ask for fitness level."""
    try:
        weight = float(update.message.text)
        if weight <= 0:
            raise ValueError
        context.user_data['weight'] = weight
        keyboard = [
            [InlineKeyboardButton("Beginner", callback_data="beginner")],
            [InlineKeyboardButton("Intermediate", callback_data="intermediate")],
            [InlineKeyboardButton("Advanced", callback_data="advanced")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Please select your fitness level:", reply_markup=reply_markup)
        return FITNESS_LEVEL
    except ValueError:
        await update.message.reply_text("Please enter a valid weight (positive number):")
        return WEIGHT

async def fitness_level(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store the fitness level and ask for goal."""
    query = update.callback_query
    await query.answer()
    context.user_data['fitness_level'] = query.data
    keyboard = [
        [InlineKeyboardButton("Weight Loss", callback_data="weight_loss")],
        [InlineKeyboardButton("Muscle Gain", callback_data="muscle_gain")],
        [InlineKeyboardButton("Endurance", callback_data="endurance")],
        [InlineKeyboardButton("General Fitness", callback_data="general_fitness")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Please select your main fitness goal:", reply_markup=reply_markup)
    return GOAL

async def goal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store the goal and ask for medical restrictions."""
    query = update.callback_query
    await query.answer()
    context.user_data['goal'] = query.data
    await query.edit_message_text(
        "Do you have any medical restrictions or conditions I should know about?\n"
        "(If none, just type 'none')"
    )
    return MEDICAL_RESTRICTIONS

async def medical_restrictions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store medical restrictions and ask for available equipment."""
    context.user_data['medical_restrictions'] = update.message.text if update.message.text.lower() != 'none' else None
    await update.message.reply_text(
        "What equipment do you have available?\n"
        "(List items separated by commas, or type 'none' if you don't have any)"
    )
    return EQUIPMENT

async def equipment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store equipment and ask for available time."""
    equipment_text = update.message.text
    context.user_data['equipment'] = [item.strip() for item in equipment_text.split(',')] if equipment_text.lower() != 'none' else None
    await update.message.reply_text(
        "How many minutes per week can you dedicate to working out?\n"
        "(Enter a number)"
    )
    return TIME

async def time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store available time and generate the fitness program."""
    try:
        time = int(update.message.text)
        if time <= 0:
            raise ValueError
        context.user_data['available_time'] = time
        
        # Get database session from context
        db: Session = context.bot_data['db']
        
        # Create user
        user_data = context.user_data
        user_create = UserCreate(
            telegram_id=update.effective_user.id,
            username=update.effective_user.username,
            name=user_data['name'],
            age=user_data['age'],
            gender=Gender(user_data['gender']),
            height=user_data['height'],
            weight=user_data['weight'],
            fitness_level=FitnessLevel(user_data['fitness_level']),
            medical_restrictions=user_data['medical_restrictions'],
            available_equipment=user_data['equipment'],
            available_time=user_data['available_time']
        )
        
        user = UserService.create_user(db, user_create)
        
        # Create fitness goal
        goal_create = FitnessGoalCreate(
            user_id=user.id,
            goal_type=GoalType(user_data['goal'])
        )
        goal = UserService.create_fitness_goal(db, goal_create)
        
        # Generate program
        program_data = FitnessProgramGenerator.generate_program(user, goal)
        
        # Create workout program
        program_create = WorkoutProgramCreate(
            user_id=user.id,
            goal_id=goal.id,
            program_data=program_data
        )
        program = UserService.create_workout_program(db, program_create)
        
        # Send the program to the user
        await update.message.reply_text(
            f"🎉 Great! I've created your personalized fitness program.\n\n"
            f"📊 Analysis:\n{program_data['analysis']}\n\n"
            f"💪 Workout Plan:\n{program_data['workout_plan']}\n\n"
            f"🍽️ Nutrition:\n{program_data['nutrition']}\n\n"
            f"📈 Progress Tracking:\n{program_data['conclusion']}\n\n"
            "Use /program to view your program again at any time!"
        )
        
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text("Please enter a valid number of minutes:")
        return TIME
    except Exception as e:
        logger.error(f"Error generating program: {str(e)}")
        await update.message.reply_text(
            "I apologize, but I encountered an error while generating your program. "
            "Please try again later or contact support."
        )
        return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel the conversation."""
    await update.message.reply_text(
        "Operation cancelled. Use /start to begin again."
    )
    return ConversationHandler.END

async def show_program(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show the user's active program."""
    db: Session = context.bot_data['db']
    user = UserService.get_user_by_telegram_id(db, update.effective_user.id)
    
    if not user:
        await update.message.reply_text(
            "You haven't created a program yet. Use /start to create one!"
        )
        return
    
    program = UserService.get_active_program(db, user.id)
    if not program:
        await update.message.reply_text(
            "You don't have an active program. Use /start to create a new one!"
        )
        return
    
    program_data = program.program_data
    await update.message.reply_text(
        f"🎯 Your Active Fitness Program:\n\n"
        f"📊 Analysis:\n{program_data['analysis']}\n\n"
        f"💪 Workout Plan:\n{program_data['workout_plan']}\n\n"
        f"🍽️ Nutrition:\n{program_data['nutrition']}\n\n"
        f"📈 Progress Tracking:\n{program_data['conclusion']}"
    ) 
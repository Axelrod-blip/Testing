import google.generativeai as genai
from app.core.config import settings
from app.schemas.user import User
from app.schemas.fitness import FitnessGoal

class FitnessProgramGenerator:
    @staticmethod
    def generate_program(user: User, goal: FitnessGoal) -> dict:
        # Configure Gemini API
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-pro')

        # Prepare the prompt
        prompt = f"""You are an experienced fitness trainer and nutritionist. The user provided:
- Name: {user.name}
- Age: {user.age}
- Gender: {user.gender}
- Height: {user.height} cm
- Weight: {user.weight} kg
- Fitness Level: {user.fitness_level}
- Goal: {goal.goal_type}
- Available Time: {user.available_time} minutes per week
- Medical Restrictions: {user.medical_restrictions or 'None'}
- Available Equipment: {', '.join(user.available_equipment) if user.available_equipment else 'None'}

Based on this data:
1. Estimate approximate calorie needs.
2. Distribute protein, fats, and carbohydrates.
3. Provide a general 2-week workout plan (number of sessions per week, types of exercises).
4. Give basic nutritional recommendations (an example daily menu).

Response format:
1. Brief analysis (1 paragraph).
2. A 2-week workout plan (short description).
3. Dietary recommendations (sample menu).
4. A conclusion and advice on tracking progress."""

        # Generate response
        response = model.generate_content(prompt)
        
        # Parse and structure the response
        program_data = {
            "analysis": response.text.split("\n\n")[0],
            "workout_plan": response.text.split("\n\n")[1],
            "nutrition": response.text.split("\n\n")[2],
            "conclusion": response.text.split("\n\n")[3]
        }
        
        return program_data 
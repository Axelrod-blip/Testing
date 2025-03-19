# Fitness Assistant Telegram Bot

A Telegram bot that provides personalized fitness programs using AI. The bot collects user information and generates customized workout and nutrition plans using Google's Gemini API.

## Features

- User onboarding with comprehensive profile creation
- Personalized fitness program generation
- Weekly workout schedules
- Exercise details with sets, reps, and rest periods
- Progressive overload strategies
- Nutrition recommendations
- Recovery guidelines

## Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Docker and Docker Compose
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- Google Gemini API Key

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
DATABASE_URL=postgresql://postgres:postgres@db:5432/fitness_bot
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
GEMINI_API_KEY=your_gemini_api_key
LOG_LEVEL=INFO
```

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd fitness-assistant-bot
```

2. Create and activate a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running with Docker

1. Build and start the containers:
```bash
docker-compose up --build
```

2. The application will be available at `http://localhost:8000`

3. The Telegram bot will be ready to receive messages

## Running Locally

1. Start the PostgreSQL database:
```bash
docker-compose up db -d
```

2. Run the FastAPI application:
```bash
uvicorn app.main:app --reload
```

3. The application will be available at `http://localhost:8000`

## API Documentation

Once the application is running, you can access:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Available Endpoints

- `GET /`: Root endpoint
- `GET /api/v1/health`: Health check endpoint
- `GET /api/v1/users/{telegram_id}`: Get user by Telegram ID
- `GET /api/v1/users/{telegram_id}/programs`: Get all workout programs for a user
- `GET /api/v1/users/{telegram_id}/active-program`: Get the active workout program for a user

## Telegram Bot Commands

- `/start`: Start the conversation and create a new fitness program
- `/help`: Show available commands
- `/cancel`: Cancel the current operation

## Development

### Database Migrations

The project uses Alembic for database migrations. To create a new migration:

```bash
alembic revision --autogenerate -m "description"
```

To apply migrations:

```bash
alembic upgrade head
```

### Code Style

The project follows PEP 8 guidelines. You can check the code style using:

```bash
flake8 .
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 
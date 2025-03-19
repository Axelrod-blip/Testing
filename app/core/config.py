from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import PostgresDsn, validator

class Settings(BaseSettings):
    PROJECT_NAME: str = "Fitness Assistant Bot"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database settings
    DATABASE_URL: PostgresDsn
    
    @validator("DATABASE_URL", pre=True)
    def assemble_db_url(cls, v: Optional[str]) -> str:
        if isinstance(v, str):
            return v
        return str(v)
    
    # Telegram settings
    TELEGRAM_BOT_TOKEN: str
    
    # Google Gemini settings
    GEMINI_API_KEY: str
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings() 
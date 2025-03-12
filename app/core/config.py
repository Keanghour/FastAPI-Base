# Configuration file (e.g., DB, settings)

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./test.db"
    SECRET_KEY: str = "aTdsPDJA6ZnJxMp6GhpAyQ"
    ALGORITHM: str = "HS256" 
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 1440
    EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # Email configuration
    # EMAIL_USERNAME: str
    # EMAIL_PASSWORD: str
    # EMAIL_FROM: str
    # EMAIL_PORT: int
    # EMAIL_SERVER: str
    # FRONTEND_URL: str  # URL of your frontend for email verification links 


    class Config:
        env_file = ".env"  # Load environment variables from .env file

settings = Settings()
from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    # Google OAuth
    google_client_id: str = ""
    google_client_secret: str = ""
    
    # App settings
    secret_key: str = "dev-secret-key-change-in-production"
    database_url: str = "sqlite+aiosqlite:///./events.db"
    frontend_url: str = "http://localhost:5173"
    backend_url: str = "http://localhost:8000"
    
    # JWT Settings
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days
    
    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()

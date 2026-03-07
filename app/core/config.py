"""
Configuration management - Simplified for Pydantic v2
"""

from pydantic_settings import BaseSettings
from pydantic import ConfigDict, field_validator
from typing import List, Optional
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    """Application settings - Simplified for Pydantic v2"""
    
    # Application
    APP_NAME: str = "HRMS Lite"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    
    # Database - Use simple string instead of PostgresDsn
    DATABASE_URL: str = "postgresql://postgres:@localhost:5432/hrms_db"
    
    # CORS - Simple string
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS origins as list"""
        if self.CORS_ORIGINS:
            return [origin.strip() for origin in self.CORS_ORIGINS.split(',') if origin.strip()]
        return []
    
    @property
    def database_config(self) -> dict:
        """Get database config as dict for SQLAlchemy"""
        return {
            "url": self.DATABASE_URL,
            "pool_size": 20,
            "max_overflow": 10,
            "pool_pre_ping": True,
        }
    
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        arbitrary_types_allowed=True
    )

try:
    settings = Settings()
    print("Settings loaded successfully!")
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"Database: {settings.DATABASE_URL}")
    print(f"CORS Origins: {settings.cors_origins_list}")
except Exception as e:
    print(f"Error loading settings: {e}")
    raise
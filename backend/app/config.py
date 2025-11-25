"""Application configuration using Pydantic Settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    DATABASE_URL: str

    # Laserfiche OAuth
    LASERFICHE_CLIENT_ID: str
    LASERFICHE_CLIENT_SECRET: str
    LASERFICHE_REDIRECT_URI: str
    LASERFICHE_PROJECT_NAME: str = "Global"  # Your Laserfiche project name (use + for spaces)

    # Security
    SECRET_KEY: str
    TOKEN_ENCRYPTION_KEY: str

    # Application
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    FRONTEND_URL: str = "http://localhost:3000"  # Where to redirect after OAuth

    # Session
    SESSION_EXPIRY_DAYS: int = 7

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    @property
    def allowed_origins_list(self) -> List[str]:
        """Parse ALLOWED_ORIGINS into a list."""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]


# Global settings instance
settings = Settings()

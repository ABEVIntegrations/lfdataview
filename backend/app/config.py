"""Application configuration using Pydantic Settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Laserfiche OAuth
    LASERFICHE_CLIENT_ID: str
    LASERFICHE_CLIENT_SECRET: str
    LASERFICHE_REDIRECT_URI: str
    LASERFICHE_PROJECT_NAME: str = "Global"  # Your Laserfiche project name (use + for spaces)

    # Security
    SECRET_KEY: str  # Used for signing OAuth state cookies
    TOKEN_ENCRYPTION_KEY: str  # Used for encrypting access tokens in cookies

    # Application
    ENVIRONMENT: str = "development"
    DEBUG: bool = False  # SECURITY: Default to False for production safety
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    FRONTEND_URL: str = "http://localhost:3000"  # Where to redirect after OAuth

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    @field_validator('TOKEN_ENCRYPTION_KEY')
    @classmethod
    def validate_encryption_key(cls, v: str) -> str:
        """Validate that TOKEN_ENCRYPTION_KEY is a valid Fernet key."""
        from cryptography.fernet import Fernet
        try:
            Fernet(v.encode())
        except Exception:
            raise ValueError(
                "TOKEN_ENCRYPTION_KEY must be a valid Fernet key. "
                "Generate one with: python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
            )
        return v

    @property
    def allowed_origins_list(self) -> List[str]:
        """Parse ALLOWED_ORIGINS into a list."""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]


# Global settings instance
settings = Settings()

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    PROJECT_NAME: str = "AI-Powered Full-Stack Application"
    API_V1_STR: str = "/api/v1"
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    ENVIRONMENT: str = "development"

    # Database Settings
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres_dev_password@localhost:5434/ai_app_db"

    # Security & JWT Configuration
    JWT_SECRET: str = "dev_secret_key_change_in_production_89f72b9a7c3e41d89"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    JWT_ISSUER: str = "ai-fullstack-app"
    JWT_AUDIENCE: str = "ai-fullstack-client"

    # Cookie Configuration
    REFRESH_COOKIE_NAME: str = "refresh_token"
    COOKIE_SECURE: bool = False  # Set to True in production (HTTPS)
    COOKIE_SAMESITE: str = "lax"
    COOKIE_PATH: str = "/api/v1/auth"

    @property
    def sync_database_url(self) -> str:
        """Returns sync PostgreSQL URL for Alembic migrations."""
        return self.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()

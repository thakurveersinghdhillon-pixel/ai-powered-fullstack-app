from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    PROJECT_NAME: str = "AI-Powered Full-Stack Application"
    API_V1_STR: str = "/api/v1"
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    ENVIRONMENT: str = "development"

    # Database Settings
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres_dev_password@localhost:5434/ai_app_db"

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

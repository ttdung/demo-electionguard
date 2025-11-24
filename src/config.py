"""Application configuration settings."""
from functools import lru_cache
from pydantic import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    app_name: str = "ElectionGuard Demo"
    debug: bool = False
    api_v1_prefix: str = "/app/v1"

    # Database
    database_url: str = "sqlite+aiosqlite:///./election_demo.db"

    # Logging
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

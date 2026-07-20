import os
from functools import lru_cache
from typing import Optional, List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Application settings using Pydantic BaseSettings."""

    # App Settings
    DEBUG: bool = False
    SECRET_KEY: str
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    API_V1_STR: str = "/api/v1"

    # Database Settings
    DATABASE_URL: str

    # Redis Settings
    REDIS_URL: str = "redis://localhost:6379/0"

    # AI / LLM Settings
    AI_BASE_URL: str = "https://openrouter.ai/api/v1"
    AI_API_KEY: str
    MODEL_RESEARCH: str = "anthropic/claude-3-opus-20240229"
    MODEL_WRITING: str = "anthropic/claude-3-sonnet-20240229"
    MODEL_EDITING: str = "anthropic/claude-3-haiku-20240307"

    # Social Provider Settings
    ENABLE_TWITTER: bool = False
    TWITTER_API_KEY: Optional[str] = None
    TWITTER_API_SECRET: Optional[str] = None
    ENABLE_REDDIT: bool = False
    REDDIT_CLIENT_ID: Optional[str] = None
    REDDIT_CLIENT_SECRET: Optional[str] = None

    # Quality Gate Thresholds
    MIN_ENGAGEMENT_SCORE: float = 0.7
    MAX_SPAM_SCORE: float = 0.2
    MIN_READABILITY_SCORE: float = 0.5
    MIN_BRAND_CONSISTENCY: float = 0.8
    ENABLE_HUMAN_APPROVAL: bool = True

    # Scheduling
    MAX_RETRIES: int = 3
    RETRY_DELAY_SECONDS: int = 300

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )

@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()

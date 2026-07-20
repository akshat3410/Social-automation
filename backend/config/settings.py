from functools import lru_cache
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Application settings loaded from environment variables / .env."""

    # App
    DEBUG: bool = False
    SECRET_KEY: str
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]
    API_V1_STR: str = "/api/v1"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    # Optional separate key for encrypting stored social tokens.
    # Falls back to a key derived from SECRET_KEY when unset.
    ENCRYPTION_KEY: str | None = None
    # Create tables at startup instead of requiring alembic (dev convenience only).
    AUTO_CREATE_TABLES: bool = False

    # Database
    DATABASE_URL: str

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Rate limiting (fixed window, per client IP)
    RATE_LIMIT_AUTH_PER_MINUTE: int = 10
    RATE_LIMIT_GENERATE_PER_MINUTE: int = 5

    # AI / LLM
    AI_BASE_URL: str = "https://openrouter.ai/api/v1"
    AI_API_KEY: str
    MODEL_RESEARCH: str = "anthropic/claude-haiku-4.5"
    MODEL_WRITING: str = "anthropic/claude-sonnet-4.5"
    MODEL_EDITING: str = "anthropic/claude-haiku-4.5"
    LLM_TIMEOUT_SECONDS: float = 60.0
    NUM_DRAFT_VARIATIONS: int = 3

    # Embeddings (OpenAI-compatible endpoint). Memory/dedup features are
    # disabled gracefully when EMBEDDINGS_API_KEY is unset.
    EMBEDDINGS_BASE_URL: str = "https://api.openai.com/v1"
    EMBEDDINGS_API_KEY: str | None = None
    EMBEDDINGS_MODEL: str = "text-embedding-3-small"

    # Social providers
    ENABLE_TWITTER: bool = False
    TWITTER_API_KEY: str | None = None
    TWITTER_API_SECRET: str | None = None
    ENABLE_REDDIT: bool = False
    REDDIT_CLIENT_ID: str | None = None
    REDDIT_CLIENT_SECRET: str | None = None

    # Quality gate thresholds
    MIN_ENGAGEMENT_SCORE: float = 0.7
    MAX_SPAM_SCORE: float = 0.2
    MIN_READABILITY_SCORE: float = 0.5
    MIN_BRAND_CONSISTENCY: float = 0.8
    MIN_HUMAN_SCORE: float = 0.6
    ENABLE_HUMAN_APPROVAL: bool = True

    # Memory
    MEMORY_SIMILARITY_THRESHOLD: float = 0.85

    # Scheduling / retries
    SCHEDULER_POLL_INTERVAL_SECONDS: int = 60
    MAX_RETRIES: int = 3
    RETRY_DELAY_SECONDS: int = 300

    # Prompts
    PROMPTS_DIR: Path = BACKEND_DIR / "prompts"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def split_cors_origins(cls, v: object) -> object:
        if isinstance(v, str) and not v.strip().startswith("["):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()  # type: ignore[call-arg]

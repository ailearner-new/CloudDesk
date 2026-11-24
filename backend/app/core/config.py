"""Configuration settings for CloudDesk Support Platform."""

from functools import lru_cache
from pathlib import Path
from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    DEMO_MODE: bool = Field(default=True, description="Run in demo mode with fake providers")
    ENVIRONMENT: str = Field(default="development", description="Environment name")
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000"],
        description="Allowed CORS origins",
    )

    # Authentication
    JWT_SECRET: str = Field(
        default="dev-secret-change-in-production",
        description="JWT signing secret",
    )
    SUPABASE_JWT_SECRET: Optional[str] = Field(
        default=None,
        description="Supabase JWT secret (overrides JWT_SECRET when set)",
    )
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    JWT_EXPIRY_HOURS: int = Field(default=8, description="Token expiry in hours")

    # Database
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./data/support.db",
        description="Database connection URL",
    )
    CHECKPOINT_DB_PATH: str = Field(
        default="./data/checkpoints.db",
        description="LangGraph checkpoint database path",
    )

    # Redis
    REDIS_URL: str = Field(default="", description="Redis connection URL")
    USE_FAKE_REDIS: bool = Field(default=True, description="Use fakeredis instead of real Redis")

    # LLM
    LLM_PROVIDER: str = Field(default="fake", description="LLM provider: fake, openai, anthropic")
    LLM_API_KEY: str = Field(default="", description="LLM API key")
    LLM_MODEL: str = Field(default="gpt-4o-mini", description="LLM model name")
    LLM_TEMPERATURE: float = Field(default=0.1, description="LLM temperature")
    LLM_MAX_TOKENS: int = Field(default=2000, description="Max tokens per request")

    # Embeddings
    EMBEDDING_PROVIDER: str = Field(default="fake", description="Embedding provider: fake, openai")
    EMBEDDING_MODEL: str = Field(default="text-embedding-3-small", description="Embedding model")
    EMBEDDING_DIMENSIONS: int = Field(default=384, description="Embedding dimensions")

    # Vector Store
    VECTOR_STORE: str = Field(default="memory", description="Vector store: memory, qdrant")
    QDRANT_URL: str = Field(default="", description="Qdrant server URL")
    QDRANT_API_KEY: str = Field(default="", description="Qdrant API key")
    QDRANT_COLLECTION: str = Field(default="clouddesk_knowledge", description="Qdrant collection name")

    # Tools & Policy
    APPROVAL_REQUIRED_FOR_REFUNDS: bool = Field(default=True, description="Require approval for refunds")
    MAX_REFUND_WITHOUT_APPROVAL: int = Field(default=0, description="Max refund cents without approval")
    TOOL_TIMEOUT_SECONDS: int = Field(default=30, description="Tool execution timeout")

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = Field(default=120, description="Requests per minute per client")

    # Sample Data
    SAMPLE_DATA_DIR: str = Field(default="sample_data", description="Sample data directory")

    # Observability
    LANGCHAIN_TRACING_V2: bool = Field(default=False, description="Enable LangSmith tracing")
    LANGCHAIN_API_KEY: str = Field(default="", description="LangSmith API key")
    LANGCHAIN_PROJECT: str = Field(default="clouddesk-support", description="LangSmith project name")

    # Derived paths
    @property
    def knowledge_base_dir(self) -> Path:
        """Path to knowledge base markdown files."""
        return Path(self.SAMPLE_DATA_DIR) / "knowledge_base"

    @property
    def effective_jwt_secret(self) -> str:
        """Effective JWT secret (Supabase takes precedence)."""
        return self.SUPABASE_JWT_SECRET or self.JWT_SECRET


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
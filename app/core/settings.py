"""
Settings module for application configuration.

Loads environment variables and provides centralized configuration management
using Pydantic settings for type validation and environment variable parsing.
Supports different configurations for development, staging, and production.
"""
from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache


class BaseConfig(BaseSettings):
    """
    Base configuration shared across all environments.
    """
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/medical_db"
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # LLM Provider Configuration
    LLM_PROVIDER: str = "ollama"  # ollama, openai, anthropic

    # Ollama settings (default)
    OLLAMA_URL: str = "http://ollama:11434"
    OLLAMA_MODEL: str = "llama3.2"
    OLLAMA_TEMPERATURE: float = 0.3
    OLLAMA_TOP_P: float = 0.9
    OLLAMA_TOP_K: int = 40
    OLLAMA_NUM_CTX: int = 4096
    OLLAMA_NUM_PREDICT: Optional[int] = None  # None uses max_length from request
    OLLAMA_TIMEOUT: int = 60

    # OpenAI settings
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-3.5-turbo"

    # Anthropic settings
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-3-haiku-20240307"

    # Application
    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"
    APP_NAME: str = "Medical Backend API"
    APP_VERSION: str = "1.0.0"

    # Security
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    CORS_ORIGINS: str = "*"

    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # seconds

    # Monitoring
    METRICS_ENABLED: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = True


class DevelopmentConfig(BaseConfig):
    """
    Development environment configuration.

    Optimized for local development with debug features enabled.
    """
    APP_ENV: str = "development"
    LOG_LEVEL: str = "DEBUG"
    DEBUG: bool = True

    # Relaxed security for development
    CORS_ORIGINS: str = "*"

    # Smaller pool for development
    DB_POOL_SIZE: int = 3
    DB_MAX_OVERFLOW: int = 5

    # Disable rate limiting in development
    RATE_LIMIT_REQUESTS: int = 1000

    class Config:
        env_file = ".env.development"
        case_sensitive = True


class StagingConfig(BaseConfig):
    """
    Staging environment configuration.

    Similar to production but with additional debugging capabilities.
    """
    APP_ENV: str = "staging"
    LOG_LEVEL: str = "INFO"
    DEBUG: bool = False

    # Moderate pool size
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20

    class Config:
        env_file = ".env.staging"
        case_sensitive = True


class ProductionConfig(BaseConfig):
    """
    Production environment configuration.

    Optimized for performance, security, and reliability.
    """
    APP_ENV: str = "production"
    LOG_LEVEL: str = "WARNING"
    DEBUG: bool = False

    # Strict CORS - must be set via environment variable
    CORS_ORIGINS: str = ""

    # Larger pool for production load
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 40
    DB_POOL_TIMEOUT: int = 60

    # Stricter rate limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60

    class Config:
        env_file = ".env.production"
        case_sensitive = True


class TestingConfig(BaseConfig):
    """
    Testing environment configuration.

    Optimized for running tests with isolated database.
    """
    APP_ENV: str = "testing"
    LOG_LEVEL: str = "ERROR"
    DEBUG: bool = False

    # Use SQLite for testing
    DATABASE_URL: str = "sqlite:///:memory:"

    # Disable metrics in tests
    METRICS_ENABLED: bool = False

    # Mock LLM provider
    LLM_PROVIDER: str = "ollama"

    class Config:
        env_file = ".env.test"
        case_sensitive = True


def get_config() -> BaseConfig:
    """
    Get configuration based on APP_ENV environment variable.

    Returns:
        Configuration instance for the current environment
    """
    import os
    env = os.getenv("APP_ENV", "development").lower()

    config_map = {
        "development": DevelopmentConfig,
        "staging": StagingConfig,
        "production": ProductionConfig,
        "testing": TestingConfig,
    }

    config_class = config_map.get(env, DevelopmentConfig)
    return config_class()


@lru_cache()
def get_settings() -> BaseConfig:
    """
    Get cached settings instance.

    Uses lru_cache for performance - settings are loaded once
    and reused throughout the application lifecycle.

    Returns:
        Cached configuration instance
    """
    return get_config()


# Default settings instance for backward compatibility
settings = get_settings()

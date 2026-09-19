import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Intelligent Disaster Management Platform"
    APP_ENV: str = "production"
    DEBUG: bool = False

    # Security & JWT
    SECRET_KEY: str = "DEV_ONLY_SECRET_CHANGE_IN_PRODUCTION_ENV_VAR"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120

    # Rate Limiting
    RATE_LIMIT_DEFAULT: str = "100/minute"
    RATE_LIMIT_AUTH: str = "10/minute"

    # Database Connection
    DATABASE_URL: str = "postgresql+psycopg2://postgres:sql123@localhost:5432/postgres"

    # API Configuration
    API_V1_STR: str = "/api/v1"
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ]

    # AI Assistant & LLM Configuration
    LLM_PROVIDER: str = "rule_based"  # rule_based, gemini, or openai
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    ASSISTANT_MODEL: str = "gemini-1.5-flash"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()


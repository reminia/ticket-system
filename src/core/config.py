from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = Field("sqlite:///./tickets.db")
    REDIS_URL: str = Field("redis://localhost:6379")
    ANTHROPIC_API_KEY: str
    OPENAI_API_KEY: str
    ANTHROPIC_PROXY_URL: str = Field("")
    OPENAI_PROXY_URL: str = Field("")
    ANTHROPIC_MODEL: str = Field("claude-3-5-sonnet")
    OPENAI_MODEL: str = Field("gpt-4o")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )


settings = Settings()

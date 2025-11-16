from typing import ClassVar

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config: ClassVar[SettingsConfigDict] = {"env_file": ".env", "case_sensitive": True}

    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/pr_reviewer_db"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8080


settings = Settings()

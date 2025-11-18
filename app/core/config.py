from typing import ClassVar, Optional

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config: ClassVar[SettingsConfigDict] = {"env_file": ".env", "case_sensitive": True}

    DATABASE_URL: Optional[str] = None

    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8080

    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 40
    DB_POOL_PRE_PING: bool = True
    DB_POOL_RECYCLE: int = 3600
    DB_POOL_TIMEOUT: int = 30
    DB_ECHO: bool = False

    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "pr_reviewer_db"
    POSTGRES_PORT: int = 5432
    POSTGRES_HOST: str = "localhost"

    TEST_DATABASE_URL: Optional[str] = None
    TEST_POSTGRES_DB: str = "pr_reviewer_db_test"
    TEST_POSTGRES_HOST: str = "db"

    @model_validator(mode="after")
    def build_database_urls(self) -> "Settings":
        """Строит DATABASE_URL из POSTGRES_* переменных если не задан явно"""
        if not self.DATABASE_URL:
            self.DATABASE_URL = (
                f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )

        if not self.TEST_DATABASE_URL:
            self.TEST_DATABASE_URL = (
                f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.TEST_POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.TEST_POSTGRES_DB}"
            )

        return self


settings = Settings()

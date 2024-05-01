"""
Application wide settings read from env variables
"""

import pathlib
from enum import Enum
from urllib.parse import quote

from pydantic_settings import BaseSettings
from starlette.config import Config

# Get pathlib path of current file
current_dir = pathlib.Path(__file__).parent
env_path = current_dir / ".." / ".." / ".." / ".env"
config = Config(env_path)


class AppSettings(BaseSettings):
    """
    Basic Application Settings
    """

    APP_NAME: str = config("APP_NAME", default="FastAPI app")
    APP_DESCRIPTION: str | None = config("APP_DESCRIPTION", default=None)
    APP_VERSION: str | None = config("APP_VERSION", default=None)
    CONTACT_NAME: str | None = config("CONTACT_NAME", default=None)
    CONTACT_EMAIL: str | None = config("CONTACT_EMAIL", default=None)
    LOG_NAME: str = config("LOG_NAME", default="app.logger")
    LOG_ACCESS_NAME: str = config("LOG_ACCESS_NAME", default="access.logger")
    LOG_LEVEL: str = config("LOG_LEVEL", default="INFO")
    LOG_JSON_FORMAT: bool = config("LOG_JSON_FORMAT", default=False)
    LOG_INCLUDE_STACK: bool = config("LOG_INCLUDE_STACK", default=True)


class PostgresSettings(BaseSettings):
    """
    Postgres Database Settings
    """

    POSTGRES_USER: str = config("POSTGRES_USER", default="postgres")
    POSTGRES_PASSWORD: str = config("POSTGRES_PASSWORD", default="postgres")
    POSTGRES_SERVER: str = config("POSTGRES_SERVER", default="localhost")
    POSTGRES_PORT: int = config("POSTGRES_PORT", default=5432)
    POSTGRES_DB: str = config("POSTGRES_DB", default="postgres")
    POSTGRES_ASYNC_PREFIX: str = config(
        "POSTGRES_ASYNC_PREFIX", default="postgresql+asyncpg://"
    )
    POSTGRES_URI: str = f"{POSTGRES_ASYNC_PREFIX}{POSTGRES_USER}:{quote(POSTGRES_PASSWORD)}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"


class RedisQueueSettings(BaseSettings):
    """
    Redis settings for ARQ queue
    """

    REDIS_QUEUE_HOST: str = config("REDIS_QUEUE_HOST", default="localhost")
    REDIS_QUEUE_PORT: int = config("REDIS_QUEUE_PORT", default=6379)


class EnvironmentOption(Enum):
    """
    Environment Options
    """

    LOCAL = "local"
    STAGING = "staging"
    PRODUCTION = "production"


class EnvironmentSettings(BaseSettings):
    """
    Environment Settings
    """

    ENVIRONMENT: EnvironmentOption = config(
        "ENVIRONMENT", default=EnvironmentOption.LOCAL
    )


class Settings(
    AppSettings,
    PostgresSettings,
    RedisQueueSettings,
    EnvironmentSettings,
):
    """
    All Application Settings
    """


settings = Settings()

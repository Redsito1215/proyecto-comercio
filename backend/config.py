from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    flask_secret_key: str = Field(default="development-only")
    mongo_uri: str = "mongodb://localhost:27017/?replicaSet=rs0"
    mongo_db: str = "comercio_inteligente"
    app_host: str = "0.0.0.0"
    app_port: int = 5001
    clickhouse_host: str = "clickhouse"
    clickhouse_port: int = 8123
    clickhouse_database: str = "comercio_analytics"


@lru_cache
def get_settings() -> Settings:
    return Settings()

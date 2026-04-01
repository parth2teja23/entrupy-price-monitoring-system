from __future__ import annotations
from __future__ import annotations
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Price Monitoring System"
    DATABASE_URL: str = "sqlite+aiosqlite:///./entrupy.db"
    API_V1_STR: str = "/api/v1"
    API_KEY: str = "secret-entrupy-key"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
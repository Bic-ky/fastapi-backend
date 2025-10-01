# app/core/config.py
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "BackendApp"
    environment: str = "development"
    debug: bool = True
    database_url: str
    secret_key: str
    algorithm: str

    # v2-style config
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",      # ignore any .env keys you haven't declared
    )

@lru_cache()
def get_settings() -> "Settings":
    return Settings()

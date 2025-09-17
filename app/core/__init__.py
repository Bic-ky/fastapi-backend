from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # App-level settings
    app_name: str = "My Awesome FastAPI App"
    environment: str = "development"
    debug: bool = True

    # Database settings (replace with your actual database URL)
    database_url: str

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables or a .env file.
    """
    # General application settings
    app_name: str = "Backend App"
    environment: str = "development"
    debug: bool = True

    database_url: str

    model_config = SettingsConfigDict(env_file=".env")

# Create a single instance of the settings for the application
settings = Settings()
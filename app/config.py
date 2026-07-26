from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI-FOS"
    app_env: str = "development"
    database_url: str = "sqlite:///./ai_fos.db"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()

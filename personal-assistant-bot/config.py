import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    telegram_bot_token: str
    telegram_allowed_user_id: int
    anthropic_api_key: str
    openai_api_key: str
    database_url: str
    user_name: str = "Pedro"
    timezone: str = "America/Sao_Paulo"
    dashboard_password: str
    jwt_secret: str = "change-me-in-production"

    class Config:
        env_file = ".env"


settings = Settings()

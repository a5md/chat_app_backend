from pydantic_settings import BaseSettings,SettingsConfigDict

class Settings(BaseSettings):
    # App
    APP_NAME: str = "Email worker"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str | None = None

    # Email
    SMTP_HOST: str
    SMTP_PORT: int = 587
    SMTP_EMAIL: str
    SMTP_PASSWORD: str

    model_config = SettingsConfigDict(
        env_file="./.env",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()

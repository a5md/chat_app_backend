from pydantic_settings import BaseSettings,SettingsConfigDict

class Settings(BaseSettings):
    # App
    APP_NAME: str = "Chat API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # API
    API_PREFIX: str = "/api/v1"

    # MongoDB
    MONGODB_URI: str
    MONGODB_DATABASE: str

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str | None = None

    # JWT
    SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    #Google Oauth2
    GOOGLE_CLIENT_ID:str

    # OTP
    OTP_EXPIRE_SECONDS: int = 300
    OTP_MAX_ATTEMPTS: int = 5

    # CORS
    ALLOWED_ORIGINS: list[str] = [ 
        "http://localhost:5173"
    ]

    model_config = SettingsConfigDict(
        env_file="../.env",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()

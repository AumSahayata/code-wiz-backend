from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_DAYS: int
    OTP_TOKEN_EXPIRE_MINTUES: int
    EMAIL_ID: str
    EMAIL_PASSWORD: str
    GOOGLE_API_KEY: str
    GROQ_API_KEY: str
    
    model_config = SettingsConfigDict(
        env_file = ".env",
        extra = "ignore"
    )
    
Config = Settings()
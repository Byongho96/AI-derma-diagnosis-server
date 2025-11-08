from pydantic_settings import BaseSettings
from pathlib import Path
from typing import ClassVar

class Settings(BaseSettings):
    ALGORITHM: str = "HS256"    # Default : Update .env file with secure values
    SECRET_KEY: str = "secret_key"    # Default : Update .env file with secure values

    # Database configuration
    DATABASE_URL: str = "mysql+pymysql://root:rootpassword@localhost:3306/mydatabase"
    
    # JWT token settings
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Static files configuration
    STATIC_DIR: ClassVar[Path] = Path("static/images")
    STATIC_URL_PREFIX: str = "/static/images"
    IMG_SIZE: int = 1024

    # AI configuration
    AI_DEVICE: str = "-1"  # "cpu" | gpu index ("-1", "0", "1", ...) | "cuda"
    OLLAMA_HOST: str = "http://localhost:11434"

    class Config:
        env_file = ".env"
        extra = 'ignore'

settings = Settings()
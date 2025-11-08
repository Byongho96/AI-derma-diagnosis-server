from pydantic_settings import BaseSettings
from pathlib import Path
from typing import ClassVar

class Settings(BaseSettings):
    ALGORITHM: str = "HS256"    # Default : Update .env file with secure values
    SECRET_KEY: str = "secret_key"    # Default : Update .env file with secure values

    # Database configuration
    DATABASE_URL: str = "mysql+pymysql://user:password@localhost:3306/mydatabase"
    
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

    # Email configuration
    MAIL_USERNAME: str = "your_email@gmail.com"    
    MAIL_PASSWORD: str = "your_app_password"   
    MAIL_FROM: str = "your_email@gmail.com"          
    MAIL_FROM_NAME: str = "My App"

    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_PORT: int = 587
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False

    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True

    class Config:
        env_file = ".env"
        extra = 'ignore'

settings = Settings()
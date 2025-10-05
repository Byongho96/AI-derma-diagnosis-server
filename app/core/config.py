# app/core/config.py
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "mysql://root:your_password@localhost/mydatabase"
    SECRET_KEY: str = "your_very_secret_key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env" # .env 파일에서 환경변수를 로드할 수 있습니다.

settings = Settings()
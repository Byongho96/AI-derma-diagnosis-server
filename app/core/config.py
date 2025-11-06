from pydantic_settings import BaseSettings
from pathlib import Path
from typing import ClassVar

class Settings(BaseSettings):
    DATABASE_URL: str = "mysql+pymysql://root:rootpassword@localhost:3306/mydatabase"
    ALGORITHM: str = "HS256"
    SECRET_KEY: str = "secret_key"
    
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    STATIC_DIR: ClassVar[Path] = Path("static/images") # 3. 타입: Path로 수정
    STATIC_URL_PREFIX: str = "/static/images"
    IMG_SIZE: int = 1024

    AI_DEVICE: str = "cpu"  # "cuda" or "cpu"

    class Config:
        env_file = ".env" # load .env

settings = Settings()
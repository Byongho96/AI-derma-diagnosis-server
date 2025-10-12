from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "mysql+pymysql://root:rootpassword@localhost:3306/mydatabase"
    ALGORITHM: str = "HS256"
    SECRET_KEY: str = "secret_key"
    
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    class Config:
        env_file = ".env" # load .env

settings = Settings()
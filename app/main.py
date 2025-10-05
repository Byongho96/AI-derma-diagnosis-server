# app/main.py
from fastapi import FastAPI

from app.api.v1 import users
from app.db.session import engine
from app.db import base

# DB 테이블 생성
base.Base.metadata.create_all(bind=engine)

app = FastAPI()

# 라우터 포함
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the API"}
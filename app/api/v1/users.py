# app/api/v1/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.user import UserCreate, UserResponse, Token
from app.crud import crud_user
from app.services import auth_service
from app.models.user import User

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    ## 회원가입 API
    - **username**: 사용자 아이디
    - **password**: 사용자 비밀번호
    """
    db_user = crud_user.get_user_by_username(db, username=user_in.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = auth_service.get_password_hash(user_in.password)
    new_user = crud_user.create_user(db=db, username=user_in.username, hashed_password=hashed_password)
    return new_user


@router.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    ## 로그인 API (토큰 발급)
    - form-data 형식으로 `username`과 `password`를 받습니다.
    - 성공 시 Access Token을 발급합니다.
    """
    user = crud_user.get_user_by_username(db, username=form_data.username)
    if not user or not auth_service.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth_service.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(auth_service.get_current_user)):
    """
    ## 내 정보 확인 API
    - **(인증 필요)** 헤더에 `Authorization: Bearer <TOKEN>` 형식으로 토큰을 포함해야 합니다.
    - 현재 로그인된 사용자의 정보를 반환합니다.
    """
    return current_user
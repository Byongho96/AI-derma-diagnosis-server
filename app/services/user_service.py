from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.crud import crud_user
from app.schemas.user import RegisterRequest
from app.services import user_service
from app.models.user import User

import hashlib

def get_password_hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return get_password_hash(plain_password) == hashed_password

def register_new_user(db: Session, user_in: RegisterRequest):
    db_user = crud_user.get_user_by_username(db, username=user_in.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "type": "user_exists",
                "msg": "Username already registered"
            },
        )

    hashed_password = user_service.get_password_hash(user_in.password)
    new_user = crud_user.create_user(db=db, username=user_in.username, hashed_password=hashed_password, email=user_in.email)
    return new_user

def authenticate_user(db: Session, username: str, password: str):
    user = crud_user.get_user_by_username(db, username=username)
    if not user or not user_service.verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "type": "invalid_credentials",
                "msg": "Incorrect username or password"
            },
        )       
    return user

def update_user_username(db: Session, user: User, new_username: str) -> User:
    db_user = crud_user.get_user_by_username(db, username=new_username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"type": "user_exists", "msg": "Username already registered"}
        )
    return crud_user.update_username(db=db, user=user, new_username=new_username)

def delete_user_account(db: Session, user: User):
    crud_user.delete_user(db=db, user=user)
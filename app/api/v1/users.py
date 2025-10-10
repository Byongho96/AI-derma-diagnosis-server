# app/api/v1/users.py

from fastapi import APIRouter, Depends, status, Header, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.user import RegisterRequest, RegisterResponse, UserResponse, UpdateUsernameRequest
from app.schemas.auth import TokenResponse, RefreshTokenRequest, RefreshTokenResponse
from app.schemas.common import MessageResponse
from app.models.user import User
from app.services import user_service
from app.services import auth_service

router = APIRouter()

@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_in: RegisterRequest, db: Session = Depends(get_db)):
    new_user = user_service.register_new_user(db=db, user_in=user_in)
    return new_user


@router.post("/login", response_model=TokenResponse)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = user_service.authenticate_user(
        db=db, username=form_data.username, password=form_data.password
    )
    
    access_token = auth_service.create_access_token(data={"sub": user.username})
    refresh_token = auth_service.create_refresh_token(data={"sub": user.username})
    
    return {
        "access_token": access_token, 
        "refresh_token": refresh_token
    }

@router.post("/refresh", response_model=RefreshTokenResponse)
def refresh_access_token(token_request: RefreshTokenRequest, db: Session = Depends(get_db)):
    token = token_request.refresh_token

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"type": "invalid_token", "msg": "Could not validate credentials"},
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    username = auth_service.verify_refresh_token(token, credentials_exception)
    new_access_token = auth_service.create_access_token(data={"sub": username})

    return {"token_type": "Bearer", "access_token": new_access_token}

@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(auth_service.get_current_user)):
    return current_user

@router.patch("/me", response_model=UserResponse, summary="Update current user's username")
def update_username(
    user_update: UpdateUsernameRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    updated_user = user_service.update_user_username(
        db=db,
        user=current_user,
        new_username=user_update.new_username
    )
    return updated_user

@router.delete("/me", response_model=MessageResponse, summary="Delete current user account")
def delete_user(
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    user_service.delete_user_account(db=db, user=current_user)
    return {"msg": "User account deleted successfully"}
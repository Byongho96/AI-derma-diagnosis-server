from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.schemas.user import (
    RegisterRequest, LoginRequest, LoginResponse, 
    UserInfo, Username, RefreshToken, AccessToken,
    Email
)
from app.schemas.common import MessageResponse
from app.services import user_service, auth_service

router = APIRouter()

@router.post("/register", response_model=UserInfo, status_code=status.HTTP_201_CREATED, summary="Register a new user")
def register_user(user_in: RegisterRequest, db: Session = Depends(get_db)):
    """
    Register a new user with the provided email, username, and password.
    """
    new_user = user_service.register_new_user(db=db, user_in=user_in)
    return new_user


@router.post("/login", response_model=LoginResponse, summary="User login to obtain access and refresh tokens")
def login_for_access_token(login_request: LoginRequest, db: Session = Depends(get_db)):
    """
    Login with email and password to receive access and refresh tokens.
    """
    user = user_service.authenticate_user(
        db=db, email=login_request.email, password=login_request.password
    )
    
    access_token = auth_service.create_access_token(data={"sub": user.id})
    refresh_token = auth_service.create_refresh_token(data={"sub": user.id})
    
    return {
        "access_token": access_token, 
        "refresh_token": refresh_token,
        "user": user
    }


@router.post("/refresh", response_model=RefreshToken, summary="Refresh access token")
def refresh_access_token(token_request: RefreshToken, db: Session = Depends(get_db)):
    """
    Refresh the access token using a valid refresh token.
    """
    token = token_request.refresh_token

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"type": "invalid_token", "msg": "Could not validate credentials"},
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    user_id = auth_service.verify_refresh_token(token, credentials_exception)
    new_access_token = auth_service.create_access_token(data={"sub": user_id})

    return {"access_token": new_access_token}


@router.get("/me", response_model=UserInfo, summary="Get current user information")
def read_users_me(current_user: User = Depends(auth_service.get_current_user)):
    """
    Retrieve information about the currently authenticated user.
    """
    return current_user


@router.patch("/me", response_model=UserInfo, summary="Update current user's username")
def update_username(
    user_in: Username,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """
    Update the username of the currently authenticated user.
    """
    updated_user = user_service.update_user_username(
        db=db,
        user=current_user,
        new_username=user_in.new_username
    )
    return updated_user

@router.post("/reset-password", response_model=MessageResponse, status_code=status.HTTP_200_OK, summary="Request password reset")
async def reset_password(
    user_in: Email,
    db: Session = Depends(get_db)
):
    """
    Requests a password reset. A new temporary password will be sent via email.
    """
    return await user_service.request_password_reset(db=db, email=user_in.email)

@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT, summary="Delete current user account")
def delete_user(
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """
    Delete the account of the currently authenticated user.
    """
    user_service.delete_user_account(db=db, user=current_user)
    return
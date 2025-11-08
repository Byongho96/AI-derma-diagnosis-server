import secrets
import hashlib

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.crud import crud_user
from app.models.user import User
from app.schemas.user import RegisterRequest
from app.services import email_service


def get_password_hash(password: str) -> str:
    """
    Hashes a password using SHA256.
    """
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain password against its hash.
    """
    return get_password_hash(plain_password) == hashed_password


def register_new_user(db: Session, user_in: RegisterRequest) -> User:
    """
    Registers a new user after validating username and email.
    """
    if crud_user.get_user_by_username(db, username=user_in.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "type": "user_exists",
                "msg": "Username already registered"
            },
        )
    
    if crud_user.get_user_by_email(db, email=user_in.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "type": "email_exists",
                "msg": "Email already registered"
            },
        )

    hashed_password = get_password_hash(user_in.password)
    
    new_user = crud_user.create_user(
        db=db, 
        username=user_in.username, 
        hashed_password=hashed_password, 
        email=user_in.email
    )
    return new_user


def authenticate_user(db: Session, email: str, password: str) -> User:
    """
    Authenticates a user by email and password.
    """
    user = crud_user.get_user_by_email(db, email=email)
    
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "type": "invalid_credentials",
                "msg": "Incorrect email or password" # 'username' -> 'email'
            },
        )       
    return user


def update_user_username(db: Session, user: User, new_username: str) -> User:
    """
    Updates a user's username after checking for conflicts.
    """
    if crud_user.get_user_by_username(db, username=new_username):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"type": "user_exists", "msg": "Username already registered"}
        )
    return crud_user.update_username(db=db, user=user, new_username=new_username)

async def request_password_reset(db: Session, email: str) -> dict:
    """
    Handles password reset request. Generates a new temp password and emails it.
    """
    user = crud_user.get_user_by_email(db, email=email)
    
    if not user:
        # To prevent email enumeration, do not reveal that the email does not exist
        print(f"Password reset attempt for non-existent email: {email}")
        return {"message": "If an account with this email exists, a new password has been sent."}
        
    temp_password = secrets.token_urlsafe(10) # Create a temporary password
    hashed_password = get_password_hash(temp_password)
    
    crud_user.update_password(db, user=user, new_hashed_password=hashed_password)
    
    await email_service.send_password_reset_email(
        email_to=user.email, 
        new_password=temp_password
    )
    
    return {"message": "If an account with this email exists, a new password has been sent."}

def delete_user_account(db: Session, user: User) -> None:
    """
    Deletes a user's account.
    """
    crud_user.delete_user(db=db, user=user)
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from datetime import datetime, timedelta
from jwt import ExpiredSignatureError, InvalidSignatureError, PyJWTError, decode, encode
from app.core.config import settings
from app.models.user import User
from app.schemas.auth import TokenData

from app.db.session import get_db


# Extract Bearer token from Authorization header
security = HTTPBearer()

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"type": "invalid_token", "msg": "Could not validate credentials"},
        headers={"WWW-Authenticate": "Bearer"}
        )

    token = credentials.credentials
    print(token)
    try:
        payload = decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        print(payload)
        user_id: str = payload.get("sub")
        print(user_id)
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=user_id)
        
    except ExpiredSignatureError:
        # 1. 토큰이 만료되었을 때
        print("❌ Error: Token has expired.")
        raise credentials_exception # 기존 예외를 그대로 발생시키거나 커스텀 가능

    except InvalidSignatureError:
        # 2. 시크릿 키가 일치하지 않을 때
        print("❌ Error: Invalid signature. Check your SECRET_KEY.")
        raise credentials_exception

    except PyJWTError as e:
        # 3. 그 외 모든 JWT 관련 에러 (형식 오류 등)
        print(f"❌ A JWT error occurred: {e}")
        raise credentials_exception

    user = db.query(User).filter(User.id == token_data.user_id).first()
    if user is None:
        raise credentials_exception
        
    return user

def verify_refresh_token(token: str, credentials_exception):
    try:
        payload = decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        return user_id
    except PyJWTError:
        raise credentials_exception

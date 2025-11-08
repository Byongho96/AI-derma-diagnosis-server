import re
from pydantic import BaseModel, Field, EmailStr, field_validator

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=50)
    username: str = Field(..., min_length=3, max_length=50, pattern="^[a-zA-Z0-9_]+$")

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not re.search(r'[a-zA-Z]', v):
            raise ValueError('Password must contain at least one letter.')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number.')
        if re.search(r'[^a-zA-Z\d@$!%*#?&]', v):
            raise ValueError('Password must only contain letters, numbers, and @$!%*#?& special characters.')
        return v

class RefreshToken(BaseModel):
    refresh_token: str

class AccessToken(BaseModel):
    access_token: str

class UserInfo(BaseModel):
    id: str
    username: str
    email: EmailStr
    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    user: UserInfo

class Username(BaseModel):
    new_username: str = Field(..., min_length=3, max_length=50, pattern="^[a-zA-Z0-9_]+$")

class Email(BaseModel):
    email: EmailStr
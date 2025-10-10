import re
from pydantic import BaseModel, Field, EmailStr, field_validator

class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, pattern="^[a-zA-Z0-9_]+$")
    password: str = Field(..., min_length=8, max_length=50)
    email: EmailStr

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

class RegisterResponse(BaseModel):
    id: int
    username: str
    email: str
    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    class Config:
        from_attributes = True

class UpdateUsernameRequest(BaseModel):
    new_username: str = Field(..., min_length=3, max_length=50, pattern="^[a-zA-Z0-9_]+$")

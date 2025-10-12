from pydantic import BaseModel
from typing import Optional

class TokenData(BaseModel):
    user_id: Optional[str] | None = None

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class RefreshTokenResponse(BaseModel):
    access_token: str

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ReviewCreate(BaseModel):
    rating: int = Field(..., ge=1, le=5, description="Rating between 1 and 5")
    comment: Optional[str] = Field(None, max_length=1000, description="Review comment")


class ReviewResponse(BaseModel):
    id: str
    user_id: Optional[str]
    rating: int
    comment: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True
        to_camel = True


class ReviewList(BaseModel):
    reviews: list[ReviewResponse]
    total_count: int
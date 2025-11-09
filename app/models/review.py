import uuid
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models.base import Base

class Review(Base):
    __tablename__ = "reviews"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    user = relationship("User", back_populates="reviews")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    rating = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True)
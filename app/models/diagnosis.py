import uuid
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models.base import Base

class Diagnosis(Base):
    __tablename__ = "diagnoses"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="diagnoses")

    total_score = Column(Integer, nullable=False)
    original_image_url = Column(String(512), nullable=False)

    # wrinkle
    wrinkle_score = Column(Integer)
    wrinkle_image_url = Column(String(512))
    wrinkle_description = Column(Text)

    # acne
    acne_score = Column(Integer)
    acne_image_url = Column(String(512))
    acne_description = Column(Text)

    # atopy
    atopy_score = Column(Integer)
    atopy_image_url = Column(String(512))
    atopy_description = Column(Text)
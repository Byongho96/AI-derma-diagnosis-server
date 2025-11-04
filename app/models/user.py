import uuid
from sqlalchemy import Column, String
from app.models.base import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, index=True)
    username = Column(String(50), unique=True)
    hashed_password = Column(String(255))
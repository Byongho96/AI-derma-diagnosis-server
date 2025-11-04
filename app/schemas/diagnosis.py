from datetime import datetime
from pydantic import BaseModel, HttpUrl

class DiagnosisRequest(BaseModel):
    image: bytes

class DiagnosisDetailItem(BaseModel):
    score: int
    imageUrl: HttpUrl | str  
    description: str
    instruction: str

class DiagnosisDetail(BaseModel):
    id: str
    
    totalScore: int
    originalImageUrl: HttpUrl | str
    createdAt: datetime
    
    wrinkle: DiagnosisDetailItem
    acne: DiagnosisDetailItem
    atopy: DiagnosisDetailItem
    
    class Config:
        from_attributes = True 

class DiagnosisSimpleItem(BaseModel):
    score: int

class DiagnosisSimple(BaseModel):
    id: str
    
    totalScore: int
    originalImageUrl: HttpUrl | str
    createdAt: datetime
    
    wrinkle: DiagnosisSimpleItem
    acne: DiagnosisSimpleItem
    atopy: DiagnosisSimpleItem
    
    class Config:
        from_attributes = True 
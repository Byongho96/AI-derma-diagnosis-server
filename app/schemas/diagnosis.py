import uuid
from datetime import datetime
from fastapi import UploadFile
from pydantic import BaseModel, HttpUrl, ConfigDict, Field, computed_field
from pydantic.alias_generators import to_camel

class DiagnosisDetailItem(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True
    )
    
    score: int
    image_url: HttpUrl | str
    description: str | None
    recentScores: list[int] = []

class DiagnosisScoreItem(BaseModel):
    score: int

class BaseDiagnosisResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=to_camel,
        populate_by_name=True
    )

    id: str | uuid.UUID
    total_score: int
    original_image_url: str
    created_at: datetime

    wrinkle_score: int | None = Field(exclude=True)
    wrinkle_image_url: str | None = Field(exclude=True)
    wrinkle_description: str | None = Field(exclude=True)
    
    acne_score: int | None = Field(exclude=True)
    acne_image_url: str | None = Field(exclude=True)
    acne_description: str | None = Field(exclude=True)
    
    atopy_score: int | None = Field(exclude=True)
    atopy_image_url: str | None = Field(exclude=True)
    atopy_description: str | None = Field(exclude=True)

class DiagnosisHistory(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=to_camel,
        populate_by_name=True
    )
    total_score: int
    wrinkle_scores: list[int] = []
    acne_scores: list[int] = []
    atopy_scores: list[int] = []

class DiagnosisDetail(BaseDiagnosisResponse):
    recent_scores: list[int] = []

    recent_wrinkle_scores: list[int] = Field([], exclude=True)
    recent_acne_scores: list[int] = Field([], exclude=True)
    recent_atopy_scores: list[int] = Field([], exclude=True)
    
    @computed_field(alias="wrinkle")
    @property
    def compute_wrinkle(self) -> DiagnosisDetailItem | None:
        if self.wrinkle_score is None: return None
        return DiagnosisDetailItem(
            score=self.wrinkle_score,
            image_url=self.wrinkle_image_url or "",
            description=self.wrinkle_description,
            recentScores=self.recent_wrinkle_scores
        )

    @computed_field(alias="acne")
    @property
    def compute_acne(self) -> DiagnosisDetailItem | None:
        if self.acne_score is None: return None
        return DiagnosisDetailItem(
            score=self.acne_score,
            image_url=self.acne_image_url or "",
            description=self.acne_description,
            recentScores=self.recent_acne_scores
        )

    @computed_field(alias="atopy")
    @property
    def compute_atopy(self) -> DiagnosisDetailItem | None:
        if self.atopy_score is None: return None
        return DiagnosisDetailItem(
            score=self.atopy_score,
            image_url=self.atopy_image_url or "",
            description=self.atopy_description,
            recentScores=self.recent_atopy_scores
        )

class RecentDiagnosis(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True
    )

    id: str | uuid.UUID
    created_at: datetime
    total_score: int
    compared_to_previous: int | None

class DiagnosisSimple(BaseDiagnosisResponse):
    
    @computed_field(alias="wrinkle")
    @property
    def compute_wrinkle(self) -> DiagnosisScoreItem | None:
        if self.wrinkle_score is None: return None
        return DiagnosisScoreItem(score=self.wrinkle_score)

    @computed_field(alias="acne")
    @property
    def compute_acne(self) -> DiagnosisScoreItem | None:
        if self.acne_score is None: return None
        return DiagnosisScoreItem(score=self.acne_score)

    @computed_field(alias="atopy")
    @property
    def compute_atopy(self) -> DiagnosisScoreItem | None:
        if self.atopy_score is None: return None
        return DiagnosisScoreItem(score=self.atopy_score)

class DiagnosisList(BaseModel):
    items: list[DiagnosisSimple]
# app/schemas/diagnosis.py

import uuid
from datetime import datetime
from pydantic import BaseModel, HttpUrl, ConfigDict, Field, computed_field
from pydantic.alias_generators import to_camel

# --- 1. 상세 항목 스키마 (GET /{id} 용) ---
# (이전에 만든 스키마)
class DiagnosisDetailItem(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True
    )
    
    score: int
    image_url: HttpUrl | str # 입력은 snake_case, 출력은 'imageUrl'
    description: str | None
    instruction: str | None # DB 모델에 instruction이 없어서 추가했습니다.

# --- 2. 간단 항목 스키마 (GET /results, GET /recent 용) ---
class DiagnosisScoreItem(BaseModel):
    score: int

# --- 3. 기본 응답 스키마 (공통 속성) ---
# DB에서 읽어와야 할 모든 평평한(flat) 필드를 정의합니다.
class BaseDiagnosisResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,     # DB 객체 속성 읽기
        alias_generator=to_camel, # JSON 출력 시 camelCase로 변환
        populate_by_name=True
    )

    # 1:1 매핑되는 필드들 (출력 시 camelCase가 됨)
    id: str | uuid.UUID
    total_score: int
    original_image_url: str
    created_at: datetime

    # 중첩 객체 생성을 위한 원본 필드 (JSON 출력 시 숨김)
    wrinkle_score: int | None = Field(exclude=True)
    wrinkle_image_url: str | None = Field(exclude=True)
    wrinkle_description: str | None = Field(exclude=True)
    # wrinkle_instruction: str | None = Field(exclude=True) # DB에 추가 필요
    
    acne_score: int | None = Field(exclude=True)
    acne_image_url: str | None = Field(exclude=True)
    acne_description: str | None = Field(exclude=True)
    # acne_instruction: str | None = Field(exclude=True)
    
    atopy_score: int | None = Field(exclude=True)
    atopy_image_url: str | None = Field(exclude=True)
    atopy_description: str | None = Field(exclude=True)
    # atopy_instruction: str | None = Field(exclude=True)


# --- 4. 상세 응답 스키마 (GET /{id}, POST / 용) ---
class DiagnosisDetail(BaseDiagnosisResponse):
    
    @computed_field(alias="wrinkle")
    @property
    def compute_wrinkle(self) -> DiagnosisDetailItem | None:
        if self.wrinkle_score is None: return None
        return DiagnosisDetailItem(
            score=self.wrinkle_score,
            image_url=self.wrinkle_image_url or "",
            description=self.wrinkle_description,
            instruction=None # "Reborn" - DB에 instruction 컬럼 추가 필요
        )

    @computed_field(alias="acne")
    @property
    def compute_acne(self) -> DiagnosisDetailItem | None:
        if self.acne_score is None: return None
        return DiagnosisDetailItem(
            score=self.acne_score,
            image_url=self.acne_image_url or "",
            description=self.acne_description,
            instruction=None
        )

    @computed_field(alias="atopy")
    @property
    def compute_atopy(self) -> DiagnosisDetailItem | None:
        if self.atopy_score is None: return None
        return DiagnosisDetailItem(
            score=self.atopy_score,
            image_url=self.atopy_image_url or "",
            description=self.atopy_description,
            instruction=None
        )

# --- 5. 간단 응답 스키마 (GET /recent 용) ---
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

# --- 6. 목록 응답 스키마 (GET /results 용) ---
class DiagnosisList(BaseModel):
    items: list[DiagnosisSimple]
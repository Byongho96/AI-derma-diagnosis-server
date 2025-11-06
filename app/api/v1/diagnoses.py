# app/api/v1/users.py

from fastapi import APIRouter, Depends, Query, UploadFile, File, Response, status, HTTPException
from datetime import date, timedelta
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.services import auth_service, diagnosis_service
from typing import Optional

from app.crud.crud_diagonsis import get_diagnoses_by_user, get_recent_diagnosis_by_user, get_diagnosis_by_id

from app.schemas.diagnosis import DiagnosisDetail, DiagnosisList, DiagnosisSimple

router = APIRouter()

@router.get("/statistics")
def get_my_diagnosis_statistics(current_user: User = Depends(auth_service.get_current_user)):
    return {
        "avgScore" : 80,
        "numDiagnosis" : 5,
    }


@router.get("/results", response_model=DiagnosisList)
def get_diagnoses(
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user), 
    start_date: Optional[date] = Query(
        None,  # 1. 기본값 (유일한 위치 인수가 될 수 있음)
        description="start date (YYYY-MM-DD)", # 2. 'description=' 키워드 사용
        example="2023-01-01"                   # 3. 'example=' 키워드 사용
    ),
    end_date: Optional[date] = Query(
        None, 
        description="end date (YYYY-MM-DD)",   # 2. 'description=' 키워드 사용
        example="2024-01-01"                     # 3. 'example=' 키워드 사용
    )
):
    """
    로그인한 사용자의 진단 기록을 기간별로 조회합니다. (최신순)
    """
    if end_date is None:
        end_date = date.today()

    if start_date is None:
        start_date = end_date - timedelta(days=365) # 1년 전

    diagnoses_list = get_diagnoses_by_user(
        db=db, 
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date
    )
    
    # 스키마가 { "items": [...] } 형태를 기대하므로 딕셔너리로 반환
    return {"items": diagnoses_list}


@router.get("/recent", response_model=DiagnosisSimple)
def get_recent_diagnosis(
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """
    로그인한 사용자의 가장 최근 진단 기록 1건을 조회합니다.
    """
    recent_diagnosis = get_recent_diagnosis_by_user(
        db=db, 
        user_id=current_user.id
    )
    
    if not recent_diagnosis:
        # 204 No Content: 응답 바디가 없어야 하므로 Response 객체 직접 반환
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    
    return recent_diagnosis


@router.get("/{diagnosis_id}", response_model=DiagnosisDetail)
def get_diagnosis_result(
    diagnosis_id: str, # ❗️주의: DB 모델이 String UUID이므로 'int'가 아닌 'str'
    db: Session = Depends(get_db),
):
    """
    특정 ID의 진단 상세 결과를 조회합니다.
    """
    diagnosis = get_diagnosis_by_id(
        db=db,
        diagnosis_id=diagnosis_id
    )
    
    if not diagnosis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diagnosis not found or does not belong to the current user"
        )
        
    return diagnosis

@router.post("/", response_model=DiagnosisDetail)
async def create_diagnosis(
    db: Session = Depends(get_db),
    file: UploadFile = File(..., description="진단할 1024x1024 크기의 이미지 파일"),
    current_user: User = Depends(auth_service.get_current_user)
):
    """
    피부 진단 이미지를 업로드합니다.
    
    1. 이미지를 받아 1024x1024로 리사이즈 크롭 후 저장합니다.
    2. YOLO 모델로 주름을 분석하고 결과 이미지 저장 및 점수를 매깁니다.
    3. LLaVA 모델로 피부 조언을 생성합니다.
    4. 모든 결과를 DB에 저장하고 반환합니다.
    """
    
    # 모든 로직은 서비스 레이어로 위임
    diagnosis_result = await diagnosis_service.process_diagnosis(
        db=db, 
        file=file, 
        user_id=current_user.id
    )
    
    return diagnosis_result

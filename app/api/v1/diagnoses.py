from datetime import date, timedelta
from typing import Optional

from fastapi import (
    APIRouter, Depends, Query, UploadFile, 
    File, Response, status, HTTPException
)
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.services import auth_service, diagnosis_service
from app.crud.crud_diagonsis import (
    get_diagnoses_by_user, get_recent_diagnoses_by_user, get_recent_diagnosis_by_user, 
    get_diagnosis_by_id
)
from app.schemas.diagnosis import (
    DiagnosisDetail, DiagnosisHistory, DiagnosisList, RecentDiagnosis
)

router = APIRouter()

@router.get("/results", response_model=DiagnosisList)
def get_diagnoses(
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user), 
    start_date: Optional[date] = Query(
        None,
        description="start date (YYYY-MM-DD)",
        example="2023-01-01"
    ),
    end_date: Optional[date] = Query(
        None, 
        description="end date (YYYY-MM-DD)",
        example="2024-01-01"
    )
):
    """
    Get a list of diagnosis records for the logged-in user within the specified date range.
    If no dates are provided, defaults to the past year.
    """
    if end_date is None:
        end_date = date.today()

    if start_date is None:
        start_date = end_date - timedelta(days=365) # One year ago

    diagnoses_list = get_diagnoses_by_user(
        db=db, 
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date
    )
    
    return {"items": diagnoses_list}


@router.get("/recent")
def get_recent_diagnosis(
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """
    Get the most recent diagnosis record for the logged-in user.
    """
    recent_diagnosis = get_recent_diagnosis_by_user(
        db=db, 
        user_id=current_user.id,
        kth=1
    )
    
    if not recent_diagnosis:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    
    second_recent_diagnosis = get_recent_diagnosis_by_user(
        db=db,
        user_id=current_user.id,
        kth=2
    )

    compared_to_previous = 0
    if second_recent_diagnosis:
        compared_to_previous = recent_diagnosis.total_score - second_recent_diagnosis.total_score

    return RecentDiagnosis(
        id=recent_diagnosis.id,
        created_at=recent_diagnosis.created_at,
        total_score=recent_diagnosis.total_score,
        compared_to_previous=compared_to_previous
    )

@router.get("/recent/week", response_model=DiagnosisHistory)
def get_weekly_diagnoses(
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user), 
    endDate: Optional[date] = Query(
        None, 
        description="end date (YYYY-MM-DD)",
        example="2024-01-01"
    )
):
    """
    Get diagnosis records for the logged-in user from the past 7 days.
    """
    if endDate is None:
        endDate = date.today()

    start_date = endDate - timedelta(days=7)

    diagnoses_list = get_diagnoses_by_user(
        db=db, 
        user_id=current_user.id,
        start_date=start_date,
        end_date=endDate
    )

    result = DiagnosisHistory(
        total_score=diagnoses_list[0].total_score if diagnoses_list else 0,
        wrinkle_scores=[diag.wrinkle_score for diag in diagnoses_list if diag.wrinkle_score is not None],
        acne_scores=[diag.acne_score for diag in diagnoses_list if diag.acne_score is not None],
        atopy_scores=[diag.atopy_score for diag in diagnoses_list if diag.atopy_score is not None],
    )
    return result


@router.get("/recent/month", response_model=DiagnosisHistory)
def get_monthly_diagnoses(
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user), 
    endDate: Optional[date] = Query(
        None, 
        description="end date (YYYY-MM-DD)",
        example="2024-01-01"
    )
):
    """
    Get diagnosis records for the logged-in user from the past 30 days.
    """
    print("endDate:", endDate)
    if endDate is None:
        endDate = date.today()
    start_date = endDate - timedelta(days=30)

    diagnoses_list = get_diagnoses_by_user(
        db=db, 
        user_id=current_user.id,
        start_date=start_date,
        end_date=endDate
    )

    result = DiagnosisHistory(
        total_score=diagnoses_list[0].total_score if diagnoses_list else 0,
        wrinkle_scores=[diag.wrinkle_score for diag in diagnoses_list if diag.wrinkle_score is not None],
        acne_scores=[diag.acne_score for diag in diagnoses_list if diag.acne_score is not None],
        atopy_scores=[diag.atopy_score for diag in diagnoses_list if diag.atopy_score is not None],
    )
    return result


@router.get("/{diagnosis_id}", response_model=DiagnosisDetail)
def get_diagnosis_result(
    diagnosis_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """
    Get detailed diagnosis result by ID for the logged-in user.
    """
    diagnosis = get_diagnosis_by_id(
        db=db,
        diagnosis_id=diagnosis_id
    )
    
    if diagnosis.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Diagnosis does not belong to the current user"
        )

    if not diagnosis:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    
    recent_diagnoses = get_recent_diagnoses_by_user(
        db=db, 
        user_id=current_user.id,
        limit=3
    )

    diagnosis_detail = DiagnosisDetail.from_orm(diagnosis)
    
    diagnosis_detail.recent_scores = [
        diagnosis.total_score for diagnosis in recent_diagnoses
    ]
    
    diagnosis_detail.recent_wrinkle_scores = [
        diagnosis.wrinkle_score for diagnosis in recent_diagnoses if diagnosis.wrinkle_score is not None
    ]
    
    diagnosis_detail.recent_acne_scores = [
        diagnosis.acne_score for diagnosis in recent_diagnoses if diagnosis.acne_score is not None
    ]

    diagnosis_detail.recent_atopy_scores = [
        diagnosis.atopy_score for diagnosis in recent_diagnoses if diagnosis.atopy_score is not None
    ]

    return diagnosis


@router.post("/", response_model=DiagnosisDetail, status_code=status.HTTP_201_CREATED) # ❗️ 201 Created
async def create_diagnosis(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """
    Create a new diagnosis record by processing the uploaded image file for the logged-in user.
    """

    diagnosis_result = await diagnosis_service.process_diagnosis(
        db=db,
        file=file,
        user_id=current_user.id
    )

    diagnosis_detail = DiagnosisDetail.from_orm(diagnosis_result)

    recent_diagnoses = get_recent_diagnoses_by_user(
        db=db,
        user_id=current_user.id,
        limit=3
    )

    diagnosis_detail.recent_scores = [
        diagnosis.total_score for diagnosis in recent_diagnoses
    ]
    
    diagnosis_detail.recent_wrinkle_scores = [
        diagnosis.wrinkle_score for diagnosis in recent_diagnoses if diagnosis.wrinkle_score is not None
    ]
    
    diagnosis_detail.recent_acne_scores = [
        diagnosis.acne_score for diagnosis in recent_diagnoses if diagnosis.acne_score is not None
    ]

    diagnosis_detail.recent_atopy_scores = [
        diagnosis.atopy_score for diagnosis in recent_diagnoses if diagnosis.atopy_score is not None
    ]

    return diagnosis_detail
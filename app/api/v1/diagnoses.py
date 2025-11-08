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
    DiagnosisDetail, DiagnosisList, RecentDiagnosis
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


@router.get("/recent", response_model=RecentDiagnosis)
def get_recent_diagnosis(
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """
    Get the most recent diagnosis record for the logged-in user.
    """
    recent_diagnosis = get_recent_diagnosis_by_user(
        db=db, 
        user_id=current_user.id
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

@router.get("/results/recent/week", response_model=DiagnosisList)
def get_weekly_diagnoses(
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user), 
):
    """
    Get diagnosis records for the logged-in user from the past 7 days.
    """
    end_date = date.today()
    start_date = end_date - timedelta(days=7)

    diagnoses_list = get_diagnoses_by_user(
        db=db, 
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date
    )
    return {"items": diagnoses_list}


@router.get("/results/recent/month", response_model=DiagnosisList)
def get_monthly_diagnoses(
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user), 
):
    """
    Get diagnosis records for the logged-in user from the past 30 days.
    """
    end_date = date.today()
    start_date = end_date - timedelta(days=30)

    diagnoses_list = get_diagnoses_by_user(
        db=db, 
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date
    )
    return {"items": diagnoses_list}


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
    
    diagnosis.recent_scores = [
        dg.total_score for dg in get_recent_diagnoses_by_user(
            db=db,
            user_id=current_user.id,
            limit=3
        )
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

    diagnosis_result.recent_scores = [
        diagnosis.total_score for diagnosis in get_recent_diagnoses_by_user(
            db=db,
            user_id=current_user.id,
            limit=3
        )
    ]

    return diagnosis_result
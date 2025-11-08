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
    get_diagnoses_by_user, get_recent_diagnosis_by_user, 
    get_diagnosis_by_id
)
from app.schemas.diagnosis import (
    DiagnosisDetail, DiagnosisList, DiagnosisSimple, DiagnosisCreate
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


@router.get("/recent", response_model=DiagnosisSimple)
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
    
    return recent_diagnosis


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

    return diagnosis_result
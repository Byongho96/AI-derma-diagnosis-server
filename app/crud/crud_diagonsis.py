from datetime import date, datetime, time

from sqlalchemy.orm import Session

from app.models.diagnosis import Diagnosis


def create_diagnosis(
    db: Session,
    *,
    user_id: str,
    original_image_url: str,
    created_at: datetime = None,
    total_score: int,
    wrinkle_score: int = None,
    wrinkle_image_url: str = None,
    wrinkle_description: str = None,
    acne_score: int = None,
    acne_image_url: str = None,
    acne_description: str = None,
    atopy_score: int = None,
    atopy_image_url: str = None,
    atopy_description: str = None
) -> Diagnosis:
    """
    Saves a new diagnosis result to the database.
    """
    db_obj = Diagnosis(
        user_id=user_id,
        original_image_url=original_image_url,
        created_at=created_at,
        total_score=total_score,
        wrinkle_score=wrinkle_score,
        wrinkle_image_url=wrinkle_image_url,
        wrinkle_description=wrinkle_description,
        acne_score=acne_score,
        acne_image_url=acne_image_url,
        acne_description=acne_description,
        atopy_score=atopy_score,
        atopy_image_url=atopy_image_url,
        atopy_description=atopy_description
    )
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_diagnoses_by_user(
    db: Session, 
    user_id: str, 
    start_date: date, 
    end_date: date
) -> list[Diagnosis]:
    """
    Gets diagnoses for a specific user within a date range, ordered by most recent.
    """
    start_datetime = datetime.combine(start_date, time.min)
    end_datetime = datetime.combine(end_date, time.max)
    
    return db.query(Diagnosis).filter(
        Diagnosis.user_id == user_id,
        Diagnosis.created_at >= start_datetime,
        Diagnosis.created_at <= end_datetime
    ).order_by(Diagnosis.created_at.desc()).all()


def get_recent_diagnosis_by_user(db: Session, user_id: str) -> Diagnosis | None:
    """
    Gets the most recent diagnosis record for a specific user.
    """
    return db.query(Diagnosis).filter(
        Diagnosis.user_id == user_id
    ).order_by(Diagnosis.created_at.desc()).first()


def get_diagnosis_by_id(db: Session, diagnosis_id: str) -> Diagnosis | None:
    """
    Gets a specific diagnosis by its ID.
    """
    return db.query(Diagnosis).filter(
        Diagnosis.id == diagnosis_id,
    ).first()
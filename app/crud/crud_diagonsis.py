
from sqlalchemy.orm import Session
from app.models.diagnosis import Diagnosis # Diagnosis 모델 임포트
from datetime import date, datetime, time


def create_diagnosis(
    db: Session,
    *,
    user_id: str,
    original_image_url: str,
    created_at: datetime,
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
    진단 결과를 데이터베이스에 저장합니다.
    (개별 인자로 받도록 수정됨)
    """
    
    # 전달받은 개별 인자들로 SQLAlchemy 모델 객체를 직접 생성
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

# app/crud/crud_diagnosis.py

# create_diagnosis 함수는 이미 있다고 가정합니다.

def get_diagnoses_by_user(
    db: Session, 
    user_id: str, 
    start_date: date, 
    end_date: date
):
    """
    특정 사용자의 기간별 진단 기록을 날짜 내림차순(최신순)으로 조회합니다.
    """
    # date 객체를 datetime 객체로 변환 (DB의 datetime 컬럼과 비교하기 위해)
    # start_date: 그날의 시작 (00:00:00)
    start_datetime = datetime.combine(start_date, time.min)
    # end_date: 그날의 끝 (23:59:59)
    end_datetime = datetime.combine(end_date, time.max)
    
    return db.query(Diagnosis).filter(
        Diagnosis.user_id == user_id,
        Diagnosis.created_at >= start_datetime,
        Diagnosis.created_at <= end_datetime
    ).order_by(Diagnosis.created_at.desc()).all()


def get_recent_diagnosis_by_user(db: Session, user_id: str):
    """
    특정 사용자의 가장 최근 진단 기록 1건을 조회합니다.
    """
    return db.query(Diagnosis).filter(
        Diagnosis.user_id == user_id
    ).order_by(Diagnosis.created_at.desc()).first()


def get_diagnosis_by_id(db: Session, diagnosis_id: str):
    """
    특정 ID의 진단 기록을 조회하되, 반드시 요청한 사용자의 소유인지 확인합니다.
    """
    return db.query(Diagnosis).filter(
        Diagnosis.id == diagnosis_id,
    ).first()
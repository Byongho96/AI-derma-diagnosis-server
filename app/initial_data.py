import logging
from sqlalchemy.orm import Session
from app.db.session import get_db, engine, SessionLocal
from app.models.base import Base    
from app.models.user import User             
from app.models.diagnosis import Diagnosis  
from app.services.user_service import get_password_hash 

# Logging Configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Dummy Data Constants
DEFAULT_USER_EMAIL = "rumiskin11@gmail.com"
DEFAULT_USER_PASSWORD = "1q2w3e4r!"

IMG_ORIGINAL = "/dummy/dummy_original.jpg"
IMG_WRINKLE = "/dummy/dummy_wrinkle.jpg"
IMG_ACNE = "/dummy/dummy_acne.jpg"
IMG_ATOPY = "/dummy/dummy_atopy.jpg"

def init_db(session: Session) -> None:
    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Check if the default user exists
    user = session.query(User).filter(User.email == DEFAULT_USER_EMAIL).first()

    if not user:
        logger.info("Creating default user...")
        hashed_password = get_password_hash(DEFAULT_USER_PASSWORD)
        default_user = User(
            email=DEFAULT_USER_EMAIL,
            username="admin",
            hashed_password=hashed_password
        )
        session.add(default_user)
        session.commit()
        session.refresh(default_user)
        user = default_user
        logger.info("Default user created.")
    else:
        logger.info("Default user already exists.")

    # Check if dummy diagnosis data exists (e.g., check only 1)
    diagnosis_count = session.query(Diagnosis).filter(Diagnosis.user_id == user.id).count()

    if diagnosis_count == 0:
        logger.info("Creating dummy diagnosis data...")
        
        dummy_data = [
            Diagnosis(
                user_id=user.id,
                total_score=76,
                created_at="2023-10-01T10:00:00",
                original_image_url=IMG_ORIGINAL,
                wrinkle_score=60,
                wrinkle_image_url=IMG_WRINKLE,
                wrinkle_description="피부에 주름의 흔적이 보입니다. 사전에 피부를 충분히 보습해 주고, 관리하는 것이 좋습니다.",
                acne_score=75,
                acne_image_url=IMG_ACNE,
                acne_description="볼 쪽에 약간의 뾰루지가 있습니다. 꾸준한 세안과 보습이 필요하고, 자극적인 음식은 피하는 것이 좋습니다.",
                atopy_score=100,
                atopy_image_url=IMG_ATOPY,
                atopy_description="피부에 아토피 증상이 없습니다. 꾸준한 관리로 이 상태를 유지하세요."
            ),
            Diagnosis(
                user_id=user.id,
                total_score=86,
                created_at="2023-10-13T13:00:00",
                original_image_url=IMG_ORIGINAL,
                wrinkle_score=80,
                wrinkle_image_url=IMG_WRINKLE,
                wrinkle_description="이마 주름이 약간 보입니다. 충분한 수분 공급과 함께 주름 개선 제품을 사용하는 것이 좋습니다.",
                acne_score=80,
                acne_image_url=IMG_ACNE,
                acne_description="T존 부위에 유분기가 많습니다. 피지 조절이 필요하며, 자주 세안하는 것을 권장합니다.",
                atopy_score=100,
                atopy_image_url=IMG_ATOPY,
                atopy_description="피부에 아토피 증상이 없습니다. 꾸준한 관리로 이 상태를 유지하세요."
            ),
            Diagnosis(
                user_id=user.id,
                total_score=97,
                created_at="2023-10-27T21:00:00",
                original_image_url=IMG_ORIGINAL,
                wrinkle_score=95,
                wrinkle_image_url=IMG_WRINKLE,
                wrinkle_description="주름이 거의 보이지 않습니다. 피부가 탄력 있고 건강해 보입니다.",
                acne_score=90,
                acne_image_url=IMG_ACNE,
                acne_description="피부가 깨끗하고 뾰루지가 없습니다. 현재의 스킨케어 루틴을 유지하세요.",
                atopy_score=100,
                atopy_image_url=IMG_ATOPY,
                atopy_description="피부에 아토피 증상이 없습니다. 꾸준한 관리로 이 상태를 유지하세요."
            )
        ]
        
        session.bulk_save_objects(dummy_data)
        session.commit()
        logger.info("Dummy diagnosis data created.")
    else:
         logger.info("Dummy diagnosis data already exists.")


def main():
    logger.info("Initializing database and seeding data...")
    with SessionLocal() as session:
        try:
            init_db(session)
            logger.info("Database initialization and seeding finished.")
        except Exception as e:
            logger.error(f"An error occurred during DB initialization: {e}")

if __name__ == "__main__":
    main()
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.review import Review


def create_review(
    db: Session,
    *,
    user_id: str = None,
    rating: int,
    comment: str = None,
    created_at: datetime = None
) -> Review:
    """
    Creates a new review in the database.
    """
    db_obj = Review(
        user_id=user_id,
        rating=rating,
        comment=comment,
        created_at=created_at
    )
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_reviews_by_user(db: Session, user_id: str) -> list[Review]:
    """
    Gets reviews for a specific user, ordered by most recent.
    """
    return db.query(Review).filter(Review.user_id == user_id).order_by(Review.created_at.desc()).all()
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.crud import crud_review
from app.models.review import Review


def create_new_review(
    db: Session, 
    user_id: str = None, 
    rating: int = None, 
    comment: str = None
) -> Review:
    """
    Creates a new review after validating rating.
    """
    if rating is None or rating < 1 or rating > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "type": "invalid_rating",
                "msg": "Rating must be between 1 and 5"
            },
        )

    new_review = crud_review.create_review(
        db=db,
        user_id=user_id,
        rating=rating,
        comment=comment
    )
    return new_review


def get_reviews_by_user(db: Session, user_id: str) -> list[Review]:
    """
    Gets all reviews from the database for a specific user, ordered by most recent.
    """
    return crud_review.get_reviews_by_user(db=db, user_id=user_id)
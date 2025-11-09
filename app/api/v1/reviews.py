from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.services import auth_service, review_service
from app.schemas.review import ReviewCreate, ReviewResponse, ReviewList

router = APIRouter()


@router.post("", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED, summary="Create a new review")
def create_review(
    review_in: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """
    Create a new anonymous review. No authentication required.
    """
    new_review = review_service.create_new_review(
        db=db,
        user_id=current_user.id,
        rating=review_in.rating,
        comment=review_in.comment
    )
    return new_review


@router.get("", response_model=ReviewList, summary="Get all reviews")
def get_reviews(db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    """
    Get all reviews from the database, ordered by most recent.
    """
    reviews = review_service.get_reviews_by_user(
        db=db,
        user_id=current_user.id
    )
    
    return ReviewList(
        reviews=reviews,
        total_count=len(reviews)
    )
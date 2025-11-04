# app/api/v1/users.py

from fastapi import APIRouter, Depends, Query
from datetime import date, timedelta

from app.models.user import User
from app.services import auth_service
from typing import Optional

router = APIRouter()

@router.get("/statistics")
def get_my_diagnosis_statistics(current_user: User = Depends(auth_service.get_current_user)):
    return {
        "avgScore" : 80,
        "numDiagnosis" : 5,
    }


@router.get("/results")
def get_diagnoses(current_user: User = Depends(auth_service.get_current_user), 
    start_date: Optional[date] = Query(
        None, 
        description="start date (YYYY-MM-DD)",
        example="2023-01-01"
    ),
    end_date: Optional[date] = Query(
        None, 
        description="end date (YYYY-MM-DD)",
        example="2024-01-01"
    )):

    if end_date is None:
        end_date = date.today()

    if start_date is None:
        start_date = end_date - timedelta(days=365) # 1 year ago

    return {
        "items": [
            {
                "totalScore": 50,
                "originalImage" : "https://...",
                "wrinkle": {
                    "score" : 45,
                },
                "acne": {
                    "score" : 45,
                },
                "atopy": {
                    "score" : 45,
                },
            },
            {
                "totalScore": 50,
                "originalImage" : "https://...",
                "wrinkle": {
                    "score" : 45,
                },
                "acne": {
                    "score" : 45,
                },
                "atopy": {
                    "score" : 45,
                },
            },
            {
                "totalScore": 50,
                "originalImage" : "https://...",
                "wrinkle": {
                    "score" : 45,
                },
                "acne": {
                    "score" : 45,
                },
                "atopy": {
                    "score" : 45,
                },
            }
        ]
    }

@router.get("/recent")
def get_recent_diagnosis(current_user: User = Depends(auth_service.get_current_user)):
    return {
        "totalScore": 50,
        "originalImage" : "https://picsum.photos/400/300",
        "wrinkle": {
            "score" : 45,
        },
        "acne": {
            "score" : 45,
        },
        "atopy": {
            "score" : 45,
        }
    }

@router.get("/{diagnosis_id}")
def get_diagnosis_result(diagnosis_id: int, current_user: User = Depends(auth_service.get_current_user)):
    return {
        "totalScore": 50,
        "originalImage" : "https://...",
        "wrinkle": {
            "score" : 45,
            "image": "https://...",
            "description" : "You have such beatiful wrinkles",
            "instruction" : "Reborn"
        },
        "acne": {
            "score" : 45,
            "image": "https://...",
            "description" : "You have such beatiful wrinkles",
            "instruction" : "Reborn"
        },
        "atopy": {
            "score" : 45,
            "image": "https://...",
            "description" : "You have such beatiful wrinkles",
            "instruction" : "Reborn"
        }
    }

@router.post("/")
def create_diagnosis(current_user: User = Depends(auth_service.get_current_user)):
    return {
        "totalScore": 50,
        "originalImage" : "https://...",
        "wrinkle": {
            "score" : 45,
            "image": "https://...",
            "description" : "You have such beatiful wrinkles",
            "instruction" : "Reborn"
        },
        "acne": {
            "score" : 45,
            "image": "https://...",
            "description" : "You have such beatiful wrinkles",
            "instruction" : "Reborn"
        },
        "atopy": {
            "score" : 45,
            "image": "https://...",
            "description" : "You have such beatiful wrinkles",
            "instruction" : "Reborn"
        }
    }
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime

from app.database import get_db
from app.models import User, Review
from app.dectecor import run_code_analysis   # reuse the analyzer
from app.auth import get_current_user

router = APIRouter(prefix="/review", tags=["Code Review"])


class ReviewRequest(BaseModel):
    code: str


class IssueSchema(BaseModel):
    summary: str
    severity: str
    suggestion: str


class ReviewResponse(BaseModel):
    id: int
    language_type: str
    is_clean: bool
    review_summary: str
    issues: list[IssueSchema]
    top_suggestions: list[str]
    created_at: datetime

    class Config:
        from_attributes = True


@router.post("/", response_model=ReviewResponse)
def create_review(
    data: ReviewRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),   # need this from your auth setup
):
    report = run_code_analysis(data.code)   # CodeReport object

    new_review = Review(
        user_id=current_user.id,
        language_type=report.language,
        code_snippet=data.code,
        is_clean=report.is_clean,
        review_summary=report.review,
        issues=[issue.model_dump() for issue in report.issues],
        top_suggestions=report.top_suggestions,
    )
    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    return new_review


@router.get("/", response_model=list[ReviewResponse])
def get_reviews(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(Review)
        .filter(Review.user_id == current_user.id)
        .order_by(Review.created_at.desc())
        .all()
    )


@router.get("/{review_id}", response_model=ReviewResponse)
def get_review_detail(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    review = (
        db.query(Review)
        .filter(Review.id == review_id, Review.user_id == current_user.id)
        .first()
    )
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review
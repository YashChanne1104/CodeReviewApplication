from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.models import User, Review
from app.auth import hash_password, verify_password

router = APIRouter()


# -------------------------
# Request Models
# -------------------------

class SignupRequest(BaseModel):
    username: str
    email: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class ReviewRequest(BaseModel):
    user_id: int
    review_summary: str
    language_type: str


# -------------------------
# Signup
# -------------------------

@router.post("/signup")
def signup(
    data: SignupRequest,
    db: Session = Depends(get_db)
):
    existing_user = (
        db.query(User)
        .filter(
            (User.username == data.username) |
            (User.email == data.email)
        )
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username or Email already exists"
        )

    new_user = User(
        username=data.username,
        email=data.email,
        password_hash=hash_password(data.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "Signup successful",
        "username": new_user.username
    }


# -------------------------
# Login
# -------------------------

@router.post("/login")
def login(
    data: LoginRequest,
    db: Session = Depends(get_db)
):
    user = (
        db.query(User)
        .filter(User.username == data.username)
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    if not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    return {
        "message": "Login successful",
        "username": user.username
    }


# -------------------------
# Users list
# -------------------------

@router.get("/users")
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()

@router.post("/review")
def review(
    data: ReviewRequest,
    db: Session = Depends(get_db)
):
    new_review = Review(
    user_id=data.user_id,
    review_summary=data.review_summary,
    language_type=data.language_type
)
    db.add(new_review)
    db.commit()
    db.refresh(new_review)

    return {
        "message": "Review successful",
        "review": new_review.review_summary
    }


@router.get("/review")
def get_review(db: Session = Depends(get_db)):
    return db.query(Review).all()
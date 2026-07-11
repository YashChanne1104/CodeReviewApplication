from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.models import User
from app.auth import hash_password, verify_password, create_access_token

router = APIRouter(tags=["login and signup"])


class SignupRequest(BaseModel):
    username: str
    email: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/signup")
def signup(data: SignupRequest, db: Session = Depends(get_db)):
    existing_user = (
        db.query(User)
        .filter((User.username == data.username) | (User.email == data.email))
        .first()
    )
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or Email already exists")

    new_user = User(
        username=data.username,
        email=data.email,
        password_hash=hash_password(data.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "Signup successful", "username": new_user.username}


@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()

    if user is None or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    access_token = create_access_token(data={"sub": str(user.id)})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user.username,
    }


@router.get("/users")
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()
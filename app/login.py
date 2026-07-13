from fastapi import APIRouter, Depends, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.auth import hash_password, verify_password, create_access_token

router = APIRouter(tags=["login and signup"])


@router.post("/signup")
def signup(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    existing_user = (
        db.query(User)
        .filter((User.username == username) | (User.email == email))
        .first()
    )

    if existing_user:
        return RedirectResponse(
            url="/signup?error=Username or Email already exists",
            status_code=303
        )

    new_user = User(
        username=username,
        email=email,
        password_hash=hash_password(password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return RedirectResponse(url="/login", status_code=303)


@router.post("/login")
def login(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == username).first()

    if user is None or not verify_password(password, user.password_hash):
        return RedirectResponse(
            url="/login?error=Invalid username or password",
            status_code=303
        )

    access_token = create_access_token(data={"sub": str(user.id)})

    response = RedirectResponse(url="/dashboard", status_code=303)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,     # JS can't read it — safer against XSS
        max_age=60 * 60 * 24,   # 1 day, matches token expiry
        samesite="lax",
    )
    return response


@router.get("/users")
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()
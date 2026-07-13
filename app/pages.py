from fastapi import APIRouter, Request, Depends, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, Review
from app.auth import get_current_user_from_request
from app.dectecor import run_code_analysis

router = APIRouter(tags=["Pages"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/")
def home_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_request(request, db)
    return templates.TemplateResponse(request, "home.html", {"user": user})


@router.get("/signup")
def signup_page(request: Request, error: str = None):
    return templates.TemplateResponse(request, "signup.html", {"error": error, "user": None})


@router.get("/login")
def login_page(request: Request, error: str = None):
    return templates.TemplateResponse(request, "login.html", {"error": error, "user": None})


@router.get("/logout")
def logout():
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("access_token")
    return response


@router.get("/dashboard")
def dashboard_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_request(request, db)
    if not user:
        return RedirectResponse(url="/login?error=Please log in first", status_code=303)

    reviews = (
        db.query(Review)
        .filter(Review.user_id == user.id)
        .order_by(Review.created_at.desc())
        .all()
    )

    return templates.TemplateResponse(request, "dashboard.html", {
        "user": user,
        "reviews": reviews,
        "result": None,
    })


@router.post("/dashboard/review")
def dashboard_review(request: Request, code: str = Form(...), db: Session = Depends(get_db)):
    user = get_current_user_from_request(request, db)
    if not user:
        return RedirectResponse(url="/login?error=Please log in first", status_code=303)

    report = run_code_analysis(code)

    new_review = Review(
        user_id=user.id,
        language_type=report.language,
        code_snippet=code,
        is_clean=report.is_clean,
        review_summary=report.review,
        issues=[issue.model_dump() for issue in report.issues],
        top_suggestions=report.top_suggestions,
    )
    db.add(new_review)
    db.commit()
    db.refresh(new_review)

    reviews = (
        db.query(Review)
        .filter(Review.user_id == user.id)
        .order_by(Review.created_at.desc())
        .all()
    )

    return templates.TemplateResponse(request, "dashboard.html", {
        "user": user,
        "reviews": reviews,
        "result": new_review,
    })


@router.get("/report/{review_id}")
def report_page(review_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_request(request, db)
    if not user:
        return RedirectResponse(url="/login?error=Please log in first", status_code=303)

    review = (
        db.query(Review)
        .filter(Review.id == review_id, Review.user_id == user.id)
        .first()
    )
    if not review:
        return RedirectResponse(url="/dashboard", status_code=303)

    return templates.TemplateResponse(request, "report.html", {"user": user, "review": review})
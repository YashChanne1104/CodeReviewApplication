from fastapi import FastAPI

from app.database import create_tables
from app.login import router as login_router
from app.dectecor import router as detector_router
from app.review import router as review_router

# Create database tables
create_tables()

app = FastAPI(
    title="AI Code Review API",
    version="1.0.0",
    description="FastAPI + Mistral AI Code Review System"
)

# Register routers
app.include_router(login_router)
app.include_router(detector_router)
app.include_router(review_router)


@app.get("/")
def home():
    return {
        "status": "success",
        "message": "AI Code Review API Running"
    }
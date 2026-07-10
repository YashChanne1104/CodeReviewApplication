from fastapi import FastAPI

from app.database import create_tables
from app.login import router as login_router

# Create tables when application starts
create_tables()

app = FastAPI(
    title="Code Review API",
    version="1.0.0"
)

app.include_router(login_router)


@app.get("/")
def home():
    return {"message": "Code Review API Running"}
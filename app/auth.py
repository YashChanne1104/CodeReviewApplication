from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import os
from app.database import get_db
from app.models import User

SECRET_KEY = os.getenv("SECRET_KEY", "fallback-dev-key-change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 2   # 1 day
bearer_scheme = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# -------------------------
# Password hashing
# -------------------------

def hash_password(password: str) -> str:
    # bcrypt only supports up to 72 bytes
    password = password.encode("utf-8")[:72].decode("utf-8", "ignore")
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    plain_password = plain_password.encode("utf-8")[:72].decode("utf-8", "ignore")
    return pwd_context.verify(plain_password, hashed_password)


# -------------------------
# JWT
# -------------------------

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# -------------------------
# For API routes (Swagger / Bearer header) — raises 401 if invalid
# -------------------------

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    return user


# -------------------------
# For page routes (cookie-based) — returns None instead of raising
# -------------------------

def get_current_user_from_request(request: Request, db: Session) -> User | None:
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            return None
    except JWTError:
        return None
    return db.query(User).filter(User.id == int(user_id)).first()
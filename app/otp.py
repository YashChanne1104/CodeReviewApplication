import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models import OTP, User
from app.email_service import send_otp_email

OTP_EXPIRY_MINUTES = 5


def generate_and_send_otp(user: User, db: Session) -> bool:
    code = str(random.randint(100000, 999999))
    expires_at = datetime.utcnow() + timedelta(minutes=OTP_EXPIRY_MINUTES)

    otp_entry = OTP(user_id=user.id, code=code, expires_at=expires_at)
    db.add(otp_entry)
    db.commit()

    return send_otp_email(user.email, code)


def verify_otp(user: User, code: str, db: Session) -> bool:
    otp_entry = (
        db.query(OTP)
        .filter(
            OTP.user_id == user.id,
            OTP.code == code,
            OTP.is_used == False,
            OTP.expires_at > datetime.utcnow(),
        )
        .order_by(OTP.created_at.desc())
        .first()
    )

    if not otp_entry:
        return False

    otp_entry.is_used = True
    db.commit()
    return True
    
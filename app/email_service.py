import smtplib
import os
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_SERVER = "smtp-relay.brevo.com"
SMTP_PORT = 587

SENDER_EMAIL = "yashchanne9122001@gmail.com"   # the address recipients will see as "From" — must be a verified sender in Brevo


def send_otp_email(to_email: str, code: str) -> bool:
    subject = "Your ReviewAgent Password Reset Code"
    body = f"""
Hi,

Your password reset code is: {code}

This code expires in 5 minutes. If you didn't request this, ignore this email.

- ReviewAgent
"""

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg["To"] = to_email

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.sendmail(SENDER_EMAIL, to_email, msg.as_string())
        return True
    except Exception as e:
        print(f"Email send failed: {e}")
        return False
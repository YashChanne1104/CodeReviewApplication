import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv


load_dotenv()

GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_PASS = os.getenv("GMAIL_APP_PASS")


def send_otp_email(to_email: str, code: str) -> bool:
    try:
        msg = MIMEMultipart()
        msg["From"]    = GMAIL_USER
        msg["To"]      = to_email
        msg["Subject"] = "Your ReviewAgent Password Reset Code"

        msg.attach(MIMEText(f"""
            <p>Hi,</p>
            <p>Your password reset code is: <strong>{code}</strong></p>
            <p>This code expires in 5 minutes.</p>
            <p>If you didn't request this, ignore this email.</p>
            <p>- ReviewAgent</p>
        """, "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(GMAIL_USER, GMAIL_PASS)
            smtp.sendmail(GMAIL_USER, to_email, msg.as_string())

        print(f"OTP email sent to {to_email}")
        return True

    except Exception as e:
        print(f"Email send failed: {e}")
        return False
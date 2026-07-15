import os
# pyrefly: ignore [missing-import]
import resend
from dotenv import load_dotenv

load_dotenv()

resend.api_key = os.getenv("RESEND_API_KEY")

SENDER_EMAIL = "onboarding@resend.dev"  


def send_otp_email(to_email: str, code: str) -> bool:
    try:
        resend.Emails.send({
            "from": f"ReviewAgent <{SENDER_EMAIL}>",
            "to": [to_email],
            "subject": "Your ReviewAgent Password Reset Code",
            "html": f"""
                <p>Hi,</p>
                <p>Your password reset code is: <strong>{code}</strong></p>
                <p>This code expires in 5 minutes. If you didn't request this, ignore this email.</p>
                <p>- ReviewAgent</p>
            """,
        })
        return True
    except Exception as e:
        print(f"Email send failed: {e}")
        return False
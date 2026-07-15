from app.email_service import send_otp_email
result = send_otp_email("[EMAIL_ADDRESS]", "123456")
print(result)
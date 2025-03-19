import random
import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.db.models import PasswordResetToken, User
# from app.services.email_service import send_email  # Commented out for now

def generate_otp() -> str:
    """Generate a 6-digit OTP."""
    return str(random.randint(100000, 999999))

# def send_otp_email(email: str, otp: str):
#     """Send OTP to the user's email."""
#     subject = "Your OTP Code"
#     body = f"Your OTP code is: {otp}. It expires in 5 minutes."
#     send_email(email, subject, body)  # Implement send_email in email_service

def create_otp(db: Session, email: str):
    """Generate and store OTP in DB, return it for testing."""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Generate OTP
    otp = generate_otp()
    expires_at = datetime.datetime.utcnow() + datetime.timedelta(minutes=5)

    # Store OTP in DB
    otp_entry = PasswordResetToken(email=email, token=otp, expires_at=expires_at)
    db.add(otp_entry)
    db.commit()

    # Commented out email sending
    # send_otp_email(email, otp)

    return {
        "message": "OTP generated successfully (email sending not yet implemented)",
        "email": email,
        "otp": otp,  # Return OTP in response for testing (REMOVE in production)
        "expires_at": expires_at.isoformat()
    }

def verify_otp(db: Session, email: str, otp: str):
    """Verify if the OTP is correct and not expired."""
    otp_entry = (
        db.query(PasswordResetToken)
        .filter(
            PasswordResetToken.email == email, 
            PasswordResetToken.token == otp
        )
        .first()
    )

    if not otp_entry:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    # Check expiration
    if otp_entry.expires_at < datetime.datetime.utcnow():
        raise HTTPException(status_code=400, detail="OTP expired")

    # Mark OTP as used
    otp_entry.token = None  # Clear the token after use
    db.commit()

    return {"message": "OTP verified successfully"}

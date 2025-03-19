from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.otp_service import create_otp, verify_otp
from app.schemas.otp_schema import OTPRequest, OTPVerifyRequest

router = APIRouter()  # Use APIRouter here

@router.post("/send")
def send_otp(request: OTPRequest, db: Session = Depends(get_db)):
    return create_otp(db, request.email)

@router.post("/verify")
def verify_otp_code(request: OTPVerifyRequest, db: Session = Depends(get_db)):
    return verify_otp(db, request.email, request.otp)

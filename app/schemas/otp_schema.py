from pydantic import BaseModel, EmailStr

class OTPRequest(BaseModel):
    email: EmailStr

class OTPVerifyRequest(BaseModel):
    email: EmailStr
    otp: str  # OTP is a string to prevent leading-zero issues

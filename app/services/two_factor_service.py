import pyotp
import qrcode
import io
import base64
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.db.models import User

def generate_2fa_secret() -> str:
    return pyotp.random_base32()

def generate_qr_code(username: str, secret: str) -> str:
    uri = pyotp.totp.TOTP(secret).provisioning_uri(name=username, issuer_name="MyApp")
    qr = qrcode.make(uri)
    img_io = io.BytesIO()
    qr.save(img_io, format="PNG")
    img_io.seek(0)

    # Convert to Base64 for JSON response
    qr_base64 = base64.b64encode(img_io.read()).decode('utf-8')
    return qr_base64

def verify_2fa_code(secret: str, token: str) -> bool:
    totp = pyotp.TOTP(secret)
    return totp.verify(token)

def enable_2fa(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.is_2fa_enabled:
        raise HTTPException(status_code=400, detail="2FA already enabled")

    # Generate secret and store it correctly
    secret = generate_2fa_secret()
    user.totp_secret = secret  
    user.is_2fa_enabled = True
    db.commit()
    db.refresh(user)

    return {
        "secret": secret,
        "qr_code": generate_qr_code(user.username, secret)  # Base64 encoded QR
    }

def disable_2fa(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.totp_secret = None
    user.is_2fa_enabled = False
    db.commit()
    return {"message": "2FA disabled successfully"}

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.two_factor_service import enable_2fa, disable_2fa, verify_2fa_code
from app.schemas.two_factor_schema import TwoFactorVerifyRequest
from app.db.models import User

router = APIRouter()

@router.post("/enable")
def enable_two_factor(user_id: int, db: Session = Depends(get_db)):
    return enable_2fa(db, user_id)

@router.post("/disable")
def disable_two_factor(user_id: int, db: Session = Depends(get_db)):
    return disable_2fa(db, user_id)

@router.post("/verify")
def verify_two_factor(data: TwoFactorVerifyRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == data.user_id).first()
    if not user or not user.is_2fa_enabled or not user.totp_secret:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="2FA is not enabled")
    
    if not verify_2fa_code(user.totp_secret, data.token):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid 2FA token")
    
    return {"message": "2FA verification successful"}

from datetime import datetime, timedelta
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.db.models import RevokedToken
from app.core.config import settings

def is_token_revoked(db: Session, token: str) -> bool:
    revoked_token = db.query(RevokedToken).filter(RevokedToken.token == token).first()
    return revoked_token is not None

def revoke_token(db: Session, token: str):
    revoked_token = RevokedToken(token=token)
    db.add(revoked_token)
    db.commit()


def create_password_reset_token(email: str) -> str:
    expires_at = datetime.utcnow() + timedelta(minutes=settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": email, "exp": expires_at}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def verify_password_reset_token(token: str) -> str:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise ValueError("Invalid token")
        return email
    except JWTError:
        raise ValueError("Invalid token")
    

def revoke_all_tokens_for_user(db: Session, user_id: int):
    # Revoke all tokens for the user (example for revoked tokens table)
    db.query(RevokedToken).filter(RevokedToken.user_id == user_id).delete()
    db.commit()


    
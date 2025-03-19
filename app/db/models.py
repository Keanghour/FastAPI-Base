# app\db\models.py
# ORM models (SQLAlchemy or other)

from datetime import datetime, timedelta, timezone
from sqlalchemy import Column, DateTime, Integer, String, Boolean, func
from .session import Base
from sqlalchemy import ForeignKey

UTC_PLUS_7 = timezone(timedelta(hours=7))

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(150), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    # Ensure timestamps use UTC+07:00
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),  # Stored in UTC
        default=lambda: datetime.now(UTC_PLUS_7)  # Python default in UTC+07:00
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        default=lambda: datetime.now(UTC_PLUS_7)
    )

    # Two-Factor Authentication Fields
    totp_secret = Column(String(32), nullable=True)  # Store user's TOTP secret
    is_2fa_enabled = Column(Boolean, default=False)  # Flag for 2FA status



class RevokedToken(Base):
    __tablename__ = "revoked_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(255), unique=True, index=True, nullable=False)
    refresh_token = Column(String(255), nullable=True)  # Allow NULL values
    revoked_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), ForeignKey("users.email"), index=True, nullable=False)
    otp = Column(String(6), unique=True, index=True, nullable=False)  # OTP as 6-digit string
    expires_at = Column(DateTime, nullable=False)
    is_used = Column(Boolean, default=False) 


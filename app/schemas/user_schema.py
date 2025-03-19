# app\schemas\user_schema.py
# User schema file

from typing import List, Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime, timezone, timedelta
import pytz


CAMBODIA_TZ = pytz.timezone("Asia/Phnom_Penh")

class UserSchema(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    # Convert UTC to UTC+07:00 before returning JSON
    def dict(self, *args, **kwargs):
        data = super().dict(*args, **kwargs)
        if self.created_at:
            data["created_at"] = self.created_at.astimezone(CAMBODIA_TZ).isoformat()
        if self.updated_at:
            data["updated_at"] = self.updated_at.astimezone(CAMBODIA_TZ).isoformat()
        return data

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    # username: str
    username_or_email: str
    password: str

class UserInDB(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool

    class Config:
        from_attributes = True 

class UserResponse(UserInDB):
    pass

class UserListResponse(BaseModel):
    users: List[UserInDB]


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

class ResetPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordConfirm(BaseModel):
    token: str
    new_password: str


class Settings(BaseModel):
    # Existing settings...
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = 30
    EMAIL_USERNAME: str
    EMAIL_PASSWORD: str
    EMAIL_FROM: str
    EMAIL_PORT: int
    EMAIL_SERVER: str
    FRONTEND_URL: str  # URL of your frontend for password reset links

    class Config:
        env_file = ".env"



class ChangeUsernameEmailRequest(BaseModel):
    new_username: Optional[str] = None
    new_email: Optional[str] = None

    
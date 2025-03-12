import logging
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.db.models import User
from app.schemas.user_schema import UserCreate, UserInDB

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
logger = logging.getLogger(__name__)

def get_user(db: Session, username: str) -> Optional[UserInDB]:
    logger.info(f"Fetching user: {username}")
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        logger.warning(f"User not found: {username}")
    return user

def get_user_by_email(db: Session, email: str) -> Optional[UserInDB]:
    logger.info(f"Fetching user by email: {email}")
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        logger.warning(f"User not found with email: {email}")
    return user

def create_user(db: Session, user: UserCreate):
    logger.info(f"Creating user: {user.username}")
    hashed_password = pwd_context.hash(user.password)
    db_user = User(username=user.username, email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# def authenticate_user(db: Session, username: str, password: str):
#     logger.info(f"Authenticating user: {username}")
#     user = get_user(db, username)
#     if not user:
#         logger.warning(f"User not found: {username}")
#         return False
#     if not pwd_context.verify(password, user.hashed_password):
#         logger.warning(f"Invalid password for user: {username}")
#         return False
#     return user

def authenticate_user(db: Session, username_or_email: str, password: str):
    # Check if the input is an email
    if "@" in username_or_email:
        user = get_user_by_email(db, email=username_or_email)
    else:
        user = get_user(db, username=username_or_email)

    if not user:
        return False

    # Verify the password
    if not pwd_context.verify(password, user.hashed_password):
        return False

    return user

def get_all_users(db: Session) -> List[UserInDB]:
    return db.query(User).all()

def get_active_users(db: Session) -> List[UserInDB]:
    return db.query(User).filter(User.is_active == True).all()


def update_user_password(db: Session, user_id: int, new_password: str):
    hashed_password = pwd_context.hash(new_password)
    user = db.query(User).filter(User.id == user_id).first()
    user.hashed_password = hashed_password
    db.commit()
    db.refresh(user)



def delete_user(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    db.delete(user)
    db.commit()
    return {"detail": "User deleted successfully"}


def update_user_username_or_email(
    db: Session,
    user_id: int,
    new_username: Optional[str] = None,
    new_email: Optional[str] = None
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Update username if provided
    if new_username:
        # Check if the new username is already taken
        existing_user = db.query(User).filter(User.username == new_username).first()
        if existing_user and existing_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken",
            )
        user.username = new_username

    # Update email if provided
    if new_email:
        # Check if the new email is already taken
        existing_user = db.query(User).filter(User.email == new_email).first()
        if existing_user and existing_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already taken",
            )
        user.email = new_email

    db.commit()
    db.refresh(user)
    return user
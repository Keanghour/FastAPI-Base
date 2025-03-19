# app\api\users.py
# User API file with routes for user-related endpoints

import logging
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from app.db.models import User 
# from app.services.email_service import send_password_reset_email  
from app.services.token_service import create_password_reset_token, revoke_token, verify_password_reset_token  
from app.db.session import SessionLocal, get_db 
from app.schemas.user_schema import ChangePasswordRequest, ChangeUsernameEmailRequest, ResetPasswordConfirm, ResetPasswordRequest, UserCreate, UserListResponse, UserLogin, UserInDB, UserResponse 
from app.services.user_service import create_user, authenticate_user, delete_user, get_active_users, get_all_users, get_user, get_user_by_email, update_user_password, pwd_context, update_user_username_or_email  
from app.core.config import settings  
from app.core.security import create_access_token, create_email_verification_token, create_refresh_token, get_current_user, verify_email_verification_token, verify_token  


router = APIRouter()
logger = logging.getLogger(__name__)



# Method POST
@router.post("/register", response_model=UserInDB)
def register(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    # Check if username already exists
    db_user_by_username = get_user(db, username=user.username)
    if db_user_by_username:
        logger.error(f"Username already registered: {user.username}")
        raise HTTPException(
            status_code=400,
            detail="Username already registered",
        )

    # Check if email already exists
    db_user_by_email = get_user_by_email(db, email=user.email)
    if db_user_by_email:
        logger.error(f"Email already registered: {user.email}")
        raise HTTPException(
            status_code=400,
            detail="Email already registered",
        )

    # Create the user
    try:
        db_user = create_user(db=db, user=user)
        
        # Generate email verification token
        verification_token = create_email_verification_token(db_user.email)
        
        # Return the verification token in the response
        return {
            **db_user.__dict__,
            "verification_token": verification_token,
            "detail": "Account created successfully. Please verify your email."
        }
    except Exception as e:
        logger.error(f"Error creating user: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while creating the user",
        )    

@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, user.username_or_email, user.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username/email or password")
    
    # Create access token
    access_token = create_access_token(data={"sub": user.username})
    
    # Create refresh token
    refresh_token = create_refresh_token(data={"sub": user.username})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/logout")
def logout(
    authorization: str = Header(...),  # Extract JWT token Auth
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Extract the token from the "Bearer <token>" format
        if not authorization.startswith("Bearer "):
            raise credentials_exception
        token = authorization.split(" ")[1]

        # Revoke the token
        revoke_token(db, token)
        return {"detail": "Successfully logged out"}
    except Exception as e:
        logger.error(f"Error during logout: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred during logout",
        )

@router.post("/change-password")
def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify the current password
    if not pwd_context.verify(request.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )

    # Update the password
    update_user_password(db, current_user.id, request.new_password)
    return {"detail": "Password updated successfully"}

@router.post("/reset-password-request")
async def reset_password_request(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    user = get_user_by_email(db, request.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Generate a password reset token
    token = create_password_reset_token(request.email)

    # Remove or comment out this line to stop sending emails
    # await send_password_reset_email(request.email, token)  # No email sending for now

    # Instead of sending the email, return the token for testing purposes
    return {"detail": "Password reset email would have been sent", "token": token}

@router.post("/reset-password")
def reset_password(
    request: ResetPasswordConfirm,
    db: Session = Depends(get_db)
):
    # Verify the token
    try:
        email = verify_password_reset_token(request.token)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token",
        )

    # Update the password
    user = get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    update_user_password(db, user.id, request.new_password)
    return {"detail": "Password reset successfully"}
    
@router.post("/refresh-token")
def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired refresh token",
    )
    try:
        # Verify the refresh token
        payload = verify_token(refresh_token)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Fetch the user
    user = get_user(db, username=username)
    if user is None:
        raise credentials_exception

    # Create a new access token
    access_token = create_access_token(data={"sub": user.username})
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }



# Method GET
@router.get("/verify-email")
def verify_email(
    token: str,
    db: Session = Depends(get_db)
):
    # Verify the token
    try:
        email = verify_email_verification_token(token)
        # print(f"Email from token: {email}")  
    except HTTPException as e:
        raise e

    # Fetch the user by email
    user = get_user_by_email(db, email=email)
    if user is None:
        # print(f"User not found for email: {email}")  
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Mark the user as verified
    user.is_verified = True
    db.commit()
    db.refresh(user)

    return {"detail": "Email verified successfully"}

# Get Current User (logged-in user)
@router.get("/users/me", response_model=UserResponse)
def read_current_user(
    authorization: str = Header(...),  
    db: Session = Depends(get_db)  
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Extract the token from the "Bearer <token>" format
        if not authorization.startswith("Bearer "):
            logger.error("Invalid token format")
            raise credentials_exception
        token = authorization.split(" ")[1]

        # Decode the JWT token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            logger.error("Username not found in token")
            raise credentials_exception
    except JWTError as e:
        logger.error(f"JWT error: {e}")
        raise credentials_exception

    # Fetch the user from the database
    user = get_user(db, username=username)
    if user is None:
        logger.error(f"User not found: {username}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user

# Get All Users
@router.get("/users", response_model=UserListResponse)
def read_all_users(db: Session = Depends(get_db)):
    users = get_all_users(db)
    return {"users": users}

# Get Active Users
@router.get("/users/active", response_model=UserListResponse)
def read_active_users(db: Session = Depends(get_db)):
    users = get_active_users(db)
    return {"users": users}

# Get User by Username
@router.get("/users/{username}", response_model=UserResponse)
def read_user_by_username(username: str, db: Session = Depends(get_db)):
    db_user = get_user(db, username=username)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user



# Method Delete
@router.delete("/delete-account")
def delete_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Delete the user
    delete_user(db, current_user.id)
    
    # Optionally, revoke all tokens for the user (if using token blacklist)
    # revoke_all_tokens_for_user(db, current_user.id)
    
    return {"detail": "Account deleted successfully"}



# Method Put
@router.put("/change-username-email")
def change_username_or_email(
    request: ChangeUsernameEmailRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Update the username or email
    updated_user = update_user_username_or_email(
        db,
        current_user.id,
        new_username=request.new_username,
        new_email=request.new_email
    )
    
    return {
        "id": updated_user.id,
        "username": updated_user.username,
        "email": updated_user.email,
        "detail": "Username or email updated successfully"
    }


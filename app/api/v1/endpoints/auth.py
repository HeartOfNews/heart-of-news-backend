"""
API endpoints for authentication and user management
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.api.deps import (
    get_current_user,
    get_current_active_user,
    get_current_verified_user,
    extract_client_info,
    oauth2_scheme,
)
from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_verification_token,
    create_password_reset_token,
    verify_token,
)
from app.crud import user, user_session
from app.db.session import get_db
from app.models.user import User, UserSession
from app.schemas.user import (
    Token,
    User as UserSchema,
    UserCreate,
    UserUpdate,
    PasswordReset,
    PasswordResetConfirm,
    EmailVerification,
    UserUpdatePassword,
)
from app.utils.email import (
    send_reset_password_email,
    send_verification_email,
    send_welcome_email,
)

router = APIRouter()


@router.post("/register", response_model=UserSchema)
def register_user(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
) -> Any:
    """
    Register a new user.
    """
    # Check if user with this email already exists
    existing_email = user.get_by_email(db, email=user_in.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Check if user with this username already exists
    existing_username = user.get_by_username(db, username=user_in.username)
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken",
        )
    
    # Create new user
    new_user = user.create(db, obj_in=user_in)
    
    # Send verification email if required
    if settings.VERIFY_EMAIL:
        token = create_verification_token(new_user.id)
        user.set_verification_token(db, db_obj=new_user, token=token)
        send_verification_email(new_user.email, token)
    else:
        # Send welcome email
        send_welcome_email(new_user.email)
    
    return new_user


@router.post("/login", response_model=Token)
def login(
    *,
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
    request: Request,
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    # Authenticate user
    authenticated_user = user.authenticate(
        db, email_or_username=form_data.username, password=form_data.password
    )
    if not authenticated_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not authenticated_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    
    # Check if user is verified (if required)
    if settings.VERIFY_EMAIL and not authenticated_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not verified",
        )
    
    # Generate access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Extract client info for session tracking
    client_info = extract_client_info(request)
    
    # Create session
    session = user_session.create_session(
        db,
        user_id=authenticated_user.id,
        token="temp",  # Will be updated below
        user_agent=client_info["user_agent"],
        ip_address=client_info["ip_address"],
        device_info=client_info["device_info"],
        expires_at=datetime.utcnow() + access_token_expires,
    )
    
    # Create token with session ID
    token = create_access_token(
        subject=str(authenticated_user.id),
        role=authenticated_user.role,
        permissions=authenticated_user.permissions,
        expires_delta=access_token_expires,
        session_id=session.id,
    )
    
    # Update session with token
    session.token = token
    db.add(session)
    db.commit()
    
    # Return token and user info
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_at": int((datetime.utcnow() + access_token_expires).timestamp()),
        "user": authenticated_user,
    }


@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    token: str = Depends(oauth2_scheme),
) -> Dict[str, str]:
    """
    Logout user by invalidating the current session.
    """
    # Get current session
    session = user_session.get_by_token(db, token=token)
    if session:
        # Invalidate session
        user_session.invalidate_session(db, session=session)
    
    return {"message": "Successfully logged out"}


@router.post("/logout-all", status_code=status.HTTP_200_OK)
def logout_all_sessions(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Logout user from all sessions.
    """
    # Invalidate all sessions
    count = user_session.invalidate_all_sessions(db, user_id=current_user.id)
    
    return {"message": f"Successfully logged out from all sessions", "count": count}


@router.get("/sessions", response_model=List[Dict[str, Any]])
def get_user_sessions(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    active_only: bool = True,
) -> Any:
    """
    Get all sessions for the current user.
    """
    sessions = user_session.get_sessions_by_user(
        db, user_id=current_user.id, active_only=active_only
    )
    
    # Format response
    result = []
    for session in sessions:
        result.append({
            "id": str(session.id),
            "created_at": session.created_at,
            "last_activity": session.last_activity,
            "expires_at": session.expires_at,
            "is_active": session.is_active,
            "device_info": session.device_info,
            "ip_address": session.ip_address,
        })
    
    return result


@router.post("/verify-email", status_code=status.HTTP_200_OK)
def verify_email(
    *,
    db: Session = Depends(get_db),
    verification_data: EmailVerification,
) -> Dict[str, str]:
    """
    Verify user email with token.
    """
    # Verify token
    user_id = verify_token(verification_data.token, "verification")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token",
        )
    
    # Get user
    db_user = user.get(db, id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Mark user as verified
    user.verify_user(db, db_obj=db_user)
    
    # Send welcome email
    send_welcome_email(db_user.email)
    
    return {"message": "Email verified successfully"}


@router.post("/resend-verification", status_code=status.HTTP_200_OK)
def resend_verification_email(
    *,
    db: Session = Depends(get_db),
    email: str = Body(..., embed=True),
) -> Dict[str, str]:
    """
    Resend verification email.
    """
    # Get user
    db_user = user.get_by_email(db, email=email)
    if not db_user:
        # Return success even if user doesn't exist for security
        return {"message": "Verification email sent if account exists"}
    
    # Check if already verified
    if db_user.is_verified:
        return {"message": "Email already verified"}
    
    # Create new verification token
    token = create_verification_token(db_user.id)
    user.set_verification_token(db, db_obj=db_user, token=token)
    
    # Send verification email
    send_verification_email(db_user.email, token)
    
    return {"message": "Verification email sent if account exists"}


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
def forgot_password(
    *,
    db: Session = Depends(get_db),
    password_reset: PasswordReset,
) -> Dict[str, str]:
    """
    Send password reset email.
    """
    # Get user
    db_user = user.get_by_email(db, email=password_reset.email)
    if not db_user:
        # Return success even if user doesn't exist for security
        return {"message": "Password reset email sent if account exists"}
    
    # Create password reset token
    token = create_password_reset_token(db_user.id)
    user.set_reset_token(db, db_obj=db_user, token=token)
    
    # Send password reset email
    send_reset_password_email(db_user.email, token)
    
    return {"message": "Password reset email sent if account exists"}


@router.post("/reset-password", status_code=status.HTTP_200_OK)
def reset_password(
    *,
    db: Session = Depends(get_db),
    password_reset: PasswordResetConfirm,
) -> Dict[str, str]:
    """
    Reset password with token.
    """
    # Verify token
    user_id = verify_token(password_reset.token, "password_reset")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token",
        )
    
    # Get user
    db_user = user.get(db, id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Update password
    user.update_password(db, db_obj=db_user, password=password_reset.new_password)
    
    # Clear reset token
    user.clear_reset_token(db, db_obj=db_user)
    
    # Invalidate all sessions for security
    user_session.invalidate_all_sessions(db, user_id=db_user.id)
    
    return {"message": "Password reset successfully"}


@router.post("/change-password", status_code=status.HTTP_200_OK)
def change_password(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_verified_user),
    password_update: UserUpdatePassword,
) -> Dict[str, str]:
    """
    Change user password.
    """
    # Verify current password
    if not verify_password(password_update.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect password",
        )
    
    # Update password
    user.update_password(db, db_obj=current_user, password=password_update.new_password)
    
    # Invalidate all other sessions for security
    sessions = user_session.get_sessions_by_user(db, user_id=current_user.id, active_only=True)
    for session in sessions:
        # Keep current session active
        if session.token != token:
            user_session.invalidate_session(db, session=session)
    
    return {"message": "Password changed successfully"}
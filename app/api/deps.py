"""
Dependencies for API endpoints
"""

from datetime import datetime
from typing import Generator, Optional

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import or_
import jwt
from jwt.exceptions import PyJWTError as JWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import decode_token
from app.crud import user, user_session
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import TokenPayload

# OAuth2 scheme for Swagger UI
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> User:
    """
    Dependency to get the current authenticated user
    
    Args:
        db: Database session
        token: JWT token
    
    Returns:
        Current user
    
    Raises:
        HTTPException: If authentication fails
    """
    try:
        # Decode token
        payload = decode_token(token)
        token_data = TokenPayload(**payload)
        
        # Check token expiration
        if token_data.exp < int(datetime.utcnow().timestamp()):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database
    db_user = user.get(db, id=token_data.sub)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if user is active
    if not db_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Check if user is verified (if required)
    if settings.VERIFY_EMAIL and not db_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not verified"
        )
    
    # Check if session is valid
    session = user_session.get_active_by_token(db, token=token)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired or invalid",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update session last activity
    user_session.update_last_activity(db, session=session)
    
    return db_user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency to get the current active user
    
    Args:
        current_user: Current authenticated user
    
    Returns:
        Current active user
    
    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


def get_current_verified_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    Dependency to get the current verified user
    
    Args:
        current_user: Current active user
    
    Returns:
        Current verified user
    
    Raises:
        HTTPException: If user is not verified
    """
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not verified"
        )
    return current_user


def get_current_admin_user(
    current_user: User = Depends(get_current_verified_user),
) -> User:
    """
    Dependency to get the current admin user
    
    Args:
        current_user: Current verified user
    
    Returns:
        Current admin user
    
    Raises:
        HTTPException: If user is not an admin
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


def get_current_editor_user(
    current_user: User = Depends(get_current_verified_user),
) -> User:
    """
    Dependency to get the current editor user
    
    Args:
        current_user: Current verified user
    
    Returns:
        Current editor user
    
    Raises:
        HTTPException: If user does not have editor role
    """
    if current_user.role not in ["admin", "editor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


def check_permission(permission: str):
    """
    Dependency factory to check if current user has a specific permission
    
    Args:
        permission: Permission name to check
    
    Returns:
        Dependency function
    """
    def dependency(current_user: User = Depends(get_current_verified_user)) -> User:
        if permission not in current_user.permissions and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing permission: {permission}"
            )
        return current_user
    
    return dependency


def extract_client_info(request: Request) -> dict:
    """
    Extract client information from request
    
    Args:
        request: FastAPI request
    
    Returns:
        Client information
    """
    user_agent = request.headers.get("user-agent", "")
    ip = request.client.host if request.client else None
    
    # Extract device info from user agent (basic extraction)
    device_info = {}
    if "Mobile" in user_agent:
        device_info["device_type"] = "mobile"
    elif "Tablet" in user_agent:
        device_info["device_type"] = "tablet"
    else:
        device_info["device_type"] = "desktop"
    
    # Extract browser info
    if "Firefox" in user_agent:
        device_info["browser"] = "Firefox"
    elif "Chrome" in user_agent:
        device_info["browser"] = "Chrome"
    elif "Safari" in user_agent:
        device_info["browser"] = "Safari"
    elif "Edge" in user_agent:
        device_info["browser"] = "Edge"
    else:
        device_info["browser"] = "Other"
    
    return {
        "user_agent": user_agent,
        "ip_address": ip,
        "device_info": device_info,
    }
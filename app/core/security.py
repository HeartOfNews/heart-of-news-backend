"""
Security utilities for authentication and authorization
"""

import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union

import jwt
from passlib.context import CryptContext
from pydantic import UUID4

from app.core.config import settings

# Initialize password context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password for storage"""
    return pwd_context.hash(password)


def create_access_token(
    subject: Union[str, UUID4],
    role: str,
    permissions: List[str] = [],
    expires_delta: Optional[timedelta] = None,
    session_id: Optional[Union[str, UUID4]] = None,
) -> str:
    """
    Create a JWT access token for the user
    
    Args:
        subject: User ID or username
        role: User role (admin, editor, user)
        permissions: List of permissions
        expires_delta: Token expiration time
        session_id: Session ID for token invalidation
    
    Returns:
        JWT token string
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    # Create session ID if not provided
    if session_id is None:
        session_id = str(uuid.uuid4())
    
    # Build token payload
    to_encode = {
        "sub": str(subject),
        "exp": expire.timestamp(),
        "iat": datetime.utcnow().timestamp(),
        "role": role,
        "permissions": permissions,
        "session_id": str(session_id),
    }
    
    # Create token
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    
    return encoded_jwt


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate a JWT token
    
    Args:
        token: JWT token string
    
    Returns:
        Decoded token payload
    
    Raises:
        jwt.PyJWTError: If token is invalid
    """
    return jwt.decode(
        token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
    )


def create_verification_token(user_id: Union[str, UUID4]) -> str:
    """
    Create a verification token for email verification
    
    Args:
        user_id: User ID
    
    Returns:
        Verification token
    """
    expire = datetime.utcnow() + timedelta(hours=24)
    payload = {
        "sub": str(user_id),
        "exp": expire.timestamp(),
        "iat": datetime.utcnow().timestamp(),
        "type": "verification",
    }
    
    return jwt.encode(
        payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )


def create_password_reset_token(user_id: Union[str, UUID4]) -> str:
    """
    Create a password reset token
    
    Args:
        user_id: User ID
    
    Returns:
        Password reset token
    """
    expire = datetime.utcnow() + timedelta(hours=4)
    payload = {
        "sub": str(user_id),
        "exp": expire.timestamp(),
        "iat": datetime.utcnow().timestamp(),
        "type": "password_reset",
    }
    
    return jwt.encode(
        payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )


def verify_token(token: str, token_type: str) -> Optional[str]:
    """
    Verify a token for email verification or password reset
    
    Args:
        token: Token to verify
        token_type: Type of token (verification or password_reset)
    
    Returns:
        User ID if token is valid, None otherwise
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        
        # Check token type
        if payload.get("type") != token_type:
            return None
        
        # Check expiration
        if datetime.fromtimestamp(payload.get("exp")) < datetime.utcnow():
            return None
        
        return payload.get("sub")
    except jwt.PyJWTError:
        return None
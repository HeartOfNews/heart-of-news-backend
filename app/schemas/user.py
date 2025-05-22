"""
Pydantic schemas for user management
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional, Union, Any

from pydantic import BaseModel, EmailStr, Field, validator, UUID4, HttpUrl


class UserBase(BaseModel):
    """Base user schema with common attributes"""
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class UserCreate(UserBase):
    """Schema for creating a new user"""
    password: str = Field(..., min_length=8)
    
    @validator("password")
    def validate_password(cls, password):
        """Validate password complexity"""
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        
        # Check for at least one uppercase, lowercase, and digit
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        
        if not (has_upper and has_lower and has_digit):
            raise ValueError(
                "Password must contain at least one uppercase letter, "
                "one lowercase letter, and one digit"
            )
        
        return password


class UserUpdate(BaseModel):
    """Schema for updating a user"""
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    profile_image: Optional[str] = None
    bio: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class UserUpdatePassword(BaseModel):
    """Schema for updating a user's password"""
    current_password: str
    new_password: str = Field(..., min_length=8)
    
    @validator("new_password")
    def validate_password(cls, password):
        """Validate password complexity"""
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        
        # Check for at least one uppercase, lowercase, and digit
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        
        if not (has_upper and has_lower and has_digit):
            raise ValueError(
                "Password must contain at least one uppercase letter, "
                "one lowercase letter, and one digit"
            )
        
        return password


class UserInDBBase(UserBase):
    """Base schema for DB users"""
    id: UUID4
    is_active: bool
    is_verified: bool
    role: str
    permissions: List[str] = []
    created_at: datetime
    updated_at: datetime


class UserInDB(UserInDBBase):
    """Schema for user in DB (includes hashed password)"""
    hashed_password: str


class User(UserInDBBase):
    """Schema for returning user information"""
    profile_image: Optional[str] = None
    bio: Optional[str] = None
    last_login: Optional[datetime] = None


class UserProfile(BaseModel):
    """Schema for user profile information"""
    username: str
    full_name: Optional[str] = None
    profile_image: Optional[str] = None
    bio: Optional[str] = None
    role: str


class Token(BaseModel):
    """Schema for access token"""
    access_token: str
    token_type: str = "bearer"
    expires_at: int  # Unix timestamp
    user: User


class TokenPayload(BaseModel):
    """Schema for token payload"""
    sub: Union[str, UUID4]
    exp: int
    role: str
    permissions: List[str] = []
    session_id: Union[str, UUID4]


class PasswordReset(BaseModel):
    """Schema for password reset request"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Schema for confirming password reset"""
    token: str
    new_password: str = Field(..., min_length=8)
    
    @validator("new_password")
    def validate_password(cls, password):
        """Validate password complexity"""
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        
        # Check for at least one uppercase, lowercase, and digit
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        
        if not (has_upper and has_lower and has_digit):
            raise ValueError(
                "Password must contain at least one uppercase letter, "
                "one lowercase letter, and one digit"
            )
        
        return password


class EmailVerification(BaseModel):
    """Schema for email verification"""
    token: str
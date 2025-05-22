"""
API endpoints for user management
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query, Path, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.api.deps import (
    get_current_user,
    get_current_active_user,
    get_current_verified_user,
    get_current_admin_user,
    check_permission,
)
from app.core.config import settings
from app.crud import user
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import (
    User as UserSchema,
    UserCreate,
    UserUpdate,
    UserProfile,
)

router = APIRouter()


@router.get("/me", response_model=UserSchema)
def get_current_user_info(
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get current user information.
    """
    return current_user


@router.put("/me", response_model=UserSchema)
def update_current_user(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    user_in: UserUpdate,
) -> Any:
    """
    Update current user information.
    """
    # Check if email is being changed and already exists
    if user_in.email and user_in.email != current_user.email:
        existing_user = user.get_by_email(db, email=user_in.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
    
    # Check if username is being changed and already exists
    if user_in.username and user_in.username != current_user.username:
        existing_user = user.get_by_username(db, username=user_in.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken",
            )
    
    # Update user
    updated_user = user.update(db, db_obj=current_user, obj_in=user_in)
    return updated_user


@router.delete("/me", status_code=status.HTTP_200_OK)
def delete_current_user(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Dict[str, str]:
    """
    Delete current user.
    """
    # Deactivate user instead of deleting
    user.deactivate(db, db_obj=current_user)
    return {"message": "User successfully deactivated"}


@router.get("/", response_model=List[UserSchema])
def get_users(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
    skip: int = 0,
    limit: int = 100,
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    is_verified: Optional[bool] = None,
    search: Optional[str] = None,
) -> Any:
    """
    Get list of users (admin only).
    """
    # Build query
    query = db.query(User)
    
    # Apply filters
    if role:
        query = query.filter(User.role == role)
    
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    if is_verified is not None:
        query = query.filter(User.is_verified == is_verified)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                User.email.ilike(search_term),
                User.username.ilike(search_term),
                User.full_name.ilike(search_term),
            )
        )
    
    # Apply pagination
    users = query.offset(skip).limit(limit).all()
    return users


@router.post("/", response_model=UserSchema)
def create_user(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
    user_in: UserCreate,
    is_admin: bool = False,
) -> Any:
    """
    Create new user (admin only).
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
    if is_admin:
        new_user = user.create_admin(db, obj_in=user_in)
    else:
        new_user = user.create(db, obj_in=user_in)
        # Admin-created users are auto-verified
        user.verify_user(db, db_obj=new_user)
    
    return new_user


@router.get("/{user_id}", response_model=UserSchema)
def get_user(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
    user_id: str = Path(..., title="User ID"),
) -> Any:
    """
    Get user by ID (admin only).
    """
    db_user = user.get(db, id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return db_user


@router.put("/{user_id}", response_model=UserSchema)
def update_user(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
    user_id: str = Path(..., title="User ID"),
    user_in: UserUpdate,
) -> Any:
    """
    Update user (admin only).
    """
    # Get user
    db_user = user.get(db, id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Check if email is being changed and already exists
    if user_in.email and user_in.email != db_user.email:
        existing_user = user.get_by_email(db, email=user_in.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
    
    # Check if username is being changed and already exists
    if user_in.username and user_in.username != db_user.username:
        existing_user = user.get_by_username(db, username=user_in.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken",
            )
    
    # Update user
    updated_user = user.update(db, db_obj=db_user, obj_in=user_in)
    return updated_user


@router.post("/{user_id}/activate", response_model=UserSchema)
def activate_user(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
    user_id: str = Path(..., title="User ID"),
) -> Any:
    """
    Activate user (admin only).
    """
    # Get user
    db_user = user.get(db, id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Activate user
    activated_user = user.activate(db, db_obj=db_user)
    return activated_user


@router.post("/{user_id}/deactivate", response_model=UserSchema)
def deactivate_user(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
    user_id: str = Path(..., title="User ID"),
) -> Any:
    """
    Deactivate user (admin only).
    """
    # Get user
    db_user = user.get(db, id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Cannot deactivate self
    if str(db_user.id) == str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate yourself",
        )
    
    # Deactivate user
    deactivated_user = user.deactivate(db, db_obj=db_user)
    return deactivated_user


@router.get("/profile/{username}", response_model=UserProfile)
def get_user_profile(
    *,
    db: Session = Depends(get_db),
    username: str = Path(..., title="Username"),
) -> Any:
    """
    Get user profile by username.
    """
    # Get user
    db_user = user.get_by_username(db, username=username)
    if not db_user or not db_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Return profile information
    return {
        "username": db_user.username,
        "full_name": db_user.full_name,
        "profile_image": db_user.profile_image,
        "bio": db_user.bio,
        "role": db_user.role,
    }
"""
SQLAlchemy models for user authentication and management
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, JSON, Integer
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship

from app.db.session import Base


class User(Base):
    """
    User model for authentication and authorization
    """
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    
    # User status and permissions
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    role = Column(String, default="user")  # admin, editor, user
    permissions = Column(ARRAY(String), default=[])
    
    # Profile information
    profile_image = Column(String)
    bio = Column(Text)
    preferences = Column(JSON, default={})
    
    # Authentication fields
    last_login = Column(DateTime)
    password_changed_at = Column(DateTime)
    verification_token = Column(String)
    reset_token = Column(String)
    failed_login_attempts = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<User {self.username}>"


class UserSession(Base):
    """
    User session model for tracking active sessions
    """
    __tablename__ = "user_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Session information
    token = Column(String, nullable=False, index=True)
    user_agent = Column(String)
    ip_address = Column(String)
    device_info = Column(JSON)
    
    # Session status
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime, nullable=False)
    revoked_at = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<UserSession {self.id}>"
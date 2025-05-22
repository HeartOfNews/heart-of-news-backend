"""
CRUD operations for user model
"""

import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union

from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from pydantic import UUID4, EmailStr

from app.core.security import get_password_hash, verify_password
from app.core.config import settings
from app.models.user import User, UserSession
from app.schemas.user import UserCreate, UserUpdate
from app.crud.base import CRUDBase


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """CRUD operations for user model"""
    
    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()
    
    def get_by_username(self, db: Session, *, username: str) -> Optional[User]:
        """Get user by username"""
        return db.query(User).filter(User.username == username).first()
    
    def get_by_email_or_username(
        self, db: Session, *, email_or_username: str
    ) -> Optional[User]:
        """Get user by email or username"""
        return db.query(User).filter(
            or_(User.email == email_or_username, User.username == email_or_username)
        ).first()
    
    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        """Create a new user"""
        # Create user instance
        db_obj = User(
            email=obj_in.email,
            username=obj_in.username,
            hashed_password=get_password_hash(obj_in.password),
            full_name=obj_in.full_name,
            is_active=True,
            is_verified=not settings.VERIFY_EMAIL,  # Skip verification if disabled
            role="user",
            permissions=[],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        
        # Add to database
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        return db_obj
    
    def create_admin(self, db: Session, *, obj_in: UserCreate) -> User:
        """Create a new admin user"""
        # Create user instance
        db_obj = User(
            email=obj_in.email,
            username=obj_in.username,
            hashed_password=get_password_hash(obj_in.password),
            full_name=obj_in.full_name,
            is_active=True,
            is_verified=True,  # Admins are auto-verified
            role="admin",
            permissions=["admin", "user", "editor"],  # All permissions
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        
        # Add to database
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        return db_obj
    
    def update(
        self, db: Session, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        """Update a user"""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        
        # Update timestamp
        update_data["updated_at"] = datetime.utcnow()
        
        return super().update(db, db_obj=db_obj, obj_in=update_data)
    
    def update_password(
        self, db: Session, *, db_obj: User, password: str
    ) -> User:
        """Update user password"""
        db_obj.hashed_password = get_password_hash(password)
        db_obj.password_changed_at = datetime.utcnow()
        db_obj.updated_at = datetime.utcnow()
        
        # Reset failed login attempts
        db_obj.failed_login_attempts = 0
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        return db_obj
    
    def set_verification_token(
        self, db: Session, *, db_obj: User, token: str
    ) -> User:
        """Set verification token for user"""
        db_obj.verification_token = token
        db_obj.updated_at = datetime.utcnow()
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        return db_obj
    
    def verify_user(self, db: Session, *, db_obj: User) -> User:
        """Mark user as verified"""
        db_obj.is_verified = True
        db_obj.verification_token = None
        db_obj.updated_at = datetime.utcnow()
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        return db_obj
    
    def set_reset_token(
        self, db: Session, *, db_obj: User, token: str
    ) -> User:
        """Set password reset token for user"""
        db_obj.reset_token = token
        db_obj.updated_at = datetime.utcnow()
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        return db_obj
    
    def clear_reset_token(self, db: Session, *, db_obj: User) -> User:
        """Clear password reset token for user"""
        db_obj.reset_token = None
        db_obj.updated_at = datetime.utcnow()
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        return db_obj
    
    def authenticate(
        self, db: Session, *, email_or_username: str, password: str
    ) -> Optional[User]:
        """Authenticate user by email/username and password"""
        user = self.get_by_email_or_username(db, email_or_username=email_or_username)
        
        if not user:
            return None
        
        # Check if user is locked out
        if user.failed_login_attempts >= settings.AUTH_MAX_FAILED_ATTEMPTS:
            if user.last_login:
                lockout_time = user.last_login + timedelta(minutes=settings.AUTH_LOCKOUT_DURATION_MINUTES)
                if lockout_time > datetime.utcnow():
                    # User is still locked out
                    return None
            
            # Lockout expired, reset counter
            user.failed_login_attempts = 0
            db.add(user)
            db.commit()
        
        # Verify password
        if not verify_password(password, user.hashed_password):
            # Increment failed login attempts
            user.failed_login_attempts += 1
            user.last_login = datetime.utcnow()
            db.add(user)
            db.commit()
            return None
        
        # Successful login, reset counter and update last login
        user.failed_login_attempts = 0
        user.last_login = datetime.utcnow()
        db.add(user)
        db.commit()
        
        return user
    
    def is_active(self, user: User) -> bool:
        """Check if user is active"""
        return user.is_active
    
    def is_verified(self, user: User) -> bool:
        """Check if user is verified"""
        return user.is_verified
    
    def is_admin(self, user: User) -> bool:
        """Check if user is an admin"""
        return user.role == "admin"
    
    def has_role(self, user: User, role: str) -> bool:
        """Check if user has a specific role"""
        return user.role == role
    
    def has_permission(self, user: User, permission: str) -> bool:
        """Check if user has a specific permission"""
        return permission in user.permissions
    
    def deactivate(self, db: Session, *, db_obj: User) -> User:
        """Deactivate a user"""
        db_obj.is_active = False
        db_obj.updated_at = datetime.utcnow()
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        return db_obj
    
    def activate(self, db: Session, *, db_obj: User) -> User:
        """Activate a user"""
        db_obj.is_active = True
        db_obj.updated_at = datetime.utcnow()
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        return db_obj


class CRUDUserSession(CRUDBase[UserSession, Dict[str, Any], Dict[str, Any]]):
    """CRUD operations for user session model"""
    
    def create_session(
        self,
        db: Session,
        *,
        user_id: UUID4,
        token: str,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
        device_info: Optional[Dict[str, Any]] = None,
        expires_at: Optional[datetime] = None,
    ) -> UserSession:
        """Create a new user session"""
        # Set default expiration if not provided
        if expires_at is None:
            expires_at = datetime.utcnow() + timedelta(days=7)
        
        # Create session
        session = UserSession(
            id=uuid.uuid4(),
            user_id=user_id,
            token=token,
            user_agent=user_agent,
            ip_address=ip_address,
            device_info=device_info,
            is_active=True,
            expires_at=expires_at,
            created_at=datetime.utcnow(),
            last_activity=datetime.utcnow(),
        )
        
        # Add to database
        db.add(session)
        db.commit()
        db.refresh(session)
        
        return session
    
    def get_by_token(self, db: Session, *, token: str) -> Optional[UserSession]:
        """Get session by token"""
        return db.query(UserSession).filter(UserSession.token == token).first()
    
    def get_active_by_token(self, db: Session, *, token: str) -> Optional[UserSession]:
        """Get active session by token"""
        return db.query(UserSession).filter(
            and_(
                UserSession.token == token,
                UserSession.is_active == True,
                UserSession.expires_at > datetime.utcnow(),
            )
        ).first()
    
    def get_sessions_by_user(
        self, db: Session, *, user_id: UUID4, active_only: bool = False
    ) -> List[UserSession]:
        """Get all sessions for a user"""
        query = db.query(UserSession).filter(UserSession.user_id == user_id)
        
        if active_only:
            query = query.filter(
                and_(
                    UserSession.is_active == True,
                    UserSession.expires_at > datetime.utcnow(),
                )
            )
        
        return query.all()
    
    def invalidate_session(self, db: Session, *, session: UserSession) -> UserSession:
        """Invalidate a user session"""
        session.is_active = False
        session.revoked_at = datetime.utcnow()
        
        db.add(session)
        db.commit()
        db.refresh(session)
        
        return session
    
    def invalidate_all_sessions(
        self, db: Session, *, user_id: UUID4
    ) -> int:
        """Invalidate all sessions for a user"""
        sessions = self.get_sessions_by_user(db, user_id=user_id, active_only=True)
        
        count = 0
        for session in sessions:
            self.invalidate_session(db, session=session)
            count += 1
        
        return count
    
    def update_last_activity(
        self, db: Session, *, session: UserSession
    ) -> UserSession:
        """Update last activity timestamp for a session"""
        session.last_activity = datetime.utcnow()
        
        db.add(session)
        db.commit()
        db.refresh(session)
        
        return session
    
    def extend_session(
        self, db: Session, *, session: UserSession, days: int = 7
    ) -> UserSession:
        """Extend session expiration"""
        session.expires_at = datetime.utcnow() + timedelta(days=days)
        
        db.add(session)
        db.commit()
        db.refresh(session)
        
        return session
    
    def cleanup_expired_sessions(self, db: Session) -> int:
        """Clean up expired sessions"""
        # Find expired sessions
        expired = db.query(UserSession).filter(
            and_(
                UserSession.is_active == True,
                UserSession.expires_at <= datetime.utcnow(),
            )
        ).all()
        
        # Invalidate each session
        count = 0
        for session in expired:
            self.invalidate_session(db, session=session)
            count += 1
        
        return count


# Create CRUD instances
user = CRUDUser(User)
user_session = CRUDUserSession(UserSession)
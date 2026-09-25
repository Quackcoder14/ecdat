import enum
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, Boolean, DateTime, Enum, ForeignKey, Index
from sqlalchemy.orm import relationship
import passlib.hash as hasher

from app.db.base import Base
from app.db.types import GUID

class UserRole(enum.Enum):
    ADMIN = "admin"
    ANALYST = "analyst"
    DEVELOPER = "developer"
    VIEWER = "viewer"

class User(Base):
    __tablename__ = "users"
    
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(Enum(UserRole), default=UserRole.VIEWER)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    projects = relationship("Project", back_populates="owner")
    scan_runs = relationship("Scan", back_populates="initiated_by")
    audit_events = relationship("AuditEvent", back_populates="user")
    
    def verify_password(self, password: str) -> bool:
        return hasher.bcrypt.verify(password, self.hashed_password)
    
    def set_password(self, password: str) -> None:
        self.hashed_password = hasher.bcrypt.hash(password)
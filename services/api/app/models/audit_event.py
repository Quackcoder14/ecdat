import enum
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Index, Enum
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.db.types import GUID, JSONB
from .project import Project
from .scan import Scan
from .user import User
from .data_mode import DataMode

class AuditAction(enum.Enum):
    PROJECT_CREATED = "project_created"
    PROJECT_UPDATED = "project_updated"
    PROJECT_DELETED = "project_deleted"
    SCAN_STARTED = "scan_started"
    SCAN_COMPLETED = "scan_completed"
    SCAN_FAILED = "scan_failed"
    ARTIFACT_UPLOADED = "artifact_uploaded"
    CBOM_EXPORTED = "cbom_exported"
    REPORT_GENERATED = "report_generated"
    AI_QUERY_SUBMITTED = "ai_query_submitted"
    LLM_PROVIDER_CHANGED = "llm_provider_changed"
    SETTINGS_UPDATED = "settings_updated"
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"

class AuditEvent(Base):
    __tablename__ = "audit_events"
    
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID, ForeignKey("users.id"), nullable=True)
    project_id = Column(GUID, ForeignKey("projects.id"), nullable=True)
    scan_id = Column(GUID, ForeignKey("scans.id"), nullable=True)
    
    action = Column(Enum(AuditAction), nullable=False)
    description = Column(Text, nullable=True)
    event_metadata = Column(JSONB, nullable=True)  # Additional context (renamed from metadata)
    data_mode = Column(Enum(DataMode), default=DataMode.SIMULATION, nullable=False)
    
    timestamp = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent = Column(String(500), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="audit_events")
    project = relationship("Project")
    scan = relationship("Scan")
    
    # Indexes
    __table_args__ = (
        Index('ix_audit_events_user_id', user_id),
        Index('ix_audit_events_project_id', project_id),
        Index('ix_audit_events_scan_id', scan_id),
        Index('ix_audit_events_action', action),
        Index('ix_audit_events_timestamp', timestamp),
        Index('ix_audit_events_data_mode', data_mode),
    )
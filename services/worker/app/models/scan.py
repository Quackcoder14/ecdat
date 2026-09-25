import enum
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, Index, Enum
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.db.types import GUID
from .project import Project
from .artifact import Artifact
from .user import User
from .data_mode import DataMode

class ScanStatus(enum.Enum):
    QUEUED = "queued"
    PREPARING = "preparing"
    SCANNING_SOURCE = "scanning_source"
    SCANNING_DEPENDENCIES = "scanning_dependencies"
    SCANNING_CONTAINERS = "scanning_containers"
    SCANNING_CERTIFICATES = "scanning_certificates"
    SCANNING_BINARIES = "scanning_binaries"
    CORRELATING = "correlating"
    GENERATING_CBOM = "generating_cbom"
    ASSESSING_RISK = "assessing_risk"
    GENERATING_RECOMMENDATIONS = "generating_recommendations"
    COMPLETED = "completed"
    FAILED = "failed"

class Scan(Base):
    __tablename__ = "scans"
    
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    project_id = Column(GUID, ForeignKey("projects.id"), nullable=False)
    artifact_id = Column(GUID, ForeignKey("artifacts.id"), nullable=False)
    scan_type = Column(String(100), nullable=False)
    config_json = Column(Text)
    status = Column(Enum(ScanStatus), default=ScanStatus.QUEUED)
    progress_percentage = Column(Integer, default=0)
    current_stage = Column(String(100))
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    initiated_by_id = Column(GUID, ForeignKey("users.id"), nullable=True)
    data_mode = Column(Enum(DataMode), default=DataMode.SIMULATION, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="scans")
    artifact = relationship("Artifact", back_populates="scans")
    initiated_by = relationship("User", back_populates="scan_runs")
    findings = relationship("Finding", back_populates="scan")
    cbom_documents = relationship("CBOMDocument", back_populates="scan")
    audit_events = relationship("AuditEvent", back_populates="scan")
    
    # Indexes
    __table_args__ = (
        Index('ix_scans_project_id', project_id),
        Index('ix_scans_artifact_id', artifact_id),
        Index('ix_scans_status', status),
        Index('ix_scans_data_mode', data_mode),
    )
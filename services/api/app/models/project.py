import enum
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Index, Enum
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.db.types import GUID
from .user import User
from .data_mode import DataMode

class ProjectStatus(enum.Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(Enum(ProjectStatus), default=ProjectStatus.ACTIVE)
    owner_id = Column(GUID, ForeignKey("users.id"), nullable=False)
    data_mode = Column(Enum(DataMode), default=DataMode.DEMO, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_scanned_at = Column(DateTime, nullable=True)
    
    # Relationships
    owner = relationship("User", back_populates="projects")
    artifacts = relationship("Artifact", back_populates="project")
    scans = relationship("Scan", back_populates="project")
    cbom_documents = relationship("CBOMDocument", back_populates="project")
    findings = relationship("Finding", back_populates="project")
    risk_assessments = relationship("RiskAssessment", back_populates="project")
    migration_recommendations = relationship("MigrationRecommendation", back_populates="project")
    
    # Indexes
    __table_args__ = (
        Index('ix_projects_name', name),
        Index('ix_projects_owner_id', owner_id),
        Index('ix_projects_data_mode', data_mode),
    )
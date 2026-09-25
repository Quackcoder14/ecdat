import enum
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, Index, JSON, Enum
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.db.types import GUID
from .project import Project
from .finding import Finding
from .data_mode import DataMode

class RiskLevel(enum.Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFORMATIONAL = "informational"

class RiskAssessment(Base):
    __tablename__ = "risk_assessments"
    
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    project_id = Column(GUID, ForeignKey("projects.id"), nullable=False)
    finding_id = Column(GUID, ForeignKey("findings.id"), nullable=False)
    
    risk_level = Column(Enum(RiskLevel), nullable=False)
    risk_score = Column(Integer, nullable=True)  # 0-100 scale
    
    # Mosca-style assessment fields
    data_security_lifetime_years = Column(Integer, nullable=True)
    migration_lead_time_years = Column(Integer, nullable=True)
    threat_horizon_years = Column(Integer, nullable=True)
    planning_status = Column(String(100), nullable=True)
    
    # Risk factors (JSON for flexibility)
    risk_factors = Column(JSON)  # List of risk factor descriptions
    risk_reasons = Column(JSON)  # Detailed reasons for the risk level
    data_mode = Column(Enum(DataMode), default=DataMode.SIMULATION, nullable=False)
    
    assessed_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    project = relationship("Project")
    finding = relationship("Finding")
    
    # Indexes
    __table_args__ = (
        Index('ix_risk_assessments_project_id', project_id),
        Index('ix_risk_assessments_finding_id', finding_id),
        Index('ix_risk_assessments_risk_level', risk_level),
        Index('ix_risk_assessments_data_mode', data_mode),
    )
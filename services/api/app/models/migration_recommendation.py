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

class MigrationComplexity(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class MigrationPriority(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class MigrationRecommendation(Base):
    __tablename__ = "migration_recommendations"
    
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    project_id = Column(GUID, ForeignKey("projects.id"), nullable=False)
    finding_id = Column(GUID, ForeignKey("findings.id"), nullable=False)
    
    # Current state
    current_algorithm = Column(String(100), nullable=False)
    current_usage = Column(String(200), nullable=False)
    current_parameters = Column(JSON, nullable=True)
    
    # Recommendation
    candidate_algorithm = Column(String(100), nullable=False)
    candidate_type = Column(String(50), nullable=False)  # e.g., "PQC", "hybrid", "retain"
    rationale = Column(Text)
    
    # Migration details
    migration_complexity = Column(Enum(MigrationComplexity), nullable=False)
    migration_priority = Column(Enum(MigrationPriority), nullable=False)
    affected_components = Column(JSON)  # List of affected component names
    compatibility_notes = Column(Text)
    performance_notes = Column(Text)
    hybrid_option = Column(String(100), nullable=True)
    data_mode = Column(Enum(DataMode), default=DataMode.SIMULATION, nullable=False)
    
    # Confidence and metadata
    confidence = Column(Integer, nullable=True)  # 0-100 scale
    generated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    project = relationship("Project")
    finding = relationship("Finding")
    
    # Indexes
    __table_args__ = (
        Index('ix_migration_recommendations_project_id', project_id),
        Index('ix_migration_recommendations_finding_id', finding_id),
        Index('ix_migration_recommendations_priority', migration_priority),
        Index('ix_migration_recommendations_data_mode', data_mode),
    )
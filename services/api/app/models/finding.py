import enum
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, Text, Integer, Float, DateTime, ForeignKey, Index, JSON, Enum
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.db.types import GUID
from .project import Project
from .scan import Scan
from .data_mode import DataMode

class FindingConfidence(enum.Enum):
    VERY_HIGH = 0.9
    HIGH = 0.75
    MEDIUM = 0.5
    LOW = 0.25

class CryptoFamily(enum.Enum):
    ASYMMETRIC = "asymmetric"
    SYMMETRIC = "symmetric"
    HASH = "hash"
    PROTOCOL = "protocol"
    CERTIFICATE = "certificate"
    LIBRARY = "library"

class QuantumStatus(enum.Enum):
    VULNERABLE = "vulnerable"
    NOT_PRIMARY_TARGET = "not_primary_target"
    CONDITIONAL = "conditional"
    UNKNOWN = "unknown"

class Finding(Base):
    __tablename__ = "findings"
    
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    project_id = Column(GUID, ForeignKey("projects.id"), nullable=False)
    scan_id = Column(GUID, ForeignKey("scans.id"), nullable=False)
    
    # Core finding data
    algorithm = Column(String(100), nullable=False)
    family = Column(Enum(CryptoFamily), nullable=False)
    parameters = Column(JSON, nullable=True)
    purpose = Column(String(200), nullable=False)
    
    # Location data
    artifact_name = Column(String(500), nullable=True)
    file_path = Column(String(1000), nullable=True)
    line_start = Column(Integer, nullable=True)
    line_end = Column(Integer, nullable=True)
    
    # Evidence and confidence
    evidence = Column(JSON)  # List of evidence strings
    confidence = Column(Float, nullable=False)  # 0.0 to 1.0
    confidence_level = Column(Enum(FindingConfidence), nullable=False)
    
    # Classification
    quantum_status = Column(Enum(QuantumStatus), nullable=False)
    
    # Source information
    source_scanner = Column(String(100), nullable=False)  # e.g., "source_scanner", "dependency_scanner"
    data_mode = Column(Enum(DataMode), default=DataMode.SIMULATION, nullable=False)
    
    # Timestamps
    discovered_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="findings")
    scan = relationship("Scan", back_populates="findings")
    
    # Indexes
    __table_args__ = (
        Index('ix_findings_project_id', project_id),
        Index('ix_findings_scan_id', scan_id),
        Index('ix_findings_algorithm', algorithm),
        Index('ix_findings_family', family),
        Index('ix_findings_quantum_status', quantum_status),
        Index('ix_findings_confidence', confidence),
        Index('ix_findings_data_mode', data_mode),
    )
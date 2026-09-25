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
from .data_mode import DataMode

class CBOMFormat(enum.Enum):
    CYCLONEDX = "cyclonedx"
    SPDX = "spdx"

class CBOMDocument(Base):
    __tablename__ = "cbom_documents"
    
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    project_id = Column(GUID, ForeignKey("projects.id"), nullable=False)
    scan_id = Column(GUID, ForeignKey("scans.id"), nullable=False)
    
    format = Column(Enum(CBOMFormat), default=CBOMFormat.CYCLONEDX)
    version = Column(String(20), default="1.7")
    bom_json = Column(JSONB, nullable=False)  # Full CBOM document
    data_mode = Column(Enum(DataMode), default=DataMode.SIMULATION, nullable=False)
    
    generated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="cbom_documents")
    scan = relationship("Scan", back_populates="cbom_documents")
    
    # Indexes
    __table_args__ = (
        Index('ix_cbom_documents_project_id', project_id),
        Index('ix_cbom_documents_scan_id', scan_id),
        Index('ix_cbom_documents_data_mode', data_mode),
    )
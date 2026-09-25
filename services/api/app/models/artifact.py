import enum
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, Index, Enum
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.db.types import GUID
from .project import Project
from .data_mode import DataMode

class ArtifactType(enum.Enum):
    GIT_REPO = "git_repo"
    ZIP_TAR = "zip_tar"
    CONTAINER_IMAGE = "container_image"
    CERTIFICATE_BUNDLE = "certificate_bundle"
    BINARY = "binary"
    DEMO_DATASET = "demo_dataset"

class ArtifactStatus(enum.Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class Artifact(Base):
    __tablename__ = "artifacts"
    
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    project_id = Column(GUID, ForeignKey("projects.id"), nullable=False)
    name = Column(String(255), nullable=False)
    artifact_type = Column(Enum(ArtifactType), nullable=False)
    filename = Column(String(500), nullable=False)
    file_path = Column(String(1000), nullable=False)
    file_size = Column(Integer)
    sha256_hash = Column(String(64), unique=True, index=True)
    status = Column(Enum(ArtifactStatus), default=ArtifactStatus.UPLOADED)
    data_mode = Column(Enum(DataMode), default=DataMode.DEMO, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    
    # Relationships
    project = relationship("Project", back_populates="artifacts")
    scans = relationship("Scan", back_populates="artifact")
    
    # Indexes
    __table_args__ = (
        Index('ix_artifacts_project_id', project_id),
        Index('ix_artifacts_sha256', sha256_hash),
        Index('ix_artifacts_data_mode', data_mode),
    )
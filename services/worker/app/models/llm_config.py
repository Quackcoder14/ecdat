import enum
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Index, Enum, Boolean
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.db.types import GUID
from .project import Project
from .data_mode import DataMode

class LLMProviderType(enum.Enum):
    MOCK = "mock"
    OPENAI_COMPATIBLE = "openai_compatible"
    OLLAMA = "ollama"
    VLLM = "vllm"

class LLMConfig(Base):
    __tablename__ = "llm_provider_configs"
    
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    project_id = Column(GUID, ForeignKey("projects.id"), nullable=True)  # NULL for global config
    
    provider_type = Column(Enum(LLMProviderType), nullable=False)
    model = Column(String(100), nullable=False)
    base_url = Column(String(500), nullable=True)
    api_key_encrypted = Column(String(500), nullable=True)  # In practice, this would be properly encrypted
    is_active = Column(Boolean, default=False)
    data_mode = Column(Enum(DataMode), default=DataMode.SIMULATION, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = relationship("Project")
    
    # Indexes
    __table_args__ = (
        Index('ix_llm_configs_project_id', project_id),
        Index('ix_llm_configs_provider_type', provider_type),
        Index('ix_llm_configs_is_active', is_active),
        Index('ix_llm_configs_data_mode', data_mode),
    )
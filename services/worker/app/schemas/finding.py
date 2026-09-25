"""
Finding schemas
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

from app.models.finding import FindingConfidence, CryptoFamily, QuantumStatus
from app.models.data_mode import DataMode


class FindingBase(BaseModel):
    algorithm: str
    family: CryptoFamily
    parameters: Optional[Dict[str, Any]] = None
    purpose: str
    artifact_name: Optional[str] = None
    file_path: Optional[str] = None
    line_start: Optional[int] = None
    line_end: Optional[int] = None
    evidence: List[str] = []
    confidence: float
    confidence_level: FindingConfidence
    quantum_status: QuantumStatus
    source_scanner: str


class FindingCreate(FindingBase):
    project_id: uuid.UUID
    scan_id: uuid.UUID


class FindingResponse(FindingBase):
    id: uuid.UUID
    project_id: uuid.UUID
    scan_id: uuid.UUID
    data_mode: DataMode
    discovered_at: datetime

    class Config:
        from_attributes = True


class FindingFilter(BaseModel):
    project_id: Optional[uuid.UUID] = None
    algorithm: Optional[str] = None
    family: Optional[str] = None
    quantum_status: Optional[str] = None
    confidence_min: Optional[float] = None

__all__ = ["FindingBase", "FindingCreate", "FindingResponse", "FindingFilter"]
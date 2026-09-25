"""
Scan schemas
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

from app.models.scan import ScanStatus
from app.models.data_mode import DataMode


class ScanBase(BaseModel):
    project_id: uuid.UUID
    artifact_id: uuid.UUID
    scan_type: str
    config_json: Optional[str] = None


class ScanCreate(ScanBase):
    pass


class ScanUpdate(BaseModel):
    scan_type: Optional[str] = None
    config_json: Optional[str] = None
    status: Optional[ScanStatus] = None


class ScanResponse(ScanBase):
    id: uuid.UUID
    status: ScanStatus
    data_mode: DataMode
    progress_percentage: int
    current_stage: Optional[str] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    initiated_by_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
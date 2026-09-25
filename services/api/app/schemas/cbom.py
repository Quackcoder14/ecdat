"""
CBOM schemas
"""

from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
import uuid

from app.models.data_mode import DataMode


class CBOMExportRequest(BaseModel):
    project_id: uuid.UUID
    format: str = "cyclonedx"


class CBOMResponse(BaseModel):
    bom: Dict[str, Any]
    project_id: uuid.UUID
    scan_id: uuid.UUID
    data_mode: DataMode
    generated_at: datetime

    class Config:
        from_attributes = True
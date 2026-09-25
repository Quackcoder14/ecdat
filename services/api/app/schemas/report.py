"""
Report schemas
"""

from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
import uuid

class ReportBase(BaseModel):
    project_id: uuid.UUID
    name: str
    type: str

class ReportCreate(ReportBase):
    pass

class ReportResponse(ReportBase):
    id: uuid.UUID
    generated_at: datetime
    status: str

    class Config:
        from_attributes = True
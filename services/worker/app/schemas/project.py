"""
Project schemas
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid

from app.models.project import ProjectStatus
from app.models.data_mode import DataMode


class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None


class ProjectResponse(ProjectBase):
    id: uuid.UUID
    status: ProjectStatus
    data_mode: DataMode
    owner_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    last_scanned_at: Optional[datetime] = None

    class Config:
        from_attributes = True

__all__ = ["ProjectBase", "ProjectCreate", "ProjectUpdate", "ProjectResponse"]
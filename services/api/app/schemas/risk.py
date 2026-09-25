"""
Risk schemas
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

from app.models.risk_assessment import RiskLevel
from app.models.data_mode import DataMode


class RiskAssessmentBase(BaseModel):
    finding_id: uuid.UUID
    risk_level: RiskLevel
    risk_score: Optional[int] = None
    data_security_lifetime_years: Optional[int] = None
    migration_lead_time_years: Optional[int] = None
    threat_horizon_years: Optional[int] = None
    planning_status: Optional[str] = None
    risk_factors: List[str] = []
    risk_reasons: List[str] = []


class RiskAssessmentCreate(RiskAssessmentBase):
    project_id: uuid.UUID


class RiskAssessmentResponse(RiskAssessmentBase):
    id: uuid.UUID
    project_id: uuid.UUID
    data_mode: DataMode
    assessed_at: datetime

    class Config:
        from_attributes = True


class RiskFilter(BaseModel):
    project_id: Optional[uuid.UUID] = None
    risk_level: Optional[str] = None


class RiskSummaryResponse(BaseModel):
    risk_distribution: Dict[str, int]
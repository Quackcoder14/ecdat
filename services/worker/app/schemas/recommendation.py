"""
Recommendation schemas
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

from app.models.migration_recommendation import MigrationComplexity, MigrationPriority
from app.models.data_mode import DataMode


class MigrationRecommendationBase(BaseModel):
    finding_id: uuid.UUID
    current_algorithm: str
    current_usage: str
    current_parameters: Optional[Dict[str, Any]] = None
    candidate_algorithm: str
    candidate_type: str
    rationale: str
    migration_complexity: MigrationComplexity
    migration_priority: MigrationPriority
    affected_components: List[str] = []
    compatibility_notes: Optional[str] = None
    performance_notes: Optional[str] = None
    hybrid_option: Optional[str] = None
    confidence: Optional[int] = None


class MigrationRecommendationCreate(MigrationRecommendationBase):
    project_id: uuid.UUID


class MigrationRecommendationResponse(MigrationRecommendationBase):
    id: uuid.UUID
    project_id: uuid.UUID
    data_mode: DataMode
    generated_at: datetime

    class Config:
        from_attributes = True


class RecommendationFilter(BaseModel):
    project_id: Optional[uuid.UUID] = None
    migration_priority: Optional[str] = None


class RecommendationSummaryResponse(BaseModel):
    recommendation_distribution: Dict[str, int]
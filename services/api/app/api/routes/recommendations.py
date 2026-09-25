"""
Migration recommendation routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from app.db.session import get_db
from app.models.migration_recommendation import MigrationRecommendation, MigrationComplexity, MigrationPriority
from app.models.finding import Finding
from app.models.project import Project
from app.models.user import User
from app.models.data_mode import DataMode
from app.schemas.recommendation import MigrationRecommendationResponse, RecommendationFilter
from app.core.security import get_current_active_user, get_data_mode

router = APIRouter()


@router.get("/{project_id}")
def get_project_recommendations(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    data_mode: DataMode = Depends(get_data_mode)
):
    """
    Get migration recommendations for a project
    """
    # Verify project ownership
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == current_user.id,
        Project.data_mode == data_mode
    ).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get recommendations with findings
    recommendations = db.query(MigrationRecommendation).join(Finding).filter(
        Finding.project_id == project_id,
        Finding.data_mode == data_mode
    ).all()
    
    return recommendations


@router.get("/{project_id}/summary")
def get_project_recommendations_summary(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    data_mode: DataMode = Depends(get_data_mode)
):
    """
    Get recommendations summary for a project
    """
    # Verify project ownership
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == current_user.id,
        Project.data_mode == data_mode
    ).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Count recommendations by priority
    priority_counts = db.query(
        MigrationRecommendation.migration_priority,
        func.count(MigrationRecommendation.id)
    ).join(Finding).filter(
        Finding.project_id == project_id,
        Finding.data_mode == data_mode
    ).group_by(MigrationRecommendation.migration_priority).all()
    
    # Convert to dictionary
    summary = {priority.value: 0 for priority in MigrationPriority}
    for priority, count in priority_counts:
        summary[priority.value] = count
    
    return summary

__all__ = ["router"]
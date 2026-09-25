"""
Reports routes
"""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import Optional
import uuid

from app.db.session import get_db
from app.models.project import Project
from app.models.user import User
from app.models.data_mode import DataMode
from app.core.security import get_current_active_user, get_data_mode

router = APIRouter()


@router.get("/{project_id}/executive-summary")
def get_executive_summary(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    data_mode: DataMode = Depends(get_data_mode)
):
    """
    Get executive summary report for a project
    """
    # Verify project ownership
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == current_user.id,
        Project.data_mode == data_mode
    ).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get basic stats
    from app.models.finding import Finding
    from app.models.risk_assessment import RiskAssessment, RiskLevel
    from app.models.migration_recommendation import MigrationRecommendation, MigrationPriority
    
    findings_count = db.query(Finding).filter(
        Finding.project_id == project_id,
        Finding.data_mode == data_mode
    ).count()
    
    risk_counts = db.query(
        RiskAssessment.risk_level,
        func.count(RiskAssessment.id)
    ).join(Finding).filter(
        Finding.project_id == project_id,
        Finding.data_mode == data_mode
    ).group_by(RiskAssessment.risk_level).all()
    
    rec_counts = db.query(
        MigrationRecommendation.migration_priority,
        func.count(MigrationRecommendation.id)
    ).join(Finding).filter(
        Finding.project_id == project_id,
        Finding.data_mode == data_mode
    ).group_by(MigrationRecommendation.migration_priority).all()
    
    # Format response
    summary = {
        "project": {
            "id": str(project.id),
            "name": project.name,
            "description": project.description,
            "data_mode": data_mode.value
        },
        "statistics": {
            "total_findings": findings_count,
            "risk_distribution": {level.value: count for level, count in risk_counts},
            "recommendation_distribution": {priority.value: count for priority, count in rec_counts}
        },
        "generated_at": datetime.utcnow().isoformat()
    }
    
    return summary


@router.get("/{project_id}/technical-report")
def get_technical_report(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    data_mode: DataMode = Depends(get_data_mode)
):
    """
    Get technical report for a project
    """
    # Verify project ownership
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == current_user.id,
        Project.data_mode == data_mode
    ).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Return technical report data
    return {
        "project_id": str(project_id),
        "report_type": "technical",
        "message": "Technical report generation would be implemented here",
        "generated_at": datetime.utcnow().isoformat()
    }

__all__ = ["router"]
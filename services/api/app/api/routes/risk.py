"""
Risk assessment routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from app.db.session import get_db
from app.models.risk_assessment import RiskAssessment, RiskLevel
from app.models.finding import Finding
from app.models.project import Project
from app.models.user import User
from app.models.data_mode import DataMode
from app.schemas.risk import RiskAssessmentResponse, RiskFilter
from app.core.security import get_current_active_user, get_data_mode

router = APIRouter()


@router.get("/{project_id}")
def get_project_risk(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    data_mode: DataMode = Depends(get_data_mode)
):
    """
    Get risk assessments for a project
    """
    # Verify project ownership
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == current_user.id,
        Project.data_mode == data_mode
    ).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get risk assessments with findings
    risk_assessments = db.query(RiskAssessment).join(Finding).filter(
        Finding.project_id == project_id,
        Finding.data_mode == data_mode
    ).all()
    
    return risk_assessments


@router.get("/{project_id}/summary")
def get_project_risk_summary(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    data_mode: DataMode = Depends(get_data_mode)
):
    """
    Get risk summary for a project
    """
    # Verify project ownership
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == current_user.id,
        Project.data_mode == data_mode
    ).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Count risks by level
    risk_counts = db.query(
        RiskAssessment.risk_level,
        func.count(RiskAssessment.id)
    ).join(Finding).filter(
        Finding.project_id == project_id,
        Finding.data_mode == data_mode
    ).group_by(RiskAssessment.risk_level).all()
    
    # Convert to dictionary
    summary = {level.value: 0 for level in RiskLevel}
    for level, count in risk_counts:
        summary[level.value] = count
    
    return summary

__all__ = ["router"]
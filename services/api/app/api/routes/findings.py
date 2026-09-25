"""
Finding management routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from app.db.session import get_db
from app.models.finding import Finding, FindingConfidence, CryptoFamily, QuantumStatus
from app.models.project import Project
from app.models.scan import Scan
from app.models.user import User
from app.models.data_mode import DataMode
from app.schemas.finding import FindingResponse, FindingFilter
from app.core.security import get_current_active_user, get_data_mode

router = APIRouter()


@router.get("/", response_model=List[FindingResponse])
def read_findings(
    skip: int = 0,
    limit: int = 100,
    project_id: Optional[uuid.UUID] = None,
    algorithm: Optional[str] = None,
    family: Optional[str] = None,
    quantum_status: Optional[str] = None,
    confidence_min: Optional[float] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    data_mode: DataMode = Depends(get_data_mode)
):
    """
    Retrieve findings with optional filtering
    """
    query = db.query(Finding).join(Project).filter(
        Project.owner_id == current_user.id,
        Finding.data_mode == data_mode
    )
    
    # Apply filters
    if project_id:
        query = query.filter(Finding.project_id == project_id)
    if algorithm:
        query = query.filter(Finding.algorithm.ilike(f"%{algorithm}%"))
    if family:
        query = query.filter(Finding.family == family)
    if quantum_status:
        query = query.filter(Finding.quantum_status == quantum_status)
    if confidence_min is not None:
        query = query.filter(Finding.confidence >= confidence_min)
    
    findings = query.offset(skip).limit(limit).all()
    return findings


@router.get("/{finding_id}", response_model=FindingResponse)
def read_finding(
    finding_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    data_mode: DataMode = Depends(get_data_mode)
):
    """
    Get a specific finding by ID
    """
    finding = db.query(Finding).join(Project).filter(
        Finding.id == finding_id,
        Project.owner_id == current_user.id,
        Finding.data_mode == data_mode
    ).first()
    if finding is None:
        raise HTTPException(status_code=404, detail="Finding not found")
    return finding

__all__ = ["router"]
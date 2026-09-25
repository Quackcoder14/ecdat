"""
Scan management routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from app.db.session import get_db
from app.models.scan import Scan, ScanStatus
from app.models.project import Project
from app.models.artifact import Artifact
from app.models.user import User
from app.models.data_mode import DataMode
from app.schemas.scan import ScanCreate, ScanResponse, ScanUpdate
from app.core.security import get_current_active_user, get_data_mode
from app.core.celery_client import celery_app

router = APIRouter()


@router.get("/", response_model=List[ScanResponse])
def read_scans(
    skip: int = 0,
    limit: int = 100,
    project_id: Optional[uuid.UUID] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    data_mode: DataMode = Depends(get_data_mode)
):
    """
    Retrieve scans
    """
    query = db.query(Scan).join(Project).filter(
        Project.owner_id == current_user.id,
        Scan.data_mode == data_mode
    )
    
    if project_id:
        query = query.filter(Scan.project_id == project_id)
    
    scans = query.offset(skip).limit(limit).all()
    return scans


@router.post("/", response_model=ScanResponse)
def create_scan(
    scan: ScanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    data_mode: DataMode = Depends(get_data_mode)
):
    """
    Create new scan
    """
    # Verify project ownership
    project = db.query(Project).filter(
        Project.id == scan.project_id,
        Project.owner_id == current_user.id,
        Project.data_mode == data_mode
    ).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Verify artifact belongs to project
    artifact = db.query(Artifact).filter(
        Artifact.id == scan.artifact_id,
        Artifact.project_id == project.id,
        Artifact.data_mode == data_mode
    ).first()
    if artifact is None:
        raise HTTPException(status_code=404, detail="Artifact not found in project")
    
    # Create scan record
    db_scan = Scan(
        project_id=scan.project_id,
        artifact_id=scan.artifact_id,
        scan_type=scan.scan_type,
        config_json=scan.config_json,
        initiated_by_id=current_user.id,
        status=ScanStatus.QUEUED,
        data_mode=data_mode
    )
    db.add(db_scan)
    db.commit()
    db.refresh(db_scan)
    
    # Queue scan task to Celery worker
    from app.tasks.scan_tasks import run_scan
    celery_app.send_task('app.tasks.scan_tasks.run_scan', args=[db_scan.id])
    
    return db_scan


@router.get("/{scan_id}", response_model=ScanResponse)
def read_scan(
    scan_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    data_mode: DataMode = Depends(get_data_mode)
):
    """
    Get a specific scan by ID
    """
    scan = db.query(Scan).join(Project).filter(
        Scan.id == scan_id,
        Project.owner_id == current_user.id,
        Scan.data_mode == data_mode
    ).first()
    if scan is None:
        raise HTTPException(status_code=404, detail="Scan not found")
    return scan


@router.get("/{scan_id}/events")
def get_scan_events(
    scan_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    data_mode: DataMode = Depends(get_data_mode)
):
    """
    Get scan progress events (for SSE or polling)
    """
    scan = db.query(Scan).join(Project).filter(
        Scan.id == scan_id,
        Project.owner_id == current_user.id,
        Scan.data_mode == data_mode
    ).first()
    if scan is None:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    return {
        "scan_id": str(scan.id),
        "status": scan.status.value,
        "progress_percentage": scan.progress_percentage,
        "current_stage": scan.current_stage,
        "started_at": scan.started_at,
        "completed_at": scan.completed_at,
        "error_message": scan.error_message
    }


__all__ = ["router"]
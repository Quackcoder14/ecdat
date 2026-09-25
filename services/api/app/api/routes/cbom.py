"""
CBOM management routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
import uuid

from app.db.session import get_db
from app.models.cbom_document import CBOMDocument
from app.models.project import Project
from app.models.user import User
from app.models.data_mode import DataMode
from app.core.security import get_current_active_user, get_data_mode
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get("/{project_id}")
def get_project_cbom(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    data_mode: DataMode = Depends(get_data_mode)
):
    """
    Get the CBOM for a project
    """
    # Verify project ownership
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == current_user.id,
        Project.data_mode == data_mode
    ).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get the most recent CBOM
    cbom = db.query(CBOMDocument).filter(
        CBOMDocument.project_id == project_id,
        CBOMDocument.data_mode == data_mode
    ).order_by(CBOMDocument.generated_at.desc()).first()
    
    if cbom is None:
        raise HTTPException(status_code=404, detail="CBOM not found for project")
    
    return JSONResponse(content=cbom.bom_json)


@router.get("/{project_id}/export")
def export_project_cbom(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    data_mode: DataMode = Depends(get_data_mode)
):
    """
    Export the CBOM for a project as JSON
    """
    # Verify project ownership
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == current_user.id,
        Project.data_mode == data_mode
    ).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get the most recent CBOM
    cbom = db.query(CBOMDocument).filter(
        CBOMDocument.project_id == project_id,
        CBOMDocument.data_mode == data_mode
    ).order_by(CBOMDocument.generated_at.desc()).first()
    
    if cbom is None:
        raise HTTPException(status_code=404, detail="CBOM not found for project")
    
    # Return as downloadable JSON
    return JSONResponse(
        content=cbom.bom_json,
        headers={
            "Content-Disposition": f"attachment; filename=cbom-project-{project_id}.json"
        }
    )

__all__ = ["router"]
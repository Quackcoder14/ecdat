"""
AI Assistant routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import uuid

from app.db.session import get_db
from app.models.project import Project
from app.models.finding import Finding
from app.models.risk_assessment import RiskAssessment
from app.models.migration_recommendation import MigrationRecommendation
from app.models.cbom_document import CBOMDocument
from app.models.user import User
from app.services.llm import LLMProviderFactory, ContextBuilder
from app.core.security import get_current_active_user, get_data_mode
from app.models.data_mode import DataMode

router = APIRouter()


class AssistantQuery(BaseModel):
    question: str
    context: Optional[Dict[str, Any]] = None


class AssistantResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]] = []
    confidence: Optional[float] = None


@router.post("/query", response_model=AssistantResponse)
def query_assistant(
    query: AssistantQuery,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    data_mode: DataMode = Depends(get_data_mode)
):
    """
    Query the AI assistant with mode-aware context
    """
    # Get LLM provider
    llm_provider = LLMProviderFactory.get_provider('mock')
    
    # Build sanitized context from user's data in the current mode
    context = build_assistant_context(db, current_user.id, data_mode, query.context)
    
    # Generate response
    response = llm_provider.generate(
        prompt=query.question,
        context=context
    )
    
    return AssistantResponse(
        answer=response.get("text", ""),
        sources=response.get("sources", []),
        confidence=response.get("confidence")
    )


@router.post("/stream")
def stream_assistant_response(
    query: AssistantQuery,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    data_mode: DataMode = Depends(get_data_mode)
):
    """
    Stream response from AI assistant (placeholder for SSE implementation)
    """
    # For now, return regular response
    # In a full implementation, this would use Server-Sent Events
    return query_assistant(query, db, current_user, data_mode)


def build_assistant_context(
    db: Session, 
    user_id: uuid.UUID, 
    data_mode: DataMode,
    additional_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Build sanitized context for the AI assistant from user's data in the current mode
    """
    # Get user's projects in the current mode
    projects = db.query(Project).filter(
        Project.owner_id == user_id,
        Project.data_mode == data_mode
    ).all()
    
    # Get recent findings across projects in the current mode
    recent_findings = db.query(Finding).join(Project).filter(
        Project.owner_id == user_id,
        Project.data_mode == data_mode,
        Finding.data_mode == data_mode
    ).order_by(Finding.discovered_at.desc()).limit(20).all()
    
    # Get risk assessments
    risk_assessments = db.query(RiskAssessment).join(Finding).join(Project).filter(
        Project.owner_id == user_id,
        Project.data_mode == data_mode,
        Finding.data_mode == data_mode
    ).all()
    
    # Get recommendations
    recommendations = db.query(MigrationRecommendation).join(Finding).join(Project).filter(
        Project.owner_id == user_id,
        Project.data_mode == data_mode,
        Finding.data_mode == data_mode
    ).all()
    
    # Get CBOM
    cbom = db.query(CBOMDocument).join(Project).filter(
        Project.owner_id == user_id,
        Project.data_mode == data_mode,
        CBOMDocument.data_mode == data_mode
    ).order_by(CBOMDocument.generated_at.desc()).first()
    
    context = {
        "data_mode": data_mode.value,
        "user_id": str(user_id),
        "projects": [
            {
                "id": str(p.id),
                "name": p.name,
                "description": p.description
            } for p in projects
        ],
        "recent_findings": [
            {
                "id": str(f.id),
                "algorithm": f.algorithm,
                "family": f.family.value if hasattr(f.family, 'value') else str(f.family),
                "purpose": f.purpose,
                "confidence": f.confidence,
                "quantum_status": f.quantum_status.value if hasattr(f.quantum_status, 'value') else str(f.quantum_status)
            } for f in recent_findings
        ],
        "risk_assessments": [
            {
                "id": str(r.id),
                "finding_id": str(r.finding_id),
                "risk_level": r.risk_level.value if hasattr(r.risk_level, 'value') else str(r.risk_level),
                "risk_score": r.risk_score
            } for r in risk_assessments
        ],
        "recommendations": [
            {
                "id": str(r.id),
                "finding_id": str(r.finding_id),
                "candidate_algorithm": r.candidate_algorithm,
                "migration_priority": r.migration_priority.value if hasattr(r.migration_priority, 'value') else str(r.migration_priority),
                "migration_complexity": r.migration_complexity.value if hasattr(r.migration_complexity, 'value') else str(r.migration_complexity),
            } for r in recommendations
        ],
        "cbom": {
            "id": str(cbom.id),
            "scan_id": str(cbom.scan_id),
            "generated_at": cbom.generated_at.isoformat() if cbom.generated_at else None,
        } if cbom else None
    }
    
    # Merge with additional context if provided
    if additional_context:
        context.update(additional_context)
    
    return context

__all__ = ["router"]
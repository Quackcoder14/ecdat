"""
System routes for health checks and status
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db.session import get_db
from app.core.config import settings
from app.scanner.core.scanner_factory import get_scanner_registry

router = APIRouter()


@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint
    """
    # Check database connection
    try:
        db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    # Overall health
    overall_status = "healthy" if db_status == "healthy" else "degraded"
    
    return {
        "status": overall_status,
        "services": {
            "database": db_status,
            "api": "healthy"
        },
        "version": "1.0.0"
    }


@router.get("/scanners")
def get_scanner_status():
    """
    Get status of all configured scanners
    """
    try:
        registry = get_scanner_registry()
        return registry.get_scanner_status()
    except Exception as e:
        # Fallback to demo scanner if registry fails
        return {
            "demo_scanner": {"name": "demo_scanner", "available": True, "type": "DemoScanner", "error": str(e)},
        }


@router.get("/config")
def get_system_config():
    """
    Get non-sensitive system configuration
    """
    return {
        "demo_mode": settings.DEMO_MODE,
        "llm_provider": settings.LLM_PROVIDER,
        "artifact_storage_path": settings.ARTIFACT_STORAGE_PATH,
        "max_artifact_size": settings.MAX_ARTIFACT_SIZE,
        "scan_timeout_seconds": settings.SCAN_TIMEOUT_SECONDS
    }

__all__ = ["router"]
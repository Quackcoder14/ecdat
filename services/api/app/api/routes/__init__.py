from fastapi import APIRouter

from . import auth, projects, scans, findings, cbom, risk, recommendations, assistant, reports, system

api_router = APIRouter()

# Include all route modules
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(scans.router, prefix="/scans", tags=["scans"])
api_router.include_router(findings.router, prefix="/findings", tags=["findings"])
api_router.include_router(cbom.router, prefix="/cbom", tags=["cbom"])
api_router.include_router(risk.router, prefix="/risk", tags=["risk"])
api_router.include_router(recommendations.router, prefix="/recommendations", tags=["recommendations"])
api_router.include_router(assistant.router, prefix="/assistant", tags=["assistant"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(system.router, prefix="/system", tags=["system"])

__all__ = ["api_router"]
"""
System schemas
"""

from pydantic import BaseModel
from typing import Optional, Dict, Any, List

class ScannerStatus(BaseModel):
    name: str
    available: bool
    type: str

class SystemHealthResponse(BaseModel):
    status: str
    services: Dict[str, str]
    version: str

class SystemConfigResponse(BaseModel):
    demo_mode: bool
    llm_provider: str
    artifact_storage_path: str
    max_artifact_size: int
    scan_timeout_seconds: int
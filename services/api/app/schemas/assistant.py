"""
Assistant schemas
"""

from pydantic import BaseModel
from typing import Optional, Dict, Any, List

class AssistantQuery(BaseModel):
    question: str
    context: Optional[Dict[str, Any]] = None

class Source(BaseModel):
    title: str
    content: str
    finding_id: Optional[str] = None

class AssistantResponse(BaseModel):
    answer: str
    sources: List[Source] = []
    confidence: Optional[float] = None
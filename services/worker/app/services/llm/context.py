"""
Context sanitizer and builder for AI assistant
"""

import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

@dataclass
class SanitizedContext:
    """Sanitized context for LLM"""
    project_name: str
    findings: List[Dict[str, Any]]
    risk_summary: Dict[str, int]
    recommendations: List[Dict[str, Any]]
    selected_finding: Optional[Dict[str, Any]] = None


class SecretRedactor:
    """Redacts secrets from text"""
    
    # Patterns for common secrets
    PATTERNS = [
        # Private keys
        (r'-----BEGIN (RSA|EC|DSA|OPENSSH|PRIVATE) KEY-----[\s\S]*?-----END \1 KEY-----', '[REDACTED PRIVATE KEY]'),
        # API keys (common patterns)
        (r'(?i)(api[_-]?key|apikey|secret[_-]?key|access[_-]?token)\s*[:=]\s*[\w\-]{20,}', r'\1=[REDACTED]'),
        # AWS keys
        (r'AKIA[0-9A-Z]{16}', '[REDACTED AWS KEY]'),
        # Generic tokens
        (r'(?i)(token|secret|password)\s*[:=]\s*[\w\-\.]{20,}', r'\1=[REDACTED]'),
        # JWT tokens
        (r'eyJ[A-Za-z0-9\-_]+\.eyJ[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+', '[REDACTED JWT]'),
        # Certificates
        (r'-----BEGIN CERTIFICATE-----[\s\S]*?-----END CERTIFICATE-----', '[REDACTED CERTIFICATE]'),
    ]
    
    @classmethod
    def redact(cls, text: str) -> str:
        """Redact secrets from text"""
        for pattern, replacement in cls.PATTERNS:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE | re.MULTILINE)
        return text


class ContextSanitizer:
    """Sanitizes context before sending to LLM"""
    
    def __init__(self):
        self.redactor = SecretRedactor()
    
    def sanitize_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize entire context dictionary"""
        sanitized = {}
        
        for key, value in context.items():
            if isinstance(value, str):
                sanitized[key] = self.redactor.redact(value)
            elif isinstance(value, dict):
                sanitized[key] = self.sanitize_context(value)
            elif isinstance(value, list):
                sanitized[key] = [
                    self.sanitize_context(item) if isinstance(item, dict) else 
                    self.redactor.redact(item) if isinstance(item, str) else item
                    for item in value
                ]
            else:
                sanitized[key] = value
        
        return sanitized
    
    def sanitize_finding(self, finding: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize a finding for LLM consumption"""
        # Only include safe fields
        safe_fields = [
            'id', 'algorithm', 'family', 'parameters', 'purpose',
            'artifact_name', 'file_path', 'line_start', 'line_end',
            'evidence', 'confidence', 'quantum_status', 'source_scanner'
        ]
        
        sanitized = {}
        for field in safe_fields:
            if field in finding:
                value = finding[field]
                if isinstance(value, str):
                    sanitized[field] = self.redactor.redact(value)
                else:
                    sanitized[field] = value
        
        return sanitized


class ContextBuilder:
    """Builds sanitized context for LLM from ECDAT data"""
    
    def __init__(self):
        self.sanitizer = ContextSanitizer()
    
    def build_context(
        self,
        project: Dict[str, Any],
        findings: List[Dict[str, Any]],
        risk_assessments: List[Dict[str, Any]],
        recommendations: List[Dict[str, Any]],
        selected_finding: Optional[Dict[str, Any]] = None,
    ) -> SanitizedContext:
        """Build sanitized context for LLM"""
        
        # Sanitize findings
        sanitized_findings = [self.sanitizer.sanitize_finding(f) for f in findings]
        
        # Build risk summary
        risk_summary = {}
        for risk in risk_assessments:
            level = risk.get('risk_level', 'UNKNOWN')
            risk_summary[level] = risk_summary.get(level, 0) + 1
        
        # Sanitize recommendations
        sanitized_recommendations = []
        for rec in recommendations:
            safe_rec = {
                'current_algorithm': rec.get('current_algorithm'),
                'current_usage': rec.get('current_usage'),
                'candidate_algorithm': rec.get('candidate_algorithm'),
                'migration_complexity': rec.get('migration_complexity'),
                'migration_priority': rec.get('migration_priority'),
                'rationale': rec.get('rationale'),
                'hybrid_option': rec.get('hybrid_option'),
            }
            sanitized_recommendations.append(safe_rec)
        
        # Sanitize selected finding
        sanitized_selected = None
        if selected_finding:
            sanitized_selected = self.sanitizer.sanitize_finding(selected_finding)
        
        return SanitizedContext(
            project_name=project.get('name', 'Unknown Project'),
            findings=sanitized_findings,
            risk_summary=risk_summary,
            recommendations=sanitized_recommendations,
            selected_finding=sanitized_selected,
        )
    
    def to_dict(self, context: SanitizedContext) -> Dict[str, Any]:
        """Convert context to dictionary for LLM"""
        return {
            'project': context.project_name,
            'findings': context.findings,
            'risk_summary': context.risk_summary,
            'recommendations': context.recommendations,
            'selected_finding': context.selected_finding,
        }
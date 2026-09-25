"""
Base interfaces for all scanners in ECDAT
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class NormalizedFinding:
    """Standardized finding format that all scanners must produce"""
    id: str
    algorithm: str
    family: str  # asymmetric, symmetric, hash, protocol, certificate, library
    parameters: Dict[str, Any]
    purpose: str
    location: Dict[str, Any]  # file, line numbers, etc.
    source: str  # scanner type that produced this
    evidence: List[str]
    confidence: float  # 0.0 to 1.0
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


class BaseScanner(ABC):
    """Base class that all scanners must inherit from"""
    
    def __init__(self, scanner_name: str):
        self.scanner_name = scanner_name
        self.available = self._check_availability()
    
    @abstractmethod
    def _check_availability(self) -> bool:
        """Check if the scanner and its dependencies are available"""
        pass
    
    @abstractmethod
    def scan(self, target: Any) -> List[NormalizedFinding]:
        """Scan the target and return normalized findings"""
        pass
    
    def get_status(self) -> Dict[str, Any]:
        """Get scanner status information"""
        return {
            "name": self.scanner_name,
            "available": self.available,
            "type": self.__class__.__name__
        }


class SourceScanner(BaseScanner):
    """Scanner for source code analysis"""
    pass


class DependencyScanner(BaseScanner):
    """Scanner for dependency analysis (SBOMs, manifests)"""
    pass


class ContainerScanner(BaseScanner):
    """Scanner for container images"""
    pass


class CertificateScanner(BaseScanner):
    """Scanner for certificates and keys"""
    pass


class BinaryScanner(BaseScanner):
    """Scanner for binary files"""
    pass
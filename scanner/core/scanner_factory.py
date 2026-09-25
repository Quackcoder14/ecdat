"""
Scanner factory and registry for managing available scanners
"""

import logging
from typing import Dict, List, Type, Optional
from .base_scanner import (
    BaseScanner, SourceScanner, DependencyScanner, 
    ContainerScanner, CertificateScanner, BinaryScanner
)
from ..demo.demo_scanner import DemoScanner, create_demo_scanner

logger = logging.getLogger(__name__)


class ScannerRegistry:
    """Registry for managing scanner availability and creation"""
    
    def __init__(self):
        self._scanners: Dict[str, Type[BaseScanner]] = {}
        self._instances: Dict[str, BaseScanner] = {}
        self._register_default_scanners()
    
    def _register_default_scanners(self):
        """Register the default scanner types"""
        # Register demo scanner as fallback
        self.register_scanner("demo_scanner", DemoScanner)
        
        # Try to register real scanners if available
        self._try_register_real_scanners()
    
    def _try_register_real_scanners(self):
        """Attempt to register real scanners, falling back to demo if unavailable"""
        # Source scanners
        try:
            from ..source.tree_sitter_scanner import TreeSitterScanner
            tree_sitter = TreeSitterScanner()
            if tree_sitter.available:
                self.register_scanner("source_tree_sitter", TreeSitterScanner)
                logger.info("Registered TreeSitter source scanner (real tool available)")
            else:
                logger.info("TreeSitter tool not available, using regex-based detection")
                self.register_scanner("source_tree_sitter", TreeSitterScanner)  # Still use it, it has fallback
        except ImportError as e:
            logger.warning(f"TreeSitter scanner not available: {e}")
            self.register_scanner("source_tree_sitter", DemoScanner)
        
        try:
            from ..source.semgrep_scanner import SemgrepScanner
            semgrep = SemgrepScanner()
            if semgrep.available:
                self.register_scanner("source_semgrep", SemgrepScanner)
                logger.info("Registered Semgrep source scanner (real tool available)")
            else:
                logger.info("Semgrep tool not available, using regex-based detection")
                self.register_scanner("source_semgrep", SemgrepScanner)  # Still use it, it has fallback
        except ImportError as e:
            logger.warning(f"Semgrep scanner not available: {e}")
            self.register_scanner("source_semgrep", DemoScanner)
        
        # Dependency scanners
        try:
            from ..dependency.syft_scanner import SyftScanner
            syft = SyftScanner()
            if syft.available:
                self.register_scanner("dependency_syft", SyftScanner)
                logger.info("Registered Syft dependency scanner (real tool available)")
            else:
                logger.info("Syft tool not available, using dependency file analysis")
                self.register_scanner("dependency_syft", SyftScanner)  # Still use it, it has fallback
        except ImportError as e:
            logger.warning(f"Syft scanner not available: {e}")
            self.register_scanner("dependency_syft", DemoScanner)
        
        # Container scanners
        try:
            from ..container.trivy_scanner import TrivyScanner
            self.register_scanner("container_trivy", TrivyScanner)
            logger.info("Registered Trivy container scanner")
        except ImportError as e:
            logger.warning(f"Trivy scanner not available: {e}")
            self.register_scanner("container_trivy", DemoScanner)
            
        try:
            from ..container.syft_scanner import ContainerSyftScanner
            self.register_scanner("container_syft", ContainerSyftScanner)
            logger.info("Registered Syft container scanner")
        except ImportError as e:
            logger.warning(f"Container Syft scanner not available: {e}")
            self.register_scanner("container_syft", DemoScanner)
        
        # Certificate scanners
        try:
            from ..certificate.openssl_scanner import OpenSSLScanner
            self.register_scanner("certificate_openssl", OpenSSLScanner)
            logger.info("Registered OpenSSL certificate scanner")
        except ImportError as e:
            logger.warning(f"OpenSSL scanner not available: {e}")
            self.register_scanner("certificate_openssl", DemoScanner)
        
        # Binary scanners
        try:
            from ..binary.strings_scanner import StringsScanner
            self.register_scanner("binary_strings", StringsScanner)
            logger.info("Registered Strings binary scanner")
        except ImportError as e:
            logger.warning(f"Strings scanner not available: {e}")
            self.register_scanner("binary_strings", DemoScanner)
    
    def register_scanner(self, name: str, scanner_class: Type[BaseScanner]):
        """Register a scanner class by name"""
        self._scanners[name] = scanner_class
        logger.debug(f"Registered scanner: {name}")
    
    def get_scanner(self, name: str) -> BaseScanner:
        """Get or create a scanner instance by name"""
        if name not in self._scanners:
            raise ValueError(f"Unknown scanner: {name}")
        
        if name not in self._instances:
            scanner_class = self._scanners[name]
            self._instances[name] = scanner_class(name)
            logger.debug(f"Created scanner instance: {name}")
        
        return self._instances[name]
    
    def get_available_scanners(self) -> List[str]:
        """Get list of available scanner names"""
        available = []
        for name, instance in self._instances.items():
            if instance.available:
                available.append(name)
        return available
    
    def get_scanner_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all registered scanners"""
        status = {}
        for name, instance in self._instances.items():
            status[name] = instance.get_status()
        return status
    
    def scan_with_all_available(self, target: Any, scanner_types: List[str] = None) -> List:
        """
        Scan target with all available scanners of specified types
        Returns combined list of findings from all scanners
        """
        if scanner_types is None:
            scanner_types = list(self._scanners.keys())
        
        all_findings = []
        for scanner_name in scanner_types:
            try:
                scanner = self.get_scanner(scanner_name)
                if scanner.available:
                    findings = scanner.scan(target)
                    all_findings.extend(findings)
                    logger.info(f"Scanner {scanner_name} produced {len(findings)} findings")
                else:
                    logger.warning(f"Scanner {scanner_name} is not available")
            except Exception as e:
                logger.error(f"Error running scanner {scanner_name}: {e}")
        
        return all_findings


# Global scanner registry instance
scanner_registry = ScannerRegistry()

def get_scanner_registry() -> ScannerRegistry:
    """Get the global scanner registry"""
    return scanner_registry
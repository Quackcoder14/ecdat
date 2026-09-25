"""
Trivy container/image scanner adapter
"""

import json
import subprocess
import tempfile
import os
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

from ..core.base_scanner import ContainerScanner, NormalizedFinding

logger = logging.getLogger(__name__)


class TrivyScanner:
    """Trivy container/image scanner adapter"""
    
    def __init__(self):
        self.name = "trivy_scanner"
        self.available = self._check_trivy_available()
    
    def _check_trivy_available(self) -> bool:
        """Check if trivy is available"""
        try:
            result = subprocess.run(["trivy", "version"], capture_output=True, timeout=10)
            self.available = result.returncode == 0
            if self.available:
                logger.info("Trivy is available")
            else:
                logger.warning("Trivy not available")
        except Exception as e:
            logger.warning(f"Trivy check failed: {e}")
            self.available = False
        return self.available
    
    def scan(self, target: Any) -> List:
        """Scan target with Trivy"""
        if not self.available:
            logger.warning("Trivy not available, skipping scan")
            return []
        
        findings = []
        
        # Determine scan target path
        if hasattr(target, 'file_path'):
            scan_path = target.file_path
        elif hasattr(target, 'name'):
            scan_path = f"/scan-input/{target.name}"
        else:
            scan_path = str(target)
        
        if not os.path.exists(scan_path):
            logger.warning(f"Scan path does not exist: {scan_path}")
            return []
        
        # Run Trivy with JSON output
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            output_file = f.name
        
        try:
            # Scan filesystem
            cmd = [
                "trivy",
                "fs",
                "--format", "json",
                "--output", output_file,
                "--quiet",
                "--scanners", "vuln,secret,config",
                "--severity", "CRITICAL,HIGH,MEDIUM,LOW",
                scan_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode not in [0, 1]:
                logger.error(f"Trivy failed: {result.stderr}")
                return []
            
            # Parse results
            if os.path.exists(output_file):
                with open(output_file, 'r') as f:
                    data = json.load(f)
                
                findings = self._parse_trivy_results(data)
                return findings
            
        except subprocess.TimeoutExpired:
            logger.error("Trivy scan timed out")
        except Exception as e:
            logger.error(f"Trivy scan failed: {e}")
        finally:
            if os.path.exists(output_file):
                os.unlink(output_file)
        
        return []
    
    def _parse_trivy_results(self, data: Dict) -> List:
        """Parse Trivy JSON output into normalized findings"""
        findings = []
        
        results = data.get("Results", [])
        
        for result in results:
            target = result.get("Target", "")
            vulns = result.get("Vulnerabilities", [])
            secrets = result.get("Secrets", [])
            misconfigs = result.get("Misconfigurations", [])
            
            # Process vulnerabilities
            for vuln in vulns:
                finding = NormalizedFinding(
                    id=f"trivy-{vuln.get('VulnerabilityID', '')}",
                    algorithm=vuln.get("PkgName", "Unknown"),
                    family="vulnerability",
                    parameters={
                        "severity": vuln.get("Severity", "UNKNOWN"),
                        "package": vuln.get("PkgName", ""),
                        "installed_version": vuln.get("InstalledVersion", ""),
                        "fixed_version": vuln.get("FixedVersion", ""),
                        "vulnerability_id": vuln.get("VulnerabilityID", ""),
                        "cvss": vuln.get("CVSS", {}),
                        "references": vuln.get("References", [])
                    },
                    purpose="vulnerability",
                    location={
                        "artifact": "container/filesystem",
                        "target": target,
                        "package": vuln.get("PkgName", "")
                    },
                    source="trivy_scanner",
                    evidence=[
                        f"Vulnerability: {vuln.get('VulnerabilityID', '')}",
                        f"Package: {vuln.get('PkgName', '')} {vuln.get('InstalledVersion', '')}",
                        f"Severity: {vuln.get('Severity', '')}",
                        f"Fixed Version: {vuln.get('FixedVersion', 'N/A')}"
                    ],
                    confidence=0.95,
                    timestamp=datetime.utcnow()
                )
                findings.append(finding)
            
            # Process secrets
            for secret in secrets:
                finding = NormalizedFinding(
                    id=f"trivy-secret-{secret.get('RuleID', '')}",
                    algorithm=secret.get("RuleID", "Secret"),
                    family="secret",
                    parameters={
                        "category": secret.get("Category", ""),
                        "severity": secret.get("Severity", "UNKNOWN"),
                        "match": secret.get("Match", "")[:100] if secret.get("Match") else ""
                    },
                    purpose="secret_exposure",
                    location={
                        "artifact": "container/filesystem",
                        "target": target,
                        "file": secret.get("File", ""),
                        "line": secret.get("Line", 0)
                    },
                    source="trivy_scanner",
                    evidence=[f"Secret: {secret.get('RuleID', '')}", f"File: {secret.get('File', '')}"],
                    confidence=0.9,
                    timestamp=datetime.utcnow()
                )
                findings.append(finding)
            
            # Process misconfigurations
            for misconfig in misconfigs:
                finding = NormalizedFinding(
                    id=f"trivy-misconfig-{misconfig.get('ID', '')}",
                    algorithm=misconfig.get("Title", "Misconfiguration"),
                    family="misconfiguration",
                    parameters={
                        "type": misconfig.get("Type", ""),
                        "severity": misconfig.get("Severity", ""),
                        "namespace": misconfig.get("Namespace", ""),
                        "query": misconfig.get("Query", "")
                    },
                    purpose="misconfiguration",
                    location={
                        "artifact": "container/filesystem",
                        "target": target,
                        "file": misconfig.get("File", ""),
                        "line": misconfig.get("Line", 0)
                    },
                    source="trivy_scanner",
                    evidence=[f"Misconfig: {misconfig.get('Title', '')}", f"File: {misconfig.get('File', '')}"],
                    confidence=0.85,
                    timestamp=datetime.utcnow()
                )
                findings.append(finding)
        
        return findings
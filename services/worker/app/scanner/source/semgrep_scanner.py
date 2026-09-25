"""
Semgrep source code scanner adapter
"""

import json
import subprocess
import tempfile
import os
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

from ..core.base_scanner import SourceScanner, NormalizedFinding
from ..core.scanner_factory import get_scanner_registry

logger = logging.getLogger(__name__)


class SemgrepScanner(SourceScanner):
    """Semgrep source code scanner adapter"""
    
    def __init__(self):
        super().__init__("semgrep_scanner")
        self._check_semgrep_available()
    
    def _check_semgrep_available(self) -> bool:
        """Check if semgrep is available"""
        try:
            result = subprocess.run(["semgrep", "--version"], capture_output=True, timeout=10)
            self.available = result.returncode == 0
            if self.available:
                logger.info("Semgrep is available")
            else:
                logger.warning("Semgrep not available")
        except Exception as e:
            logger.warning(f"Semgrep check failed: {e}")
            self.available = False
        return self.available
    
    def _check_availability(self) -> bool:
        return self.available
    
    def scan(self, target: Any) -> List[NormalizedFinding]:
        """Scan target with Semgrep"""
        if not self.available:
            logger.warning("Semgrep not available, skipping scan")
            return []
        
        findings = []
        
        # Determine scan target path
        if hasattr(target, 'file_path'):
            scan_path = target.file_path
        elif hasattr(target, 'name'):
            # For artifacts, scan the extracted directory
            scan_path = f"/scan-input/{target.name}"
        else:
            scan_path = str(target)
        
        if not os.path.exists(scan_path):
            logger.warning(f"Scan path does not exist: {scan_path}")
            return []
        
        # Run Semgrep with crypto rules
        crypto_rules = self._get_crypto_rules()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(crypto_rules, f)
            rules_file = f.name
        
        try:
            # Run semgrep
            cmd = [
                "semgrep",
                "scan",
                "--config", rules_file,
                "--json",
                "--quiet",
                scan_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode not in [0, 1]:  # 0 = no findings, 1 = findings found
                logger.error(f"Semgrep failed: {result.stderr}")
                return []
            
            # Parse results
            if result.stdout:
                data = json.loads(result.stdout)
                findings = self._parse_semgrep_results(data, scan_path)
                return findings
            
        except subprocess.TimeoutExpired:
            logger.error("Semgrep scan timed out")
        except Exception as e:
            logger.error(f"Semgrep scan failed: {e}")
        finally:
            os.unlink(rules_file)
        
        return []
    
    def _get_crypto_rules(self) -> Dict:
        """Get crypto-focused Semgrep rules"""
        return {
            "rules": [
                {
                    "id": "crypto-rsa-keygen",
                    "pattern-either": [
                        "rsa.generate_private_key(...,
                        "RSA.generate_key(...",
                        "RSA_generate_key(...",
                    ],
                    "message": "RSA key generation detected",
                    "languages": ["python", "java", "go", "javascript", "typescript", "c", "cpp"],
                    "severity": "INFO",
                    "metadata": {
                        "algorithm": "RSA",
                        "family": "asymmetric",
                        "purpose": "key_generation",
                        "confidence": "VERY_HIGH"
                    }
                },
                {
                    "id": "crypto-rsa-sign",
                    "pattern-either": [
                        "private_key.sign(...,
                        "signature = ...sign(...",
                        "RSA_sign(...",
                    ],
                    "message": "RSA signing detected",
                    "languages": ["python", "java", "go", "javascript", "typescript", "c", "cpp"],
                    "severity": "INFO",
                    "metadata": {
                        "algorithm": "RSA",
                        "family": "asymmetric",
                        "purpose": "digital_signature",
                        "confidence": "HIGH"
                    }
                },
                {
                    "id": "crypto-ecdsa",
                    "pattern-either": [
                        "ecdsa.sign(...",
                        "ECDSA.sign(...",
                        "ecdsa.Sign(...",
                    ],
                    "message": "ECDSA signing detected",
                    "languages": ["python", "go", "javascript", "typescript", "c", "cpp"],
                    "severity": "INFO",
                    "metadata": {
                        "algorithm": "ECDSA",
                        "family": "asymmetric",
                        "purpose": "digital_signature",
                        "confidence": "HIGH"
                    }
                },
                {
                    "id": "crypto-ecdh",
                    "pattern-either": [
                        "ecdh.generate_key(...",
                        "ECDH(...",
                        "ecdh_key_exchange(...",
                    ],
                    "message": "ECDH key exchange detected",
                    "languages": ["python", "go", "javascript", "typescript", "c", "cpp"],
                    "severity": "INFO",
                    "metadata": {
                        "algorithm": "ECDH",
                        "family": "asymmetric",
                        "purpose": "key_establishment",
                        "confidence": "HIGH"
                    }
                },
                {
                    "id": "crypto-aes-gcm",
                    "pattern-either": [
                        "AES.new(..., mode=GCM)",
                        "Cipher.getInstance(\"AES/GCM\")",
                        "aes.GCM(...",
                    ],
                    "message": "AES-GCM encryption detected",
                    "languages": ["python", "java", "go", "javascript", "typescript", "c", "cpp"],
                    "severity": "INFO",
                    "metadata": {
                        "algorithm": "AES",
                        "family": "symmetric",
                        "purpose": "data_encryption",
                        "confidence": "HIGH"
                    }
                },
                {
                    "id": "crypto-sha256",
                    "pattern-either": [
                        "hashlib.sha256(...",
                        "SHA256(...",
                        "sha256(...",
                    ],
                    "message": "SHA-256 hashing detected",
                    "languages": ["python", "java", "go", "javascript", "typescript", "c", "cpp"],
                    "severity": "INFO",
                    "metadata": {
                        "algorithm": "SHA-256",
                        "family": "hash",
                        "purpose": "hashing",
                        "confidence": "HIGH"
                    }
                },
                {
                    "id": "crypto-3des",
                    "pattern-either": [
                        "DESede",
                        "3DES",
                        "DESede",
                    ],
                    "message": "3DES (legacy) detected",
                    "languages": ["java", "c", "cpp"],
                    "severity": "WARNING",
                    "metadata": {
                        "algorithm": "3DES",
                        "family": "symmetric",
                        "purpose": "data_encryption",
                        "confidence": "HIGH"
                    }
                }
            ]
        }
    
    def _parse_semgrep_results(self, data: Dict, scan_path: str) -> List[NormalizedFinding]:
        """Parse Semgrep JSON output into normalized findings"""
        findings = []
        
        for result in data.get("results", []):
            path = result.get("path", "")
            start_line = result.get("start", {}).get("line", 0)
            end_line = result.get("end", {}).get("line", 0)
            
            # Extract metadata
            extra = result.get("extra", {})
            metadata = extra.get("metadata", {})
            
            algorithm = metadata.get("algorithm", "UNKNOWN")
            family = metadata.get("family", "unknown")
            purpose = metadata.get("purpose", "unknown")
            confidence_str = metadata.get("confidence", "MEDIUM")
            
            # Map confidence
            confidence_map = {
                "VERY_HIGH": 0.95,
                "HIGH": 0.85,
                "MEDIUM": 0.7,
                "LOW": 0.5
            }
            confidence = confidence_map.get(confidence_str, 0.7)
            
            # Extract evidence
            evidence = []
            if "lines" in extra:
                evidence = extra["lines"]
            else:
                # Extract code snippet
                lines = extra.get("lines", "")
                if lines:
                    evidence = [lines]
            
            finding = NormalizedFinding(
                id=f"semgrep-{Path(path).stem}-{start_line}",
                algorithm=algorithm,
                family=family,
                parameters={},  # Could extract from match
                purpose=purpose,
                location={
                    "artifact": "scan-target",
                    "file": path,
                    "line_start": start_line,
                    "line_end": end_line
                },
                source="semgrep_scanner",
                evidence=evidence,
                confidence=confidence,
                timestamp=datetime.utcnow()
            )
            findings.append(finding)
        
        return findings
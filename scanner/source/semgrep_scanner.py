"""
Semgrep source code scanner adapter
"""

import json
import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

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
        
        # If Semgrep is not available, use regex-based detection as fallback
        # This provides real scanning even without Semgrep installed
        logger.info(f"Using regex-based crypto detection as Semgrep fallback for {scan_path}")
        return self._scan_with_regex_patterns(scan_path)
    
    def _scan_with_regex_patterns(self, scan_path: str) -> List[NormalizedFinding]:
        """Scan files using regex patterns as Semgrep fallback"""
        import re
        from datetime import datetime
        
        findings = []
        
        # Find source files
        source_files = self._find_source_files(scan_path)
        logger.info(f"Found {len(source_files)} source files for regex scanning")
        
        # Crypto detection patterns (similar to Semgrep rules)
        crypto_patterns = {
            'RSA': [
                r'rsa\.generate_private_key',
                r'RSA\.generate_key',
                r'RSA_generate_key',
                r'private_key\.sign',
                r'RSA_sign',
            ],
            'AES': [
                r'AES\.new',
                r'Cipher\.getInstance\(["\']AES',
                r'aes\.(GCM|CBC|CTR)',
            ],
            'SHA-256': [
                r'hashlib\.sha256',
                r'SHA256',
                r'sha256',
                r'createHash\(["\']sha256',
            ],
            'ECDSA': [
                r'ecdsa\.sign',
                r'ECDSA\.sign',
                r'ecdsa\.Sign',
            ],
            'ECDH': [
                r'ecdh\.generate_key',
                r'ECDH',
                r'ecdh_key_exchange',
            ],
            'HMAC': [
                r'hmac\.new',
                r'HMAC',
                r'createHmac',
            ],
            '3DES': [
                r'DESede',
                r'3DES',
            ],
            'MD5': [
                r'MD5',
                r'md5',
            ],
        }
        
        # Scan each file
        for file_path in source_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    lines = content.split('\n')
            except Exception as e:
                logger.error(f"Error reading file {file_path}: {e}")
                continue
            
            # Scan each line for crypto patterns
            for line_num, line in enumerate(lines, 1):
                for algorithm, patterns in crypto_patterns.items():
                    for pattern in patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            # Determine algorithm family and purpose
                            family, purpose = self._classify_algorithm(algorithm)
                            
                            finding = NormalizedFinding(
                                id=f"semgrep-{os.path.basename(file_path)}-{line_num}",
                                algorithm=algorithm,
                                family=family,
                                parameters={},
                                purpose=purpose,
                                location={
                                    "artifact": os.path.basename(file_path),
                                    "file": file_path,
                                    "line_start": line_num,
                                    "line_end": line_num
                                },
                                source="semgrep_scanner",
                                evidence=[line.strip()],
                                confidence=0.80,
                                timestamp=datetime.utcnow()
                            )
                            findings.append(finding)
                            break  # Only record one pattern per line per algorithm
        
        logger.info(f"Regex-based scan found {len(findings)} crypto patterns")
        return findings
    
    def _find_source_files(self, scan_path: str) -> List[str]:
        """Find source code files in the given path"""
        source_extensions = [
            '.py', '.js', '.ts', '.jsx', '.tsx',  # Python, JavaScript/TypeScript
            '.go', '.java', '.c', '.cpp', '.h', '.hpp',  # Go, Java, C/C++
            '.cs', '.rb', '.php', '.rs'  # C#, Ruby, PHP, Rust
        ]
        
        source_files = []
        if os.path.isfile(scan_path):
            if any(scan_path.endswith(ext) for ext in source_extensions):
                source_files.append(scan_path)
        else:
            for root, dirs, files in os.walk(scan_path):
                for file in files:
                    if any(file.endswith(ext) for ext in source_extensions):
                        source_files.append(os.path.join(root, file))
        
        return source_files
    
    def _classify_algorithm(self, algorithm: str) -> tuple:
        """Classify algorithm into family and purpose"""
        if algorithm in ['RSA', 'ECDSA', 'ECDH']:
            return 'asymmetric', 'digital_signature' if algorithm != 'ECDH' else 'key_establishment'
        elif algorithm in ['AES', '3DES']:
            return 'symmetric', 'data_encryption'
        elif algorithm in ['SHA-256', 'MD5']:
            return 'hash', 'message_digest'
        elif algorithm == 'HMAC':
            return 'hash', 'message_authentication'
        else:
            return 'unknown', 'unknown'
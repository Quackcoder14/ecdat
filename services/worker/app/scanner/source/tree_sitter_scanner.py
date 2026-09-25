"""
Tree-sitter source code scanner adapter
"""

import json
import subprocess
import tempfile
import os
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

from ..core.base_scanner import SourceScanner, NormalizedFinding

logger = logging.getLogger(__name__)


class TreeSitterScanner(SourceScanner):
    """Tree-sitter AST-based source code scanner"""
    
    def __init__(self):
        super().__init__("tree_sitter_scanner")
        self._check_tree_sitter_available()
    
    def _check_tree_sitter_available(self) -> bool:
        """Check if tree-sitter is available"""
        try:
            # Check if tree-sitter CLI is available
            result = subprocess.run(["tree-sitter", "--version"], capture_output=True, timeout=10)
            self.available = result.returncode == 0
            if self.available:
                logger.info("Tree-sitter is available")
            else:
                logger.warning("Tree-sitter not available")
        except Exception as e:
            logger.warning(f"Tree-sitter check failed: {e}")
            self.available = False
        return self.available
    
    def _check_availability(self) -> bool:
        return self.available
    
    def scan(self, target: Any) -> List[NormalizedFinding]:
        """Scan target with Tree-sitter"""
        if not self.available:
            logger.warning("Tree-sitter not available, skipping scan")
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
        
        # Run tree-sitter parsing with crypto queries
        # This would use tree-sitter CLI or Python bindings
        # For now, return empty - would be implemented with actual tree-sitter
        logger.info(f"Tree-sitter scan would run on {scan_path}")
        
        # Placeholder - actual implementation would:
        # 1. Parse files with tree-sitter
        # 2. Run crypto-specific queries
        # 3. Extract findings with exact locations
        # 4. Return NormalizedFinding objects
        
        return findings
    
    def _get_crypto_queries(self) -> Dict:
        """Get tree-sitter crypto queries for different languages"""
        return {
            "python": """
                (call
                  function: (attribute
                    object: (identifier) @module
                    attribute: (identifier) @func)
                  (#match? @module "rsa|ecdsa|ecdh|cryptography|hashlib|secrets")
                  (#match? @func "generate|sign|verify|encrypt|decrypt|derive|hash"))
            """,
            "javascript": """
                (call_expression
                  function: (member_expression
                    object: (identifier) @obj
                    property: (identifier) @method)
                  (#match? @obj "crypto|forge|node-forge|elliptic|node-rsa|ecdsa-sig-formatter")
                  (#match? @method "generate|sign|verify|encrypt|decrypt|derive|createHash|createHmac|pbkdf2"))
            """,
            "java": """
                (method_invocation
                  name: (identifier) @method
                  object: (field_access
                    field: (identifier) @field)
                  (#match? @field "Cipher|KeyGenerator|KeyPairGenerator|MessageDigest|Mac|Signature|KeyAgreement|KeyFactory"))
            """,
            "go": """
                (call_expression
                  function: (selector_expression
                    operand: (selector_expression
                      operand: (identifier) @pkg
                      field: (field_identifier) @type)
                    field: (field_identifier) @method)
                  (#match? @pkg "crypto|golang.org/x/crypto")
                  (#match? @method "GenerateKey|Sign|Verify|Encrypt|Decrypt|DeriveKey|Hash"))
            """,
            "c": """
                (call_expression
                  function: (identifier) @func
                  (#match? @func "RSA_|EVP_|ECDSA_|ECDH_|AES_|DES_|SHA256|SHA384|SHA512|MD5|SHA1|HMAC_|PBKDF2_|BN_|SSL_|TLS_|X509_|OPENSSL_|BIO_|RSA_|ECDSA_|ECDH_|AES_|DES_|HMAC_|PBKDF2_|BN_"))
            """,
            "cpp": """
                (call_expression
                  function: (field_expression
                    argument: (identifier) @ns
                    field: (field_identifier) @func)
                  (#match? @ns "CryptoPP|Botan|OpenSSL|mbedtls|wolfSSL|nettle|gnutls")
                  (#match? @func "Generate|Sign|Verify|Encrypt|Decrypt|Derive|Hash"))
            """,
            "rust": """
                (call_expression
                  function: (scoped_identifier
                    path: (path
                      segment: (ident) @crate
                      segment: (ident) @module)
                    path: (path
                      segment: (ident) @func))
                  (#match? @crate "ring|rustls|openssl|pqcrypto|p256|ecdsa|rsa|aes|sha2|hmac|pbkdf2"))
            """
        }
    
    def scan(self, target: Any) -> List[NormalizedFinding]:
        """Scan target with Tree-sitter"""
        if not self.available:
            logger.warning("Tree-sitter not available, skipping scan")
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
        
        # For now, return empty - actual implementation would:
        # 1. Walk scan_path for source files
        # 2. Parse each file with tree-sitter
        # 3. Run crypto queries
        # 4. Return NormalizedFinding objects
        
        logger.info(f"Tree-sitter scan would run on {scan_path}")
        
        # Placeholder - actual implementation would:
        # 1. Walk scan_path for source files
        # 2. Parse each file with tree-sitter
        # 4. Run crypto queries
        # 5. Extract findings with exact locations
        # 5. Return NormalizedFinding objects
        
        return findings
    
    def _parse_tree_sitter_results(self, data: Dict, scan_path: str) -> List[NormalizedFinding]:
        """Parse Tree-sitter query results into normalized findings"""
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
            
            confidence_map = {
                "VERY_HIGH": 0.95,
                "HIGH": 0.85,
                "MEDIUM": 0.7,
                "LOW": 0.5
            }
            confidence = confidence_map.get(confidence_str, 0.7)
            
            evidence = []
            if "lines" in extra:
                evidence = extra["lines"]
            else:
                lines = extra.get("lines", "")
                if lines:
                    evidence = [lines]
            
            finding = NormalizedFinding(
                id=f"treesitter-{Path(path).stem}-{start_line}",
                algorithm=algorithm,
                family=family,
                parameters={},
                purpose=purpose,
                location={
                    "artifact": "scan-target",
                    "file": path,
                    "line_start": start_line,
                    "line_end": end_line
                },
                source="tree_sitter_scanner",
                evidence=evidence,
                confidence=confidence,
                timestamp=datetime.utcnow()
            )
            findings.append(finding)
        
        return findings
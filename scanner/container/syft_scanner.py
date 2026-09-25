"""
Syft container scanner adapter (for container images)
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


class ContainerSyftScanner:
    """Syft container image scanner adapter"""
    
    def __init__(self):
        self.name = "container_syft_scanner"
        self.available = self._check_syft_available()
    
    def _check_syft_available(self) -> bool:
        """Check if syft is available"""
        try:
            result = subprocess.run(["syft", "version"], capture_output=True, timeout=10)
            self.available = result.returncode == 0
            if self.available:
                logger.info("Syft container scanner is available")
            else:
                logger.warning("Syft container scanner not available")
        except Exception as e:
            logger.warning(f"Syft container scanner check failed: {e}")
            self.available = False
        return self.available
    
    def _check_availability(self) -> bool:
        return self.available
    
    def scan(self, target: Any) -> List[NormalizedFinding]:
        """Scan target container with Syft"""
        if not self.available:
            logger.warning("Syft container scanner not available, skipping scan")
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
        
        # Run Syft with JSON output on container image/archive
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            output_file = f.name
        
        try:
            # Scan container image archive
            cmd = [
                "syft",
                scan_path,
                "-o", f"json={output_file}",
                "-q"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode != 0:
                logger.error(f"Syft container scan failed: {result.stderr}")
                return []
            
            # Parse SBOM output
            if os.path.exists(output_file):
                with open(output_file, 'r') as f:
                    sbom = json.load(f)
                
                findings = self._parse_syft_sbom(sbom, "container")
                return findings
            
        except subprocess.TimeoutExpired:
            logger.error("Syft container scan timed out")
        except Exception as e:
            logger.error(f"Syft container scan failed: {e}")
        finally:
            if os.path.exists(output_file):
                os.unlink(output_file)
        
        return []
    
    def _parse_syft_sbom(self, sbom: Dict, scan_type: str = "container") -> List[NormalizedFinding]:
        """Parse Syft SBOM output into normalized findings"""
        findings = []
        
        artifacts = sbom.get("artifacts", [])
        
        for artifact in artifacts:
            name = artifact.get("name", "")
            version = artifact.get("version", "")
            artifact_type = artifact.get("type", "")
            
            # Look for crypto-related packages
            crypto_keywords = [
                "crypto", "cryptography", "openssl", "bouncycastle",
                "rsa", "ecdsa", "ecdh", "elliptic", "ecies",
                "aes", "des", "3des", "rc4", "blowfish", "twofish",
                "sha", "md5", "hmac", "pbkdf2", "bcrypt", "scrypt",
                "tls", "ssl", "x509", "certificate", "pki",
                "jwt", "jose", "jwa", "jwk", "jws", "jwe"
            ]
            
            is_crypto = any(kw in name.lower() for kw in crypto_keywords)
            
            if is_crypto:
                algorithm = self._classify_algorithm(name, version)
                family = self._classify_family(name)
                purpose = self._determine_purpose(name)
                
                finding = NormalizedFinding(
                    id=f"syft-container-{name}-{version}",
                    algorithm=algorithm,
                    family=family,
                    parameters={"version": version, "type": artifact_type, "scan_type": scan_type},
                    purpose=purpose,
                    location={
                        "artifact": "container-image",
                        "package": f"{name}@{version}"
                    },
                    source="container_syft_scanner",
                    evidence=[f"Package: {name}@{version}", f"Type: {artifact_type}", f"Scan type: {scan_type}"],
                    confidence=0.85,
                    timestamp=datetime.utcnow()
                )
                findings.append(finding)
        
        return findings
    
    def _classify_algorithm(self, name: str, version: str) -> str:
        """Classify the algorithm based on package name"""
        name_lower = name.lower()
        
        if "rsa" in name_lower:
            return "RSA"
        elif "ecdsa" in name_lower or "elliptic" in name_lower:
            return "ECDSA"
        elif "ecdh" in name_lower:
            return "ECDH"
        elif "aes" in name_lower:
            return "AES"
        elif "des" in name_lower or "3des" in name_lower:
            return "3DES"
        elif "chacha" in name_lower:
            return "ChaCha20-Poly1305"
        elif "sha256" in name_lower or "sha-256" in name_lower:
            return "SHA-256"
        elif "sha384" in name_lower:
            return "SHA-384"
        elif "sha512" in name_lower:
            return "SHA-512"
        elif "sha1" in name_lower:
            return "SHA-1"
        elif "md5" in name_lower:
            return "MD5"
        elif "hmac" in name_lower:
            return "HMAC"
        elif "pbkdf2" in name_lower or "bcrypt" in name_lower or "scrypt" in name_lower:
            return "PBKDF2"
        elif "rsa" in name_lower:
            return "RSA"
        elif "ecdsa" in name_lower:
            return "ECDSA"
        elif "ecdh" in name_lower:
            return "ECDH"
        elif "tls" in name_lower or "ssl" in name_lower:
            return "TLS"
        elif "x509" in name_lower or "certificate" in name_lower:
            return "X.509"
        elif "jwt" in name_lower or "jose" in name_lower:
            return "JWT"
        else:
            return name
    
    def _classify_family(self, name: str) -> str:
        """Classify the crypto family"""
        name_lower = name.lower()
        
        if any(kw in name_lower for kw in ["rsa", "ecdsa", "ecdh", "elliptic", "dsa", "diffie"]):
            return "asymmetric"
        elif any(kw in name_lower for kw in ["aes", "des", "3des", "chacha", "blowfish", "twofish", "rc4"]):
            return "symmetric"
        elif any(kw in name_lower for kw in ["sha", "md5", "hmac", "pbkdf2", "bcrypt", "scrypt"]):
            return "hash"
        elif any(kw in name_lower for kw in ["tls", "ssl", "x509", "certificate", "pki"]):
            return "protocol"
        elif any(kw in name_lower for kw in ["jwt", "jose", "jwa", "jwk", "jws", "jwe"]):
            return "protocol"
        else:
            return "library"
    
    def _determine_purpose(self, name: str) -> str:
        """Determine the cryptographic purpose"""
        name_lower = name.lower()
        
        if any(kw in name_lower for kw in ["sign", "signature", "ecdsa", "dsa"]):
            return "digital_signature"
        elif any(kw in name_lower for kw in ["encrypt", "aes", "des", "chacha", "cipher"]):
            return "data_encryption"
        elif any(kw in name_lower for kw in ["ecdh", "diffie", "key_exchange", "key_agreement"]):
            return "key_establishment"
        elif any(kw in name_lower for kw in ["rsa", "key_gen", "keygen"]):
            return "key_generation"
        elif any(kw in name_lower for kw in ["hash", "sha", "md5", "digest"]):
            return "hashing"
        elif any(kw in name_lower for kw in ["hmac", "mac"]):
            return "message_authentication"
        elif any(kw in name_lower for kw in ["pbkdf2", "bcrypt", "scrypt", "derive"]):
            return "key_derivation"
        elif any(kw in name_lower for kw in ["tls", "ssl", "certificate", "x509"]):
            return "transport_security"
        else:
            return "cryptographic_library"
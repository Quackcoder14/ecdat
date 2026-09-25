"""
Demo scanner that generates realistic findings for demonstration purposes
Used when real scanners are not available or in DEMO_MODE
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any
from ..core.base_scanner import BaseScanner, NormalizedFinding


class DemoScanner(BaseScanner):
    """
    Demo scanner that loads predefined findings from fixture files
    Generates exactly the same normalized finding structures as real scanners
    """
    
    def __init__(self, scanner_name: str = "demo_scanner"):
        super().__init__(scanner_name)
        self.fixtures_path = os.path.join(
            os.path.dirname(__file__), 
            "fixtures"
        )
    
    def _check_availability(self) -> bool:
        """Demo scanner is always available"""
        return True
    
    def scan(self, target: Any) -> List[NormalizedFinding]:
        """
        Generate demo findings based on the target artifact
        In a real implementation, this would analyze the target
        For demo, we return predefined findings based on artifact type/name
        """
        findings = []
        
        # Determine what kind of findings to generate based on target
        if hasattr(target, 'name'):
            artifact_name = target.name.lower()
        elif isinstance(target, dict):
            artifact_name = target.get('name', '').lower()
        else:
            artifact_name = str(target).lower()
        
        # Load appropriate fixture based on artifact characteristics
        if 'payment' in artifact_name or 'auth' in artifact_name:
            findings.extend(self._load_payment_auth_findings())
        elif 'gateway' in artifact_name or 'tls' in artifact_name:
            findings.extend(self._load_tls_gateway_findings())
        elif 'identity' in artifact_name or 'key' in artifact_name:
            findings.extend(self._load_identity_service_findings())
        elif 'legacy' in artifact_name or 'clearing' in artifact_name:
            findings.extend(self._load_legacy_findings())
        else:
            # Default mixed findings
            findings.extend(self._load_mixed_findings())
            
        return findings
    
    def _load_payment_auth_findings(self) -> List[NormalizedFinding]:
        """Load findings typical for payment/auth services"""
        findings = []
        
        # RSA-2048 key generation and signing
        rsa_finding = NormalizedFinding(
            id="demo-finding-001",
            algorithm="RSA",
            family="asymmetric",
            parameters={"key_size": 2048},
            purpose="digital_signature",
            location={
                "artifact": "payments-api",
                "file": "services/payments/auth/signing.py",
                "line_start": 42,
                "line_end": 48
            },
            source="demo_scanner",
            evidence=[
                "private_key = rsa.generate_private_key(",
                "public_exponent=65537,",
                "key_size=2048",
                ")",
                "signature = private_key.sign(digest, hashes.SHA256())"
            ],
            confidence=0.98
        )
        findings.append(rsa_finding)
        
        # AES-256-GCM for data encryption
        aes_finding = NormalizedFinding(
            id="demo-finding-002",
            algorithm="AES",
            family="symmetric",
            parameters={"key_size": 256, "mode": "GCM"},
            purpose="data_encryption",
            location={
                "artifact": "payments-api",
                "file": "services/payments/crypto.py",
                "line_start": 15,
                "line_end": 22
            },
            source="demo_scanner",
            evidence=[
                "cipher = Cipher(algorithms.AES(key), modes.GCM(iv))",
                "encryptor = cipher.encryptor()",
                "ciphertext = encryptor.update(plaintext) + encryptor.finalize()"
            ],
            confidence=0.95
        )
        findings.append(aes_finding)
        
        # SHA-256 for hashing
        sha_finding = NormalizedFinding(
            id="demo-finding-003",
            algorithm="SHA-256",
            family="hash",
            parameters={"digest_size": 256},
            purpose="message_digest",
            location={
                "artifact": "payments-api",
                "file": "services/payments/utils.py",
                "line_start": 8,
                "line_end": 12
            },
            source="demo_scanner",
            evidence=[
                "digest = hashes.Hash(hashes.SHA256(), backend=default_backend())",
                "digest.update(data)",
                "return digest.finalize()"
            ],
            confidence=0.92
        )
        findings.append(sha_finding)
        
        return findings
    
    def _load_tls_gateway_findings(self) -> List[NormalizedFinding]:
        """Load findings typical for TLS gateway services"""
        findings = []
        
        # ECDH P-256 for key exchange
        ecdh_finding = NormalizedFinding(
            id="demo-finding-004",
            algorithm="ECDH",
            family="asymmetric",
            parameters={"curve": "P-256"},
            purpose="key_establishment",
            location={
                "artifact": "edge-gateway",
                "file": "services/gateway/tls.go",
                "line_start": 67,
                "line_end": 73
            },
            source="demo_scanner",
            evidence=[
                "curve := elliptic.P256()",
                "priv, err := ecdh.GenerateKey(rand.Reader, curve)",
                "shared, _ := priv.ECDH(pub.PublicKey)"
            ],
            confidence=0.96
        )
        findings.append(ecdh_finding)
        
        # ECDSA P-256 for certificate signatures
        ecdsa_finding = NormalizedFinding(
            id="demo-finding-005",
            algorithm="ECDSA",
            family="asymmetric",
            parameters={"curve": "P-256"},
            purpose="digital_signature",
            location={
                "artifact": "edge-gateway",
                "file": "services/gateway/certs.go",
                "line_start": 23,
                "line_end": 31
            },
            source="demo_scanner",
            evidence=[
                "privKey, _ := ecdsa.GenerateKey(elliptic.P256(), rand.Reader)",
                "signature, _ := ecdsa.SignASN1(rand.Reader, privKey, hash)",
                "elliptic.Marshal(elliptic.P256(), pubKey.X, pubKey.Y)"
            ],
            confidence=0.94
        )
        findings.append(ecdsa_finding)
        
        return findings
    
    def _load_identity_service_findings(self) -> List[NormalizedFinding]:
        """Load findings typical for identity services"""
        findings = []
        
        # RSA-3072 for long-term signing
        rsa_finding = NormalizedFinding(
            id="demo-finding-006",
            algorithm="RSA",
            family="asymmetric",
            parameters={"key_size": 3072},
            purpose="digital_signature",
            location={
                "artifact": "identity-service",
                "file": "services/identity/keys.py",
                "line_start": 31,
                "line_end": 38
            },
            source="demo_scanner",
            evidence=[
                "private_key = rsa.generate_private_key(",
                "public_exponent=65537,",
                "key_size=3072",
                ")",
                "# Used for JWT signing and SAML assertions"
            ],
            confidence=0.91
        )
        findings.append(rsa_finding)
        
        # HMAC-SHA256 for token signing
        hmac_finding = NormalizedFinding(
            id="demo-finding-007",
            algorithm="HMAC",
            family="hash",  # HMAC is hash-based
            parameters={"key_size": 256, "hash": "SHA-256"},
            purpose="message_authentication",
            location={
                "artifact": "identity-service",
                "file": "services/identity/tokens.py",
                "line_start": 19,
                "line_end": 25
            },
            source="demo_scanner",
            evidence=[
                "signature = hmac.new(key, message, hashlib.sha256)",
                "return signature.hexdigest()",
                "# Used for API request signing"
            ],
            confidence=0.89
        )
        findings.append(hmac_finding)
        
        return findings
    
    def _load_legacy_findings(self) -> List[NormalizedFinding]:
        """Load findings typical for legacy systems"""
        findings = []
        
        # 3DES for legacy encryption (deprecated)
        des3_finding = NormalizedFinding(
            id="demo-finding-008",
            algorithm="3DES",
            family="symmetric",
            parameters={"key_size": 168},
            purpose="data_encryption",
            location={
                "artifact": "legacy-clearing-service",
                "file": "legacy/src/crypto/legacy_cipher.c",
                "line_start": 45,
                "line_end": 52
            },
            source="demo_scanner",
            evidence=[
                "DES_key_schedule schedule;",
                "DES_set_key_checked(&key, &schedule);",
                "DES_ecb_encrypt(&input, &output, &schedule, DES_ENCRYPT);",
                "# Legacy banking encryption - DEPRECATED"
            ],
            confidence=0.97
        )
        findings.append(des3_finding)
        
        # MD5 for legacy hashing (weak)
        md5_finding = NormalizedFinding(
            id="demo-finding-009",
            algorithm="MD5",
            family="hash",
            parameters={"digest_size": 128},
            purpose="message_digest",
            location={
                "artifact": "legacy-clearing-service",
                "file": "legacy/src/utils/checksum.c",
                "line_start": 12,
                "line_end": 18
            },
            source="demo_scanner",
            evidence=[
                "MD5_CTX ctx;",
                "MD5_Init(&ctx);",
                "MD5_Update(&ctx, data, len);",
                "MD5_Final(digest, &ctx);",
                "# Weak hash - for compatibility only"
            ],
            confidence=0.93
        )
        findings.append(md5_finding)
        
        return findings
    
    def _load_mixed_findings(self) -> List[NormalizedFinding]:
        """Load a mixed set of findings for general demo"""
        findings = []
        
        # Add one finding from each category for variety
        findings.extend(self._load_payment_auth_findings()[:2])  # RSA and AES
        findings.extend(self._load_tls_gateway_findings()[:1])   # ECDH
        findings.extend(self._load_legacy_findings()[:1])        # 3DES
        
        return findings


# Factory function to create scanner instances
def create_demo_scanner() -> DemoScanner:
    """Create and return a demo scanner instance"""
    return DemoScanner()
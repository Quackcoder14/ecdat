"""
Syft dependency/SBOM scanner adapter
"""

import json
import subprocess
import tempfile
import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..core.base_scanner import DependencyScanner, NormalizedFinding
from ..core.scanner_factory import get_scanner_registry

logger = logging.getLogger(__name__)


class SyftScanner(DependencyScanner):
    """Syft SBOM/dependency scanner adapter"""
    
    def __init__(self):
        super().__init__("syft_scanner")
        self._check_syft_available()
    
    def _check_syft_available(self) -> bool:
        """Check if syft is available"""
        try:
            result = subprocess.run(["syft", "version"], capture_output=True, timeout=10)
            self.available = result.returncode == 0
            if self.available:
                logger.info("Syft is available")
            else:
                logger.warning("Syft not available")
        except Exception as e:
            logger.warning(f"Syft check failed: {e}")
            self.available = False
        return self.available
    
    def _check_availability(self) -> bool:
        return self.available
    
    def scan(self, target: Any) -> List[NormalizedFinding]:
        """Scan target with Syft"""
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
        
        # Try to use Syft if available
        if self.available:
            try:
                findings = self._scan_with_syft(scan_path)
                if findings:
                    logger.info(f"Syft scan found {len(findings)} crypto dependencies")
                    return findings
            except Exception as e:
                logger.warning(f"Syft scan failed, falling back to dependency file analysis: {e}")
        
        # Fallback to dependency file analysis
        logger.info(f"Using dependency file analysis for {scan_path}")
        return self._scan_dependency_files(scan_path)
    
    def _scan_with_syft(self, scan_path: str) -> List[NormalizedFinding]:
        """Scan using Syft CLI"""
        import tempfile
        
        # Run Syft with JSON output
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            output_file = f.name
        
        try:
            cmd = [
                "syft",
                scan_path,
                "-o", f"json={output_file}",
                "-q"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode != 0:
                logger.error(f"Syft failed: {result.stderr}")
                return []
            
            # Parse SBOM output
            if os.path.exists(output_file):
                with open(output_file, 'r') as f:
                    sbom = json.load(f)
                
                findings = self._parse_syft_sbom(sbom)
                return findings
            
        except subprocess.TimeoutExpired:
            logger.error("Syft scan timed out")
        except Exception as e:
            logger.error(f"Syft scan failed: {e}")
        finally:
            if os.path.exists(output_file):
                os.unlink(output_file)
        
        return []
    
    def _scan_dependency_files(self, scan_path: str) -> List[NormalizedFinding]:
        """Scan dependency files (requirements.txt, package.json, etc.)"""
        from datetime import datetime
        
        findings = []
        
        # Find dependency files
        dependency_files = self._find_dependency_files(scan_path)
        logger.info(f"Found {len(dependency_files)} dependency files")
        
        for dep_file in dependency_files:
            try:
                file_findings = self._parse_dependency_file(dep_file)
                findings.extend(file_findings)
            except Exception as e:
                logger.error(f"Error parsing dependency file {dep_file}: {e}")
        
        return findings
    
    def _find_dependency_files(self, scan_path: str) -> List[str]:
        """Find dependency files in the given path"""
        dependency_files = []
        
        # Common dependency file patterns
        dep_patterns = [
            'requirements.txt',
            'package.json',
            'package-lock.json',
            'yarn.lock',
            'Pipfile',
            'Pipfile.lock',
            'poetry.lock',
            'pyproject.toml',
            'go.mod',
            'go.sum',
            'pom.xml',
            'build.gradle',
            'Gemfile',
            'Gemfile.lock',
            'Cargo.toml',
            'Cargo.lock'
        ]
        
        if os.path.isfile(scan_path):
            if os.path.basename(scan_path) in dep_patterns:
                dependency_files.append(scan_path)
        else:
            for root, dirs, files in os.walk(scan_path):
                for file in files:
                    if file in dep_patterns:
                        dependency_files.append(os.path.join(root, file))
        
        return dependency_files
    
    def _parse_dependency_file(self, file_path: str) -> List[NormalizedFinding]:
        """Parse a dependency file and extract crypto-related packages"""
        from datetime import datetime
        
        findings = []
        filename = os.path.basename(file_path)
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return findings
        
        # Crypto-related package keywords
        crypto_keywords = [
            "crypto", "cryptography", "openssl", "bouncycastle",
            "rsa", "ecdsa", "elliptic", "ecdh", "ecies",
            "aes", "des", "3des", "rc4", "blowfish", "twofish",
            "sha", "md5", "hmac", "pbkdf2", "bcrypt", "scrypt",
            "tls", "ssl", "x509", "certificate", "pki",
            "jwt", "jose", "jwa", "jwk", "jws", "jwe"
        ]
        
        # Parse based on file type
        if filename == 'requirements.txt':
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Extract package name (before version specifiers)
                    pkg_name = line.split('==')[0].split('>=')[0].split('<=')[0].split('~=')[0].split('!=')[0].strip()
                    if any(kw in pkg_name.lower() for kw in crypto_keywords):
                        findings.append(self._create_dependency_finding(pkg_name, line, file_path))
        
        elif filename == 'package.json':
            try:
                import json
                pkg_data = json.loads(content)
                dependencies = pkg_data.get('dependencies', {})
                dev_dependencies = pkg_data.get('devDependencies', {})
                
                for pkg_name, version in {**dependencies, **dev_dependencies}.items():
                    if any(kw in pkg_name.lower() for kw in crypto_keywords):
                        findings.append(self._create_dependency_finding(pkg_name, version, file_path))
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON in {file_path}")
        
        elif filename == 'go.mod':
            lines = content.split('\n')
            for line in lines:
                if line.strip().startswith('require '):
                    parts = line.split()
                    if len(parts) >= 2:
                        pkg_name = parts[1]
                        if any(kw in pkg_name.lower() for kw in crypto_keywords):
                            findings.append(self._create_dependency_finding(pkg_name, parts[2] if len(parts) > 2 else "latest", file_path))
        
        return findings
    
    def _create_dependency_finding(self, pkg_name: str, version: str, file_path: str) -> NormalizedFinding:
        """Create a finding from a dependency"""
        from datetime import datetime
        
        algorithm = self._classify_algorithm(pkg_name, version)
        family = self._classify_family(pkg_name)
        purpose = self._determine_purpose(pkg_name)
        
        return NormalizedFinding(
            id=f"syft-{pkg_name}-{version}",
            algorithm=algorithm,
            family=family,
            parameters={"version": version, "type": "dependency"},
            purpose=purpose,
            location={
                "artifact": "dependencies",
                "file": file_path,
                "package": f"{pkg_name}@{version}"
            },
            source="syft_scanner",
            evidence=[f"Package: {pkg_name}@{version}", f"File: {os.path.basename(file_path)}"],
            confidence=0.75,
            timestamp=datetime.utcnow()
        )
    
    def _parse_syft_sbom(self, sbom: Dict) -> List[NormalizedFinding]:
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
                "rsa", "ecdsa", "elliptic", "ecdh", "ecies",
                "aes", "des", "3des", "rc4", "blowfish", "twofish",
                "sha", "md5", "hmac", "pbkdf2", "bcrypt", "scrypt",
                "tls", "ssl", "x509", "certificate", "pki",
                "jwt", "jose", "jwa", "jwk", "jws", "jwe"
            ]
            
            is_crypto = any(kw in name.lower() for kw in crypto_keywords)
            
            if is_crypto:
                # Determine algorithm family
                algorithm = self._classify_algorithm(name, version)
                family = self._classify_family(name)
                purpose = self._determine_purpose(name)
                
                finding = NormalizedFinding(
                    id=f"syft-{name}-{version}",
                    algorithm=algorithm,
                    family=family,
                    parameters={"version": version, "type": artifact_type},
                    purpose=purpose,
                    location={
                        "artifact": "dependencies",
                        "package": f"{name}@{version}"
                    },
                    source="syft_scanner",
                    evidence=[f"Package: {name}@{version}", f"Type: {artifact_type}"],
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
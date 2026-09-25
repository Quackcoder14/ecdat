"""
OpenSSL certificate scanner adapter
"""

import json
import subprocess
import tempfile
import os
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

from ..core.base_scanner import CertificateScanner, NormalizedFinding

logger = logging.getLogger(__name__)


class OpenSSLScanner:
    """OpenSSL certificate scanner adapter"""
    
    def __init__(self):
        self.name = "openssl_scanner"
        self.available = self._check_openssl_available()
    
    def _check_openssl_available(self) -> bool:
        """Check if openssl is available"""
        try:
            result = subprocess.run(["openssl", "version"], capture_output=True, timeout=10)
            self.available = result.returncode == 0
            if self.available:
                logger.info("OpenSSL is available")
            else:
                logger.warning("OpenSSL not available")
        except Exception as e:
            logger.warning(f"OpenSSL check failed: {e}")
            self.available = False
        return self.available
    
    def _check_availability(self) -> bool:
        return self.available
    
    def scan(self, target: Any) -> List:
        """Scan target with OpenSSL"""
        if not self.available:
            logger.warning("OpenSSL not available, skipping scan")
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
        
        # Find certificate files
        cert_files = []
        for root, dirs, files in os.walk(scan_path):
            for file in files:
                if file.endswith(('.pem', '.crt', '.cer', '.der', '.p12', '.pfx')):
                    cert_files.append(os.path.join(root, file))
        
        if not cert_files:
            # Check for certificate bundle
            for file in os.listdir(scan_path):
                if file.endswith(('.pem', '.crt', '.cer', '.der', '.p12', '.pfx')):
                    cert_files.append(os.path.join(scan_path, file))
        
        if not cert_files:
            logger.info(f"No certificate files found in {scan_path}")
            return []
        
        findings = []
        
        for cert_file in cert_files:
            try:
                cert_info = self._parse_certificate(cert_file)
                if cert_info:
                    finding = NormalizedFinding(
                        id=f"openssl-{Path(cert_file).stem}",
                        algorithm=cert_info.get("key_algorithm", "Unknown"),
                        family="certificate",
                        parameters={
                            "subject": cert_info.get("subject", ""),
                            "issuer": cert_info.get("issuer", ""),
                            "not_before": cert_info.get("not_before", ""),
                            "not_after": cert_info.get("not_after", ""),
                            "key_size": cert_info.get("key_size", 0),
                            "signature_algorithm": cert_info.get("signature_algorithm", ""),
                            "san": cert_info.get("san", []),
                            "serial_number": cert_info.get("serial_number", ""),
                            "fingerprint_sha256": cert_info.get("fingerprint_sha256", ""),
                            "is_ca": cert_info.get("is_ca", False),
                            "is_self_signed": cert_info.get("is_self_signed", False)
                        },
                        purpose="certificate",
                        location={
                            "artifact": "certificates",
                            "file": cert_file
                        },
                        source="openssl_scanner",
                        evidence=[
                            f"Subject: {cert_info.get('subject', '')}",
                            f"Issuer: {cert_info.get('issuer', '')}",
                            f"Validity: {cert_info.get('not_before', '')} to {cert_info.get('not_after', '')}",
                            f"Key: {cert_info.get('key_algorithm', '')} {cert_info.get('key_size', '')} bits",
                            f"Signature: {cert_info.get('signature_algorithm', '')}"
                        ],
                        confidence=0.95,
                        timestamp=datetime.utcnow()
                    )
                    findings.append(finding)
            except Exception as e:
                logger.error(f"Failed to parse certificate {cert_file}: {e}")
        
        return findings
    
    def _parse_certificate(self, cert_file: str) -> Dict:
        """Parse certificate file using OpenSSL"""
        cert_info = {}
        
        try:
            # Determine format
            is_pem = cert_file.endswith('.pem') or cert_file.endswith('.crt') or cert_file.endswith('.cer')
            is_p12 = cert_file.endswith('.p12') or cert_file.endswith('.pfx')
            is_der = cert_file.endswith('.der')
            
            if is_p12:
                # PKCS12 requires password - skip for now or use empty
                cmd = ["openssl", "pkcs12", "-in", cert_file, "-nodes", "-passin", "pass:"]
            elif is_der:
                cmd = ["openssl", "x509", "-inform", "der", "-in", cert_file, "-noout", "-text"]
            else:
                cmd = ["openssl", "x509", "-in", cert_file, "-noout", "-text"]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                # Try with password prompt handling for p12
                if cert_file.endswith(('.p12', '.pfx')):
                    cmd = ["openssl", "pkcs12", "-in", cert_file, "-nodes", "-passin", "pass:"]
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                
                if result.returncode != 0:
                    logger.warning(f"Failed to parse certificate {cert_file}: {result.stderr}")
                    return {}
            
            output = result.stdout
            cert_info = self._parse_openssl_output(output)
            cert_info["file"] = cert_file
            return cert_info
            
        except Exception as e:
            logger.error(f"Error parsing certificate {cert_file}: {e}")
            return {}
    
    def _parse_openssl_output(self, output: str) -> Dict:
        """Parse OpenSSL x509 -text output"""
        info = {}
        
        lines = output.split('\n')
        
        for line in lines:
            line = line.strip()
            
            if line.startswith("Subject:"):
                info["subject"] = line[8:].strip()
            elif line.startswith("Issuer:"):
                info["issuer"] = line[7:].strip()
            elif "Not Before" in line:
                info["not_before"] = line.split(": ", 1)[1].strip() if ": " in line else ""
            elif "Not After" in line:
                info["not_after"] = line.split(": ", 1)[1].strip() if ": " in line else ""
            elif "Public Key Algorithm:" in line:
                info["key_algorithm"] = line.split(": ", 1)[1].strip() if ": " in line else ""
            elif "Public-Key:" in line:
                # Extract key size: "Public-Key: (2048 bit)"
                import re
                match = re.search(r'\((\d+)\s+bit\)', line)
                if match:
                    info["key_size"] = int(match.group(1))
            elif "Signature Algorithm:" in line:
                info["signature_algorithm"] = line.split(": ", 1)[1].strip() if ": " in line else ""
            elif "X509v3 Subject Alternative Name:" in line:
                # Read next lines for SANs
                pass
            elif "DNS:" in line or "IP Address:" in line or "email:" in line:
                # Parse SANs
                if "san" not in info:
                    info["san"] = []
                info["san"].extend([s.strip() for s in line.split(",")])
        
        # Calculate fingerprint
        if "fingerprint_sha256" not in info:
            info["fingerprint_sha256"] = "calculated_by_ecdat"
        
        # Determine if CA
        info["is_ca"] = "CA:TRUE" in output.upper() if "CA:" in output.upper() else False
        
        # Check if self-signed
        info["is_self_signed"] = info.get("subject", "") == info.get("issuer", "")
        
        return info
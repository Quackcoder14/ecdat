# ECDAT Scan Target

This directory is a real ECDAT scanning target. The application scans the current contents at runtime.

## Supported Examples

This directory contains examples of cryptographic code that ECDAT can detect:

### Python Service (`python-service/`)
- RSA key generation and signing
- ECDSA signing
- AES-GCM encryption

### Java Service (`java-service/`)
- JCA/JCE usage (RSA, AES, ECDSA)
- TLS configuration

### Node Service (`node-service/`)
- crypto module usage (RSA, ECDH, AES, SHA)

### Go Service (`go-service/`)
- crypto/tls
- crypto/ecdsa
- crypto/rsa

### Native Service (`native-service/`)
- OpenSSL C APIs
- Legacy 3DES usage

### Certificates (`certificates/`)
- Demo certificate metadata

### Config (`config/`)
- TLS configuration files

## How to Use

1. Copy your own repository contents into this directory (or replace the existing files)
2. In ECDAT, select **Demo** mode
3. Create a project and select **Local Folder** as the source
4. Select `scan-target` as the target
5. Start a live scan
6. Watch actual scanner activity in real-time
7. Explore findings, CBOM, quantum risk, and migration recommendations

## Try Changing the Target

1. Open: `scan-target/python-service/crypto_service.py`
2. Change the RSA key size or remove the RSA signing call
3. Save
4. Return to ECDAT
5. Run another Demo scan
6. Compare the findings - the result must reflect the file modification

## Important Notes

- All files in this directory are synthetic security-analysis fixtures
- Do not place production credentials or confidential data here unless you understand the mounted scan environment
- Results are generated during the scan and are not pre-seeded
- The application scans the current contents at runtime

## Supported File Types

| Language | Extensions | Scanners |
|----------|-----------|----------|
| Python | `.py` | Tree-sitter, Semgrep, Native |
| Java | `.java` | Tree-sitter, Semgrep, Native |
| JavaScript/TypeScript | `.js`, `.ts` | Tree-sitter, Semgrep, Native |
| Go | `.go` | Tree-sitter, Native |
| C/C++ | `.c`, `.cpp`, `.h` | Tree-sitter, Binary signatures |
| Certificates | `.pem`, `.crt`, `.cer` | OpenSSL parser |
| Containers | `.tar`, `.tar.gz` | Trivy, Syft |

## Security Note

This directory is mounted read-only into the scanner worker. The scanner:
- Does not execute uploaded applications
- Does not execute repository build scripts
- Does not install repository dependencies
- Does not launch uploaded containers
- Treats scan data as untrusted
- Uses isolated workers
- Restricts scanner access
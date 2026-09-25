# ECDAT Live Scanning Documentation

**How Real Scanning Works in Demo Mode**

---

## Table of Contents

1. [Overview](#overview)
2. [Supported Input Types](#supported-input-types)
3. [Scanner Adapters](#scanner-adapters)
4. [Security Isolation](#security-isolation)
5. [SSE Event Stream](#sse-event-stream)
6. [Finding Persistence](#finding-persistence)
7. [CBOM Generation](#cbom-generation)
8. [Risk Generation](#risk-generation)
9. [What Happens When Tools Are Unavailable](#what-happens-when-tools-are-unavailable)
10. [Live Scan Demonstration Guide](#live-scan-demonstration-guide)

---

## Overview

In **Demo mode**, ECDAT performs **real, live scanning** of user-supplied artifacts at scan time. There are no pre-computed results, no hidden fixture loading, and no mock data substitution.

**The Promise**: When you select Demo mode, provide a scan target, and start a scan — ECDAT actually executes scanner processes against the current contents of your target at that moment.

---

## Supported Input Types

| Input Type | Description | Implementation |
|------------|-------------|----------------|
| **Local Folder** | Mounted read-only directory | `./scan-target:/scan-input:ro` |
| **Git Repository** | Clone URL + optional branch/ref | `git clone` into isolated temp dir |
| **ZIP/TAR Archive** | Uploaded archive | Extracted to isolated temp dir |
| **Container Image** | OCI tar / Docker archive | Trivy/Syft image archive scanning |
| **Certificate Bundle** | PEM/DER bundles | OpenSSL parsing |
| **Binary** | Native executables | Strings, symbols, signature matching |

### Local Folder (Primary Demo Path)

```
User provides: ./scan-target/
                ↓
Docker mounts: ./scan-target:/scan-input:ro
                ↓
Worker sees:   /scan-input (read-only)
                ↓
Scanners scan: /scan-input contents
```

---

## Scanner Adapters

### Adapter Pattern

Every external scanner has a dedicated adapter implementing:

```python
class ScannerAdapter:
    async def scan(self, target_path: str) -> List[NormalizedFinding]:
        ...
    
    async def health_check(self) -> bool:
        ...
    
    def parse_output(self, raw_output: str) -> List[NormalizedFinding]:
        ...
```

### Implemented Adapters

| Adapter | Tool | Command | Output Format |
|---------|------|---------|---------------|
| **SemgrepAdapter** | `semgrep scan --json` | `semgrep scan --config=rules.yaml --json` | JSON |
| **SyftAdapter** | `syft` | `syft dir:/path -o json=output.json` | JSON (SBOM) |
| **TrivyAdapter** | `trivy fs` | `trivy fs --format json --output file.json` | JSON |
| **OpenSSLAdapter** | `openssl x509` | `openssl x509 -in cert.pem -text` | Parsed text |
| **NativeSourceScanner** | Tree-sitter + custom rules | In-process | In-memory |
| **NativeBinaryScanner** | `strings`, `nm`/`objdump` | In-process | In-memory |

### NormalizedFinding — Common Interface

All adapters emit:

```python
@dataclass
class NormalizedFinding:
    id: str
    algorithm: str
    family: str              # asymmetric, symmetric, hash, protocol, certificate, library
    parameters: Dict
    purpose: str             # digital_signature, key_establishment, data_encryption, etc.
    location: Dict           # file, line_start, line_end, artifact
    source: str              # scanner type
    evidence: List[str]      # code snippets
    confidence: float        # 0.0 - 1.0
    timestamp: datetime
    quantum_status: str      # VULNERABLE, NOT_PRIMARY_TARGET, CONDITIONAL, UNKNOWN
```

---

## Security Isolation

### Worker Container Isolation

```dockerfile
# Worker Dockerfile
FROM python:3.11-slim
# No docker.sock mount
# No host filesystem access
# Read-only /scan-input mount
# CPU/Memory limits
# No network (offline preferred)
# Non-root user
```

### Mount Configuration

```yaml
# docker-compose.yml
worker:
  volumes:
    - ./scan-target:/scan-input:ro  # Read-only!
    - artifacts:/app/artifacts
```

### Scan Target Validation

```python
SCAN_INPUT_ROOT = "/scan-input"

def validate_target(path: str) -> str:
    """Resolve and validate path is within SCAN_INPUT_ROOT"""
    resolved = Path(path).resolve()
    root = Path(SCAN_INPUT_ROOT).resolve()
    
    if not resolved.is_relative_to(root):
        raise ValueError("Path traversal attempt detected")
    
    return str(resolved)
```

### Security Guarantees

| Protection | Implementation |
|---|---|
| No arbitrary host paths | API only accepts pre-registered scan inputs |
| No shell injection | `subprocess.run([cmd, arg1, arg2], shell=False)` |
| Path traversal prevention | Path resolution within `SCAN_INPUT_ROOT` |
| Archive extraction limits | Max size, max files, expansion ratio |
| Binary execution | NEVER — static analysis only |
| Network isolation | Offline by default; optional vuln DB only |
| Resource limits | CPU, memory, timeout per scanner |

---

## SSE Event Stream

### Connection

```
GET /api/scans/{scan_id}/events
Accept: text/event-stream
```

### Event Format

```
event: FINDING_DISCOVERED
data: {"type": "FINDING_DISCOVERED", "scan_id": "...", "stage": "SOURCE_ANALYSIS", "scanner": "native-source-scanner", "timestamp": "2025-01-15T14:03:12Z", "progress": 37, "finding": {...}}

event: STAGE_COMPLETED
data: {"type": "STAGE_COMPLETED", "scan_id": "...", "stage": "SOURCE_ANALYSIS", "duration_ms": 1250, "findings_count": 12, "timestamp": "..."}

event: SCAN_COMPLETED
data: {"type": "SCAN_COMPLETED", "scan_id": "...", "duration_ms": 18500, "total_findings": 47, "timestamp": "..."}
```

### Frontend Consumption (React)

```typescript
const eventSource = new EventSource(`/api/scans/${scanId}/events`);

eventSource.addEventListener('FINDING_DISCOVERED', (event) => {
  const data = JSON.parse(event.data);
  setFindings(prev => [...prev, data.finding]);
  setProgress(data.progress);
});

eventSource.addEventListener('STAGE_COMPLETED', (event) => {
  const data = JSON.parse(event.data);
  setCurrentStage(data.stage);
});

eventSource.onerror = () => {
  // Auto-reconnect with Last-Event-ID
  eventSource.close();
  reconnect();
};
```

### Reconnection Logic

```typescript
function reconnect() {
  const lastEventId = getLastEventId();
  const url = `/api/scans/${scanId}/events${lastEventId ? `?last_event_id=${lastEventId}` : ''}`;
  const es = new EventSource(url);
  // ... same handlers
}
```

---

## Finding Persistence

### Immediate Persistence

```
Scanner discovers finding
         │
         ▼
NormalizedFinding created
         │
         ▼
DB INSERT (immediate)
         │
         ▼
Redis PUBLISH scan:{scan_id}
         │
         ▼
SSE → Frontend (batched)
         │
         ▼
UI: Finding appears instantly
```

### Database Schema

```sql
-- findings table
CREATE TABLE findings (
    id UUID PRIMARY KEY,
    project_id UUID REFERENCES projects(id),
    scan_id UUID REFERENCES scans(id),
    data_mode data_mode_enum NOT NULL,
    
    algorithm VARCHAR(100) NOT NULL,
    family crypto_family_enum NOT NULL,
    parameters JSONB,
    purpose VARCHAR(200) NOT NULL,
    
    artifact_name VARCHAR(500),
    file_path VARCHAR(1000),
    line_start INT,
    line_end INT,
    
    evidence JSONB,
    confidence REAL NOT NULL,
    confidence_level confidence_enum NOT NULL,
    quantum_status quantum_status_enum NOT NULL,
    source_scanner VARCHAR(100) NOT NULL,
    
    discovered_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for mode-aware queries
CREATE INDEX ix_findings_data_mode ON findings(data_mode);
CREATE INDEX ix_findings_scan_id ON findings(scan_id);
CREATE INDEX ix_findings_project_id ON findings(project_id);
```

### Finding Provenance

Every finding in Demo mode:
```json
{
  "scan_id": "uuid",
  "scanner": "native-source-scanner",
  "scanner_version": "1.0.0",
  "artifact_id": "uuid",
  "timestamp": "2025-01-15T14:03:12Z",
  "location": {
    "file": "crypto_service.py",
    "line_start": 42,
    "line_end": 48
  },
  "evidence": [
    "private_key = rsa.generate_private_key(...)",
    "key_size=2048"
  ],
  "confidence": 0.98,
  "rule_id": "crypto-rsa-keygen"
}
```

---

## CBOM Generation

### Pipeline

```
Live Findings (from THIS scan)
         │
         ▼
Normalization & Deduplication
         │
         ▼
Correlation (app ↔ library ↔ algorithm)
         │
         ▼
CBOM Builder (CycloneDX 1.7)
         │
         ▼
CBOM Document (JSONB)
         │
         ▼
Storage + Export
```

### CBOM Document Metadata

```json
{
  "bomFormat": "CycloneDX",
  "specVersion": "1.7",
  "metadata": {
    "timestamp": "2025-01-15T14:03:20Z",
    "tools": [{
      "vendor": "ECDAT",
      "name": "ECDAT Scanner",
      "version": "1.0.0"
    }],
    "source_scan_id": "scan-uuid",
    "knowledge_base_version": "1.0",
    "scanner_provenance": ["native-source-scanner", "syft-scanner"]
  }
}
```

### Component Structure

```json
{
  "components": [
    {
      "type": "application",
      "name": "RSA",
      "version": "2048",
      "description": "RSA used for digital_signature",
      "properties": [
        {"name": "ecdat:algorithm_family", "value": "asymmetric"},
        {"name": "ecdat:purpose", "value": "digital_signature"},
        {"name": "ecdat:quantum_status", "value": "VULNERABLE"},
        {"name": "ecdat:confidence", "value": "0.98"},
        {"name": "ecdat:source_scanner", "value": "native-source-scanner"},
        {"name": "ecdat:evidence", "value": "private_key = rsa.generate_private_key(key_size=2048)"},
        {"name": "ecdat:file_path", "value": "crypto_service.py:42-48"}
      ]
    }
  ]
}
```

---

## Risk Generation

### Deterministic Pipeline

```
Live Finding (from THIS scan)
         │
         ▼
Crypto Knowledge Base Lookup
         │
         ▼
Context Extraction (purpose, criticality, lifetime)
         │
         ▼
Deterministic Risk Rules
         │
         ▼
Risk Assessment
         │
         ▼
Storage + Event
```

### Risk Rules (Configurable)

```yaml
# knowledge/rules/risk_rules.yaml
risk_factors:
  quantum_vulnerable:
    weight: 0.30
    description: "Algorithm vulnerable to quantum attacks via Shor's algorithm"
    
  asymmetric_algorithm:
    weight: 0.20
    description: "Asymmetric cryptography requires complex migration"
    
  long_data_lifetime:
    weight: 0.25
    description: "Data must remain secure for extended period"
    
  high_business_criticality:
    weight: 0.15
    description: "Asset belongs to critical application"
    
  complex_migration:
    weight: 0.10
    description: "Migration requires significant protocol changes"

risk_levels:
  CRITICAL:   {min_score: 80}
  HIGH:       {min_score: 60, max_score: 79}
  MEDIUM:     {min_score: 40, max_score: 59}
  LOW:        {min_score: 20, max_score: 39}
  INFORMATIONAL: {min_score: 0, max_score: 19}
```

### Mosca Planning

```python
# Configurable defaults
mosca_defaults:
  default_data_security_lifetime_years: 10
  default_migration_lead_time_years: 3
  default_threat_horizon_years: 10
  
# Planning logic
if (data_security_lifetime + migration_lead_time) > threat_horizon:
    status = "Within migration concern window"
else:
    status = "No immediate concern"
```

---

## What Happens When Tools Are Unavailable

### Graceful Degradation

| Scanner | Unavailable Behavior |
|---------|---------------------|
| Semgrep | Marked UNAVAILABLE; native source scanner runs |
| Syft | Marked UNAVAILABLE; native dependency scanner runs |
| Trivy | Marked UNAVAILABLE; container scanning skipped |
| OpenSSL | Marked UNAVAILABLE; native cert parser runs |
| Native scanners | Always available (built-in) |

### Scanner Capability Panel

```
┌─────────────────────────────────────────────────────┐
│ Scanner Capabilities                                │
├─────────────────────────────────────────────────────┤
│ Semgrep        │ Available     v1.85.0  ✓         │
│ Syft           │ Available     v0.86.0  ✓         │
│ Trivy          │ Unavailable                   ✗   │
│ OpenSSL        │ Available     v3.0.12  ✓         │
└─────────────────────────────────────────────────────┘
```

### Scan Provenance Records Missing Capability

```json
{
  "scan_id": "uuid",
  "scanner_runs": [
    {"scanner": "native-source-scanner", "status": "COMPLETED", "duration_ms": 1250, "findings": 12},
    {"scanner": "semgrep_scanner", "status": "UNAVAILABLE", "duration_ms": 0, "findings": 0},
    {"scanner": "syft_scanner", "status": "COMPLETED", "duration_ms": 2100, "findings": 8},
    {"scanner": "trivy_scanner", "status": "UNAVAILABLE", "duration_ms": 0, "findings": 0}
  ]
}
```

**UI Transparency**: "Semgrep unavailable — using native source scanner instead"

---

## Live Scan Demonstration Guide

### 5-Minute Demo Script

#### Prerequisites
```bash
# 1. Start ECDAT
docker compose up --build

# 2. Seed demo data
docker compose exec api python -m scripts.seed

# 3. Open http://localhost:3000
# Login: admin@ecdat.demo / demo123
```

### Demo Steps (5 Minutes)

| Step | Action | Expected |
|------|--------|----------|
| 1 | Open http://localhost:3000 | Login page |
| 2 | Login: `admin@ecdat.demo` / `demo123` | Dashboard loads |
| 3 | Click **DEMO** in header | Mode shows "DEMO · Live data" |
| 4 | Click **Projects** → **+ New project** | Create "Live Test" |
| 5 | Open "Live Test" → **Start Scan** | Scan creation dialog |
| 6 | Source: **Local Folder** → Target: **scan-target** | Target selected |
| 7 | Click **Start scan** | Scan page opens |
| 8 | Watch live events: "Source scanner started", "RSA usage detected", etc. | Real-time updates |
| 9 | Click **Findings** as they appear | Real findings with evidence |
| 10 | Wait for completion → Open **CBOM Explorer** | CycloneDX JSON |
| 11 | Open **Quantum Risk** → See Mosca panel | Risk distribution + planning |
| 12 | Open **PQC Migration** → See recommendations | ML-DSA, ML-KEM candidates |
| 13 | **Modify source**: Edit `scan-target/python-service/crypto_service.py` | Change RSA key size |
| 14 | Run **another scan** | New findings, different CBOM |
| 15 | Switch to **SIMULATION** mode | Seeded data appears separately |

### Target Modification Test (Critical Proof)

```bash
# 1. Initial scan finds RSA-2048
# 2. Edit scan-target/python-service/crypto_service.py
#    Change: key_size=2048 → key_size=4096
#    OR remove rsa.generate_private_key call entirely
# 2. Run second live scan
# 3. Verify:
#    - New scan has different scan_id
#    - Findings reflect change (RSA-4096 or RSA removed)
#    - CBOM regenerated from new findings
#    - Risk/recommendations reflect new scan
```

---

## Configuration

### Environment Variables

```env
# Scan configuration
SCAN_INPUT_ROOT=/scan-input
MAX_ARTIFACT_SIZE=104857600
SCAN_TIMEOUT_SECONDS=300

# Scanner paths (auto-detected if in PATH)
SEMGREP_PATH=semgrep
SYFT_PATH=syft
TRIVY_PATH=trivy
OPENSSL_PATH=openssl

# Limits
MAX_FILE_SIZE=52428800        # 50MB per file
MAX_TOTAL_FILES=10000         # Max files per scan
MAX_ARCHIVE_EXPANSION=1048576000  # 1GB max expansion
MAX_SCAN_DURATION=1800        # 30 minutes max
```

### Stage Weights (Configurable)

```python
STAGE_WEIGHTS = {
    "artifact_discovery": 0.10,
    "source_scanning": 0.25,
    "dependency_scanning": 0.15,
    "certificate_scanning": 0.10,
    "binary_scanning": 0.10,
    "correlation": 0.10,
    "cbom_generation": 0.05,
    "risk_assessment": 0.10,
    "recommendations": 0.05,
}
```

---

## Troubleshooting

### Common Issues

| Symptom | Cause | Fix |
|---|---|---|
| "Scanner unavailable" | Binary not in PATH | Install tool; check `which semgrep` |
| "Permission denied" | Mount not read-only | Verify `:ro` in docker-compose |
| "Path not found" | Wrong mount path | Check `./scan-target:/scan-input:ro` |
| "Scan timeout" | Large target | Increase `SCAN_TIMEOUT_SECONDS` |
| "No findings" | Target has no crypto | Add crypto code to target |

### Debug Commands

```bash
# Check scanner availability
curl http://localhost:8000/api/system/scanners

# View scan events
curl http://localhost:8000/api/scans/{scan_id}/events

# Worker logs
docker compose logs worker

# API logs
docker compose logs api

# Check scan-target mount
docker compose exec worker ls -la /scan-input
```

---

## Limitations & Scope

### Current Capabilities

| Area | Status |
|---|---|
| Source code (Python, JS/TS, Java, Go, C/C++, Rust) | ✅ Tree-sitter + Semgrep + Native |
| Dependencies (Python, JS, Java, Go, Rust, C/C++) | ✅ Syft |
| Container images (tar archives) | ✅ Trivy + Syft |
| Certificates (PEM, DER, PKCS12) | ✅ OpenSSL |
| Binaries (ELF, PE, Mach-O) | ✅ Strings + Symbols |
| Git repositories | ✅ Clone + scan |
| Archives (ZIP, TAR, TGZ) | ✅ Extract + scan |

### Not Yet Implemented

| Feature | Status |
|---|---|
| GitHub/GitLab API discovery | Planned |
| Cloud provider (AWS/Azure/GCP) | Not planned |
| Runtime/endpoint scanning | Not planned |
| Hardware security modules | Not planned |

---

## Quick Reference: Scanner Capabilities

| Scanner | Input | Output | Speed | External Dependency |
|---------|-------|--------|-------|---------------------|
| Native Source | Source code | NormalizedFindings | Fast | None |
| Semgrep | Source code | NormalizedFindings | Medium | semgrep binary |
| Syft | Source/Deps/Container | NormalizedFindings + SBOM | Medium | syft binary |
| Trivy | Container/FS | Vulns + Secrets + Config | Slow | trivy binary |
| OpenSSL | Certificates | NormalizedFindings | Fast | openssl binary |
| Native Binary | Binaries | NormalizedFindings | Fast | strings, nm, objdump |

---

*Last Updated: 2025-01-15*  
*ECDAT Live Scanning Documentation v1.0*
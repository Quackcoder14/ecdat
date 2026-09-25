# ECDAT User Guide

**Cryptographic Discovery & Quantum Readiness Platform**

---

## Table of Contents

1. [What is ECDAT?](#what-is-ecdat)
2. [Two Modes: Simulation vs Demo](#two-modes-simulation-vs-demo)
3. [Getting Started](#getting-started)
4. [Mode Switching](#mode-switching)
5. [Creating a Project](#creating-a-project)
6. [Preparing a Scan Target](#preparing-a-scan-target)
7. [Running a Live Scan](#running-a-live-scan)
8. [Understanding Results](#understanding-results)
6. [CBOM Explorer](#cbom-explorer)
7. [Quantum Risk Assessment](#quantum-risk-assessment)
8. [PQC Migration Planning](#pqc-migration-planning)
9. [AI Assistant](#ai-assistant)
10. [Reports & Exports](#reports--exports)
11. [Settings](#settings)
12. [Troubleshooting](#troubleshooting)

---

## What is ECDAT?

ECDAT (Enterprise Cryptographic Discovery & Quantum Readiness Platform) is an enterprise-grade platform for discovering, assessing, and planning migration of cryptographic assets across heterogeneous enterprise artifacts.

**Core Capabilities:**
- **Cryptographic Discovery**: Multi-scanner framework (source code, dependencies, containers, certificates, binaries)
- **CBOM Generation**: CycloneDX 1.7 compatible Cryptography Bill of Materials
- **Quantum Risk Assessment**: Mosca-style planning horizon analysis
- **PQC Migration Planning**: NIST-standardized algorithm recommendations (ML-KEM, ML-DSA, SLH-DSA)
- **AI Assistant**: Explains findings with evidence citations (not LLM-generated risk scores)

---

## Two Modes: Simulation vs Demo

ECDAT operates in two distinct modes:

### SIMULATION — "Seeded Data"
- **Purpose**: Explore ECDAT using a controlled demonstration dataset
- **Data Source**: Pre-seeded deterministic findings
- **Use Case**: Learning the UI, testing features, demonstrations
- **Badge**: `SIMULATION` / "Seeded data"

### DEMO — "Live Scan of Supplied Data"
- **Purpose**: Real assessment of YOUR cryptographic assets
- **Data Source**: YOUR repositories, folders, certificates, binaries
- **Use Case**: Actual cryptographic assessment, compliance, migration planning
- **Badge**: `DEMO` / "Live data"
- **Key Principle**: **Never uses seeded findings** — only analyzes what you supply

---

## Getting Started

### Prerequisites
- Docker & Docker Compose
- Git

### Quick Start

```bash
# Clone and navigate
cd ecdat

# Start all services
docker compose up --build

# Wait for services to be healthy, then seed demo data
docker compose exec api python -m scripts.seed
```

### Access Points
- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Demo Credentials
- **Email**: admin@ecdat.demo
- **Password**: demo123

---

## Mode Switching

### The Mode Switcher
Located in the top header bar:
```
ECDAT  [ SIMULATION ▾ ]    [Search]  [Bell]  [User]
```

### Mode Labels
| Mode | Label | Badge | Tooltip |
|------|-------|-------|---------|
| Simulation | SIMULATION | "Seeded data" | "Explore ECDAT using deterministic seeded demonstration data." |
| Demo | DEMO | "Live data" | "Analyze only repositories and artefacts supplied to ECDAT. No seeded findings are used." |

### Switching Behavior
- **Immediate**: Click to switch, data refreshes instantly
- **Persistent**: Mode preference saved in localStorage
- **Active Scan Protection**: If a live scan is running, a confirmation appears:
  > "An active live scan is running. Switching modes will change the displayed dataset; the scan will continue in the background."
  > [Continue] [Cancel]

---

## Creating a Project

1. Navigate to **Projects**
2. Click **+ New project**
3. Fill in:
   - **Name**: e.g., "Payment Services"
   - **Description**: Optional description
4. Click **Create**

### Project Data Mode
- **Simulation Mode**: New projects default to `SIMULATION` (seeded data)
- **Demo Mode**: New projects automatically use `DEMO` (your real data)

---

## Preparing a Scan Target

### Supported Source Types
| Type | Description | Example |
|------|-------------|---------|
| **Local Folder** | Mounted read-only scan workspace | `scan-target/` |
| **Git Repository** | Clone URL + optional branch | `https://github.com/org/repo.git` |
| **ZIP/TAR Archive** | Upload compressed source | `source.tar.gz` |
| **Container Image** | Docker/OCI archive | `image.tar` |
| **Certificate Bundle** | PEM/DER certificates | `certs.pem` |
| **Binary** | Native executables | `app.exe` |

### The scan-target Directory
A real scan target is provided at:
```
scan-target/
├── README.md
├── python-service/
│   ├── requirements.txt
│   └── crypto_service.py
├── java-service/
│   ├── pom.xml
│   └── src/
├── node-service/
│   ├── package.json
│   └── src/
├── go-service/
│   ├── go.mod
│   └── main.go
├── native-service/
│   └── legacy_crypto.c
├── certificates/
│   └── demo-certificate.pem
├── config/
│   └── tls.conf
└── Dockerfile
```

### Using Your Own Code
1. Replace contents of `scan-target/` with your repository
2. Or mount your own directory: `-v /path/to/your/code:/scan-input:ro`

---

## Running a Live Scan

### Step-by-Step

1. **Select Demo Mode** (top header)
2. **Open Projects** → Click **+ New project** → Name it "Live Test"
3. **Open Project** → Click **Start Scan**
4. **Source**: Select **Local Folder**
5. **Target**: Select **scan-target**
6. **Configuration**: Review defaults (all scanners enabled)
4. **Confirm**: Review scan settings → **Start Live Scan**

### Scan Confirmation Dialog
Before starting:
> "Live scan"
> "Results will be generated from the current contents of the selected source."
> "Pre-seeded findings are not used in Demo mode."
> [Cancel] [Start scan]

---

## Understanding Results

### Live Scan Progress
During scan, watch real-time progress:

```
14:03:11  Source scanner started
14:03:12  Parsed python-service/crypto_service.py
14:03:12  RSA usage detected — Confidence: Very High
14:03:13  Parsed go-service/tls.go
14:03:13  ECDH usage detected — Confidence: High
14:03:14  Certificate metadata extracted
14:03:16  CBOM correlation started
14:03:18  Risk assessment started
14:03:19  Recommendations generated
14:03:20  Scan completed
```

### Live Findings Panel
As findings arrive:
- Real-time count updates
- Subtle entrance animation
- Batched updates (100-250ms) for performance

### Finding Details
Click any finding to see:
- **Algorithm**: RSA, ECDSA, ECDH, AES, etc.
- **Family**: Asymmetric, Symmetric, Hash, Protocol, Certificate
- **Parameters**: Key size, curve, mode, etc.
- **Usage**: Digital signature, key establishment, encryption, etc.
- **Quantum Status**: VULNERABLE / NOT_PRIMARY_TARGET / CONDITIONAL
- **Confidence**: Very High / High / Medium / Low
- **Evidence**: Code snippets with line numbers
- **Scanner**: Which scanner found it
- **Location**: File path and line numbers

---

## CBOM Explorer

### Viewing the CBOM
Navigate to **CBOM Explorer** to see:
- **Filter Bar**: Algorithm, Quantum Status, Purpose, Confidence
- **Inventory Table**: All cryptographic assets with metadata
- **Export**: JSON (CycloneDX 1.7) or CSV

### CBOM Detail
Click any asset to see:
- Algorithm details
- Usage context
- Evidence snippets
- Risk assessment
- Migration recommendation
- "How ECDAT identified this" explanation

---

## Quantum Risk Assessment

### Risk Dashboard
Navigate to **Quantum Risk** for:
- **Risk Distribution**: Critical / High / Medium / Low / Informational
- **Mosca Planning Panel**: X (data lifetime) + Y (migration time) vs Z (threat horizon)
- **Risk Asset Table**: Detailed breakdown with Mosca status

### Mosca-Style Planning
```
Data Security Lifetime (X):    10 years
Migration Lead Time (Y):        3.2 years
Threat Horizon Assumption (Z): 10 years
─────────────────────────────────────────
X + Y = 13.2 years > Z = 10 years
→ WITHIN MIGRATION CONCERN WINDOW
```

### Risk Drivers
Each high-risk asset shows:
- Quantum-vulnerable asymmetric algorithm
- Critical business application
- Long data lifetime
- Migration lead time exceeds planning buffer

---

## PQC Migration Planning

### Migration Table
| Current Crypto | Usage | Candidate | Complexity | Priority |
|---|---|---|---|---|
| RSA-2048 | Digital Signature | ML-DSA-65 | Medium | High |
| ECDH P-256 | Key Establishment | ML-KEM-768 | High | High |
| ECDSA P-256 | Authentication | ML-DSA-65 | Medium | High |
| AES-256-GCM | Encryption | Retain | Low | Low |
| SHA-256 | Hashing | Retain | Low | Low |
| 3DES | Legacy Encryption | AES-256-GCM | Medium | Medium |

### Hybrid Migration
For all asymmetric algorithms, hybrid deployment is recommended:
- RSA-2048 + ML-DSA-65
- ECDH P-256 + ML-KEM-768
- ECDSA P-256 + ML-DSA-65

### Migration Detail
Click any recommendation to see:
- Current state → Target state
- Why this candidate
- Dependencies & compatibility notes
- Performance impact notes
- Suggested migration sequence

---

## AI Assistant

### Accessing the Assistant
Navigate to **AI Assistant** in the sidebar.

### Context Selector
Choose context:
- **Current Project** (default)
- **Current Scan**
- **Selected Finding**
- **Entire CBOM**

### Example Questions
> "Why is RSA-2048 flagged as quantum-vulnerable?"
> "Which assets have the longest migration lead time?"
> "Summarize the high-risk assets in this project."
> "What would a hybrid migration look like for the authentication service?"
> "Explain this CBOM finding."

### Response Format
- **Evidence-based**: Answers cite actual findings
- **Citations**: Visible references to specific findings
- **No Fabrication**: "AI explains ECDAT findings; risk classification and migration mapping are generated by deterministic engines."

### Demo Mode AI
- Uses MockLLMProvider (deterministic responses)
- No external API required
- Context-aware responses based on actual findings

---

## Reports & Exports

### Report Types
| Report | Description | Format |
|---|---|---|
| **Executive Summary** | High-level overview for leadership | Browser / Print |
| **Technical Report** | Detailed technical findings | Browser / Print |
| **CBOM Export** | CycloneDX 1.7 compatible | JSON Download |
| **Findings Export** | All findings with evidence | CSV Download |

### Generating Reports
1. Navigate to **Reports**
2. Select report type
3. Click **Generate** or **Export**

---

## Settings

### Tabs
| Tab | Purpose |
|---|---|
| **General** | App settings, timeouts, storage |
| **Scanners** | Scanner capability panel (Available/Unavailable) |
| **LLM Provider** | Configure LLM (Mock, OpenAI-compatible, Ollama) |
| **Security** | Audit logging, secret redaction, session timeout |

### Scanner Capabilities Panel
Shows real-time status:
| Scanner | Status | Version |
|---|---|---|
| Semgrep | Available / Unavailable | v1.85.0 |
| Syft | Available / Unavailable | v0.86.0 |
| Trivy | Available / Unavailable | v0.48.3 |
| OpenSSL | Available / Unavailable | 3.0.12 |

### LLM Provider Configuration
| Provider | Description |
|---|---|
| Mock (Demo) | Built-in deterministic responses |
| OpenAI Compatible | Any OpenAI-compatible endpoint |
| Ollama | Local LLM via Ollama |

---

## Troubleshooting

### Login Issues
- **401 Unauthorized**: Check credentials (`admin@ecdat.demo` / `demo123`)
- **500 Error**: Check API logs (`docker compose logs api`)

### Scan Failures
| Issue | Resolution |
|---|---|
| Scanner unavailable | Check Settings → Scanners; install missing tools |
| Scan timeout | Increase timeout in Settings → General |
| No findings | Verify target has crypto code; check scanner availability |
| Scan fails | Check worker logs: `docker compose logs worker` |

### No Findings in Demo Mode
- Verify you selected **Demo** mode (not Simulation)
- Ensure you selected a valid scan target
- Check that target contains detectable crypto code

### AI Assistant Not Working
- Check LLM provider in Settings → LLM Provider
- In Demo mode: "AI Assistant is not configured" if no provider set
- Simulation mode uses Mock provider automatically

---

## Key Principles

1. **Evidence First** — Not AI first. Every finding traces to evidence.
2. **Deterministic Engines** — Risk, CBOM, PQC mapping are deterministic.
3. **LLM is Explanatory** — AI only explains, never determines risk.
4. **Real Scanning in Demo** — No precomputed results; live analysis at scan time.
5. **Mode Isolation** — Simulation and Demo data never mix.

---

## Support

- **Documentation**: `docs/USER_GUIDE.md`, `docs/WORKFLOW.md`, `docs/LIVE_SCANNING.md`
- **API Docs**: http://localhost:8000/docs
- **Issues**: Check scanner availability, worker logs, API logs

---

*ECDAT — Cryptographic Discovery & Quantum Readiness Platform*
# ECDAT - Cryptographic Discovery & Quantum Readiness Platform

An enterprise cryptographic discovery, assessment, and quantum-readiness platform.

## Architecture

```
User
  ↓
Next.js (Frontend)
  ↓
FastAPI (Backend API)
  ↓
Celery / Redis (Async Task Queue)
  ↓
Isolated Scanner Worker
  ↓
Knowledge Base
  ↓
Correlation Engine
  ↓
CBOM Generator
  ↓
Risk Engine
  ↓
PQC Recommendations
  ↓
AI Gateway
  ↓
LLM Provider
```

**Key Principle:** The LLM is an explanation layer, NOT the source of truth. Deterministic engines handle all cryptographic discovery, classification, risk scoring, and PQC mapping.

## Features

- **Cryptographic Discovery**: Multi-scanner framework (source code, dependencies, containers, certificates, binaries)
- **CBOM Generation**: CycloneDX 1.7 compatible Cryptography Bill of Materials
- **Quantum Risk Assessment**: Mosca-style planning horizon analysis
- **PQC Migration Planning**: NIST-standardized algorithm recommendations (ML-KEM, ML-DSA, SLH-DSA)
- **AI Assistant**: Explains findings with evidence citations (not LLM-generated risk scores)
- **Scanner Framework**: Plugin architecture with demo mode (no external tools required)

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Git

### Start the Application

```bash
# Clone and navigate
cd ecdat

# Start all services
docker compose up --build

# Wait for services to be healthy, then seed demo data
docker compose exec api python -m scripts.seed
```

### Access the Application

- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Demo Credentials

- **Email**: admin@ecdat.demo
- **Password**: demo123

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection | `postgresql://ecdat:ecdat_secure_password@postgres:5432/ecdat` |
| `REDIS_URL` | Redis connection | `redis://redis:6379` |
| `JWT_SECRET` | JWT signing secret | `super-secret-jwt-key-change-in-production` |
| `LLM_PROVIDER` | LLM provider type | `mock` |
| `LLM_MODEL` | Model name | `demo-model` |
| `DEMO_MODE` | Enable demo mode | `true` |
| `MAX_ARTIFACT_SIZE` | Max upload size (bytes) | `104857600` |
| `SCAN_TIMEOUT_SECONDS` | Scan timeout | `300` |

## Project Structure

```
ecdat/
├── apps/
│   └── web/                 # Next.js frontend
├── services/
│   ├── api/                 # FastAPI backend
│   └── worker/              # Celery worker
├── scanner/
│   ├── core/                # Scanner interfaces
│   ├── source/              # Source code scanners
│   ├── dependency/          # Dependency scanners
│   ├── container/           # Container scanners
│   ├── certificate/         # Certificate scanners
│   ├── binary/              # Binary scanners
│   └── demo/                # Demo scanner
├── knowledge/
│   ├── algorithms/          # Algorithm definitions
│   ├── pqc/                 # PQC algorithm definitions
│   ├── mappings/            # Classical→PQC mappings
│   └── rules/               # Risk rules
├── scripts/
│   └── seed.py              # Demo data seeder
├── docker-compose.yml
└── README.md
```

## Development

### Backend Only

```bash
cd services/api
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your settings
uvicorn main:app --reload
```

### Frontend Only

```bash
cd apps/web
npm install
npm run dev
```

### Run Tests

```bash
# Backend tests
cd services/api
pytest

# Frontend tests
cd apps/web
npm test

# Lint
cd services/api && ruff check .
cd apps/web && npm run lint
```

## Scanner Framework

ECDAT uses a plugin-based scanner architecture:

| Scanner Type | Tools (Production) | Demo Mode |
|--------------|-------------------|-----------|
| Source Code | Tree-sitter, Semgrep | ✅ Mock |
| Dependencies | Syft | ✅ Mock |
| Containers | Trivy, Syft | ✅ Mock |
| Certificates | OpenSSL | ✅ Mock |
| Binaries | strings, YARA | ✅ Mock |

**Demo Mode**: Runs entirely without external tools using realistic fixture data.

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `POST /api/auth/token` | Login |
| `GET /api/projects` | List projects |
| `POST /api/projects` | Create project |
| `GET /api/projects/{id}` | Get project |
| `POST /api/projects/{id}/scans` | Start scan |
| `GET /api/scans/{id}` | Get scan status |
| `GET /api/scans/{id}/events` | Scan progress (SSE) |
| `GET /api/projects/{id}/cbom` | Get CBOM |
| `GET /api/projects/{id}/cbom/export` | Export CBOM JSON |
| `GET /api/projects/{id}/risk` | Risk summary |
| `GET /api/projects/{id}/recommendations` | Migration recommendations |
| `POST /api/assistant/query` | AI assistant query |

## Security

- JWT-based authentication with role-based access control
- Secret redaction in AI context
- Artifact sandboxing (no execution of uploaded files)
- Input validation and sanitization
- Audit logging for all operations

## License

MIT License - see LICENSE file for details.
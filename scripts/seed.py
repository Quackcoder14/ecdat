"""
Seed script for demo data
"""

import uuid
import os
import sys
from datetime import datetime
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from passlib.hash import bcrypt

# Ensure services/api is in Python path
API_DIR = Path(__file__).resolve().parent.parent / "services" / "api"
WORKSPACE_DIR = Path(__file__).resolve().parent.parent
for p in [str(API_DIR), str(WORKSPACE_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from app.models import (
        Base, User, UserRole, Project, ProjectStatus,
        Artifact, ArtifactType, ArtifactStatus,
        Scan, ScanStatus,
        Finding, FindingConfidence, CryptoFamily, QuantumStatus,
        CBOMDocument, CBOMFormat,
        RiskAssessment, RiskLevel,
        MigrationRecommendation, MigrationComplexity, MigrationPriority,
        AuditEvent, AuditAction,
        DataMode,
    )
except ImportError:
    from services.api.app.models import (
        Base, User, UserRole, Project, ProjectStatus,
        Artifact, ArtifactType, ArtifactStatus,
        Scan, ScanStatus,
        Finding, FindingConfidence, CryptoFamily, QuantumStatus,
        CBOMDocument, CBOMFormat,
        RiskAssessment, RiskLevel,
        MigrationRecommendation, MigrationComplexity, MigrationPriority,
        AuditEvent, AuditAction,
        DataMode,
    )

# Database URL - Use SQLite for local development (matching the API)
DATABASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "services", "api", "ecdat.db"))
DATABASE_URL = f"sqlite:///{DATABASE_PATH.replace(os.sep, '/')}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def seed():
    db = SessionLocal()
    try:
        # Create tables
        Base.metadata.create_all(bind=engine)
        
        # Create demo user
        user = db.query(User).filter(User.email == "admin@ecdat.demo").first()
        if not user:
            user = User(
                id=uuid.uuid4(),
                email="admin@ecdat.demo",
                hashed_password=bcrypt.hash("demo123"),
                full_name="Demo Admin",
                role=UserRole.ADMIN,
                is_active=True,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"Created demo user: {user.email}")
        
        # Create demo project (SIMULATION mode)
        project = db.query(Project).filter(Project.name == "Acme Payments Platform").first()
        if not project:
            project = Project(
                id=uuid.uuid4(),
                name="Acme Payments Platform",
                description="Representative payment, identity, and API infrastructure used for ECDAT demonstration.",
                status=ProjectStatus.ACTIVE,
                owner_id=user.id,
                data_mode=DataMode.SIMULATION,
            )
            db.add(project)
            db.commit()
            db.refresh(project)
            print(f"Created project: {project.name}")
        
        # Create interactive demo project (DEMO mode)
        demo_project = db.query(Project).filter(Project.name == "Interactive Demo Project").first()
        if not demo_project:
            demo_project = Project(
                id=uuid.uuid4(),
                name="Interactive Demo Project",
                description="Interactive demo project for real-time scanning with demo scanner.",
                status=ProjectStatus.ACTIVE,
                owner_id=user.id,
                data_mode=DataMode.DEMO,
            )
            db.add(demo_project)
            db.commit()
            db.refresh(demo_project)
            print(f"Created demo project: {demo_project.name}")
        
        # Create demo artifacts
        artifacts_data = [
            {"name": "payments-api", "type": ArtifactType.GIT_REPO, "filename": "payments-api.tar.gz"},
            {"name": "identity-service", "type": ArtifactType.GIT_REPO, "filename": "identity-service.tar.gz"},
            {"name": "edge-gateway", "type": ArtifactType.GIT_REPO, "filename": "edge-gateway.tar.gz"},
            {"name": "legacy-clearing-service", "type": ArtifactType.GIT_REPO, "filename": "legacy-clearing.tar.gz"},
            {"name": "certificate-bundle", "type": ArtifactType.CERTIFICATE_BUNDLE, "filename": "certs.tar.gz"},
            {"name": "container-image", "type": ArtifactType.CONTAINER_IMAGE, "filename": "app.tar"},
        ]
        
        for art_data in artifacts_data:
            artifact = db.query(Artifact).filter(
                Artifact.name == art_data["name"],
                Artifact.project_id == project.id
            ).first()
            if not artifact:
                artifact = Artifact(
                    id=uuid.uuid4(),
                    project_id=project.id,
                    name=art_data["name"],
                    artifact_type=art_data["type"],
                    filename=art_data["filename"],
                    file_path=f"/app/artifacts/{art_data['filename']}",
                    file_size=1024000,
                    sha256_hash=f"sha256:{art_data['name']}",
                    status=ArtifactStatus.COMPLETED,
                    data_mode=DataMode.SIMULATION,
                )
                db.add(artifact)
        
        db.commit()
        print("Created demo artifacts")
        
        # Create demo artifacts for interactive demo project
        demo_artifacts_data = [
            {"name": "demo-payment-service", "type": ArtifactType.DEMO_DATASET, "filename": "demo-payment.json"},
            {"name": "demo-auth-module", "type": ArtifactType.DEMO_DATASET, "filename": "demo-auth.json"},
            {"name": "demo-crypto-lib", "type": ArtifactType.DEMO_DATASET, "filename": "demo-crypto.json"},
        ]
        
        for art_data in demo_artifacts_data:
            artifact = db.query(Artifact).filter(
                Artifact.name == art_data["name"],
                Artifact.project_id == demo_project.id
            ).first()
            if not artifact:
                artifact = Artifact(
                    id=uuid.uuid4(),
                    project_id=demo_project.id,
                    name=art_data["name"],
                    artifact_type=art_data["type"],
                    filename=art_data["filename"],
                    file_path=f"/app/artifacts/{art_data['filename']}",
                    file_size=102400,
                    sha256_hash=f"sha256:{art_data['name']}",
                    status=ArtifactStatus.COMPLETED,
                    data_mode=DataMode.DEMO,
                )
                db.add(artifact)
        
        db.commit()
        print("Created interactive demo artifacts")
        
        # Create demo scan
        scan = db.query(Scan).filter(
            Scan.project_id == project.id,
            Scan.status == ScanStatus.COMPLETED
        ).first()
        if not scan:
            artifact = db.query(Artifact).filter(Artifact.name == "payments-api").first()
            scan = Scan(
                id=uuid.uuid4(),
                project_id=project.id,
                artifact_id=artifact.id,
                scan_type="full",
                config_json='{"depth": "full", "source": true, "dependencies": true, "certificates": true}',
                status=ScanStatus.COMPLETED,
                progress_percentage=100,
                current_stage="COMPLETED",
                initiated_by_id=user.id,
                data_mode=DataMode.SIMULATION,
                started_at=datetime.utcnow(),
                completed_at=datetime.utcnow(),
            )
            db.add(scan)
            db.commit()
            db.refresh(scan)
            print(f"Created demo scan: {scan.id}")
        
        # Create demo findings
        findings_data = [
            {
                "algorithm": "RSA",
                "family": CryptoFamily.ASYMMETRIC,
                "parameters": {"key_size": 2048},
                "purpose": "digital_signature",
                "artifact_name": "payments-api",
                "file_path": "services/payments/auth/signing.py",
                "line_start": 42,
                "line_end": 48,
                "evidence": [
                    "private_key = rsa.generate_private_key(",
                    "public_exponent=65537,",
                    "key_size=2048",
                    ")",
                    "signature = private_key.sign(digest, hashes.SHA256())"
                ],
                "confidence": 0.98,
                "confidence_level": FindingConfidence.VERY_HIGH,
                "quantum_status": QuantumStatus.VULNERABLE,
                "source_scanner": "demo_scanner",
            },
            {
                "algorithm": "ECDH",
                "family": CryptoFamily.ASYMMETRIC,
                "parameters": {"curve": "P-256"},
                "purpose": "key_establishment",
                "artifact_name": "edge-gateway",
                "file_path": "services/gateway/tls.go",
                "line_start": 67,
                "line_end": 73,
                "evidence": [
                    "curve := elliptic.P256()",
                    "priv, err := ecdh.GenerateKey(rand.Reader, curve)",
                    "shared, _ := priv.ECDH(pub.PublicKey)"
                ],
                "confidence": 0.96,
                "confidence_level": FindingConfidence.VERY_HIGH,
                "quantum_status": QuantumStatus.VULNERABLE,
                "source_scanner": "demo_scanner",
            },
            {
                "algorithm": "AES",
                "family": CryptoFamily.SYMMETRIC,
                "parameters": {"key_size": 256, "mode": "GCM"},
                "purpose": "data_encryption",
                "artifact_name": "payments-api",
                "file_path": "services/payments/crypto.py",
                "line_start": 15,
                "line_end": 22,
                "evidence": [
                    "cipher = Cipher(algorithms.AES(key), modes.GCM(iv))",
                    "encryptor = cipher.encryptor()",
                    "ciphertext = encryptor.update(plaintext) + encryptor.finalize()"
                ],
                "confidence": 0.95,
                "confidence_level": FindingConfidence.VERY_HIGH,
                "quantum_status": QuantumStatus.NOT_PRIMARY_TARGET,
                "source_scanner": "demo_scanner",
            },
            {
                "algorithm": "ECDSA",
                "family": CryptoFamily.ASYMMETRIC,
                "parameters": {"curve": "P-256"},
                "purpose": "digital_signature",
                "artifact_name": "edge-gateway",
                "file_path": "services/gateway/certs.go",
                "line_start": 23,
                "line_end": 31,
                "evidence": [
                    "privKey, _ := ecdsa.GenerateKey(elliptic.P256(), rand.Reader)",
                    "signature, _ := ecdsa.SignASN1(rand.Reader, privKey, hash)",
                    "elliptic.Marshal(elliptic.P256(), pubKey.X, pubKey.Y)"
                ],
                "confidence": 0.94,
                "confidence_level": FindingConfidence.VERY_HIGH,
                "quantum_status": QuantumStatus.VULNERABLE,
                "source_scanner": "demo_scanner",
            },
            {
                "algorithm": "3DES",
                "family": CryptoFamily.SYMMETRIC,
                "parameters": {"key_size": 168},
                "purpose": "data_encryption",
                "artifact_name": "legacy-clearing-service",
                "file_path": "legacy/src/crypto/legacy_cipher.c",
                "line_start": 45,
                "line_end": 52,
                "evidence": [
                    "DES_key_schedule schedule;",
                    "DES_set_key_checked(&key, &schedule);",
                    "DES_ecb_encrypt(&input, &output, &schedule, DES_ENCRYPT);",
                    "# Legacy banking encryption - DEPRECATED"
                ],
                "confidence": 0.97,
                "confidence_level": FindingConfidence.VERY_HIGH,
                "quantum_status": QuantumStatus.NOT_PRIMARY_TARGET,
                "source_scanner": "demo_scanner",
            },
        ]
        
        for i, finding_data in enumerate(findings_data):
            finding = db.query(Finding).filter(
                Finding.scan_id == scan.id,
                Finding.algorithm == finding_data["algorithm"],
                Finding.file_path == finding_data["file_path"]
            ).first()
            if not finding:
                finding = Finding(
                    id=uuid.uuid4(),
                    project_id=project.id,
                    scan_id=scan.id,
                    data_mode=DataMode.SIMULATION,
                    **finding_data
                )
                db.add(finding)
        
        db.commit()
        print("Created demo findings")
        
        # Create risk assessments
        findings = db.query(Finding).filter(Finding.scan_id == scan.id).all()
        for finding in findings:
            risk = db.query(RiskAssessment).filter(RiskAssessment.finding_id == finding.id).first()
            if not risk:
                if finding.quantum_status == QuantumStatus.VULNERABLE:
                    risk_level = RiskLevel.HIGH
                    risk_score = 80
                    factors = ["quantum_vulnerable", "asymmetric_algorithm", "high_confidence"]
                    reasons = [
                        "Asymmetric cryptography is vulnerable to quantum algorithms (Shor's algorithm)",
                        "Asymmetric cryptography generally requires more complex migration",
                        "High confidence finding with strong evidence"
                    ]
                elif finding.family == CryptoFamily.SYMMETRIC and "3DES" in finding.algorithm:
                    risk_level = RiskLevel.MEDIUM
                    risk_score = 50
                    factors = ["legacy_algorithm", "deprecated"]
                    reasons = ["Legacy algorithm (3DES) deprecated since 2017", "Small block size vulnerable to SWEET32"]
                else:
                    risk_level = RiskLevel.LOW
                    risk_score = 20
                    factors = ["not_primary_target"]
                    reasons = ["Symmetric/hash algorithms not primary quantum target"]
                
                risk = RiskAssessment(
                    id=uuid.uuid4(),
                    project_id=project.id,
                    finding_id=finding.id,
                    risk_level=risk_level,
                    risk_score=risk_score,
                    risk_factors=factors,
                    risk_reasons=reasons,
                    data_mode=DataMode.SIMULATION,
                    data_security_lifetime_years=10,
                    migration_lead_time_years=3,
                    threat_horizon_years=10,
                    planning_status="Within migration concern window",
                )
                db.add(risk)
        
        db.commit()
        print("Created risk assessments")
        
        # Create migration recommendations
        for finding in findings:
            if finding.quantum_status == QuantumStatus.VULNERABLE:
                rec = db.query(MigrationRecommendation).filter(
                    MigrationRecommendation.finding_id == finding.id
                ).first()
                if not rec:
                    if "ECDH" in finding.algorithm:
                        candidate = "ML-KEM-768"
                        complexity = MigrationComplexity.HIGH
                    elif "ECDSA" in finding.algorithm:
                        candidate = "ML-DSA-65"
                        complexity = MigrationComplexity.MEDIUM
                    else:
                        candidate = "ML-DSA-65"
                        complexity = MigrationComplexity.MEDIUM
                    
                    rec = MigrationRecommendation(
                        id=uuid.uuid4(),
                        project_id=project.id,
                        finding_id=finding.id,
                        current_algorithm=finding.algorithm,
                        current_usage=finding.purpose,
                        current_parameters=finding.parameters,
                        candidate_algorithm=candidate,
                        candidate_type="PQC",
                        rationale=f"{finding.algorithm} is vulnerable to quantum attacks. {candidate} is a NIST-standardized PQC replacement.",
                        migration_complexity=complexity,
                        migration_priority=MigrationPriority.HIGH,
                        affected_components=[finding.artifact_name] if finding.artifact_name else [],
                        compatibility_notes="Requires protocol/library updates for PQC support",
                        performance_notes="PQC algorithms have larger keys/signatures; evaluate performance impact",
                        hybrid_option=f"{finding.algorithm} + {candidate}",
                        confidence=90,
                        data_mode=DataMode.SIMULATION,
                    )
                    db.add(rec)
        
        db.commit()
        print("Created migration recommendations")
        
        # Create CBOM document
        cbom = {
            "bomFormat": "CycloneDX",
            "specVersion": "1.7",
            "version": 1,
            "metadata": {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "tools": [{
                    "vendor": "ECDAT",
                    "name": "ECDAT Scanner",
                    "version": "1.0.0",
                }],
            },
            "components": [],
        }
        
        for finding in findings:
            component = {
                "type": "library" if finding.family == CryptoFamily.LIBRARY else "application",
                "name": finding.algorithm,
                "version": finding.parameters.get("key_size", "1.0") if finding.parameters else "1.0",
                "description": f"{finding.algorithm} used for {finding.purpose}",
                "properties": [
                    {"name": "ecdat:algorithm_family", "value": finding.family.value},
                    {"name": "ecdat:purpose", "value": finding.purpose},
                    {"name": "ecdat:quantum_status", "value": finding.quantum_status.value},
                    {"name": "ecdat:confidence", "value": str(finding.confidence)},
                ],
            }
            cbom["components"].append(component)
        
        cbom_doc = db.query(CBOMDocument).filter(
            CBOMDocument.project_id == project.id,
            CBOMDocument.scan_id == scan.id
        ).first()
        if not cbom_doc:
            cbom_doc = CBOMDocument(
                id=uuid.uuid4(),
                project_id=project.id,
                scan_id=scan.id,
                format=CBOMFormat.CYCLONEDX,
                bom_json=cbom,
                data_mode=DataMode.SIMULATION,
            )
            db.add(cbom_doc)
        
        db.commit()
        print("Created CBOM document")
        
        # Create audit events
        audit_events = [
            AuditEvent(
                id=uuid.uuid4(),
                user_id=user.id,
                project_id=project.id,
                action=AuditAction.PROJECT_CREATED,
                description="Created demo project",
                data_mode=DataMode.SIMULATION,
            ),
            AuditEvent(
                id=uuid.uuid4(),
                user_id=user.id,
                project_id=project.id,
                scan_id=scan.id,
                action=AuditAction.SCAN_STARTED,
                description="Started demo scan",
                data_mode=DataMode.SIMULATION,
            ),
            AuditEvent(
                id=uuid.uuid4(),
                user_id=user.id,
                project_id=project.id,
                scan_id=scan.id,
                action=AuditAction.SCAN_COMPLETED,
                description=f"Scan completed with 5 findings",
                data_mode=DataMode.SIMULATION,
            ),
        ]
        
        for event in audit_events:
            existing = db.query(AuditEvent).filter(
                AuditEvent.project_id == event.project_id,
                AuditEvent.action == event.action
            ).first()
            if not existing:
                db.add(event)
        
        db.commit()
        print("Created audit events")
        
        # Create audit events for demo project
        demo_audit_events = [
            AuditEvent(
                id=uuid.uuid4(),
                user_id=user.id,
                project_id=demo_project.id,
                action=AuditAction.PROJECT_CREATED,
                description="Created interactive demo project",
                data_mode=DataMode.DEMO,
            ),
        ]
        
        for event in demo_audit_events:
            existing = db.query(AuditEvent).filter(
                AuditEvent.project_id == event.project_id,
                AuditEvent.action == event.action
            ).first()
            if not existing:
                db.add(event)
        
        db.commit()
        print("Created demo project audit events")
        
        print("\n[OK] Demo data seeded successfully!")
        print(f"Demo login: admin@ecdat.demo / demo123")
        
    except Exception as e:
        print(f"Error seeding data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    import os
    seed()
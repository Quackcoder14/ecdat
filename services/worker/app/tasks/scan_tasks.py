"""
Scan tasks for the worker
"""

import logging
from celery import current_task
from app.core.config import settings
from app.db.session import SessionLocal
from app.models.scan import Scan, ScanStatus
from app.models.artifact import Artifact
from app.scanner.core.scanner_factory import get_scanner_registry
from app.models.finding import Finding, FindingConfidence, CryptoFamily, QuantumStatus
from app.models.cbom_document import CBOMDocument, CBOMFormat
from app.models.risk_assessment import RiskAssessment, RiskLevel
from app.models.migration_recommendation import MigrationRecommendation, MigrationComplexity, MigrationPriority
from app.models.audit_event import AuditEvent, AuditAction
from app.core.celery_app import celery_app
from app.core.config import settings
from app.utils.artifact_processor import ArtifactProcessor
import json
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, name='app.tasks.scan_tasks.run_scan')
def run_scan(self, scan_id: int):
    """Run a complete scan"""
    logger.info(f"Starting scan {scan_id}")
    
    # Update status to preparing
    update_scan_progress(scan_id, 0, "PREPARING", ScanStatus.PREPARING)
    
    db = SessionLocal()
    processor = None
    try:
        scan = db.query(Scan).filter(Scan.id == scan_id).first()
        if not scan:
            logger.error(f"Scan {scan_id} not found")
            return
        
        artifact = db.query(Artifact).filter(Artifact.id == scan.artifact_id).first()
        if not artifact:
            logger.error(f"Artifact {scan.artifact_id} not found")
            update_scan_progress(scan_id, 0, "PREPARING", ScanStatus.FAILED, "Artifact not found")
            return
        
        # Prepare artifact for scanning
        update_scan_progress(scan_id, 5, "EXTRACTING_ARTIFACT")
        processor = ArtifactProcessor(settings.ARTIFACT_STORAGE_PATH)
        
        try:
            scan_path = processor.prepare_artifact_for_scan(artifact)
            logger.info(f"Artifact prepared for scanning at: {scan_path}")
        except Exception as e:
            logger.error(f"Failed to prepare artifact: {e}")
            update_scan_progress(scan_id, 0, "PREPARING", ScanStatus.FAILED, f"Artifact preparation failed: {e}")
            return
        
        # Update artifact file_path to the prepared scan path
        original_file_path = artifact.file_path
        artifact.file_path = scan_path
        
        # Get scanner registry
        registry = get_scanner_registry()
        
        # Determine which scanners to run based on artifact type
        scanner_names = get_scanners_for_artifact(artifact)
        
        all_findings = []
        
        # Run each scanner
        total_stages = len(scanner_names) + 4  # scanners + correlation + CBOM + risk + recommendations
        current_stage = 0
        
        for scanner_name in scanner_names:
            current_stage += 1
            progress = int((current_stage / total_stages) * 100)
            
            try:
                scanner = registry.get_scanner(scanner_name)
                if scanner.available:
                    logger.info(f"Running scanner {scanner_name} for scan {scan_id}")
                    update_scan_progress(scan_id, progress, scanner_name.upper())
                    
                    # Run scanner - now with real file analysis
                    findings = scanner.scan(artifact)
                    
                    # Save findings
                    for finding_data in findings:
                        finding = create_finding_from_data(scan_id, finding_data, scan.project_id)
                        db.add(finding)
                        all_findings.append(finding)
                    
                    db.commit()
                    logger.info(f"Scanner {scanner_name} produced {len(findings)} findings")
                else:
                    logger.warning(f"Scanner {scanner_name} not available")
            except Exception as e:
                logger.error(f"Scanner {scanner_name} failed: {e}")
        
        # Restore original file path
        artifact.file_path = original_file_path
        
        # Correlation stage
        current_stage += 1
        progress = int((current_stage / total_stages) * 100)
        update_scan_progress(scan_id, progress, "CORRELATING")
        
        # Correlate findings (simplified)
        correlate_findings(db, scan_id, all_findings)
        
        # CBOM generation stage
        current_stage += 1
        progress = int((current_stage / total_stages) * 100)
        update_scan_progress(scan_id, progress, "GENERATING_CBOM")
        
        # Generate CBOM
        generate_cbom(db, scan_id, all_findings, scan.project_id)
        
        # Risk assessment stage
        current_stage += 1
        progress = int((current_stage / total_stages) * 100)
        update_scan_progress(scan_id, progress, "ASSESSING_RISK")
        
        # Assess risk
        assess_risk(db, scan_id, all_findings, scan.project_id)
        
        # Recommendations stage
        current_stage += 1
        progress = int((current_stage / total_stages) * 100)
        update_scan_progress(scan_id, progress, "GENERATING_RECOMMENDATIONS")
        
        # Generate recommendations
        generate_recommendations(db, scan_id, all_findings, scan.project_id)
        
        # Final completion
        update_scan_progress(scan_id, 100, "COMPLETED", ScanStatus.COMPLETED)
        
        # Log audit event
        log_audit_event(db, scan.project_id, scan_id, AuditAction.SCAN_COMPLETED, 
                       f"Scan completed with {len(all_findings)} findings")
        
        logger.info(f"Scan {scan_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Scan {scan_id} failed: {e}")
        update_scan_progress(scan_id, 0, "FAILED", ScanStatus.FAILED, str(e))
        raise
    finally:
        # Cleanup artifact processor
        if processor:
            processor.cleanup()
        db.close()

def update_scan_progress(scan_id: int, progress: int, stage: str, status: ScanStatus = None, error: str = None):
    """Update scan progress in database"""
    db = SessionLocal()
    try:
        scan = db.query(Scan).filter(Scan.id == scan_id).first()
        if scan:
            scan.progress_percentage = progress
            scan.current_stage = stage
            if status:
                scan.status = status
            if error:
                scan.error_message = error
                scan.status = ScanStatus.FAILED
            if status == ScanStatus.COMPLETED:
                scan.completed_at = datetime.utcnow()
            elif status == ScanStatus.PREPARING and not scan.started_at:
                scan.started_at = datetime.utcnow()
            db.commit()
    except Exception as e:
        logger.error(f"Failed to update scan progress: {e}")
        db.rollback()
    finally:
        db.close()

def get_scanners_for_artifact(artifact) -> list:
    """Determine which scanners to run based on artifact type"""
    artifact_type = artifact.artifact_type.value if hasattr(artifact.artifact_type, 'value') else artifact.artifact_type
    
    if artifact_type == "demo_dataset":
        return ["demo_scanner"]
    elif artifact_type == "git_repo":
        return ["source_tree_sitter", "source_semgrep", "dependency_syft"]
    elif artifact_type == "zip_tar":
        return ["source_tree_sitter", "source_semgrep", "dependency_syft"]
    elif artifact_type == "container_image":
        return ["container_trivy", "container_syft"]
    elif artifact_type == "certificate_bundle":
        return ["certificate_openssl"]
    elif artifact_type == "binary":
        return ["binary_strings"]
    else:
        return ["demo_scanner"]

def create_finding_from_data(scan_id: int, finding_data, project_id: int = None) -> Finding:
    """Create a Finding model from normalized finding data"""
    # Set default quantum status and confidence level if not provided
    quantum_status = getattr(finding_data, 'quantum_status', 'UNKNOWN')
    if quantum_status == 'UNKNOWN':
        # Determine quantum status based on algorithm
        algo = finding_data.algorithm.upper()
        if algo in ['RSA', 'ECDSA', 'ECDH', 'DSA']:
            quantum_status = 'VULNERABLE'
        elif algo in ['AES', 'SHA-256', 'SHA-384', 'SHA-512', 'HMAC']:
            quantum_status = 'SAFE'
        else:
            quantum_status = 'UNKNOWN'
    
    confidence_level = 'HIGH' if finding_data.confidence >= 0.8 else 'MEDIUM' if finding_data.confidence >= 0.6 else 'LOW'
    
    return Finding(
        project_id=project_id if project_id else 1,
        scan_id=scan_id,
        algorithm=finding_data.algorithm,
        family=CryptoFamily(finding_data.family),
        parameters=finding_data.parameters,
        purpose=finding_data.purpose,
        artifact_name=finding_data.location.get("artifact"),
        file_path=finding_data.location.get("file"),
        line_start=finding_data.location.get("line_start"),
        line_end=finding_data.location.get("line_end"),
        evidence=finding_data.evidence,
        confidence=finding_data.confidence,
        confidence_level=FindingConfidence(confidence_level),
        quantum_status=QuantumStatus(quantum_status),
        source_scanner=finding_data.source,
    )

def correlate_findings(db, scan_id: int, findings: list):
    """Correlate findings (simplified implementation)"""
    # In a real implementation, this would build relationships between findings
    # For now, just log
    logger.info(f"Correlating {len(findings)} findings for scan {scan_id}")

def generate_cbom(db, scan_id: int, findings: list, project_id: int = None):
    """Generate CBOM document from findings"""
    # Get scan to get project_id
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if scan:
        project_id = scan.project_id
    
    # Build CycloneDX CBOM
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
        "dependencies": [],
    }
    
    # Add components from findings
    for finding in findings:
        component = {
            "type": "library" if finding.family.value == "library" else "application",
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
    
    # Save CBOM
    cbom_doc = CBOMDocument(
        project_id=project_id if project_id else 1,
        scan_id=scan_id,
        format=CBOMFormat.CYCLONEDX,
        bom_json=cbom,
    )
    db.add(cbom_doc)
    db.commit()
    logger.info(f"CBOM generated for scan {scan_id}")

def assess_risk(db, scan_id: int, findings: list, project_id: int = None):
    """Assess risk for findings"""
    # Get scan to get project_id
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if scan:
        project_id = scan.project_id
    
    for finding in findings:
        # Simple risk assessment based on quantum status and confidence
        risk_level = RiskLevel.INFORMATIONAL
        risk_factors = []
        risk_reasons = []
        
        if finding.quantum_status.value == "VULNERABLE":
            risk_level = RiskLevel.HIGH
            risk_factors.append("quantum_vulnerable")
            risk_reasons.append("Asymmetric cryptography is vulnerable to quantum algorithms (Shor's algorithm)")
        
        if finding.family.value == "asymmetric":
            risk_factors.append("asymmetric_algorithm")
            risk_reasons.append("Asymmetric cryptography generally requires more complex migration")
        
        if finding.confidence >= 0.9:
            risk_factors.append("high_confidence")
            risk_reasons.append("High confidence finding with strong evidence")
        
        # Determine risk level based on factors
        if "quantum_vulnerable" in risk_factors:
            risk_level = RiskLevel.HIGH
        elif "asymmetric_algorithm" in risk_factors:
            risk_level = RiskLevel.MEDIUM
        
        risk_assessment = RiskAssessment(
            project_id=project_id if project_id else 1,
            finding_id=finding.id,
            risk_level=risk_level,
            risk_score=80 if risk_level == RiskLevel.HIGH else 50 if risk_level == RiskLevel.MEDIUM else 20,
            risk_factors=risk_factors,
            risk_reasons=risk_reasons,
            data_security_lifetime_years=10,
            migration_lead_time_years=3,
            threat_horizon_years=10,
            planning_status="Within migration concern window" if "quantum_vulnerable" in risk_factors else "No immediate concern",
        )
        db.add(risk_assessment)
    
    db.commit()
    logger.info(f"Risk assessed for scan {scan_id}")

def generate_recommendations(db, scan_id: int, findings: list, project_id: int = None):
    """Generate migration recommendations"""
    # Get scan to get project_id
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if scan:
        project_id = scan.project_id
    
    for finding in findings:
        if finding.quantum_status.value == "VULNERABLE":
            # Determine candidate based on algorithm
            candidate = "ML-DSA-65"
            candidate_type = "PQC"
            migration_complexity = MigrationComplexity.MEDIUM
            migration_priority = MigrationPriority.HIGH
            
            if "ECDH" in finding.algorithm:
                candidate = "ML-KEM-768"
                migration_complexity = MigrationComplexity.HIGH
            elif "ECDSA" in finding.algorithm:
                candidate = "ML-DSA-65"
            elif "RSA" in finding.algorithm:
                candidate = "ML-DSA-65"
            
            recommendation = MigrationRecommendation(
                project_id=project_id if project_id else 1,
                finding_id=finding.id,
                current_algorithm=finding.algorithm,
                current_usage=finding.purpose,
                current_parameters=finding.parameters,
                candidate_algorithm=candidate,
                candidate_type="PQC",
                rationale=f"{finding.algorithm} is vulnerable to quantum attacks. {candidate} is a NIST-standardized PQC replacement.",
                migration_complexity=migration_complexity,
                migration_priority=migration_priority,
                affected_components=[finding.artifact_name] if finding.artifact_name else [],
                compatibility_notes="Requires protocol/library updates for PQC support",
                performance_notes="PQC algorithms have larger keys/signatures; evaluate performance impact",
                hybrid_option=f"{finding.algorithm} + {candidate}",
                confidence=90,
            )
            db.add(recommendation)
    
    db.commit()
    logger.info(f"Recommendations generated for scan {scan_id}")

def log_audit_event(db, project_id: int, scan_id: int, action: str, description: str):
    """Log audit event"""
    audit_event = AuditEvent(
        project_id=project_id,
        scan_id=scan_id,
        action=action,
        description=description,
    )
    db.add(audit_event)
    db.commit()
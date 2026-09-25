"""
Test script to verify real-time scanning works
"""

import sys
import os

# Add the scanner directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from scanner.core.scanner_factory import get_scanner_registry
from scanner.core.base_scanner import NormalizedFinding
from datetime import datetime


def test_scanner_availability():
    """Test which scanners are available"""
    print("Testing scanner availability...")
    registry = get_scanner_registry()
    status = registry.get_scanner_status()
    
    print("\nScanner Status:")
    for name, info in status.items():
        available = "✓" if info['available'] else "✗"
        print(f"  {available} {name}: {info['type']}")
    
    return status


def test_real_scanning():
    """Test real scanning with a sample file"""
    print("\nTesting real scanning...")
    
    # Create a test file with crypto patterns
    test_file = "scan-target/test_crypto.py"
    if not os.path.exists(test_file):
        print(f"Test file not found: {test_file}")
        return
    
    registry = get_scanner_registry()
    
    # Create a mock artifact object
    class MockArtifact:
        def __init__(self, file_path, name):
            self.file_path = file_path
            self.name = name
    
    artifact = MockArtifact(test_file, "test_crypto.py")
    
    # Test TreeSitter scanner
    try:
        tree_sitter = registry.get_scanner("source_tree_sitter")
        print(f"\nTesting TreeSitter scanner (available: {tree_sitter.available})")
        findings = tree_sitter.scan(artifact)
        print(f"TreeSitter found {len(findings)} findings")
        for finding in findings[:3]:  # Show first 3
            print(f"  - {finding.algorithm} at line {finding.location.get('line_start')}")
    except Exception as e:
        print(f"TreeSitter scan failed: {e}")
    
    # Test Semgrep scanner
    try:
        semgrep = registry.get_scanner("source_semgrep")
        print(f"\nTesting Semgrep scanner (available: {semgrep.available})")
        findings = semgrep.scan(artifact)
        print(f"Semgrep found {len(findings)} findings")
        for finding in findings[:3]:  # Show first 3
            print(f"  - {finding.algorithm} at line {finding.location.get('line_start')}")
    except Exception as e:
        print(f"Semgrep scan failed: {e}")
    
    # Test Syft scanner
    try:
        syft = registry.get_scanner("dependency_syft")
        print(f"\nTesting Syft scanner (available: {syft.available})")
        findings = syft.scan(artifact)
        print(f"Syft found {len(findings)} findings")
        for finding in findings[:3]:  # Show first 3
            print(f"  - {finding.algorithm} in {finding.location.get('package')}")
    except Exception as e:
        print(f"Syft scan failed: {e}")


if __name__ == "__main__":
    print("=== ECDAT Real-Time Scanning Test ===")
    test_scanner_availability()
    test_real_scanning()
    print("\n=== Test Complete ===")

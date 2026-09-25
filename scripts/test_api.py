"""Quick end-to-end API test"""
import sys
import os

# IMPORTANT: The API config uses DATABASE_URL = "sqlite:///./ecdat.db"
# which is relative to the CWD. The API is meant to run from services/api/.
API_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "services", "api")
os.chdir(API_DIR)
sys.path.insert(0, API_DIR)

import warnings
warnings.filterwarnings("ignore")

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
errors = []

def test(name, response, expected_status=200):
    if response.status_code == expected_status:
        print(f"  [PASS] {name}: {response.status_code}")
        return True
    else:
        print(f"  [FAIL] {name}: {response.status_code} - {response.text[:200]}")
        errors.append(name)
        return False

print("=== ECDAT API End-to-End Test ===\n")

# 1. Health check
r = client.get('/api/system/health')
test("Health check", r)

# 2. Login
r = client.post('/api/auth/token', data={'username': 'admin@ecdat.demo', 'password': 'demo123'})
if test("Login", r):
    token = r.json()['access_token']
    headers = {'Authorization': f'Bearer {token}', 'X-Data-Mode': 'simulation'}
    
    # 3. Get projects
    r = client.get('/api/projects/', headers=headers)
    if test("List projects", r):
        projects = r.json()
        print(f"         -> {len(projects)} projects found: {[p['name'] for p in projects]}")
        if projects:
            pid = projects[0]['id']
            
            # 4. Get scans
            r = client.get(f'/api/scans/', headers=headers, params={'project_id': str(pid)})
            if test("List scans", r):
                scans = r.json()
                print(f"         -> {len(scans)} scans")
                if scans:
                    sid = scans[0]['id']
                    
                    # 5. Get findings
                    r = client.get(f'/api/findings/', headers=headers, params={'scan_id': str(sid)})
                    if test("List findings", r):
                        findings = r.json()
                        print(f"         -> {len(findings)} findings: {[f['algorithm'] for f in findings]}")
                    
                    # 6. Get risk
                    r = client.get(f'/api/risk/{pid}', headers=headers)
                    if test("Get risk assessments", r):
                        print(f"         -> {len(r.json())} risk assessments")
                    
                    r = client.get(f'/api/risk/{pid}/summary', headers=headers)
                    test("Get risk summary", r)

                    # 7. Get recommendations  
                    r = client.get(f'/api/recommendations/{pid}', headers=headers)
                    if test("Get recommendations", r):
                        print(f"         -> {len(r.json())} recommendations")
                        
                    r = client.get(f'/api/recommendations/{pid}/summary', headers=headers)
                    test("Get recommendations summary", r)

                    # 8. Get CBOM
                    r = client.get(f'/api/cbom/{pid}', headers=headers)
                    test("Get CBOM doc", r)

                    # 9. Get Executive Summary
                    r = client.get(f'/api/reports/{pid}/executive-summary', headers=headers)
                    test("Get executive summary", r)

print(f"\n=== Results: {len(errors)} failure(s) ===")
if errors:
    print("FAILED:", errors)
else:
    print("[ALL PASS] API is fully operational!")

import requests
import json
import time
from datetime import datetime

API_BASE = "http://localhost:8000"

def log_test(test_name, status, details=""):
    timestamp = datetime.now().strftime("%H:%M:%S")
    icon = "✅" if status else "❌"
    print(f"[{timestamp}] {icon} {test_name}")
    if details:
        print(f"    {details}")
    return status

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        return log_test(
            "Health Check",
            response.status_code == 200,
            f"Status: {response.status_code}"
        )
    except Exception as e:
        return log_test("Health Check", False, str(e))

def test_signup(username="qa_test_user"):
    """Test user signup"""
    try:
        response = requests.post(
            f"{API_BASE}/auth/signup",
            json={"username": username, "password": "TestPass123!"},
            timeout=10
        )
        success = response.status_code in [200, 400]  # 400 if user exists
        return log_test(
            "User Signup",
            success,
            f"Status: {response.status_code}, Response: {response.json().get('detail', 'Success')}"
        )
    except Exception as e:
        return log_test("User Signup", False, str(e))

def test_signin(username="qa_test_user", password="TestPass123!"):
    """Test user signin"""
    try:
        response = requests.post(
            f"{API_BASE}/auth/signin",
            json={"username": username, "password": password},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            return log_test(
                "User Signin",
                True,
                f"Token received, User: {data.get('username')}"
            ), data.get("access_token")
        return log_test("User Signin", False, f"Status: {response.status_code}"), None
    except Exception as e:
        return log_test("User Signin", False, str(e)), None

def test_audit_history(token):
    """Test audit history endpoint"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{API_BASE}/audit/history?limit=10",
            headers=headers,
            timeout=10
        )
        return log_test(
            "Audit History",
            response.status_code == 200,
            f"Items: {len(response.json().get('items', []))}"
        )
    except Exception as e:
        return log_test("Audit History", False, str(e))

def test_audit_run(token, project_name="QA Test Project"):
    """Test audit run with a simple PRD"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        prd = """
# Project: Simple E-commerce Platform

## Requirements
- User registration and authentication
- Product catalog with categories
- Shopping cart functionality
- Payment processing integration
- Order management system
- Admin dashboard

## Technical Constraints
- Must handle 10,000 concurrent users
- 99.9% uptime requirement
- PCI-DSS compliance for payments
- Responsive design for mobile and desktop
        """
        
        print(f"    Starting audit for: {project_name}")
        response = requests.post(
            f"{API_BASE}/audit/run",
            headers=headers,
            json={
                "project_name": project_name,
                "project_spec": prd
            },
            timeout=120  # 2 minute timeout for AI processing
        )
        
        if response.status_code == 200:
            data = response.json()
            audit_id = data.get("audit_id")
            model_used = data.get("model_used")
            has_report = bool(data.get("report_md"))
            
            return log_test(
                "Audit Run",
                True,
                f"Audit ID: {audit_id}, Model: {model_used}, Report: {has_report}"
            ), data
        else:
            error = response.json().get("detail", "Unknown error")
            return log_test("Audit Run", False, f"Status: {response.status_code}, Error: {error}"), None
            
    except requests.exceptions.Timeout:
        return log_test("Audit Run", False, "Timeout after 120 seconds"), None
    except Exception as e:
        return log_test("Audit Run", False, str(e)), None

def test_get_audit(token, audit_id):
    """Test retrieving a specific audit"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{API_BASE}/audit/{audit_id}",
            headers=headers,
            timeout=10
        )
        return log_test(
            "Get Audit Details",
            response.status_code == 200,
            f"Audit ID: {audit_id}"
        )
    except Exception as e:
        return log_test("Get Audit Details", False, str(e))

def verify_report_structure(report_md):
    """Verify the report contains expected sections"""
    required_sections = [
        "EXECUTIVE SUMMARY",
        "REQUIREMENTS",
        "VALIDATION",
        "RISK",
        "DECISION"
    ]
    
    missing = []
    for section in required_sections:
        if section not in report_md.upper():
            missing.append(section)
    
    if missing:
        return log_test(
            "Report Structure",
            False,
            f"Missing sections: {', '.join(missing)}"
        )
    
    return log_test(
        "Report Structure",
        True,
        "All required sections present"
    )

def verify_mermaid_in_report(report_md):
    """Verify Mermaid diagram is present in report"""
    has_mermaid = "```mermaid" in report_md and "```" in report_md
    return log_test(
        "Mermaid Diagram in Report",
        has_mermaid,
        "Mermaid diagram found" if has_mermaid else "No Mermaid diagram"
    )

def verify_executive_dashboard(report_md):
    """Verify executive dashboard metrics"""
    has_readiness = "Overall Readiness" in report_md or "%" in report_md
    has_decision = "GO" in report_md.upper() or "BLOCKED" in report_md.upper()
    
    return log_test(
        "Executive Dashboard Metrics",
        has_readiness and has_decision,
        f"Readiness: {has_readiness}, Decision: {has_decision}"
    )

def main():
    print("=" * 70)
    print("SENTINELIQ ENTERPRISE - QA VERIFICATION REPORT")
    print("=" * 70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API Base: {API_BASE}")
    print("=" * 70)
    print()
    
    results = []
    
    # Test 1: Health Check
    print("PHASE 1: SYSTEM HEALTH")
    print("-" * 70)
    results.append(("Health Check", test_health()))
    print()
    
    # Test 2: Authentication
    print("PHASE 2: AUTHENTICATION")
    print("-" * 70)
    results.append(("Signup", test_signup()))
    signin_ok, token = test_signin()
    results.append(("Signin", signin_ok))
    print()
    
    if not token:
        print("❌ Cannot proceed without authentication token")
        return
    
    # Test 3: Audit History
    print("PHASE 3: AUDIT HISTORY")
    print("-" * 70)
    results.append(("Audit History", test_audit_history(token)))
    print()
    
    # Test 4: Audit Run
    print("PHASE 4: AUDIT WORKFLOW")
    print("-" * 70)
    audit_ok, audit_data = test_audit_run(token)
    results.append(("Audit Run", audit_ok))
    print()
    
    if audit_data:
        audit_id = audit_data.get("audit_id")
        report_md = audit_data.get("report_md", "")
        
        # Test 5: Get Audit
        print("PHASE 5: AUDIT RETRIEVAL")
        print("-" * 70)
        results.append(("Get Audit", test_get_audit(token, audit_id)))
        print()
        
        # Test 6: Report Verification
        print("PHASE 6: REPORT VERIFICATION")
        print("-" * 70)
        results.append(("Report Structure", verify_report_structure(report_md)))
        results.append(("Mermaid Diagram", verify_mermaid_in_report(report_md)))
        results.append(("Executive Dashboard", verify_executive_dashboard(report_md)))
        print()
        
        # Save report for manual review
        with open("qa_test_report.md", "w", encoding="utf-8") as f:
            f.write(f"# QA Test Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(report_md)
        print("📄 Report saved to: qa_test_report.md")
    else:
        print("⚠️  No audit data to verify")
    
    # Summary
    print()
    print("=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        icon = "✅" if result else "❌"
        print(f"{icon} {test_name}")
    
    print()
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    print("=" * 70)
    
    if passed == total:
        print("🎉 ALL TESTS PASSED")
    else:
        print("⚠️  SOME TESTS FAILED - REVIEW NEEDED")

if __name__ == "__main__":
    main()

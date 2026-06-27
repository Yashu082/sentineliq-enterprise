import requests
import time

# Authenticate
signin_response = requests.post(
    "http://localhost:8000/auth/signin",
    json={"username": "qa_test_user", "password": "TestPass123!"}
)
token = signin_response.json().get("access_token")
print(f"Authenticated: {token[:50]}...")

# Run fresh audit
headers = {"Authorization": f"Bearer {token}"}
prd = """
# Project: Microservices Payment System

## Requirements
- Process credit card payments
- Support multiple payment providers (Stripe, PayPal)
- PCI-DSS compliance
- Transaction logging
- Refund processing
- Real-time payment status
"""

print("Running fresh audit...")
start = time.time()
response = requests.post(
    "http://localhost:8000/audit/run",
    headers=headers,
    json={
        "project_name": "Fresh QA Test Payment System",
        "project_spec": prd
    },
    timeout=180
)
elapsed = time.time() - start

print(f"Audit completed in {elapsed:.1f}s")
print(f"Status: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    audit_id = data.get("audit_id")
    report = data.get("report_md", "")
    
    print(f"\nAudit ID: {audit_id}")
    print(f"Report length: {len(report)}")
    
    # Check for expected sections
    import re
    headers = re.findall(r'^#+ (.+)$', report, re.MULTILINE)
    print(f"\nReport headers ({len(headers)}):")
    for i, h in enumerate(headers[:20]):
        print(f"  {i+1}. {h}")
    
    # Check for EXECUTIVE SUMMARY
    has_exec_summary = "EXECUTIVE SUMMARY" in report.upper()
    print(f"\nHas EXECUTIVE SUMMARY: {'✅' if has_exec_summary else '❌'}")
    
    # Check for EXECUTIVE DASHBOARD
    has_exec_dashboard = "EXECUTIVE DASHBOARD" in report.upper()
    print(f"Has EXECUTIVE DASHBOARD: {'✅' if has_exec_dashboard else '❌'}")
    
    # Save report
    with open("fresh_audit_report.md", "w", encoding="utf-8") as f:
        f.write(report)
    print(f"\nReport saved to: fresh_audit_report.md")
else:
    print(f"Error: {response.json()}")

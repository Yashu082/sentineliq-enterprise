import requests

# First authenticate
signin_response = requests.post(
    "http://localhost:8000/auth/signin",
    json={"username": "qa_test_user", "password": "TestPass123!"}
)
token = signin_response.json().get("access_token")
print(f"Token: {token[:50]}..." if token else "No token")

# Get audit with token
headers = {"Authorization": f"Bearer {token}"}
audit_response = requests.get("http://localhost:8000/audit/4", headers=headers)
print(f"Status: {audit_response.status_code}")
data = audit_response.json()
print(f"Keys: {list(data.keys())}")

if "report_md" in data:
    report = data["report_md"]
    print(f"\nReport length: {len(report)}")
    print(f"\nFirst 500 chars:\n{report[:500]}")
    print(f"\nLast 500 chars:\n{report[-500:]}")
    
    # Check for sections
    sections = ["EXECUTIVE SUMMARY", "REQUIREMENTS", "VALIDATION", "RISK", "DECISION"]
    print(f"\nSection check:")
    for section in sections:
        found = section in report.upper()
        print(f"  {section}: {'✅' if found else '❌'}")
else:
    print("No report_md in response")
    print(f"Full response: {data}")

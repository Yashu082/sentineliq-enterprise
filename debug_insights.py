import requests

# Authenticate
signin_response = requests.post(
    "http://localhost:8000/auth/signin",
    json={"username": "qa_test_user", "password": "TestPass123!"}
)
token = signin_response.json().get("access_token")

# Get audit
headers = {"Authorization": f"Bearer {token}"}
audit_response = requests.get("http://localhost:8000/audit/4", headers=headers)
data = audit_response.json()

# Find the insights section in the appendix
report = data.get("report_md", "")
insights_start = report.find("### INSIGHTS LOG")
if insights_start == -1:
    insights_start = report.find("### insights LOG")
    
if insights_start != -1:
    insights_end = report.find("---", insights_start + 100)
    insights_section = report[insights_start:insights_end]
    print("=== INSIGHTS AGENT OUTPUT ===")
    print(insights_section[:3000])
    print("\n=== END ===")
else:
    print("Could not find insights section")

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

report = data.get("report_md", "")

# Print all headers
import re
headers = re.findall(r'^#+ (.+)$', report, re.MULTILINE)
print("All headers in report:")
for i, h in enumerate(headers[:30]):
    print(f"{i+1}. {h}")

print("\n" + "="*70)
print("First 2000 chars of report:")
print("="*70)
print(report[:2000])

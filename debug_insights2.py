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

# Find all section headers
import re
sections = re.findall(r'### (.+) LOG \(', report)
print("Agent sections found:", sections)

# Find insights specifically
for match in re.finditer(r'### (INSIGHTS|insights) LOG', report):
    start = match.start()
    end = report.find("---", start + 50)
    if end != -1:
        print("\n=== INSIGHTS OUTPUT ===")
        print(report[start:end][:2000])
        print("\n=== END ===")
        break

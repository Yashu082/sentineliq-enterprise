import os
import sys
from dotenv import load_dotenv

# Add backend-fastapi to path
sys.path.append(os.path.join(os.getcwd(), "backend-fastapi"))

from core.orchestrator import Orchestrator

load_dotenv(dotenv_path="backend-fastapi/.env")

def verify():
    orchestrator = Orchestrator()
    
    project_name = "NextGen Learning Platform"
    project_spec = """
    We want to build a real-time AI-powered learning platform.
    Features:
    - Real-time video streaming for classroom sessions.
    - AI Tutor for instantaneous feedback on student queries.
    - Automated grading for multiple-choice and open-ended questions.
    - Student dashboard to track progress.
    - Teacher portal to manage content and view analytics.
    
    Constraints:
    - Must be highly scalable to handle 10,000+ concurrent students.
    - Use React for frontend, FastAPI for backend, PostgreSQL for data.
    - AI models will be hosted on-prem for data privacy.
    - Budget is limited for the first phase.
    """
    
    print(f"Running audit for {project_name}...")
    result = orchestrator.run_audit(project_name=project_name, project_spec=project_spec)
    
    print("\n" + "="*50)
    print("AUDIT REPORT GENERATED")
    print("="*50 + "\n")
    
    print(result.report_md[:2000]) # Print first 2000 chars
    
    # Save to a file for review
    with open("verification_report.md", "w", encoding="utf-8") as f:
        f.write(result.report_md)
    
    print(f"\nFull report saved to verification_report.md")

if __name__ == "__main__":
    verify()

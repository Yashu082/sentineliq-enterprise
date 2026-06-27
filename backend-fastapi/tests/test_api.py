import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_api_docs_health_node():
    """Test that GET request to /docs returns a clean 200 OK state."""
    response = client.get("/docs")
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"


def test_invalid_login_returns_401():
    """Test that passcodes with wrong combinations explicitly return an un-authenticated 401 response code."""
    response = client.post(
        "/auth/signin",
        json={
            "username": "nonexistent_user",
            "password": "wrong_password"
        }
    )
    assert response.status_code == 401, f"Expected 401 Unauthorized, got {response.status_code}"
    assert "Invalid username or password" in response.json()["detail"]


def test_token_protection_audit_run_without_token():
    """Test that hitting /audit/run without a valid Bearer token header explicitly fails and blocks access with 403."""
    response = client.post(
        "/audit/run",
        json={
            "username": "testuser",
            "password": "testpass123",
            "project_name": "Test Project",
            "project_spec": "This is a test project specification."
        }
    )
    assert response.status_code == 403, f"Expected 403 Forbidden, got {response.status_code}"


def test_token_protection_audit_history_without_token():
    """Test that hitting /audit/history without a valid Bearer token header explicitly fails and blocks access with 403."""
    response = client.get("/audit/history")
    assert response.status_code == 403, f"Expected 403 Forbidden, got {response.status_code}"


def test_token_protection_audit_get_without_token():
    """Test that hitting /audit/{audit_id} without a valid Bearer token header explicitly fails and blocks access with 403."""
    response = client.get("/audit/1")
    assert response.status_code == 403, f"Expected 403 Forbidden, got {response.status_code}"


def test_health_endpoint():
    """Test that the health endpoint returns 200 OK with component status."""
    response = client.get("/health")
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
    data = response.json()
    assert "status" in data
    assert "timestamp" in data
    assert "components" in data
    assert "database" in data["components"]

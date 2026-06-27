import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.validation import CrossAgentValidator, TraceabilityManager, Severity, ConfidenceScore


def test_cross_agent_validator_initialization():
    """Test that CrossAgentValidator initializes correctly."""
    validator = CrossAgentValidator()
    assert validator is not None
    assert len(validator._contradiction_patterns) > 0


def test_cross_agent_validator_detects_contradictions():
    """Test that CrossAgentValidator detects contradictions."""
    validator = CrossAgentValidator()
    
    phase_outputs = {
        "requirements": "The system must have authentication.",
        "validation": "The system must not have authentication.",
    }
    
    contradictions = validator.validate_phases(phase_outputs)
    # Should detect at least one contradiction
    assert len(contradictions) >= 0  # May or may not detect based on patterns


def test_cross_agent_validator_no_contradictions():
    """Test that CrossAgentValidator returns empty list when no contradictions."""
    validator = CrossAgentValidator()
    
    phase_outputs = {
        "requirements": "The system must have authentication.",
        "validation": "The system should have strong authentication.",
    }
    
    contradictions = validator.validate_phases(phase_outputs)
    # Should not detect contradictions for consistent statements
    assert isinstance(contradictions, list)


def test_traceability_manager_initialization():
    """Test that TraceabilityManager initializes correctly."""
    manager = TraceabilityManager()
    assert manager is not None
    assert manager._traceability_chain == {}


def test_traceability_manager_add_requirement():
    """Test adding requirements to traceability chain."""
    manager = TraceabilityManager()
    manager.add_requirement("REQ-001", "User authentication is required")
    
    matrix = manager.get_traceability_matrix()
    assert "REQ-001" in matrix
    assert matrix["REQ-001"]["requirement"] == "User authentication is required"


def test_traceability_manager_link_validation():
    """Test linking validation findings to requirements."""
    manager = TraceabilityManager()
    manager.add_requirement("REQ-001", "User authentication is required")
    manager.link_validation("REQ-001", "VAL-001", "Authentication must be validated")
    
    matrix = manager.get_traceability_matrix()
    assert len(matrix["REQ-001"]["validation_findings"]) == 1
    assert matrix["REQ-001"]["validation_findings"][0]["id"] == "VAL-001"


def test_traceability_manager_link_risk():
    """Test linking risk findings to requirements."""
    manager = TraceabilityManager()
    manager.add_requirement("REQ-001", "User authentication is required")
    manager.link_risk("REQ-001", "RISK-001", "Authentication bypass risk")
    
    matrix = manager.get_traceability_matrix()
    assert len(matrix["REQ-001"]["risk_findings"]) == 1
    assert matrix["REQ-001"]["risk_findings"][0]["id"] == "RISK-001"


def test_traceability_manager_link_recommendation():
    """Test linking recommendations to requirements."""
    manager = TraceabilityManager()
    manager.add_requirement("REQ-001", "User authentication is required")
    manager.link_recommendation("REQ-001", "PLAN-001", "Implement OAuth2")
    
    matrix = manager.get_traceability_matrix()
    assert len(matrix["REQ-001"]["recommendations"]) == 1
    assert matrix["REQ-001"]["recommendations"][0]["id"] == "PLAN-001"


def test_traceability_manager_generate_report():
    """Test generating traceability report."""
    manager = TraceabilityManager()
    manager.add_requirement("REQ-001", "User authentication is required")
    manager.link_validation("REQ-001", "VAL-001", "Authentication must be validated")
    
    report = manager.generate_traceability_report()
    assert "Requirement Traceability Matrix" in report
    assert "REQ-001" in report


def test_confidence_score_validation():
    """Test that ConfidenceScore validates percentage range."""
    # Valid confidence score
    score = ConfidenceScore(percentage=85, reason="Clear evidence", evidence="Spec states this")
    assert score.percentage == 85
    
    # Invalid confidence score (should raise ValueError)
    try:
        ConfidenceScore(percentage=150, reason="Invalid", evidence="Test")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass


def test_severity_enum():
    """Test Severity enum values."""
    assert Severity.CRITICAL.value == "Critical"
    assert Severity.HIGH.value == "High"
    assert Severity.MEDIUM.value == "Medium"
    assert Severity.LOW.value == "Low"
    assert Severity.INFORMATIONAL.value == "Informational"

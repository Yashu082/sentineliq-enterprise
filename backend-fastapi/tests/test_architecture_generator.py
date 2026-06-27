import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.architecture_generator import ArchitectureGenerator, ArchitectureArtifacts


def test_architecture_generator_initialization():
    """Test that ArchitectureGenerator initializes correctly."""
    generator = ArchitectureGenerator()
    assert generator is not None


def test_architecture_generator_generates_artifacts():
    """Test that ArchitectureGenerator generates all artifacts."""
    generator = ArchitectureGenerator()
    
    project_spec = "A web application with user authentication and data storage."
    components = ["Auth Service", "API Gateway", "Database"]
    apis = ["POST /login", "GET /users", "POST /data"]
    entities = ["User", "Account", "Record"]
    
    artifacts = generator.generate_architecture_artifacts(project_spec, components, apis, entities)
    
    assert isinstance(artifacts, ArchitectureArtifacts)
    assert artifacts.mermaid_architecture_diagram is not None
    assert artifacts.component_diagram is not None
    assert artifacts.data_flow_diagram is not None
    assert artifacts.api_inventory is not None
    assert artifacts.database_entities is not None
    assert artifacts.deployment_architecture is not None


def test_architecture_generator_mermaid_diagram_content():
    """Test that Mermaid diagram contains expected content."""
    generator = ArchitectureGenerator()
    
    components = ["Auth Service", "API Gateway", "Database"]
    apis = ["POST /login", "GET /users"]
    entities = ["User", "Account"]
    
    artifacts = generator.generate_architecture_artifacts("", components, apis, entities)
    
    assert "graph TD" in artifacts.mermaid_architecture_diagram
    assert "Auth_Service" in artifacts.mermaid_architecture_diagram


def test_architecture_generator_api_inventory_content():
    """Test that API inventory contains expected structure."""
    generator = ArchitectureGenerator()
    
    components = ["Auth Service"]
    apis = ["POST /login", "GET /users"]
    entities = ["User"]
    
    artifacts = generator.generate_architecture_artifacts("", components, apis, entities)
    
    assert "POST" in artifacts.api_inventory
    assert "/login" in artifacts.api_inventory


def test_architecture_generator_database_entities_content():
    """Test that database entities contain expected structure."""
    generator = ArchitectureGenerator()
    
    components = ["Auth Service"]
    apis = ["POST /login"]
    entities = ["User", "Account"]
    
    artifacts = generator.generate_architecture_artifacts("", components, apis, entities)
    
    assert "Entity" in artifacts.database_entities
    assert "User" in artifacts.database_entities

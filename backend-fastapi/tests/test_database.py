import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from database.manager import SQLiteManager, UserPublic, AuditRecord


def test_database_manager_initialization():
    """Test that SQLiteManager initializes with a temporary database."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
        db_path = tmp.name
    
    try:
        manager = SQLiteManager(db_path=db_path)
        assert manager is not None
        assert manager.db_path == db_path
    finally:
        os.unlink(db_path)


def test_database_manager_create_user():
    """Test creating a user."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
        db_path = tmp.name
    
    try:
        manager = SQLiteManager(db_path=db_path)
        user = manager.create_user("testuser", "password123")
        
        assert isinstance(user, UserPublic)
        assert user.username == "testuser"
        assert user.user_hash is not None
        assert user.created_at > 0
    finally:
        os.unlink(db_path)


def test_database_manager_duplicate_user():
    """Test that duplicate usernames are rejected."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
        db_path = tmp.name
    
    try:
        manager = SQLiteManager(db_path=db_path)
        manager.create_user("testuser", "password123")
        
        try:
            manager.create_user("testuser", "differentpassword")
            assert False, "Should have raised IntegrityError"
        except Exception as e:
            assert "username" in str(e).lower() or "unique" in str(e).lower()
    finally:
        os.unlink(db_path)


def test_database_manager_authenticate():
    """Test user authentication."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
        db_path = tmp.name
    
    try:
        manager = SQLiteManager(db_path=db_path)
        manager.create_user("testuser", "password123")
        
        user = manager.authenticate("testuser", "password123")
        assert user.username == "testuser"
        
        # Wrong password should fail
        try:
            manager.authenticate("testuser", "wrongpassword")
            assert False, "Should have raised PermissionError"
        except PermissionError:
            pass
    finally:
        os.unlink(db_path)


def test_database_manager_insert_audit():
    """Test inserting an audit record."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
        db_path = tmp.name
    
    try:
        manager = SQLiteManager(db_path=db_path)
        user = manager.create_user("testuser", "password123")
        
        audit_id = manager.insert_audit(
            user_hash=user.user_hash,
            project_name="Test Project",
            spec="Test specification",
            report_md="# Test Report",
            model_used="gemini:gemini-2.5-flash",
        )
        
        assert audit_id > 0
    finally:
        os.unlink(db_path)


def test_database_manager_list_audits():
    """Test listing audit records."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
        db_path = tmp.name
    
    try:
        manager = SQLiteManager(db_path=db_path)
        user = manager.create_user("testuser", "password123")
        
        manager.insert_audit(
            user_hash=user.user_hash,
            project_name="Project 1",
            spec="Spec 1",
            report_md="# Report 1",
            model_used="gemini:gemini-2.5-flash",
        )
        
        manager.insert_audit(
            user_hash=user.user_hash,
            project_name="Project 2",
            spec="Spec 2",
            report_md="# Report 2",
            model_used="groq:llama-3.3-70b-versatile",
        )
        
        audits = manager.list_audits(user_hash=user.user_hash, limit=10)
        assert len(audits) == 2
        assert audits[0]["project_name"] == "Project 2"  # Most recent first
    finally:
        os.unlink(db_path)


def test_database_manager_get_audit():
    """Test getting a specific audit record."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
        db_path = tmp.name
    
    try:
        manager = SQLiteManager(db_path=db_path)
        user = manager.create_user("testuser", "password123")
        
        audit_id = manager.insert_audit(
            user_hash=user.user_hash,
            project_name="Test Project",
            spec="Test specification",
            report_md="# Test Report",
            model_used="gemini:gemini-2.5-flash",
        )
        
        audit = manager.get_audit(user_hash=user.user_hash, audit_id=audit_id)
        assert isinstance(audit, AuditRecord)
        assert audit.id == audit_id
        assert audit.project_name == "Test Project"
    finally:
        os.unlink(db_path)


def test_database_manager_user_isolation():
    """Test that users cannot see each other's audits."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
        db_path = tmp.name
    
    try:
        manager = SQLiteManager(db_path=db_path)
        user1 = manager.create_user("user1", "password123")
        user2 = manager.create_user("user2", "password123")
        
        manager.insert_audit(
            user_hash=user1.user_hash,
            project_name="User1 Project",
            spec="Spec",
            report_md="# Report",
            model_used="gemini:gemini-2.5-flash",
        )
        
        # User2 should not see User1's audits
        audits = manager.list_audits(user_hash=user2.user_hash, limit=10)
        assert len(audits) == 0
    finally:
        os.unlink(db_path)

from __future__ import annotations

import hashlib
import os
import secrets
import sqlite3
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SCHEMA_SQL = """
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT NOT NULL UNIQUE,
  user_hash TEXT NOT NULL UNIQUE,
  password_salt TEXT NOT NULL,
  password_hash TEXT NOT NULL,
  created_at INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS audits (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_hash TEXT NOT NULL,
  project_name TEXT NOT NULL,
  spec TEXT NOT NULL,
  report_md TEXT NOT NULL,
  model_used TEXT NOT NULL,
  created_at INTEGER NOT NULL,
  FOREIGN KEY(user_hash) REFERENCES users(user_hash) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS schema_migrations (
  version INTEGER PRIMARY KEY,
  applied_at INTEGER NOT NULL
);
"""


def _now() -> int:
    return int(time.time())


def _sha256_hex(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _pbkdf2_sha256(password: str, salt: str, rounds: int = 210_000) -> str:
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), rounds)
    return dk.hex()


@dataclass(frozen=True)
class UserPublic:
    username: str
    user_hash: str
    created_at: int


@dataclass(frozen=True)
class AuditRecord:
    id: int
    user_hash: str
    project_name: str
    spec: str
    report_md: str
    model_used: str
    created_at: int


class SQLiteManager:
    """
    SQLite State Controller (hashing, matching, isolating histories).

    - Uses per-username stable user_hash for row scoping.
    - Stores PBKDF2 password hash (never plaintext).
    """

    def __init__(self, db_path: str | os.PathLike[str] | None = None) -> None:
        base = Path(db_path) if db_path else Path(__file__).resolve().parents[1] / "sentineliq.db"
        base.parent.mkdir(parents=True, exist_ok=True)
        self._db_path = str(base)
        self._lock = threading.Lock()
        self._init_db()

    @property
    def db_path(self) -> str:
        return self._db_path

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._lock:
            conn = self._connect()
            try:
                conn.executescript(SCHEMA_SQL)
                conn.commit()
                # Initialize migration tracking
                self._run_migrations(conn)
            finally:
                conn.close()

    def _run_migrations(self, conn: sqlite3.Connection) -> None:
        """Run database migrations."""
        # Check if migrations table exists and has entries
        cursor = conn.execute("SELECT MAX(version) FROM schema_migrations")
        result = cursor.fetchone()
        current_version = result[0] if result and result[0] is not None else 0
        
        # Apply migrations sequentially
        migrations = self._get_migrations()
        for version, migration_sql in migrations:
            if version > current_version:
                try:
                    conn.executescript(migration_sql)
                    conn.execute(
                        "INSERT INTO schema_migrations (version, applied_at) VALUES (?, ?)",
                        (version, _now())
                    )
                    conn.commit()
                except Exception as e:
                    conn.rollback()
                    raise RuntimeError(f"Migration {version} failed: {e}")

    def _get_migrations(self) -> list[tuple[int, str]]:
        """
        Return list of (version, migration_sql) tuples.
        Add new migrations here as needed.
        """
        return [
            # Example migration structure:
            # (1, "ALTER TABLE audits ADD COLUMN status TEXT DEFAULT 'completed';"),
        ]

    def create_user(self, username: str, password: str) -> UserPublic:
        username = username.strip()
        if not username:
            raise ValueError("Username required.")
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters.")

        # Stable user_hash keyed off username + pepper-ish random salt stored per user.
        # We also store password hash separately.
        salt = secrets.token_hex(16)
        password_hash = _pbkdf2_sha256(password, salt)
        user_hash = _sha256_hex(f"sentineliq::{username.lower()}::{salt}")

        with self._lock:
            conn = self._connect()
            try:
                conn.execute(
                    "INSERT INTO users (username, user_hash, password_salt, password_hash, created_at) VALUES (?, ?, ?, ?, ?)",
                    (username, user_hash, salt, password_hash, _now()),
                )
                conn.commit()
            finally:
                conn.close()

        return self.get_user(username)

    def get_user(self, username: str) -> UserPublic:
        with self._lock:
            conn = self._connect()
            try:
                row = conn.execute(
                    "SELECT username, user_hash, created_at FROM users WHERE username = ?",
                    (username,),
                ).fetchone()
            finally:
                conn.close()
        if not row:
            raise KeyError("User not found.")
        return UserPublic(username=row["username"], user_hash=row["user_hash"], created_at=row["created_at"])

    def authenticate(self, username: str, password: str) -> UserPublic:
        with self._lock:
            conn = self._connect()
            try:
                row = conn.execute(
                    "SELECT username, user_hash, password_salt, password_hash, created_at FROM users WHERE username = ?",
                    (username,),
                ).fetchone()
            finally:
                conn.close()
        if not row:
            raise PermissionError("Invalid username or password.")

        expected = row["password_hash"]
        salt = row["password_salt"]
        actual = _pbkdf2_sha256(password, salt)
        if not secrets.compare_digest(expected, actual):
            raise PermissionError("Invalid username or password.")

        return UserPublic(username=row["username"], user_hash=row["user_hash"], created_at=row["created_at"])

    def insert_audit(
        self,
        *,
        user_hash: str,
        project_name: str,
        spec: str,
        report_md: str,
        model_used: str,
    ) -> int:
        with self._lock:
            conn = self._connect()
            try:
                cur = conn.execute(
                    "INSERT INTO audits (user_hash, project_name, spec, report_md, model_used, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (user_hash, project_name, spec, report_md, model_used, _now()),
                )
                conn.commit()
                return int(cur.lastrowid)
            finally:
                conn.close()

    def list_audits(self, *, user_hash: str, limit: int = 50) -> list[dict[str, Any]]:
        limit = max(1, min(int(limit), 200))
        with self._lock:
            conn = self._connect()
            try:
                rows = conn.execute(
                    "SELECT id, project_name, model_used, created_at FROM audits WHERE user_hash = ? ORDER BY id DESC LIMIT ?",
                    (user_hash, limit),
                ).fetchall()
            finally:
                conn.close()
        return [
            {
                "id": int(r["id"]),
                "project_name": r["project_name"],
                "model_used": r["model_used"],
                "created_at": int(r["created_at"]),
            }
            for r in rows
        ]

    def get_audit(self, *, user_hash: str, audit_id: int) -> AuditRecord:
        with self._lock:
            conn = self._connect()
            try:
                row = conn.execute(
                    "SELECT id, user_hash, project_name, spec, report_md, model_used, created_at FROM audits WHERE user_hash = ? AND id = ?",
                    (user_hash, int(audit_id)),
                ).fetchone()
            finally:
                conn.close()
        if not row:
            raise KeyError("Audit not found.")
        return AuditRecord(
            id=int(row["id"]),
            user_hash=row["user_hash"],
            project_name=row["project_name"],
            spec=row["spec"],
            report_md=row["report_md"],
            model_used=row["model_used"],
            created_at=int(row["created_at"]),
        )


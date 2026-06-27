# backend-fastapi/main.py
from __future__ import annotations

import os
import re  # FIXED: Added missing regular expression library import
import sqlite3
from datetime import datetime, timedelta, timezone
from typing import Any

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from pydantic import BaseModel, Field

from core import Orchestrator
from core.logging_config import setup_logging
from core.error_handler import sentinel_error_handler
from core.rate_limiter import rate_limit_middleware
from database.manager import SQLiteManager, UserPublic

load_dotenv()

# Setup structured logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
setup_logging(LOG_LEVEL)

app = FastAPI(title="SentinelIQ API", version="1.0.0")

FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "480"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN, "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add rate limiting middleware
app.middleware("http")(rate_limit_middleware)

# Add global error handler
app.exception_handler(Exception)(sentinel_error_handler)

db = SQLiteManager()
orchestrator = Orchestrator()
security = HTTPBearer()

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict[str, Any]:
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_hash: str = payload.get("user_hash")
        if username is None or user_hash is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return {"username": username, "user_hash": user_hash}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user(token_data: dict[str, Any] = Depends(verify_token)) -> UserPublic:
    try:
        user = db.get_user(token_data["username"])
        if user.user_hash != token_data["user_hash"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User hash mismatch",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

class SignUpRequest(BaseModel):
    username: str = Field(..., min_length=2, max_length=64)
    password: str = Field(..., min_length=8, max_length=256)

class SignInRequest(BaseModel):
    username: str = Field(..., min_length=2, max_length=64)
    password: str = Field(..., min_length=8, max_length=256)

class AuthResponse(BaseModel):
    username: str
    user_hash: str
    created_at: int
    access_token: str
    token_type: str = "bearer"

class AuditRunRequest(BaseModel):
    project_name: str = Field(..., min_length=2, max_length=120)
    project_spec: str = Field(..., min_length=10, max_length=20000)

class AuditRunResponse(BaseModel):
    audit_id: int
    project_name: str
    report_md: str
    model_used: str
    created_at: int
    metrics: dict[str, int] = Field(default_factory=dict)

@app.get("/health")
def health() -> dict[str, Any]:
    """Health check endpoint for monitoring and load balancers."""
    try:
        db._connect().close()
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "components": {
            "database": db_status,
            "llm_primary": "configured" if os.getenv("GEMINI_API_KEY") else "missing",
            "llm_failover": "configured" if os.getenv("GROQ_API_KEY") else "missing",
        },
    }

@app.post("/auth/signup", response_model=AuthResponse)
def signup(req: SignUpRequest) -> AuthResponse:
    try:
        user = db.create_user(req.username, req.password)
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username, "user_hash": user.user_hash}, expires_delta=access_token_expires
        )
        return AuthResponse(
            username=user.username, user_hash=user.user_hash, created_at=user.created_at, access_token=access_token
        )
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="Username already exists.")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/auth/signin", response_model=AuthResponse)
def signin(req: SignInRequest) -> AuthResponse:
    try:
        user = db.authenticate(req.username, req.password)
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username, "user_hash": user.user_hash}, expires_delta=access_token_expires
        )
        return AuthResponse(
            username=user.username, user_hash=user.user_hash, created_at=user.created_at, access_token=access_token
        )
    except PermissionError:
        raise HTTPException(status_code=401, detail="Invalid username or password.")

@app.post("/audit/run", response_model=AuditRunResponse)
def run_audit(req: AuditRunRequest, current_user: UserPublic = Depends(get_current_user)) -> AuditRunResponse:
    try:
        result = orchestrator.run_audit(project_name=req.project_name, project_spec=req.project_spec)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audit failed: {e}")

    audit_id = db.insert_audit(
        user_hash=current_user.user_hash,
        project_name=req.project_name,
        spec=req.project_spec,
        report_md=result.report_md,
        model_used=result.model_used,
    )

    record = db.get_audit(user_hash=current_user.user_hash, audit_id=audit_id)
    raw_text = record.report_md
    
    def parse_score(metric_name: str) -> int:
        match = re.search(f"{metric_name}:\s*(\d+)\s*/\s*10", raw_text, re.IGNORECASE)
        return int(match.group(1)) * 10 if match else 50

    metrics_scorecard = {
        "architecture": parse_score("Architecture"),
        "security": parse_score("Security"),
        "compliance": parse_score("Compliance"),
        "req_quality": parse_score("Requirements\s*Quality")
    }

    return AuditRunResponse(
        audit_id=record.id,
        project_name=record.project_name,
        report_md=record.report_md,
        model_used=record.model_used,
        created_at=record.created_at,
        metrics=metrics_scorecard
    )

@app.get("/audit/history")
def audit_history(limit: int = 50, current_user: UserPublic = Depends(get_current_user)) -> dict[str, Any]:
    return {"items": db.list_audits(user_hash=current_user.user_hash, limit=limit)}

@app.get("/audit/{audit_id}")
def audit_get(audit_id: int, current_user: UserPublic = Depends(get_current_user)) -> dict[str, Any]:
    try:
        record = db.get_audit(user_hash=current_user.user_hash, audit_id=audit_id)
        raw_text = record.report_md
        
        def parse_score(metric_name: str) -> int:
            match = re.search(f"{metric_name}:\s*(\d+)\s*/\s*10", raw_text, re.IGNORECASE)
            return int(match.group(1)) * 10 if match else 50

        metrics_scorecard = {
            "architecture": parse_score("Architecture"),
            "security": parse_score("Security"),
            "compliance": parse_score("Compliance"),
            "req_quality": parse_score("Requirements\s*Quality")
        }
        
        return {
            "id": record.id,
            "project_name": record.project_name,
            "report_md": record.report_md,
            "model_used": record.model_used,
            "created_at": record.created_at,
            "metrics": metrics_scorecard  # Added metrics parser to history retrieval endpoint as well
        }
    except KeyError:
        raise HTTPException(status_code=404, detail="Audit not found.")
# SentinelIQ Enterprise - Architecture Documentation

## System Overview

SentinelIQ Enterprise is a production-grade, multi-agent AI architecture review platform designed for enterprise software teams. The system follows a decoupled microservices architecture with clear separation between the frontend React application and the FastAPI backend AI orchestration engine.

## Architecture Principles

1. **Separation of Concerns**: Frontend UI and Backend AI engine are completely decoupled
2. **Stateless Authentication**: JWT-based authentication with no session storage
3. **Data Privacy**: User data isolation using cryptographic hashing
4. **Resilience**: Multi-LLM failover for high availability
5. **Observability**: Structured logging and health checks for monitoring

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend Layer                          │
│  React 18 + Vite + Tailwind CSS + React Markdown            │
│  Port: 3000                                                 │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTPS + JWT Bearer Token
                       │ CORS-Protected
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    API Gateway Layer                         │
│  FastAPI + Uvicorn + Rate Limiting + Error Handling         │
│  Port: 8000                                                  │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        ▼                             ▼
┌──────────────────┐        ┌──────────────────┐
│   AI Engine      │        │  Data Layer      │
│  5-Agent Pipeline│        │  SQLite + WAL     │
│  - Requirements  │        │  User Isolation  │
│  - Validation    │        │  Audit History   │
│  - Planning      │        │  Migrations      │
│  - Risk Analysis │        └──────────────────┘
│  - Executive     │
│  Insights        │
└────────┬─────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐ ┌────────┐
│ Gemini │ │  Groq  │
│ 2.5    │ │ Llama  │
│ Flash  │ │ 3.3    │
└────────┘ └────────┘
```

## Component Details

### Frontend (React)

- **Framework**: React 18 with Vite for fast development
- **Styling**: Custom matte-dark theme inspired by GroqCloud
- **Markdown Rendering**: React Markdown with remark-gfm for GitHub-flavored markdown
- **State Management**: React hooks (useState, useEffect, useRef)
- **API Communication**: Fetch API with JWT Bearer authentication
- **Features**:
  - User authentication (signup/signin)
  - Audit execution with real-time phase tracking
  - Audit history management
  - Markdown report rendering and download
  - Error handling and status display

### Backend (FastAPI)

- **Framework**: FastAPI with Uvicorn ASGI server
- **Authentication**: JWT (JSON Web Tokens) with PBKDF2 password hashing
- **Database**: SQLite with WAL mode for performance
- **AI Orchestration**: 5-agent pipeline with intelligent failover
- **Features**:
  - RESTful API endpoints
  - JWT-based authentication
  - Rate limiting (60 requests/minute)
  - Structured logging
  - Central error handling
  - Health checks
  - Database migrations

### AI Orchestration Engine

The core AI engine consists of 5 specialized agents:

1. **Requirements Analyst**: Extracts concrete requirements with confidence scoring
2. **Validation Engineer**: Validates for gaps and contradictions
3. **Delivery Planner**: Creates implementation plans
4. **Risk & Security Officer**: Identifies security and operational risks
5. **Executive Insights Synthesizer**: Generates executive summaries with scores

**Key Features**:
- Cross-agent validation to detect contradictions
- Confidence scoring for all findings (0-100%)
- Requirement traceability (Requirement → Validation → Risk → Recommendation)
- Severity classification (Critical/High/Medium/Low/Informational)
- Automatic architecture artifact generation
- LLM failover (Gemini → Groq) on rate limits

### Data Layer

**SQLite Database Schema**:

```sql
users (
  id INTEGER PRIMARY KEY,
  username TEXT UNIQUE,
  user_hash TEXT UNIQUE,
  password_salt TEXT,
  password_hash TEXT,
  created_at INTEGER
)

audits (
  id INTEGER PRIMARY KEY,
  user_hash TEXT,
  project_name TEXT,
  spec TEXT,
  report_md TEXT,
  model_used TEXT,
  created_at INTEGER,
  FOREIGN KEY(user_hash) REFERENCES users(user_hash)
)

schema_migrations (
  version INTEGER PRIMARY KEY,
  applied_at INTEGER
)
```

**Security Features**:
- PBKDF2 password hashing with 210,000 rounds
- Per-user cryptographic hash for data isolation
- Parameterized queries to prevent SQL injection
- WAL mode for concurrent access

## Security Architecture

### Authentication Flow

1. User submits username/password
2. Server validates credentials using PBKDF2 hash comparison
3. Server generates JWT token with 8-hour expiration
4. Client stores token and includes in Authorization header
5. Server validates token on each protected request

### Data Isolation

- Each user has a unique `user_hash` generated from username + random salt
- All audit records are scoped by `user_hash`
- Database queries always include `user_hash` filter
- No cross-user data access possible

### API Security

- CORS configured to specific origins only
- Rate limiting (60 requests/minute per user)
- JWT Bearer token required for protected endpoints
- No secrets in code (environment variables only)
- Consistent error handling without stack traces

## Deployment Architecture

### Development Environment

```yaml
Frontend: React dev server (port 3000)
Backend: FastAPI/Uvicorn (port 8000)
Database: SQLite file
```

### Production Recommendations

```yaml
Frontend:
  - Nginx reverse proxy
  - Static file serving
  - SSL/TLS termination
  - CDN for assets

Backend:
  - Gunicorn/Uvicorn workers
  - Docker containerization
  - Kubernetes orchestration
  - Horizontal pod autoscaling

Database:
  - PostgreSQL migration (from SQLite)
  - Read replicas for scaling
  - Automated backups
  - Connection pooling

Monitoring:
  - Structured logging aggregation
  - Metrics collection (Prometheus)
  - Alerting (PagerDuty)
  - Distributed tracing
```

## Scalability Considerations

### Current Limitations

- SQLite is single-node (migration to PostgreSQL recommended for production)
- In-memory rate limiting (Redis recommended for distributed systems)
- Single-process AI orchestration (queue-based system for high throughput)

### Scaling Strategy

1. **Horizontal Scaling**: Deploy multiple backend instances behind load balancer
2. **Database Migration**: Move to PostgreSQL for better concurrency
3. **Caching Layer**: Add Redis for rate limiting and session management
4. **Queue System**: Implement Celery/RabbitMQ for background AI tasks
5. **CDN**: Serve static assets via CDN for better performance

## Monitoring & Observability

### Health Checks

- `/health` endpoint returns component status
- Database connectivity check
- LLM API configuration check
- Timestamp for monitoring

### Logging

- Structured JSON logging
- Log levels: DEBUG, INFO, WARNING, ERROR
- Request/response logging
- Error stack traces
- Performance metrics

### Metrics to Track

- Request rate and latency
- Error rate by endpoint
- LLM API call success/failure
- Rate limit violations
- Database query performance
- User registration/activation rates

## Technology Stack Summary

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Frontend | React 18, Vite, Tailwind CSS | UI Framework |
| Backend | FastAPI, Uvicorn, Pydantic | API Framework |
| Authentication | JWT, PBKDF2 | Security |
| Database | SQLite (WAL mode) | Data Storage |
| AI Models | Gemini 2.5 Flash, Llama 3.3 | LLM Providers |
| Testing | Pytest, HTTPX | Test Framework |
| Deployment | Docker, GitHub Actions | CI/CD |

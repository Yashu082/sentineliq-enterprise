# SentinelIQ Enterprise - System Design Document

## Overview

SentinelIQ Enterprise is an AI-powered architecture review platform that uses a multi-agent orchestration system to analyze Product Requirement Documents (PRDs) and provide enterprise-grade insights, risk assessments, and architectural recommendations.

## Design Goals

1. **Enterprise-Grade Output**: Produce reports suitable for CTOs and senior architects
2. **Reliability**: Multi-LLM failover for high availability
3. **Security**: User data isolation and secure authentication
4. **Scalability**: Microservices architecture for horizontal scaling
5. **Observability**: Structured logging and monitoring hooks

## System Components

### 1. Frontend Application (React)

**Purpose**: User interface for submitting PRDs and viewing audit results

**Key Features**:
- User authentication (signup/signin)
- PRD submission form
- Real-time audit progress tracking
- Markdown report rendering
- Audit history management
- Report download functionality

**Technology Stack**:
- React 18 with hooks
- Vite for fast development
- React Markdown for report rendering
- Custom matte-dark theme

**State Management**:
- Local component state (useState, useEffect)
- No global state management (Redux not needed for current scope)

**API Communication**:
- Fetch API with JWT Bearer authentication
- Error handling with user-friendly messages
- Loading states for async operations

### 2. Backend API (FastAPI)

**Purpose**: RESTful API for authentication, audit execution, and data management

**Key Features**:
- JWT-based authentication
- Rate limiting (60 req/min)
- Structured logging
- Central error handling
- Health checks
- Database migrations

**Technology Stack**:
- FastAPI with Uvicorn
- Pydantic for data validation
- SQLite with WAL mode
- JWT for authentication

**API Endpoints**:
- `POST /auth/signup` - User registration
- `POST /auth/signin` - User authentication
- `POST /audit/run` - Execute audit
- `GET /audit/history` - List user's audits
- `GET /audit/{id}` - Get specific audit
- `GET /health` - Health check

### 3. AI Orchestration Engine

**Purpose**: Coordinate 5 specialized AI agents to analyze PRDs

**Architecture**:
```
User Input (PRD)
    ↓
Shared Context (PRD + Compliance Benchmarks)
    ↓
┌─────────────────────────────────────┐
│  Sequential Agent Pipeline         │
│  ┌───────────────────────────────┐ │
│  │ 1. Requirements Analyst       │ │
│  │    - Extract requirements      │ │
│  │    - Confidence scoring       │ │
│  │    - Severity classification  │ │
│  └───────────────────────────────┘ │
│              ↓                     │
│  ┌───────────────────────────────┐ │
│  │ 2. Validation Engineer        │ │
│  │    - Validate gaps            │ │
│  │    - Detect contradictions     │ │
│  │    - Link to requirements     │ │
│  └───────────────────────────────┘ │
│              ↓                     │
│  ┌───────────────────────────────┐ │
│  │ 3. Delivery Planner           │ │
│  │    - Implementation plan      │ │
│  │    - Architecture suggestions │ │
│  │    - Milestones               │ │
│  └───────────────────────────────┘ │
│              ↓                     │
│  ┌───────────────────────────────┐ │
│  │ 4. Risk & Security Officer    │ │
│  │    - Security risks           │ │
│  │    - Compliance issues        │ │
│  │    - Mitigations              │ │
│  └───────────────────────────────┘ │
│              ↓                     │
│  ┌───────────────────────────────┐ │
│  │ 5. Executive Insights         │ │
│  │    - Cross-agent validation   │ │
│  │    - Score aggregation        │ │
│  │    - Decision (GO/BLOCKED)    │ │
│  └───────────────────────────────┘ │
└─────────────────────────────────────┘
    ↓
Report Generation
    ↓
Architecture Artifacts
    ↓
Final Report
```

**Agent Communication**:
- Each agent sees previous agent outputs
- Context is stitched together with phase history
- Cross-agent validation before executive summary
- Contradictions detected and resolved

**LLM Failover Strategy**:
```
Primary LLM (Gemini 2.5 Flash)
    ↓
429/503 Error Detected?
    ↓ Yes
Failover to Groq (Llama 3.3)
    ↓
Continue with same response schema
```

### 4. Cross-Agent Validation System

**Purpose**: Detect contradictions between agent outputs and resolve conflicts

**Implementation**:
- Pattern-based contradiction detection
- Semantic analysis for inconsistencies
- Resolution suggestions
- Integration with Executive Insights agent

**Contradiction Types**:
- Direct contradiction (must vs must not)
- Inconsistency (required vs optional)
- Gap (missing information)

### 5. Traceability System

**Purpose**: Ensure every recommendation traces back to requirements

**Traceability Chain**:
```
Requirement [REQ-001]
    ↓
Validation Finding [VAL-001]
    ↓
Risk Finding [RISK-001]
    ↓
Recommendation [PLAN-001]
```

**Implementation**:
- Regex-based ID extraction from agent outputs
- Link validation based on requirement references
- Matrix generation for reports

### 6. Architecture Generator

**Purpose**: Automatically generate architecture artifacts from PRDs

**Artifacts Generated**:
1. Mermaid Architecture Diagram
2. Component Diagram
3. Data Flow Diagram
4. API Inventory
5. Database Entity Suggestions
6. Deployment Architecture

**Implementation**:
- LLM-powered generation
- Structured prompts for consistency
- Integration into final report

### 7. Database Layer

**Purpose**: Persistent storage for users and audit records

**Schema Design**:
```sql
users (
  id INTEGER PRIMARY KEY,
  username TEXT UNIQUE,
  user_hash TEXT UNIQUE,  -- Cryptographic hash for isolation
  password_salt TEXT,
  password_hash TEXT,    -- PBKDF2 with 210,000 rounds
  created_at INTEGER
)

audits (
  id INTEGER PRIMARY KEY,
  user_hash TEXT,         -- Foreign key to users
  project_name TEXT,
  spec TEXT,              -- Original PRD
  report_md TEXT,         -- Generated report
  model_used TEXT,        -- LLM model used
  created_at INTEGER,
  FOREIGN KEY(user_hash) REFERENCES users(user_hash)
)

schema_migrations (
  version INTEGER PRIMARY KEY,
  applied_at INTEGER
)
```

**Security Features**:
- PBKDF2 password hashing (210,000 rounds)
- Per-user cryptographic hash for data isolation
- Parameterized queries (SQL injection prevention)
- WAL mode for concurrent access

### 8. Production Hardening Layer

**Components**:

**Structured Logging**:
- JSON-formatted logs
- Timestamp, level, logger, message
- Module, function, line number
- Exception tracking

**Rate Limiting**:
- Token bucket algorithm
- 60 requests/minute per user
- In-memory storage (Redis for distributed)
- Response headers for limits

**Central Error Handling**:
- Custom exception hierarchy
- Consistent error responses
- Structured error logging
- User-friendly messages

**Retry Logic**:
- Exponential backoff
- Configurable attempts
- Configurable delays
- Specific exception handling

**Health Checks**:
- Database connectivity
- LLM API configuration
- Component status reporting
- Timestamp for monitoring

## Data Flow

### Audit Execution Flow

```
1. User submits PRD via Frontend
   ↓
2. Frontend sends POST /audit/run with JWT token
   ↓
3. Backend validates token and user
   ↓
4. Backend calls Orchestrator.run_audit()
   ↓
5. Orchestrator builds shared context
   ↓
6. Sequential agent execution:
   - Requirements Analyst
   - Validation Engineer
   - Delivery Planner
   - Risk & Security Officer
   ↓
7. Cross-agent validation
   ↓
8. Executive Insights synthesis
   ↓
9. Traceability matrix generation
   ↓
10. Architecture artifact generation
    ↓
11. Report assembly
    ↓
12. Database storage
    ↓
13. Return report to Frontend
    ↓
14. Frontend renders markdown report
```

### Authentication Flow

```
1. User submits credentials
   ↓
2. Backend hashes password with PBKDF2
   ↓
3. Backend compares with stored hash
   ↓
4. If valid, generate JWT token
   ↓
5. Token includes: username, user_hash, exp
   ↓
6. Return token to client
   ↓
7. Client stores token
   ↓
8. Client includes token in Authorization header
   ↓
9. Backend validates token signature and expiration
   ↓
10. Backend extracts user_hash for data scoping
```

## Security Architecture

### Threat Model

**Potential Threats**:
1. Credential theft
2. SQL injection
3. XSS attacks
4. CSRF attacks
5. Rate limit abuse
6. Data leakage between users
7. LLM API key exposure

**Mitigations**:

1. **Credential Theft**:
   - PBKDF2 with 210,000 rounds
   - JWT tokens with 8-hour expiration
   - HTTPS in production

2. **SQL Injection**:
   - Parameterized queries
   - ORM (SQLAlchemy for future PostgreSQL migration)

3. **XSS Attacks**:
   - React's built-in XSS protection
   - React Markdown sanitization

4. **CSRF Attacks**:
   - JWT Bearer authentication (stateless)
   - SameSite cookie attributes (if using cookies)

5. **Rate Limit Abuse**:
   - Per-user rate limiting
   - Configurable limits
   - Distributed limiting with Redis

6. **Data Leakage**:
   - Per-user cryptographic hashing
   - All queries scoped by user_hash
   - No cross-user data access

7. **API Key Exposure**:
   - Environment variables only
   - Never in code or logs
   - Secret management in production

## Performance Considerations

### Current Performance Characteristics

- **Audit Execution**: 30-60 seconds (5 agents × LLM latency)
- **Database Queries**: <100ms (SQLite)
- **API Response**: <500ms (non-audit endpoints)
- **Frontend Rendering**: <1s (markdown)

### Bottlenecks

1. **LLM API Latency**: Sequential agent execution
2. **SQLite Concurrency**: Single-node database
3. **Rate Limiting**: In-memory storage

### Optimization Strategies

1. **Parallel Agent Execution**:
   - Run independent agents in parallel
   - Merge results in executive summary
   - Estimated 40% reduction in execution time

2. **Database Migration**:
   - Move to PostgreSQL for better concurrency
   - Connection pooling
   - Read replicas for scaling

3. **Caching Layer**:
   - Redis for rate limiting
   - Cache frequently accessed data
   - Session storage

4. **Queue System**:
   - Background task processing
   - Celery + RabbitMQ
   - Async audit execution

## Scalability Architecture

### Horizontal Scaling

```
┌─────────────────────────────────────┐
│         Load Balancer               │
│  (Nginx, HAProxy, AWS ALB)         │
└──────────────┬──────────────────────┘
               │
       ┌───────┴───────┐
       ▼               ▼
┌──────────────┐ ┌──────────────┐
│  Backend 1   │ │  Backend 2   │
│  (FastAPI)   │ │  (FastAPI)   │
└──────┬───────┘ └──────┬───────┘
       │                 │
       └────────┬────────┘
                ▼
       ┌────────────────┐
       │  PostgreSQL    │
       │  (Primary)     │
       └────────┬───────┘
                │
       ┌────────┴────────┐
       ▼                 ▼
┌──────────────┐ ┌──────────────┐
│  Read Replica│ │  Read Replica│
└──────────────┘ └──────────────┘
```

### Vertical Scaling

- Increase CPU cores for LLM parallelization
- Add RAM for caching
- Use SSD for database storage

## Monitoring & Observability

### Metrics to Track

1. **System Metrics**:
   - CPU usage
   - Memory usage
   - Disk I/O
   - Network I/O

2. **Application Metrics**:
   - Request rate
   - Response time
   - Error rate
   - Active users

3. **Business Metrics**:
   - Audits per day
   - User registrations
   - LLM API costs
   - Average report size

### Logging Strategy

**Log Levels**:
- DEBUG: Detailed debugging information
- INFO: General informational messages
- WARNING: Warning messages
- ERROR: Error messages
- CRITICAL: Critical errors

**Log Format**:
```json
{
  "timestamp": "2024-01-01T00:00:00.000Z",
  "level": "INFO",
  "logger": "main",
  "message": "Audit started",
  "module": "main",
  "function": "run_audit",
  "line": 42,
  "extra": {
    "user_hash": "abc123",
    "project_name": "My Project"
  }
}
```

### Alerting

**Critical Alerts**:
- Database connection failures
- LLM API rate limits exceeded
- Error rate > 5%
- Response time > 10s

**Warning Alerts**:
- High memory usage (>80%)
- High CPU usage (>80%)
- Rate limit violations

## Future Enhancements

### Planned Features

1. **Real-time WebSocket Updates**:
   - Live audit progress
   - Push notifications

2. **Collaboration Features**:
   - Shared audits
   - Comments and annotations
   - Team workspaces

3. **Advanced Analytics**:
   - Trend analysis
   - Comparison reports
   - Custom dashboards

4. **Integration Ecosystem**:
   - Jira integration
   - GitHub integration
   - Slack notifications

5. **Multi-tenant Support**:
   - Organization accounts
   - Team management
   - Billing integration

### Technical Debt

1. **Database Migration**: SQLite → PostgreSQL
2. **Caching Layer**: Add Redis
3. **Queue System**: Add Celery + RabbitMQ
4. **Frontend Framework**: Consider Next.js for SSR
5. **Testing**: Increase coverage to 90%+

## Conclusion

SentinelIQ Enterprise is designed as a production-grade, enterprise AI architecture review platform. The system prioritizes security, reliability, and scalability while maintaining a clean, maintainable codebase. The modular architecture allows for easy enhancement and adaptation to future requirements.

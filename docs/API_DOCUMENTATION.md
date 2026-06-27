# SentinelIQ Enterprise - API Documentation

## Base URL

```
Development: http://localhost:8000
Production: https://api.your-domain.com
```

## Authentication

Most endpoints require JWT Bearer authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

### Authentication Flow

1. **Sign Up**: Create a new account
2. **Sign In**: Authenticate and receive JWT token
3. **Use Token**: Include token in subsequent requests

## Endpoints

### Health Check

#### GET /health

Check system health and component status.

**Authentication**: None required

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00.000Z",
  "components": {
    "database": "healthy",
    "llm_primary": "configured",
    "llm_failover": "configured"
  }
}
```

**Status Codes**:
- `200 OK`: System is healthy
- `503 Service Unavailable`: System is degraded

---

### Authentication

#### POST /auth/signup

Create a new user account.

**Authentication**: None required

**Request Body**:
```json
{
  "username": "string (2-64 characters)",
  "password": "string (8-256 characters)"
}
```

**Response**:
```json
{
  "username": "string",
  "user_hash": "string",
  "created_at": 1234567890,
  "access_token": "string",
  "token_type": "bearer"
}
```

**Status Codes**:
- `200 OK`: User created successfully
- `400 Bad Request`: Invalid input (password too short, etc.)
- `409 Conflict`: Username already exists

**Example**:
```bash
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "securepassword123"}'
```

---

#### POST /auth/signin

Authenticate and receive JWT token.

**Authentication**: None required

**Request Body**:
```json
{
  "username": "string (2-64 characters)",
  "password": "string (8-256 characters)"
}
```

**Response**:
```json
{
  "username": "string",
  "user_hash": "string",
  "created_at": 1234567890,
  "access_token": "string",
  "token_type": "bearer"
}
```

**Status Codes**:
- `200 OK`: Authentication successful
- `401 Unauthorized`: Invalid credentials

**Example**:
```bash
curl -X POST http://localhost:8000/auth/signin \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "securepassword123"}'
```

---

### Audit Operations

#### POST /audit/run

Execute a full architecture audit using the 5-agent pipeline.

**Authentication**: Required (JWT Bearer token)

**Request Body**:
```json
{
  "project_name": "string (2-120 characters)",
  "project_spec": "string (10-20000 characters)"
}
```

**Response**:
```json
{
  "audit_id": 123,
  "project_name": "string",
  "report_md": "string (markdown formatted report)",
  "model_used": "string (e.g., 'gemini:gemini-2.5-flash')",
  "created_at": 1234567890
}
```

**Status Codes**:
- `200 OK`: Audit completed successfully
- `401 Unauthorized`: Invalid or missing token
- `500 Internal Server Error`: Audit failed (LLM error, etc.)

**Rate Limiting**: 60 requests per minute per user

**Example**:
```bash
curl -X POST http://localhost:8000/audit/run \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-token>" \
  -d '{
    "project_name": "My Project",
    "project_spec": "A web application with user authentication and data storage..."
  }'
```

**Report Structure**:

The returned `report_md` includes:
1. **Requirements**: Extracted requirements with confidence scores
2. **Validation Checklist**: Validation findings with severity levels
3. **Delivery Plan**: Implementation recommendations
4. **Risks & Mitigations**: Security and operational risks
5. **Executive Insights**: Summary with scores and decision
6. **Requirement Traceability Matrix**: Traceability chain
7. **Architecture Artifacts**: Mermaid diagrams, API inventory, etc.
8. **Provenance**: Model usage per phase

---

#### GET /audit/history

Retrieve the authenticated user's audit history.

**Authentication**: Required (JWT Bearer token)

**Query Parameters**:
- `limit` (optional): Number of records to return (default: 50, max: 200)

**Response**:
```json
{
  "items": [
    {
      "id": 123,
      "project_name": "string",
      "model_used": "string",
      "created_at": 1234567890
    }
  ]
}
```

**Status Codes**:
- `200 OK`: History retrieved successfully
- `401 Unauthorized**: Invalid or missing token

**Example**:
```bash
curl -X GET "http://localhost:8000/audit/history?limit=10" \
  -H "Authorization: Bearer <your-token>"
```

---

#### GET /audit/{audit_id}

Retrieve a specific audit record.

**Authentication**: Required (JWT Bearer token)

**Path Parameters**:
- `audit_id`: Integer ID of the audit

**Response**:
```json
{
  "id": 123,
  "project_name": "string",
  "report_md": "string (markdown formatted report)",
  "model_used": "string",
  "created_at": 1234567890
}
```

**Status Codes**:
- `200 OK`: Audit retrieved successfully
- `401 Unauthorized**: Invalid or missing token
- `404 Not Found**: Audit not found or doesn't belong to user

**Example**:
```bash
curl -X GET http://localhost:8000/audit/123 \
  -H "Authorization: Bearer <your-token>"
```

---

## Error Responses

All endpoints may return error responses in the following format:

```json
{
  "error": "ERROR_CODE",
  "message": "Human-readable error message",
  "details": {}
}
```

### Common Error Codes

- `VALIDATION_ERROR`: Input validation failed
- `AUTHENTICATION_ERROR`: Authentication failed
- `AUTHORIZATION_ERROR`: Authorization failed
- `RATE_LIMIT_ERROR`: Rate limit exceeded
- `LLM_ERROR`: LLM operation failed
- `INTERNAL_ERROR`: Unexpected server error

### Rate Limiting

When rate limits are exceeded, the response includes:

```json
{
  "error": "RATE_LIMIT_ERROR",
  "message": "Rate limit exceeded",
  "details": {
    "remaining": 0,
    "limit": 60
  }
}
```

Response headers include:
- `X-RateLimit-Limit`: Requests per minute limit
- `X-RateLimit-Remaining`: Remaining requests
- `X-RateLimit-Reset`: Unix timestamp when limit resets

---

## Data Models

### UserPublic

```typescript
{
  username: string;
  user_hash: string;
  created_at: number;  // Unix timestamp
}
```

### AuditRecord

```typescript
{
  id: number;
  user_hash: string;
  project_name: string;
  spec: string;
  report_md: string;
  model_used: string;
  created_at: number;  // Unix timestamp
}
```

### ConfidenceScore

```typescript
{
  percentage: number;  // 0-100
  reason: string;
  evidence: string;
}
```

### Severity

Enum values:
- `Critical`
- `High`
- `Medium`
- `Low`
- `Informational`

---

## SDK Examples

### Python

```python
import requests

API_BASE = "http://localhost:8000"

# Sign up
response = requests.post(f"{API_BASE}/auth/signup", json={
    "username": "testuser",
    "password": "securepassword123"
})
token = response.json()["access_token"]

# Run audit
headers = {"Authorization": f"Bearer {token}"}
response = requests.post(f"{API_BASE}/audit/run", 
    headers=headers,
    json={
        "project_name": "My Project",
        "project_spec": "Project specification..."
    }
)
report = response.json()["report_md"]
print(report)
```

### JavaScript

```javascript
const API_BASE = "http://localhost:8000";

// Sign up
const signupResponse = await fetch(`${API_BASE}/auth/signup`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'testuser',
    password: 'securepassword123'
  })
});
const { access_token } = await signupResponse.json();

// Run audit
const auditResponse = await fetch(`${API_BASE}/audit/run`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${access_token}`
  },
  body: JSON.stringify({
    project_name: 'My Project',
    project_spec: 'Project specification...'
  })
});
const { report_md } = await auditResponse.json();
console.log(report_md);
```

---

## Interactive API Documentation

Swagger UI is available at:
```
http://localhost:8000/docs
```

ReDoc is available at:
```
http://localhost:8000/redoc
```

These provide interactive documentation where you can test endpoints directly.

---

## Webhooks (Future)

Planned webhook support for:
- Audit completion notifications
- Error alerts
- Usage reports

---

## Changelog

### v1.0.0
- Initial release
- 5-agent AI pipeline
- JWT authentication
- Cross-agent validation
- Confidence scoring
- Requirement traceability
- Architecture artifact generation
- Rate limiting
- Structured logging
- Health checks

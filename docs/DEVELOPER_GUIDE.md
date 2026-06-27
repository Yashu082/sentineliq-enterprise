# SentinelIQ Enterprise - Developer Guide

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- Git
- API Keys:
  - Google Gemini API Key
  - Groq API Key

### Local Development Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd sentineliq-enterprise
```

2. **Backend Setup**
```bash
cd backend-fastapi
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

3. **Configure Environment Variables**
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

Required environment variables:
```env
GEMINI_API_KEY=your_gemini_api_key
GROQ_API_KEY=your_groq_api_key
SECRET_KEY=your_jwt_secret_key
FRONTEND_ORIGIN=http://localhost:3000
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480
LOG_LEVEL=INFO
```

4. **Frontend Setup**
```bash
cd frontend-react
npm install
```

5. **Run Development Servers**

Backend (Terminal 1):
```bash
cd backend-fastapi
python -m uvicorn main:app --reload --port 8000
```

Frontend (Terminal 2):
```bash
cd frontend-react
npm run dev
```

6. **Access the Application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Project Structure

```
sentineliq-enterprise/
├── backend-fastapi/
│   ├── config/
│   │   └── knowledge_base.py      # Compliance benchmarks
│   ├── core/
│   │   ├── orchestrator.py         # AI pipeline orchestration
│   │   ├── prompts.py             # Agent system prompts
│   │   ├── validation.py          # Cross-agent validation
│   │   ├── architecture_generator.py  # Architecture artifacts
│   │   ├── logging_config.py      # Structured logging
│   │   ├── rate_limiter.py        # Rate limiting
│   │   ├── error_handler.py       # Central error handling
│   │   └── retry.py               # Retry logic with backoff
│   ├── database/
│   │   └── manager.py             # SQLite database manager
│   ├── tests/
│   │   ├── test_api.py            # API endpoint tests
│   │   ├── test_validation.py     # Validation module tests
│   │   ├── test_architecture_generator.py
│   │   ├── test_production_hardening.py
│   │   └── test_database.py       # Database tests
│   ├── main.py                    # FastAPI application entry
│   ├── requirements.txt           # Python dependencies
│   └── .env                       # Environment configuration
├── frontend-react/
│   ├── src/
│   │   ├── App.jsx                # Main React component
│   │   ├── index.jsx              # React entry point
│   │   └── index.css              # Custom styling
│   ├── package.json               # Node dependencies
│   └── vite.config.js             # Vite configuration
├── docs/                          # Documentation
│   ├── ARCHITECTURE.md
│   ├── DEVELOPER_GUIDE.md
│   ├── DEPLOYMENT_GUIDE.md
│   └── API_DOCUMENTATION.md
└── README.md                      # Project overview
```

## Core Modules

### Orchestrator (`core/orchestrator.py`)

The heart of the AI pipeline. Manages the 5-agent execution with failover.

**Key Methods**:
- `run_audit(project_name, project_spec)`: Executes the full audit pipeline
- `_call_with_failover()`: Handles LLM failover from Gemini to Groq
- `_build_traceability()`: Builds requirement traceability matrix

**Usage Example**:
```python
from core import Orchestrator

orchestrator = Orchestrator()
result = orchestrator.run_audit(
    project_name="My Project",
    project_spec="Project specification here..."
)
print(result.report_md)
```

### Validation (`core/validation.py`)

Implements cross-agent validation and traceability.

**Key Classes**:
- `CrossAgentValidator`: Detects contradictions between agent outputs
- `TraceabilityManager`: Manages requirement traceability chain
- `ConfidenceScore`: Represents confidence with percentage, reason, evidence
- `Severity`: Enum for severity levels (Critical/High/Medium/Low/Informational)

**Usage Example**:
```python
from core.validation import CrossAgentValidator, TraceabilityManager

validator = CrossAgentValidator()
contradictions = validator.validate_phases(phase_outputs)

traceability = TraceabilityManager()
traceability.add_requirement("REQ-001", "User authentication required")
traceability.link_validation("REQ-001", "VAL-001", "Validation finding")
```

### Architecture Generator (`core/architecture_generator.py`)

Generates architecture artifacts from project specifications.

**Key Methods**:
- `generate_architecture_artifacts()`: Returns all architecture artifacts
- `_generate_mermaid_architecture()`: Creates Mermaid diagrams
- `_generate_api_inventory()`: Creates API endpoint inventory

### Database Manager (`database/manager.py`)

Manages SQLite database operations with user isolation.

**Key Methods**:
- `create_user(username, password)`: Creates new user with PBKDF2 hashing
- `authenticate(username, password)`: Validates credentials
- `insert_audit()`: Stores audit results
- `list_audits()`: Retrieves user's audit history
- `get_audit()`: Retrieves specific audit record

## Testing

### Running Tests

```bash
# Run all tests
cd backend-fastapi
pytest tests/

# Run specific test file
pytest tests/test_validation.py

# Run with coverage
pytest tests/ --cov=core --cov=database --cov-report=html

# Run with verbose output
pytest tests/ -v
```

### Test Structure

- **Unit Tests**: Test individual modules in isolation
- **Integration Tests**: Test module interactions
- **API Tests**: Test HTTP endpoints
- **Database Tests**: Test database operations with temporary databases

### Writing Tests

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.validation import CrossAgentValidator

def test_cross_agent_validator():
    validator = CrossAgentValidator()
    phase_outputs = {
        "requirements": "System must have auth",
        "validation": "System must not have auth"
    }
    contradictions = validator.validate_phases(phase_outputs)
    assert isinstance(contradictions, list)
```

## API Development

### Adding New Endpoints

1. Define request/response models in `main.py`:
```python
class NewRequest(BaseModel):
    field: str

class NewResponse(BaseModel):
    result: str
```

2. Create the endpoint:
```python
@app.post("/api/new-endpoint", response_model=NewResponse)
def new_endpoint(req: NewRequest, current_user: UserPublic = Depends(get_current_user)):
    # Your logic here
    return NewResponse(result="success")
```

3. Add tests in `tests/test_api.py`:
```python
def test_new_endpoint():
    response = client.post("/api/new-endpoint", json={"field": "value"})
    assert response.status_code == 200
```

## Adding New Agents

1. Define the agent persona in `core/prompts.py`:
```python
PERSONAS["new_agent"] = Persona(
    id="new_agent",
    name="New Agent Name",
    system_prompt="Your system prompt here..."
)
```

2. Add the agent to the pipeline in `core/orchestrator.py`:
```python
phases_order = ["requirements", "validation", "planning", "risk", "insights", "new_agent"]
```

3. Update the report builder to include the new agent's output.

## Debugging

### Backend Debugging

1. **Enable Debug Logging**:
```env
LOG_LEVEL=DEBUG
```

2. **Use Python Debugger**:
```python
import pdb; pdb.set_trace()
```

3. **Check Database**:
```bash
sqlite3 sentineliq.db
.tables
SELECT * FROM users;
```

### Frontend Debugging

1. **Open Browser DevTools** (F12)
2. **Check Network Tab** for API requests
3. **Check Console** for JavaScript errors
4. **React DevTools** for component state inspection

## Common Issues

### Database Lock Error
- **Cause**: Multiple processes accessing SQLite
- **Solution**: Ensure only one backend instance is running, or use PostgreSQL

### LLM API Rate Limits
- **Cause**: Exceeding API rate limits
- **Solution**: System automatically fails over to backup LLM

### JWT Token Expiration
- **Cause**: Token expired after 8 hours
- **Solution**: Re-authenticate to get new token

### CORS Errors
- **Cause**: Frontend origin not in allowed list
- **Solution**: Update `FRONTEND_ORIGIN` in `.env`

## Performance Optimization

### Backend
- Use connection pooling for database (when migrating to PostgreSQL)
- Implement caching for frequently accessed data
- Use async/await for I/O operations
- Add Redis for distributed rate limiting

### Frontend
- Implement code splitting with React.lazy()
- Use memoization for expensive computations
- Optimize re-renders with React.memo()
- Lazy load markdown rendering

## Contributing

1. Create a feature branch
2. Make your changes
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## Code Style

- **Python**: Follow PEP 8
- **JavaScript**: Follow ESLint rules
- **Comments**: Document complex logic
- **Commit Messages**: Use conventional commits format

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Pytest Documentation](https://docs.pytest.org/)
- [SQLite Documentation](https://www.sqlite.org/docs.html)

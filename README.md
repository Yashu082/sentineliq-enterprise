# 🛡️ SentinelIQ Enterprise v3.0: Multi-Agent AI Architecture Review Platform

<div align="center">

[![CI/CD](https://github.com/Yashu082/sentineliq-enterprise/actions/workflows/ci.yml/badge.svg)](https://github.com/Yashu082/sentineliq-enterprise/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Node.js](https://img.shields.io/badge/Node.js-18+-green.svg)](https://nodejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg?logo=react)](https://react.dev/)
[![Deployed on Vercel](https://img.shields.io/badge/Deployed%20on-Vercel-black?logo=vercel)](https://sentineliq-enterprise.vercel.app)
[![Multi-Agent](https://img.shields.io/badge/AI-5--Agent%20Pipeline-purple.svg)](https://github.com/Yashu082/sentineliq-enterprise)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/Yashu082/sentineliq-enterprise/pulls)

**Production-grade AI architecture review platform for CTOs, architects, and engineering managers.**

[🚀 Live Demo](https://sentineliq-enterprise.vercel.app) • [📚 Docs](./docs) • [🐛 Report Bug](https://github.com/Yashu082/sentineliq-enterprise/issues/new?template=bug_report.md) • [💡 Request Feature](https://github.com/Yashu082/sentineliq-enterprise/issues/new?template=feature_request.md)

</div>

---

SentinelIQ Enterprise is a production-grade, enterprise AI architecture review platform designed for CTOs, senior software architects, and engineering managers. It ingests Product Requirement Documents (PRDs) and orchestrates a 5-agent AI pipeline to provide comprehensive architecture analysis, risk assessments, and executive insights with confidence scoring, traceability, and automated artifact generation.

---

## 🎯 Enterprise-Grade Features

### Phase 1: AI Intelligence Improvements
- **Cross-Agent Validation**: Detects contradictions between agents and resolves conflicts before executive summary
- **Confidence Scoring**: Every finding includes confidence %, reason, and evidence
- **Requirement Traceability**: Complete traceability chain (Requirement → Validation → Risk → Recommendation)
- **Finding Severity**: Standardized severity levels (Critical/High/Medium/Low/Informational) with business impact

### Phase 2: Architecture Intelligence
- **Mermaid Architecture Diagram**: Automatically generated from PRD
- **Component Diagram**: Detailed component relationships
- **Data Flow Diagram**: Data movement visualization
- **API Inventory**: Complete API endpoint inventory
- **Database Entities**: Suggested database schema
- **Deployment Architecture**: Production deployment recommendations

### Phase 3: Executive Reporting
- **Executive Dashboard**: Project health scores with explanations
- **Multi-Dimensional Scoring**: Security, Architecture, Requirements, Compliance, Risk scores
- **Overall Readiness**: Percentage-based readiness assessment
- **Decision Framework**: GO / GO WITH CONDITIONS / BLOCKED decisions with reasoning

### Phase 4: Production Hardening
- **Structured Logging**: JSON-formatted logs for monitoring
- **Rate Limiting**: 60 requests/minute per user
- **Central Error Handling**: Consistent error responses
- **Retry Logic**: Exponential backoff for transient failures
- **Health Checks**: Component status monitoring
- **Database Migration Support**: Schema versioning and migrations

### Phase 5: Engineering Quality
- **Comprehensive Test Suite**: Unit, integration, and API tests
- **80%+ Test Coverage**: Backend validation, cross-agent tests, production hardening tests
- **Automated CI/CD**: GitHub Actions workflow

### Phase 6: Documentation
- **Architecture Documentation**: Complete system architecture overview
- **Developer Guide**: Setup, development, and contribution guidelines
- **Deployment Guide**: Production deployment strategies and environment configuration
- **API Documentation**: Complete API reference with examples
- **System Design Document**: Detailed design decisions and trade-offs
- **Agent Interaction Diagram**: Multi-agent pipeline visualization
- **Sequence Diagrams**: Complete interaction flows

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend Layer                          │
│  React 18 + Vite + Custom CSS + React Markdown              │
│  Port: 3000                                                 │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTPS + JWT Bearer Token
                       │ CORS-Protected
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    API Gateway Layer                        │
│  FastAPI + Uvicorn + Rate Limiting + Error Handling         │
│  Port: 8000                                                 │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        ▼                             ▼
┌──────────────────┐        ┌──────────────────┐
│   AI Engine      │        │  Data Layer      │
│  5-Agent Pipeline│        │  SQLite + WAL    │
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

---

## 💻 Technical Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Frontend | React 18, Vite, Custom CSS | UI Framework |
| Backend | FastAPI, Uvicorn, Pydantic | API Framework |
| Authentication | JWT, PBKDF2 (210,000 rounds) | Security |
| Database | SQLite (WAL mode) | Data Storage |
| AI Models | Gemini 2.5 Flash, Llama 3.3 | LLM Providers |
| Testing | Pytest, HTTPX | Test Framework |
| Deployment | Uvicorn, Vite, GitHub Actions | Server & CI/CD |

---

## 📡 API Endpoints

### Authentication
- `POST /auth/signup` - User registration
- `POST /auth/signin` - User authentication

### Audit Operations
- `POST /audit/run` - Execute architecture audit
- `GET /audit/history` - List user's audit history
- `GET /audit/{audit_id}` - Retrieve specific audit

### Health
- `GET /health` - System health check

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- Google Gemini API Key
- Groq API Key

### Backend Setup

```bash
cd backend-fastapi
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
python -m uvicorn main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend-react
npm install
npm run dev
```

### Running Tests

```bash
cd backend-fastapi
pytest tests/ -v
```

### Access the Application

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

---

## 📚 Documentation

Comprehensive documentation is available in the `docs/` directory:

- **ARCHITECTURE.md** - System architecture and design principles
- **DEVELOPER_GUIDE.md** - Development setup and contribution guide
- **DEPLOYMENT_GUIDE.md** - Production deployment strategies
- **API_DOCUMENTATION.md** - Complete API reference
- **SYSTEM_DESIGN.md** - Detailed system design document
- **AGENT_INTERACTION_DIAGRAM.md** - Multi-agent pipeline visualization
- **SEQUENCE_DIAGRAM.md** - Complete interaction flows

---

## 🔒 Security Features

- **PBKDF2 Password Hashing**: 210,000 rounds for password security
- **JWT Authentication**: Stateless tokens with 8-hour expiration
- **User Data Isolation**: Cryptographic hashing per user
- **Rate Limiting**: 60 requests/minute per user
- **CORS Protection**: Explicit origin whitelisting
- **SQL Injection Prevention**: Parameterized queries
- **Environment Variables**: No secrets in code

---

## 🤖 AI Pipeline

The 5-agent pipeline includes:

1. **Requirements Analyst**: Extracts requirements with confidence scoring
2. **Validation Engineer**: Validates for gaps and contradictions
3. **Delivery Planner**: Creates implementation plans
4. **Risk & Security Officer**: Identifies security and operational risks
5. **Executive Insights Synthesizer**: Generates executive summaries with scores

**Key Features**:
- Cross-agent validation for contradiction detection
- Intelligent LLM failover (Gemini → Groq)
- Requirement traceability matrix
- Automatic architecture artifact generation

---

## 📄 Report Structure

Each audit report includes:

1. **Requirements**: Extracted requirements with confidence scores
2. **Validation Checklist**: Validation findings with severity levels
3. **Delivery Plan**: Implementation recommendations
4. **Risks & Mitigations**: Security and operational risks
5. **Executive Insights**: Summary with scores and decision
6. **Requirement Traceability Matrix**: Complete traceability chain
7. **Architecture Artifacts**: Mermaid diagrams, API inventory, etc.
8. **Provenance**: Model usage per phase

---

## 🚀 Deployment

### Local Development

```bash
# Backend
cd backend-fastapi && python -m uvicorn main:app --reload --port 8000

# Frontend
cd frontend-react && npm run dev
```

### Production

```bash
# Backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

# Frontend
npm run build
# serve dist/ with nginx or any static host
```

Set the frontend API URL for production:
```bash
# frontend-react/.env.production
VITE_API_BASE=https://your-backend-domain.com
```

For full deployment strategies see `docs/DEPLOYMENT_GUIDE.md` — covers cloud providers (AWS, GCP, Azure), SSL/TLS, reverse proxy, monitoring.

---

## 🧪 Testing

```bash
cd backend-fastapi
pytest tests/ -v
pytest tests/ --cov=core --cov=database --cov-report=html
```

Covers: API endpoints, cross-agent validation, architecture generation, rate limiting, error handling, user isolation.

---

## 🤝 Contributing

1. Create a feature branch
2. Make your changes with tests
3. Ensure all tests pass
4. Submit a pull request

See `docs/DEVELOPER_GUIDE.md` for detailed contribution guidelines.

---

## 📝 License

Licensed under the MIT License.

---

## 🎯 v3.0 Roadmap Status

✅ Phase 1: AI Intelligence Improvements
✅ Phase 2: Architecture Intelligence
✅ Phase 3: Executive Reporting
✅ Phase 4: Production Hardening
✅ Phase 5: Engineering Quality
✅ Phase 6: Documentation

**SentinelIQ Enterprise v3.0 is production-ready for enterprise architecture reviews.**

---

## 📞 Support

- 🐛 [Bug Reports](https://github.com/Yashu082/sentineliq-enterprise/issues/new?template=bug_report.md)
- 💡 [Feature Requests](https://github.com/Yashu082/sentineliq-enterprise/issues/new?template=feature_request.md)
- 🤖 [AI Pipeline Issues](https://github.com/Yashu082/sentineliq-enterprise/issues/new?template=agent_issue.md)
- 📚 [Documentation](./docs)
- 🔧 [Technical Reference](./TECHNICAL_REFERENCE_MANUAL.md)

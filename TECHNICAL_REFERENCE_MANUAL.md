# SentinelIQ Enterprise v3 - Technical Reference Manual
**Master Architectural Blueprint for Developer Interviews**

**Generated**: June 27, 2026  
**Workspace**: `sentineliq-enterprise - V3`  
**Purpose**: Exhaustive technical documentation for architecture walkthrough interviews

---

## Table of Contents
1. [Workspace Structure Overview](#workspace-structure-overview)
2. [Hidden Directories](#hidden-directories)
3. [Backend FastAPI Microservice](#backend-fastapi-microservice)
4. [Frontend React Application](#frontend-react-application)
5. [Root Diagnostic Scripts](#root-diagnostic-scripts)
6. [Root Documentation](#root-documentation)
7. [Architecture Summary](#architecture-summary)

---

## Workspace Structure Overview

### Root Workspace: `sentineliq-enterprise - V3/`

**WHAT IT IS**: The monorepo root containing a decoupled full-stack SaaS architecture with backend microservice, frontend SPA, diagnostic tooling, and comprehensive documentation.

**WHY IT IS THERE**: Provides a unified workspace for enterprise architecture review platform development, enabling coordinated development of backend AI orchestration, frontend user interface, and quality assurance tooling.

**ARCHITECT PITCH**: "We're running a decoupled microservices architecture with FastAPI backend and React frontend. The root contains our QA automation scripts and documentation, enabling continuous validation of our 5-agent AI pipeline. The separation of concerns allows independent scaling and deployment of each component while maintaining development velocity through shared tooling."

**RATING**: [ESSENTIAL CORE]

---

## Hidden Directories

### `.github/workflows/`

#### `deploy.yml`

**WHAT IT IS**: GitHub Actions CI/CD workflow configuration file defining automated testing and deployment pipeline for the backend FastAPI service.

**WHY IT IS THERE**: Automates quality assurance on every push/PR to main/master branches, ensuring code quality through automated Python 3.11 environment setup, dependency installation, and pytest execution.

**ARCHITECT PITCH**: "Our CI/CD pipeline runs on GitHub Actions, automatically spinning up Python 3.11 environments, installing dependencies, and executing our test suite on every push. This ensures our 5-agent AI orchestration pipeline maintains code quality standards before merging to production branches."

**RATING**: [ESSENTIAL CORE]

---

### `.pytest_cache/`

#### `.gitignore`, `CACHEDIR.TAG`, `README.md`, `v/`

**WHAT IT IS**: Pytest cache directory storing test execution metadata, last-failed test records, and performance optimization data for accelerated test runs.

**WHY IT IS THERE**: Improves test execution speed by caching test results and enabling selective re-running of only changed or previously failed tests. Standard pytest optimization mechanism.

**ARCHITECT PITCH**: "The pytest cache directory stores test execution metadata to optimize our test suite performance. It enables incremental test execution and last-failed test re-runs, reducing CI/CD pipeline duration during development iterations."

**RATING**: [DEV-DEPENDENCY / TOOLING]

---

### `.qodo/`

#### `agents/`, `workflows/`

**WHAT IT IS**: Qodo AI assistant configuration directories for agent-based development workflows and AI-powered code generation/customization.

**WHY IT IS THERE**: Provides integration with Qodo's AI development assistant for enhanced code generation, refactoring, and workflow automation within the IDE environment.

**ARCHITECT PITCH**: "We leverage Qodo's AI assistant for accelerated development workflows. The configuration directories enable our team to use AI-powered code generation and refactoring while maintaining consistency with our architectural patterns."

**RATING**: [DEV-DEPENDENCY / TOOLING]

---

## Backend FastAPI Microservice

### `backend-fastapi/`

**WHAT IT IS**: Python-based microservice implementing the core AI orchestration engine, REST API endpoints, authentication, database management, and 5-agent pipeline execution.

**WHY IT IS THERE**: Serves as the backend brain of SentinelIQ, handling JWT authentication, SQLite database operations, LLM provider failover (Gemini → Groq), and multi-agent architecture review pipeline orchestration.

**ARCHITECT PITCH**: "Our FastAPI backend is the orchestration engine for the entire platform. It implements a 5-agent AI pipeline with Gemini-to-Groq failover, JWT authentication with PBKDF2 hashing, SQLite with WAL mode for data persistence, and comprehensive error handling with rate limiting. The microservice architecture allows independent scaling and deployment."

**RATING**: [ESSENTIAL CORE]

---

#### `main.py`

**WHAT IT IS**: FastAPI application entry point defining REST API endpoints, middleware configuration, authentication logic, and request/response models for the SentinelIQ API.

**WHY IT IS THERE**: Provides the HTTP interface for frontend consumption, handling authentication (signup/signin), audit execution, history retrieval, and health monitoring with CORS protection and rate limiting.

**ARCHITECT PITCH**: "main.py is our FastAPI application entry point, defining the complete REST API surface. It implements JWT-based authentication with 8-hour token expiration, CORS middleware for frontend integration, rate limiting at 60 requests/minute, and endpoints for audit execution and retrieval. The health check endpoint provides component status monitoring for load balancers."

**RATING**: [ESSENTIAL CORE]

---

#### `requirements.txt`

**WHAT IT IS**: Python dependency specification file listing all required packages for the FastAPI backend service.

**WHY IT IS THERE**: Ensures reproducible build environments by specifying exact package versions for FastAPI, Uvicorn, LLM providers (Google GenAI, Groq), security libraries (python-jose), and testing frameworks (pytest, httpx).

**ARCHITECT PITCH**: "Our requirements.txt defines the complete dependency graph for the backend service. It includes FastAPI with Uvicorn for the ASGI server, Google GenAI and Groq SDKs for LLM provider integration, python-jose for JWT handling, and pytest with httpx for comprehensive API testing."

**RATING**: [ESSENTIAL CORE]

---

#### `Dockerfile`

**WHAT IT IS**: Docker containerization configuration for building a lightweight Python 3.11-slim image with all dependencies and runtime configuration for the FastAPI service.

**WHY IT IS THERE**: Enables containerized deployment with consistent runtime environments, portability across cloud providers, and simplified scaling through container orchestration platforms.

**ARCHITECT PITCH**: "Our Dockerfile uses Python 3.11-slim for a minimal attack surface and image size. It copies requirements first for Docker layer caching, installs dependencies without cache for reproducibility, exposes port 8000, and runs the Uvicorn ASGI server with 0.0.0.0 binding for container networking."

**RATING**: [ESSENTIAL CORE]

---

#### `.env.example`

**WHAT IT IS**: Environment variable template file documenting required configuration parameters for API keys, JWT settings, CORS configuration, and LLM model selection.

**WHY IT IS THERE**: Provides a security-conscious template for developers to configure their local environments without committing sensitive API keys to version control.

**ARCHITECT PITCH**: "The .env.example file serves as our configuration template, documenting all required environment variables including Gemini and Groq API keys, JWT secret and algorithm settings, CORS origin configuration, and LLM model selection parameters. This enables secure local development without exposing credentials."

**RATING**: [ESSENTIAL CORE]

---

#### `.env`

**WHAT IT IS**: Actual environment configuration file containing sensitive API keys and runtime parameters (gitignored, not committed to version control).

**WHY IT IS THERE**: Stores actual runtime configuration including LLM provider API keys, JWT secrets, and environment-specific settings for local development and production deployments.

**ARCHITECT PITCH**: "The .env file contains our sensitive runtime configuration including Gemini and Groq API keys, JWT secrets, and CORS settings. This file is gitignored to prevent credential exposure, with .env.example serving as the template for new developers."

**RATING**: [ESSENTIAL CORE]

---

#### `.dockerignore`

**WHAT IT IS**: Docker build exclusion configuration file specifying files and directories to exclude from Docker image builds to reduce image size and improve build performance.

**WHY IT IS THERE**: Prevents unnecessary files from being included in Docker images, reducing attack surface, build time, and image size by excluding development artifacts, cache directories, and documentation.

**ARCHITECT PITCH**: "Our .dockerignore file excludes development artifacts like .venv, __pycache__, .pytest_cache, and documentation from Docker builds. This reduces image size, minimizes attack surface, and improves build performance by only including production-critical files."

**RATING**: [ESSENTIAL CORE]

---

#### `sentineliq.db`

**WHAT IT IS**: SQLite database file storing user accounts, audit records, and schema migration history with WAL (Write-Ahead Logging) mode for concurrent access.

**WHY IT IS THERE**: Provides persistent storage for user authentication data, audit history, and report content with ACID compliance and concurrent read access through WAL mode.

**ARCHITECT PITCH**: "The SQLite database with WAL mode provides persistent storage for user accounts and audit records. WAL mode enables concurrent read access without locking, supporting multiple frontend connections while maintaining ACID compliance for data integrity."

**RATING**: [ESSENTIAL CORE]

---

#### `qa_test_report.md`

**WHAT IT IS**: Generated quality assurance test report documenting the results of automated API testing and audit execution verification.

**WHY IT IS THERE**: Serves as a historical record of QA test executions, providing evidence of system functionality and regression testing results for development teams.

**ARCHITECT PITCH**: "The qa_test_report.md is generated by our automated QA suite, documenting test execution results including authentication, audit workflow, and report structure validation. It provides a historical record of system health and regression testing evidence."

**RATING**: [DEV-DEPENDENCY / TOOLING]

---

### `backend-fastapi/config/`

#### `knowledge_base.py`

**WHAT IT IS**: Configuration module defining engineering compliance benchmarks that anchor the AI agents' evaluation rubric for architecture reviews.

**WHY IT IS THERE**: Provides a localized, opinionated dataset of compliance benchmarks (API security, data privacy, LLM resilience) that guide agent evaluation consistency and quality.

**ARCHITECT PITCH**: "knowledge_base.py defines our engineering compliance benchmarks that anchor the AI agents' evaluation rubric. It includes benchmarks for API security baseline, user data privacy isolation, and resilient LLM orchestration, ensuring consistent evaluation standards across all architecture reviews."

**RATING**: [ESSENTIAL CORE]

---

### `backend-fastapi/core/`

#### `orchestrator.py`

**WHAT IT IS**: Core orchestration engine implementing the 5-agent AI pipeline with LLM provider failover, cross-agent validation, token management, and architecture artifact generation.

**WHY IT IS THERE**: Executes the multi-agent architecture review pipeline, managing agent sequencing, LLM provider failover (Gemini → Groq on 429/503/403 errors), cross-agent contradiction detection, and traceability matrix construction.

**ARCHITECT PITCH**: "orchestrator.py is the heart of our AI pipeline, implementing a 5-agent architecture review engine with intelligent LLM failover. It manages agent sequencing, cross-agent validation for contradiction detection, token ceiling compliance for Groq, and automatic architecture artifact generation. The failover mechanism seamlessly switches from Gemini to Groq on rate limits or service unavailability."

**RATING**: [ESSENTIAL CORE]

---

#### `architecture_generator.py`

**WHAT IT IS**: Architecture artifact generation module that creates Mermaid diagrams, component diagrams, data flow diagrams, API inventories, and deployment architecture from extracted metadata.

**WHY IT IS THERE**: Automatically generates visual and textual architecture artifacts from agent outputs, providing comprehensive system architecture documentation without manual intervention.

**ARCHITECT PITCH**: "architecture_generator.py automatically generates architecture artifacts from agent-extracted metadata. It creates Mermaid architecture diagrams, component diagrams, data flow diagrams, API inventories, database entity documentation, and deployment architecture recommendations. This provides comprehensive system documentation without manual effort."

**RATING**: [ESSENTIAL CORE]

---

#### `validation.py`

**WHAT IT IS**: Cross-agent validation framework implementing contradiction detection, confidence scoring, and requirement traceability management across the 5-agent pipeline.

**WHY IT IS THERE**: Ensures consistency and quality of agent outputs by detecting contradictions between phases, managing requirement traceability chains (Requirement → Validation → Risk → Recommendation), and providing structured severity classification.

**ARCHITECT PITCH**: "validation.py implements our cross-agent validation framework, detecting contradictions between agent phases using pattern matching and semantic analysis. It manages requirement traceability matrices linking requirements to validations, risks, and recommendations, ensuring complete audit trails and consistent evaluation quality."

**RATING**: [ESSENTIAL CORE]

---

#### `prompts.py`

**WHAT IT IS**: Persona definition module containing system prompts for the 5 AI agents (Requirements Analyst, Validation Engineer, Delivery Planner, Risk Officer, Executive Synthesizer).

**WHY IT IS THERE**: Defines the role-specific system prompts that guide each AI agent's behavior, ensuring consistent evaluation perspectives and structured output formats across the pipeline.

**ARCHITECT PITCH**: "prompts.py defines the system prompts for our 5 AI agents, each with a specific persona and evaluation perspective. The Requirements Analyst extracts requirements with confidence scoring, the Validation Engineer identifies technical gaps, the Delivery Planner creates implementation roadmaps, the Risk Officer assesses security and operational risks, and the Executive Synthesizer generates CTO-level summaries."

**RATING**: [ESSENTIAL CORE]

---

#### `error_handler.py`

**WHAT IT IS**: Centralized error handling framework defining custom exception types and global error response formatting for consistent API error responses.

**WHY IT IS THERE**: Provides consistent error responses across the application, implementing structured error codes, detailed error messages, and proper HTTP status codes for different error scenarios.

**ARCHITECT PITCH**: "error_handler.py implements our centralized error handling framework with custom exception types for validation, authentication, authorization, rate limiting, and LLM errors. It provides consistent error responses with structured error codes and messages, ensuring predictable API behavior for frontend consumers."

**RATING**: [ESSENTIAL CORE]

---

#### `rate_limiter.py`

**WHAT IT IS**: Rate limiting middleware implementing token bucket algorithm for API request throttling per user, with configurable limits and remaining request headers.

**WHY IT IS THERE**: Prevents API abuse and ensures fair resource allocation by limiting request frequency per user, protecting against DoS attacks and LLM provider quota exhaustion.

**ARCHITECT PITCH**: "rate_limiter.py implements token bucket rate limiting at 60 requests per minute per user. It uses in-memory storage for development (Redis recommended for production), provides remaining request headers for client feedback, and protects against API abuse and LLM provider quota exhaustion."

**RATING**: [ESSENTIAL CORE]

---

#### `logging_config.py`

**WHAT IT IS**: Structured logging configuration implementing JSON-formatted logs with timestamp, level, module, function, and exception tracking for production monitoring.

**WHY IT IS THERE**: Provides production-ready logging infrastructure with structured JSON output for log aggregation systems, enabling effective monitoring and debugging in distributed environments.

**ARCHITECT PITCH**: "logging_config.py implements structured JSON logging with timestamp, level, module, function, and exception tracking. It suppresses noisy third-party loggers and provides production-ready log output compatible with log aggregation systems like ELK or Splunk."

**RATING**: [ESSENTIAL CORE]

---

#### `retry.py`

**WHAT IT IS**: Retry logic decorator implementing exponential backoff for transient failures, with configurable maximum attempts, delays, and exception handling.

**WHY IT IS THERE**: Provides resilience against transient failures in external service calls (LLM providers, database) by implementing automatic retry with exponential backoff.

**ARCHITECT PITCH**: "retry.py implements exponential backoff retry logic for transient failures. It provides configurable maximum attempts, initial delay, maximum delay, and exponential base parameters. This ensures resilience against temporary LLM provider outages or database connectivity issues."

**RATING**: [ESSENTIAL CORE]

---

#### `__init__.py`

**WHAT IT IS**: Python package initialization file marking the `core` directory as a Python package for proper module imports.

**WHY IT IS THERE**: Enables Python to recognize the `core` directory as a package, allowing imports like `from core import Orchestrator` and proper module resolution.

**ARCHITECT PITCH**: "The __init__.py file marks the core directory as a Python package, enabling clean module imports and proper namespace organization for our orchestration, validation, and utility modules."

**RATING**: [ESSENTIAL CORE]

---

### `backend-fastapi/database/`

#### `manager.py`

**WHAT IT IS**: SQLite database manager implementing user authentication, audit CRUD operations, schema migrations, and thread-safe connection handling with PBKDF2 password hashing.

**WHY IT IS THERE**: Provides the data persistence layer with secure user authentication, audit history management, schema versioning, and thread-safe operations for concurrent access.

**ARCHITECT PITCH**: "manager.py implements our SQLite data layer with PBKDF2 password hashing at 210,000 rounds for security. It provides user authentication, audit CRUD operations, schema migration support, and thread-safe connection handling. User data isolation is achieved through cryptographic user_hash scoping."

**RATING**: [ESSENTIAL CORE]

---

#### `__init__.py`

**WHAT IT IS**: Python package initialization file marking the `database` directory as a Python package for proper module imports.

**WHY IT IS THERE**: Enables Python to recognize the `database` directory as a package, allowing imports like `from database.manager import SQLiteManager`.

**ARCHITECT PITCH**: "The __init__.py file marks the database directory as a Python package, enabling clean module imports for our database manager and related data access components."

**RATING**: [ESSENTIAL CORE]

---

### `backend-fastapi/tests/`

#### `test_api.py`

**WHAT IT IS**: API endpoint test suite validating authentication, audit execution, history retrieval, and error handling using pytest and httpx.

**WHY IT IS THERE**: Ensures API contract compliance, authentication flow correctness, and proper error responses through automated integration testing.

**ARCHITECT PITCH**: "test_api.py validates our API endpoints including authentication flows, audit execution, history retrieval, and error handling. It uses pytest and httpx for comprehensive integration testing, ensuring API contract compliance and proper HTTP status codes."

**RATING**: [ESSENTIAL CORE]

---

#### `test_architecture_generator.py`

**WHAT IT IS**: Architecture generator test suite validating Mermaid diagram generation, component diagram rendering, and artifact creation from extracted metadata.

**WHY IT IS THERE**: Ensures the automatic architecture artifact generation produces valid Mermaid syntax and correctly represents system components and relationships.

**ARCHITECT PITCH**: "test_architecture_generator.py validates our automatic architecture artifact generation, ensuring Mermaid diagram syntax validity and correct representation of components, APIs, and data entities extracted from agent outputs."

**RATING**: [ESSENTIAL CORE]

---

#### `test_database.py`

**WHAT IT IS**: Database layer test suite validating user authentication, audit CRUD operations, data isolation, and migration functionality.

**WHY IT IS THERE**: Ensures data integrity, user isolation, authentication security, and proper database operations through comprehensive unit and integration testing.

**ARCHITECT PITCH**: "test_database.py validates our data layer including user authentication with PBKDF2 hashing, audit CRUD operations, user data isolation through cryptographic hashing, and schema migration functionality."

**RATING**: [ESSENTIAL CORE]

---

#### `test_production_hardening.py`

**WHAT IT IS**: Production hardening test suite validating rate limiting, error handling, retry logic, and security measures.

**WHY IT IS THERE**: Ensures production-ready security and resilience features are correctly implemented and functioning as designed.

**ARCHITECT PITCH**: "test_production_hardening.py validates our production hardening features including rate limiting, error handling, retry logic with exponential backoff, and security measures. This ensures our service is production-ready with proper resilience and security controls."

**RATING**: [ESSENTIAL CORE]

---

#### `test_validation.py`

**WHAT IT IS**: Cross-agent validation test suite validating contradiction detection, confidence scoring, and traceability matrix construction.

**WHY IT IS THERE**: Ensures the cross-agent validation framework correctly identifies contradictions, manages traceability chains, and produces consistent evaluation results.

**ARCHITECT PITCH**: "test_validation.py validates our cross-agent validation framework, ensuring contradiction detection between agent phases, confidence scoring accuracy, and traceability matrix construction linking requirements to validations, risks, and recommendations."

**RATING**: [ESSENTIAL CORE]

---

#### `__init__.py`

**WHAT IT IS**: Python package initialization file marking the `tests` directory as a Python package for proper test discovery and execution.

**WHY IT IS THERE**: Enables pytest to discover and execute tests within the tests directory as a cohesive test suite.

**ARCHITECT PITCH**: "The __init__.py file marks the tests directory as a Python package, enabling pytest to discover and execute our comprehensive test suite for API, database, validation, and production hardening components."

**RATING**: [ESSENTIAL CORE]

---

### `backend-fastapi/.venv/`

**WHAT IT IS**: Python virtual environment directory containing isolated Python interpreter and installed packages for backend development.

**WHY IT IS THERE**: Provides an isolated Python environment for backend development, preventing dependency conflicts with system Python or other projects.

**ARCHITECT PITCH**: "The .venv directory contains our Python virtual environment, isolating backend dependencies from system Python and other projects. This ensures reproducible development environments and prevents dependency conflicts."

**RATING**: [DEV-DEPENDENCY / TOOLING]

---

### `backend-fastapi/__pycache__/`

**WHAT IT IS**: Python bytecode cache directory storing compiled .pyc files for accelerated module loading during development.

**WHY IT IS THERE**: Improves Python startup performance by caching compiled bytecode, reducing import times during development iterations.

**ARCHITECT PITCH**: "The __pycache__ directory stores Python bytecode for accelerated module loading. This improves development performance by reducing import times during iterative development."

**RATING**: [DEV-DEPENDENCY / TOOLING]

---

### `backend-fastapi/.pytest_cache/`

**WHAT IT IS**: Pytest cache directory storing test execution metadata and last-failed test records for accelerated test runs.

**WHY IT IS THERE**: Improves test execution speed by caching test results and enabling selective re-running of changed or previously failed tests.

**ARCHITECT PITCH**: "The .pytest_cache directory stores test execution metadata for accelerated test runs. It enables incremental test execution and last-failed test re-runs, reducing CI/CD pipeline duration."

**RATING**: [DEV-DEPENDENCY / TOOLING]

---

## Frontend React Application

### `frontend-react/`

**WHAT IT IS**: React 18 single-page application implementing the user interface for SentinelIQ with Vite build tooling, glassmorphism design, and real-time audit visualization.

**WHY IT IS THERE**: Provides the user-facing interface for authentication, audit submission, report visualization, and audit history management with modern UX and responsive design.

**ARCHITECT PITCH**: "Our React frontend implements a modern SPA with Vite for fast development and optimized production builds. It features glassmorphism design, real-time audit pipeline visualization, Mermaid diagram rendering, and comprehensive report viewing with table of contents navigation and PDF export capability."

**RATING**: [ESSENTIAL CORE]

---

#### `package.json`

**WHAT IT IS**: Node.js package configuration file defining dependencies, scripts, and metadata for the React frontend application.

**WHY IT IS THERE**: Specifies React 18, Vite, Mermaid, React Markdown, and development dependencies, along with build and development scripts for the frontend application.

**ARCHITECT PITCH**: "package.json defines our frontend dependencies including React 18, Vite for build tooling, Mermaid for diagram rendering, React Markdown for report display, and remark-gfm for GitHub Flavored Markdown support. It also defines development and build scripts for local development and production deployment."

**RATING**: [ESSENTIAL CORE]

---

#### `package-lock.json`

**WHAT IT IS**: NPM lock file recording exact dependency versions and integrity hashes for reproducible builds across different environments.

**WHY IT IS THERE**: Ensures reproducible builds by locking exact dependency versions, preventing version drift and ensuring consistent behavior across development and production environments.

**ARCHITECT PITCH**: "The package-lock.json file ensures reproducible builds by locking exact dependency versions and integrity hashes. This prevents version drift and ensures consistent behavior across development, staging, and production environments."

**RATING**: [ESSENTIAL CORE]

---

#### `index.html`

**WHAT IT IS**: HTML entry point for the React application, defining the root div and script loading for the Vite development server.

**WHY IT IS THERE**: Provides the HTML skeleton for the SPA, mounting the React application at the root div and loading the Vite development server script.

**ARCHITECT PITCH**: "index.html is our HTML entry point, providing the root div for React mounting and loading the Vite development server script. It includes proper meta tags for viewport configuration and character encoding."

**RATING**: [ESSENTIAL CORE]

---

#### `vite.config.js`

**WHAT IT IS**: Vite build configuration file defining React plugin, development server settings, and build optimization parameters.

**WHY IT IS THERE**: Configures Vite for React development with strict port 3000, React Fast Refresh, and optimized production builds.

**ARCHITECT PITCH**: "vite.config.js configures Vite for React development with the React plugin, strict port 3000 for development consistency, and optimized production builds. It enables Fast Refresh for hot module replacement during development."

**RATING**: [ESSENTIAL CORE]

---

### `frontend-react/src/`

#### `App.jsx`

**WHAT IT IS**: Main React application component implementing authentication, audit submission, report visualization, phase loading animation, error handling, and audit history management.

**WHY IT IS THERE**: Provides the complete user interface for SentinelIQ, including authentication forms, audit submission, real-time pipeline visualization, report dashboard, and audit history browsing.

**ARCHITECT PITCH**: "App.jsx is our main application component, implementing the complete user interface including authentication with JWT token management, audit submission with real-time phase loading animation, report dashboard with metrics extraction, Mermaid diagram rendering, and audit history management. It features glassmorphism design and responsive layout."

**RATING**: [ESSENTIAL CORE]

---

#### `index.jsx`

**WHAT IT IS**: React application entry point that mounts the App component to the DOM root element using React 18's createRoot API.

**WHY IT IS THERE**: Initializes the React application by creating a root and rendering the App component with StrictMode for development warnings.

**ARCHITECT PITCH**: "index.jsx is our React entry point, using React 18's createRoot API to mount the App component to the DOM. It enables StrictMode for additional development warnings and best practices enforcement."

**RATING**: [ESSENTIAL CORE]

---

#### `index.css`

**WHAT IT IS**: Comprehensive CSS stylesheet implementing glassmorphism design system, responsive layout, animations, and print styles for the React application.

**WHY IT IS THERE**: Provides the complete visual design system including glassmorphism effects, responsive grid layouts, phase loading animations, error display styling, and print-optimized styles for PDF export.

**ARCHITECT PITCH**: "index.css implements our glassmorphism design system with backdrop blur effects, gradient backgrounds, and responsive grid layouts. It includes phase loading animations, error display styling, table of contents navigation, and print-optimized styles for PDF export with inverted Mermaid diagrams."

**RATING**: [ESSENTIAL CORE]

---

### `frontend-react/dist/`

**WHAT IT IS**: Vite build output directory containing optimized production assets including bundled JavaScript, CSS, and static files.

**WHY IT IS THERE**: Stores the production-ready build artifacts generated by Vite for deployment to web servers or CDN hosting.

**ARCHITECT PITCH**: "The dist directory contains our Vite production build output, including bundled and minified JavaScript, CSS, and static assets optimized for deployment to web servers or CDN hosting."

**RATING**: [DEV-DEPENDENCY / TOOLING]

---

### `frontend-react/node_modules/`

**WHAT IT IS**: NPM dependency directory containing all installed Node.js packages and their transitive dependencies for the frontend application.

**WHY IT IS THERE**: Provides the runtime dependencies for the React application, including React, Vite, Mermaid, React Markdown, and development tools.

**ARCHITECT PITCH**: "The node_modules directory contains our NPM dependencies including React 18, Vite, Mermaid, React Markdown, and their transitive dependencies. This provides the runtime environment for our frontend application."

**RATING**: [DEV-DEPENDENCY / TOOLING]

---

## Root Diagnostic Scripts

### `check_report.py`

**WHAT IT IS**: Python diagnostic script for testing audit report retrieval and structure validation via API calls.

**WHY IT IS THERE**: Provides quick validation of audit report structure and content during development and debugging, checking for required sections and content length.

**ARCHITECT PITCH**: "check_report.py is a diagnostic script for validating audit report structure through API testing. It authenticates, retrieves audit reports, checks for required sections like EXECUTIVE SUMMARY and REQUIREMENTS, and validates content length for debugging purposes."

**RATING**: [DEV-DEPENDENCY / TOOLING]

---

### `debug_insights.py`

**WHAT IT IS**: Python debugging script for extracting and inspecting the insights agent output from audit reports.

**WHY IT IS THERE**: Enables focused debugging of the executive insights agent output by isolating and displaying the insights section from audit reports.

**ARCHITECT PITCH**: "debug_insights.py is a debugging tool for inspecting the insights agent output. It authenticates, retrieves audit reports, and extracts the insights section for focused debugging of the executive synthesis phase."

**RATING**: [DEV-DEPENDENCY / TOOLING]

---

### `debug_insights2.py`

**WHAT IT IS**: Enhanced Python debugging script with regex-based section extraction for comprehensive insights agent output analysis.

**WHY IT IS THERE**: Provides improved insights section extraction using regex patterns for more reliable debugging of executive synthesis agent outputs.

**ARCHITECT PITCH**: "debug_insights2.py is an enhanced debugging tool with regex-based section extraction for reliable insights agent output analysis. It handles case-insensitive matching and provides comprehensive output inspection."

**RATING**: [DEV-DEPENDENCY / TOOLING]

---

### `debug_report_structure.py`

**WHAT IT IS**: Python diagnostic script for analyzing report structure by extracting all headers and displaying the first portion of report content.

**WHY IT IS THERE**: Enables structural analysis of generated reports by extracting and displaying all markdown headers and content preview for debugging.

**ARCHITECT PITCH**: "debug_report_structure.py analyzes report structure by extracting all markdown headers using regex patterns. It displays the complete header hierarchy and content preview for structural debugging and validation."

**RATING**: [DEV-DEPENDENCY / TOOLING]

---

### `qa_verification.py`

**WHAT IT IS**: Comprehensive automated QA test suite validating health checks, authentication, audit workflow, report structure, and executive dashboard metrics.

**WHY IT IS THERE**: Provides end-to-end automated testing of the complete SentinelIQ platform, generating detailed verification reports with pass/fail status.

**ARCHITECT PITCH**: "qa_verification.py is our comprehensive automated QA suite, testing health checks, authentication flows, audit workflow execution, report structure validation, and executive dashboard metrics. It generates detailed verification reports with pass/fail status and success rate calculations."

**RATING**: [DEV-DEPENDENCY / TOOLING]

---

### `run_fresh_audit.py`

**WHAT IT IS**: Python script for executing fresh audit tests with timing measurements and structural validation of generated reports.

**WHY IT IS THERE**: Enables performance testing and structural validation of fresh audit executions, measuring execution time and validating report structure.

**ARCHITECT PITCH**: "run_fresh_audit.py executes fresh audit tests with timing measurements. It authenticates, runs new audits, measures execution time, validates report structure including EXECUTIVE SUMMARY and EXECUTIVE DASHBOARD sections, and saves reports for manual review."

**RATING**: [DEV-DEPENDENCY / TOOLING]

---

### `verify_audit.py`

**WHAT IT IS**: Python script for direct orchestrator testing without API layer, executing audits with sample project specifications.

**WHY IT IS THERE**: Enables unit testing of the orchestrator component independently of the API layer for focused debugging and validation.

**ARCHITECT PITCH**: "verify_audit.py tests the orchestrator directly without the API layer, executing audits with sample project specifications. This enables focused debugging of the 5-agent pipeline and architecture artifact generation independent of HTTP concerns."

**RATING**: [DEV-DEPENDENCY / TOOLING]

---

## Root Documentation

### `README.md`

**WHAT IT IS**: Comprehensive project documentation providing overview, architecture, technical stack, API endpoints, setup instructions, and feature descriptions.

**WHY IT IS THERE**: Serves as the primary entry point for developers, providing complete project understanding, setup instructions, and architectural guidance.

**ARCHITECT PITCH**: "README.md is our primary project documentation, providing a comprehensive overview of SentinelIQ Enterprise including system architecture, technical stack, API endpoints, setup instructions, security features, AI pipeline details, and deployment guidance. It serves as the developer onboarding guide and architectural reference."

**RATING**: [ESSENTIAL CORE]

---

### `QA_VERIFICATION_REPORT.md`

**WHAT IT IS**: Detailed QA verification report documenting test results, security verification, performance observations, and production readiness assessment.

**WHY IT IS THERE**: Provides historical record of QA testing activities, security verification results, and production readiness certification for the SentinelIQ platform.

**ARCHITECT PITCH**: "QA_VERIFICATION_REPORT.md documents our comprehensive QA verification results, including authentication testing, audit workflow validation, LLM provider failover testing, frontend component verification, security verification, and performance observations. It serves as production readiness certification and historical testing evidence."

**RATING**: [ESSENTIAL CORE]

---

### `verification_report.md`

**WHAT IT IS**: Sample generated audit report demonstrating the complete output of the 5-agent pipeline for a learning platform project specification.

**WHY IT IS THERE**: Provides example output of the SentinelIQ audit system, showcasing the structure and content of generated architecture review reports.

**ARCHITECT PITCH**: "verification_report.md is a sample generated audit report demonstrating the complete output of our 5-agent pipeline. It showcases the executive dashboard, requirements extraction, validation findings, delivery planning, risk assessment, and architecture artifacts generated by the system."

**RATING**: [DEV-DEPENDENCY / TOOLING]

---

### `docs/`

**WHAT IT IS**: Comprehensive documentation directory containing detailed architecture, development, deployment, API, system design, and interaction diagram documentation.

**WHY IT IS THERE**: Provides in-depth technical documentation covering all aspects of the SentinelIQ platform for developers, architects, and operations teams.

**ARCHITECT PITCH**: "The docs directory contains comprehensive technical documentation including ARCHITECTURE.md for system design, DEVELOPER_GUIDE.md for setup and contribution, DEPLOYMENT_GUIDE.md for production deployment, API_DOCUMENTATION.md for API reference, SYSTEM_DESIGN.md for detailed design decisions, AGENT_INTERACTION_DIAGagram.md for pipeline visualization, and SEQUENCE_DIAGRAM.md for interaction flows."

**RATING**: [ESSENTIAL CORE]

---

#### `docs/AGENT_INTERACTION_DIAGagram.md`

**WHAT IT IS**: Documentation of multi-agent pipeline interaction patterns and workflow visualization for the 5-agent architecture review system.

**WHY IT IS THERE**: Provides detailed explanation of agent interaction patterns, data flow between phases, and pipeline orchestration logic.

**ARCHITECT PITCH**: "AGENT_INTERACTION_DIAGagram.md documents our multi-agent pipeline interaction patterns, visualizing the 5-agent workflow, data flow between phases, and orchestration logic. It provides detailed explanation of how agents collaborate to generate comprehensive architecture reviews."

**RATING**: [ESSENTIAL CORE]

---

#### `docs/API_DOCUMENTATION.md`

**WHAT IT IS**: Complete API reference documentation including endpoint specifications, request/response schemas, authentication requirements, and usage examples.

**WHY IT IS THERE**: Provides comprehensive API documentation for frontend developers and external API consumers, including all endpoints, schemas, and authentication details.

**ARCHITECT PITCH**: "API_DOCUMENTATION.md provides complete API reference documentation including authentication endpoints, audit operation endpoints, health check endpoints, request/response schemas, error handling, and usage examples. It serves as the definitive guide for API consumers."

**RATING**: [ESSENTIAL CORE]

---

#### `docs/ARCHITECTURE.md`

**WHAT IT IS**: High-level system architecture documentation describing design principles, component interactions, technology choices, and architectural decisions.

**WHY IT IS THERE**: Provides architectural guidance for developers and stakeholders, explaining system design, component relationships, and technical decision rationale.

**ARCHITECT PITCH**: "ARCHITECTURE.md documents our high-level system architecture including design principles, component interactions, technology choices, and architectural decisions. It provides the rationale behind our microservices architecture, LLM provider selection, and security design patterns."

**RATING**: [ESSENTIAL CORE]

---

#### `docs/DEPLOYMENT_GUIDE.md`

**WHAT IT IS**: Production deployment documentation covering Docker containerization, Kubernetes deployment, environment configuration, and operational procedures.

**WHY IT IS THERE**: Provides comprehensive deployment guidance for operations teams, including container deployment, Kubernetes configuration, monitoring setup, and operational procedures.

**ARCHITECT PITCH**: "DEPLOYMENT_GUIDE.md provides comprehensive deployment guidance including Docker containerization, Kubernetes deployment manifests, environment configuration, monitoring setup, scaling strategies, and operational procedures. It serves as the operations handbook for production deployment."

**RATING**: [ESSENTIAL CORE]

---

#### `docs/DEVELOPER_GUIDE.md`

**WHAT IT IS**: Developer onboarding documentation covering setup procedures, development workflows, contribution guidelines, and coding standards.

**WHY IT IS THERE**: Provides comprehensive guidance for new developers joining the project, including environment setup, development workflows, testing procedures, and contribution guidelines.

**ARCHITECT PITCH**: "DEVELOPER_GUIDE.md is our developer onboarding documentation, covering environment setup, development workflows, testing procedures, coding standards, and contribution guidelines. It ensures consistent development practices and smooth onboarding for new team members."

**RATING**: [ESSENTIAL CORE]

---

#### `docs/SEQUENCE_DIAGRAM.md`

**WHAT IT IS**: Detailed sequence diagram documentation illustrating complete interaction flows between components, agents, and external services.

**WHY IT IS THERE**: Provides comprehensive visualization of system interaction flows, including authentication flows, audit execution flows, and error handling scenarios.

**ARCHITECT PITCH**: "SEQUENCE_DIAGRAM.md documents complete interaction flows between components, including authentication sequences, audit execution flows, LLM provider interactions, and error handling scenarios. It provides comprehensive visualization of system behavior for architectural understanding."

**RATING**: [ESSENTIAL CORE]

---

#### `docs/SYSTEM_DESIGN.md`

**WHAT IT IS**: Detailed system design documentation covering data models, algorithms, design patterns, and technical implementation details.

**WHY IT IS THERE**: Provides in-depth technical documentation of system implementation details, including data structures, algorithms, design patterns, and technical trade-offs.

**ARCHITECT PITCH**: "SYSTEM_DESIGN.md provides detailed technical documentation of our implementation, including data models, algorithms, design patterns, and technical trade-offs. It serves as the comprehensive technical reference for system implementation details."

**RATING**: [ESSENTIAL CORE]

---

## Architecture Summary

### System Architecture Overview

SentinelIQ Enterprise v3 implements a decoupled microservices architecture with the following key characteristics:

**Backend Layer (FastAPI)**:
- 5-agent AI pipeline with cross-agent validation
- LLM provider failover (Gemini → Groq) for resilience
- JWT authentication with PBKDF2 password hashing
- SQLite with WAL mode for data persistence
- Rate limiting and structured error handling
- Comprehensive test coverage (80%+)

**Frontend Layer (React)**:
- Modern SPA with Vite build tooling
- Glassmorphism design system
- Real-time audit pipeline visualization
- Mermaid diagram rendering
- PDF export capability
- Responsive layout with table of contents navigation

**DevOps Layer**:
- GitHub Actions CI/CD pipeline
- Docker containerization
- Environment-based configuration
- Comprehensive diagnostic tooling
- Automated QA verification suite

**Documentation Layer**:
- Comprehensive technical documentation
- API reference with examples
- Deployment guides for Docker/Kubernetes
- Developer onboarding guides
- Architecture decision records

### Key Technical Decisions

1. **Microservices Architecture**: Enables independent scaling and deployment of backend and frontend
2. **SQLite with WAL Mode**: Provides ACID compliance with concurrent read access for development
3. **LLM Provider Failover**: Ensures resilience against rate limits and service outages
4. **Cross-Agent Validation**: Maintains consistency and quality across AI-generated content
5. **PBKDF2 Password Hashing**: Provides enterprise-grade security for user authentication
6. **React with Vite**: Enables fast development with optimized production builds
7. **Structured Logging**: Facilitates production monitoring and debugging
8. **Comprehensive Testing**: Ensures code quality and regression prevention

### Production Readiness

SentinelIQ Enterprise v3 is production-ready with:
- ✅ Comprehensive authentication and authorization
- ✅ Resilient LLM orchestration with failover
- ✅ Rate limiting and abuse protection
- ✅ Structured error handling and logging
- ✅ Comprehensive test coverage
- ✅ Automated CI/CD pipeline
- ✅ Containerized deployment support
- ✅ Complete documentation suite

---

**Document Status**: Complete  
**Last Updated**: June 27, 2026  
**Version**: 1.0  
**Maintained By**: SentinelIQ Architecture Team

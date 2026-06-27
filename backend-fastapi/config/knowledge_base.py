from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ComplianceBenchmark:
    id: str
    title: str
    description: str
    checks: list[str]


# Localized Engineering Compliance Benchmarks Dataset Mapping.
# Keep this small and opinionated; it anchors the agents' evaluation rubric.
BENCHMARKS: list[ComplianceBenchmark] = [
    ComplianceBenchmark(
        id="api.security.basics",
        title="API Security Baseline",
        description="Minimum baseline for REST services in production.",
        checks=[
            "CORS configured explicitly (origins, methods, headers).",
            "No secrets in repo; use env vars for API keys.",
            "Request validation via Pydantic schemas; reject malformed input.",
            "Consistent error handling without leaking stack traces.",
            "Rate-limit and/or abuse protection plan documented.",
        ],
    ),
    ComplianceBenchmark(
        id="data.privacy.isolation",
        title="User Data Privacy & Isolation",
        description="Ensure user histories are isolated and cannot be cross-read.",
        checks=[
            "User identity mapped to a stable hash key; never store raw passwords.",
            "All history queries scoped by user_hash.",
            "Database uses parameterized queries (no string interpolation).",
            "Exported reports contain no other users' data.",
        ],
    ),
    ComplianceBenchmark(
        id="resilience.llm.failover",
        title="Resilient LLM Orchestration",
        description="Maintain uptime when primary LLM is rate-limited or degraded.",
        checks=[
            "Primary LLM called first; failover only on transient errors (429/503).",
            "Failover is transparent to caller (same response schema).",
            "Errors are logged with minimal sensitive content.",
            "Timeouts defined to avoid hanging requests.",
        ],
    ),
]


def as_dict() -> list[dict[str, Any]]:
    return [
        {
            "id": b.id,
            "title": b.title,
            "description": b.description,
            "checks": list(b.checks),
        }
        for b in BENCHMARKS
    ]


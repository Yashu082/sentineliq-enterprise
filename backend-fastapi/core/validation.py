from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import Any


class Severity(str, Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    INFORMATIONAL = "Informational"


@dataclass(frozen=True)
class ConfidenceScore:
    percentage: int  # 0-100
    reason: str
    evidence: str

    def __post_init__(self) -> None:
        if not 0 <= object.__getattribute__(self, "percentage") <= 100:
            raise ValueError("Confidence percentage must be between 0 and 100")


@dataclass(frozen=True)
class Finding:
    id: str
    severity: Severity
    confidence: ConfidenceScore
    description: str
    business_impact: str
    source_phase: str  # requirements, validation, planning, risk, insights
    traceability: dict[str, str]  # Maps requirement_id -> validation_id -> risk_id -> recommendation_id


@dataclass(frozen=True)
class Contradiction:
    phase_a: str
    phase_b: str
    finding_a: str
    finding_b: str
    conflict_type: str  # "direct_contradiction", "inconsistency", "gap"
    resolution: str


class CrossAgentValidator:
    """
    Detects contradictions and inconsistencies between agent outputs.
    Performs cross-validation before the Executive Summary phase.
    """

    def __init__(self) -> None:
        self._contradiction_patterns = [
            (r"(not|no|never|without)\s+\w+", r"(must|should|required|mandatory)"),
            (r"(optional|nice.to.have)", r"(critical|essential|mandatory)"),
            (r"(low\s+priority|can.wait)", r"(high\s+priority|urgent|immediate)"),
        ]

    def validate_phases(self, phase_outputs: dict[str, str]) -> list[Contradiction]:
        """
        Analyzes phase outputs for contradictions and inconsistencies.
        Returns a list of detected contradictions with resolutions.
        """
        contradictions: list[Contradiction] = []
        phases = list(phase_outputs.keys())

        for i in range(len(phases)):
            for j in range(i + 1, len(phases)):
                phase_a, phase_b = phases[i], phases[j]
                output_a = phase_outputs[phase_a]
                output_b = phase_outputs[phase_b]

                detected = self._detect_contradictions(output_a, output_b, phase_a, phase_b)
                contradictions.extend(detected)

        return contradictions

    def _detect_contradictions(
        self, output_a: str, output_b: str, phase_a: str, phase_b: str
    ) -> list[Contradiction]:
        contradictions: list[Contradiction] = []

        # Extract key statements from each output
        statements_a = self._extract_statements(output_a)
        statements_b = self._extract_statements(output_b)

        # Compare statements for contradictions
        for stmt_a in statements_a:
            for stmt_b in statements_b:
                conflict_type = self._check_contradiction(stmt_a, stmt_b)
                if conflict_type:
                    resolution = self._generate_resolution(stmt_a, stmt_b, conflict_type, phase_a, phase_b)
                    contradictions.append(
                        Contradiction(
                            phase_a=phase_a,
                            phase_b=phase_b,
                            finding_a=stmt_a,
                            finding_b=stmt_b,
                            conflict_type=conflict_type,
                            resolution=resolution,
                        )
                    )

        return contradictions

    def _extract_statements(self, output: str) -> list[str]:
        """
        Extracts individual statements from agent output.
        Splits by bullet points, numbered lists, and sentences.
        """
        statements: list[str] = []

        # Split by common delimiters
        lines = output.split("\n")
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Remove markdown formatting
            line = re.sub(r"^[\*\-\+]\s+", "", line)
            line = re.sub(r"^\d+\.\s+", "", line)
            line = re.sub(r"^#{1,6}\s+", "", line)

            if line and len(line) > 10:  # Filter out very short lines
                statements.append(line)

        return statements

    def _check_contradiction(self, stmt_a: str, stmt_b: str) -> str | None:
        """
        Checks if two statements contradict each other.
        Returns the conflict type or None if no contradiction.
        """
        stmt_a_lower = stmt_a.lower()
        stmt_b_lower = stmt_b.lower()

        # Check for direct negation patterns
        for pattern_a, pattern_b in self._contradiction_patterns:
            if re.search(pattern_a, stmt_a_lower) and re.search(pattern_b, stmt_b_lower):
                return "direct_contradiction"
            if re.search(pattern_b, stmt_a_lower) and re.search(pattern_a, stmt_b_lower):
                return "direct_contradiction"

        # Check for semantic contradictions
        contradiction_keywords = [
            ("must", "must not"),
            ("required", "optional"),
            ("critical", "low priority"),
            ("immediate", "deferred"),
            ("always", "never"),
        ]

        for pos, neg in contradiction_keywords:
            if pos in stmt_a_lower and neg in stmt_b_lower:
                return "inconsistency"
            if neg in stmt_a_lower and pos in stmt_b_lower:
                return "inconsistency"

        return None

    def _generate_resolution(
        self, stmt_a: str, stmt_b: str, conflict_type: str, phase_a: str, phase_b: str
    ) -> str:
        """
        Generates a resolution suggestion for detected contradictions.
        """
        if conflict_type == "direct_contradiction":
            return (
                f"Direct contradiction detected between {phase_a} and {phase_b}. "
                f"Review both findings: '{stmt_a}' vs '{stmt_b}'. "
                f"Recommend prioritizing the {phase_b} phase as it comes later in the pipeline "
                f"and incorporates more context."
            )
        elif conflict_type == "inconsistency":
            return (
                f"Inconsistency detected between {phase_a} and {phase_b}. "
                f"Clarify the requirement: '{stmt_a}' conflicts with '{stmt_b}'. "
                f"Consider merging both perspectives or explicitly documenting the trade-off."
            )
        else:
            return (
                f"Potential gap detected between {phase_a} and {phase_b}. "
                f"Review: '{stmt_a}' and '{stmt_b}' for alignment."
            )


class TraceabilityManager:
    """
    Manages requirement traceability across phases.
    Ensures every recommendation traces back to Requirement -> Validation -> Risk -> Recommendation.
    """

    def __init__(self) -> None:
        self._traceability_chain: dict[str, dict[str, Any]] = {}

    def add_requirement(self, req_id: str, description: str) -> None:
        """Add a requirement to the traceability chain."""
        self._traceability_chain[req_id] = {
            "requirement": description,
            "validation_findings": [],
            "risk_findings": [],
            "recommendations": [],
        }

    def link_validation(self, req_id: str, validation_id: str, finding: str) -> None:
        """Link a validation finding to a requirement."""
        if req_id in self._traceability_chain:
            self._traceability_chain[req_id]["validation_findings"].append(
                {"id": validation_id, "finding": finding}
            )

    def link_risk(self, req_id: str, risk_id: str, finding: str) -> None:
        """Link a risk finding to a requirement."""
        if req_id in self._traceability_chain:
            self._traceability_chain[req_id]["risk_findings"].append({"id": risk_id, "finding": finding})

    def link_recommendation(self, req_id: str, recommendation_id: str, recommendation: str) -> None:
        """Link a recommendation to a requirement."""
        if req_id in self._traceability_chain:
            self._traceability_chain[req_id]["recommendations"].append(
                {"id": recommendation_id, "recommendation": recommendation}
            )

    def get_traceability_matrix(self) -> dict[str, dict[str, Any]]:
        """Returns the complete traceability matrix."""
        return self._traceability_chain

    def generate_traceability_report(self) -> str:
        """Generates a markdown traceability report."""
        if not self._traceability_chain:
            return "No traceability data available."

        lines = ["## Requirement Traceability Matrix\n"]
        lines.append("| Requirement ID | Requirement | Validation | Risk | Recommendation |")
        lines.append("|---|---|---|---|---|")

        for req_id, data in self._traceability_chain.items():
            req_desc = data["requirement"][:50] + "..." if len(data["requirement"]) > 50 else data["requirement"]
            validations = ", ".join([v["id"] for v in data["validation_findings"]])
            risks = ", ".join([r["id"] for r in data["risk_findings"]])
            recommendations = ", ".join([r["id"] for r in data["recommendations"]])

            lines.append(f"| {req_id} | {req_desc} | {validations} | {risks} | {recommendations} |")

        return "\n".join(lines)

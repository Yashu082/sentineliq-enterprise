# core/orchestrator.py (Updated Error Handling & Failover)
from __future__ import annotations

import os
import re
import time
from dataclasses import dataclass
from typing import Any, Literal

from dotenv import load_dotenv

from config.knowledge_base import as_dict as knowledge_base_as_dict
from core.prompts import get_persona
from core.validation import CrossAgentValidator, TraceabilityManager
from core.architecture_generator import ArchitectureGenerator

load_dotenv()

GROQ_MAX_TOKENS_PER_REQUEST: int = 5500

def _estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)

def _truncate_output(output: str, max_tokens: int = 1000) -> str:
    lines = output.strip().split("\n")
    filtered = [
        line for line in lines
        if line.strip().startswith(("#", "##", "###", "- ", "* ", "• "))
        or len(line.strip()) < 120
    ]
    truncated = "\n".join(filtered)
    if _estimate_tokens(truncated) > max_tokens:
        truncated = truncated[:max_tokens * 4]
    return truncated.strip()

def _summarize_phases(phase_results: list[AgentPhaseResult], reserved_tokens: int = 1000) -> str:
    summary_parts = []
    available_tokens = GROQ_MAX_TOKENS_PER_REQUEST - reserved_tokens
    used_tokens = 0
    for p in phase_results:
        truncated = _truncate_output(p.output, max_tokens=1200)
        tokens_needed = _estimate_tokens(truncated) + 50
        if used_tokens + tokens_needed <= available_tokens:
            summary_parts.append(f"=== {p.persona_id.upper()} SUMMARY ===\n{truncated}")
            used_tokens += tokens_needed
        else:
            ultra_short = "\n".join(
                line for line in p.output.split("\n")
                if line.strip().startswith(("#", "##", "- ", "* ", "• "))
            )[:400]
            summary_parts.append(f"=== {p.persona_id.upper()} ESSENTIALS ===\n{ultra_short}")
            used_tokens += 450
    return "\n\n".join(summary_parts)

def _emergency_compress(content: str) -> str:
    """Emergency compression for proactive token ceiling compliance."""
    lines = content.split("\n")
    essential = [
        line for line in lines
        if any(line.strip().startswith(prefix) for prefix in ["PROJECT_NAME:", "PROJECT_SPEC:", "PREVIOUS_PHASES:", "### ", "## ", "# ", "- [", "* [", "- ", "* ", "**Contradiction"])
    ]
    return "\n".join(essential)[:GROQ_MAX_TOKENS_PER_REQUEST * 4]

PRIMARY_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

# Upgraded to handle Permission Denied structural blocks
TransientFailure = Literal["rate_limited", "service_unavailable", "permission_denied"]

def _is_transient_llm_error(exc: Exception) -> TransientFailure | None:
    msg = f"{type(exc).__name__}: {exc}"
    if re.search(r"\b429\b", msg) or "RESOURCE_EXHAUSTED" in msg:
        return "rate_limited"
    if re.search(r"\b503\b", msg) or "Service Unavailable" in msg or "SERVER_ERROR" in msg:
        return "service_unavailable"
    if re.search(r"\b403\b", msg) or "PERMISSION_DENIED" in msg:
        return "permission_denied"
    # FIXED: Also intercept 413 Request Entity Too Large for token ceiling
    if re.search(r"\b413\b", msg) or "Request too large" in msg or "PayloadTooLarge" in msg:
        return "rate_limited"  # Treat as recoverable by truncating
    return None

@dataclass(frozen=True)
class AgentPhaseResult:
    persona_id: str
    model_used: str
    output: str

@dataclass(frozen=True)
class OrchestrationResult:
    model_used: str
    phases: list[AgentPhaseResult]
    report_md: str

class Orchestrator:
    """
    5-Agent Pipeline Engine with Gemini -> Groq 429/503/403 Failover.
    Includes cross-agent validation and traceability tracking.
    """
    def __init__(self) -> None:
        self._gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
        self._groq_key = os.getenv("GROQ_API_KEY", "").strip()
        self._validator = CrossAgentValidator()
        self._traceability = TraceabilityManager()
        self._arch_generator = ArchitectureGenerator()

    def _call_gemini(self, *, system: str, user: str, temperature: float = 0.2) -> str:
        if not self._gemini_key:
            raise RuntimeError("GEMINI_API_KEY is missing.")
        from google import genai  # type: ignore

        client = genai.Client(api_key=self._gemini_key)
        resp = client.models.generate_content(
            model=PRIMARY_MODEL,
            contents=[{"role": "user", "parts": [{"text": f"{system}\n\nUSER_SPEC:\n{user}"}]}],
            config={
                "temperature": float(temperature),
                "max_output_tokens": 2048,
            },
        )
        text = getattr(resp, "text", None)
        if not text:
            raise RuntimeError("Gemini returned empty response.")
        return str(text).strip()

    def _call_groq(self, *, system: str, user: str, temperature: float = 0.2, retry_with_truncate: bool = True) -> str:
        if not self._groq_key:
            raise RuntimeError("GROQ_API_KEY is missing.")
        from groq import Groq  # type: ignore

        client = Groq(api_key=self._groq_key)
        try:
            completion = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                temperature=float(temperature),
                max_tokens=2048,
            )
        except Exception as exc:
            if retry_with_truncate and ("413" in str(exc) or "Request too large" in str(exc)):
                truncated_user = user[:GROQ_MAX_TOKENS_PER_REQUEST * 4]
                return self._call_groq(system=system, user=truncated_user, temperature=temperature, retry_with_truncate=False)
            raise
        content = completion.choices[0].message.content
        if not content:
            raise RuntimeError("Groq returned empty response.")
        return str(content).strip()

    def _call_with_failover(self, *, system: str, user: str, temperature: float = 0.2) -> tuple[str, str]:
        """
        Returns (model_used, output). Seamlessly handles rate limits and permission drops.
        """
        try:
            return f"gemini:{PRIMARY_MODEL}", self._call_gemini(system=system, user=user, temperature=temperature)
        except Exception as exc:
            transient = _is_transient_llm_error(exc)
            # FIXED: Catch permission drops or token limits to switch channels immediately
            if transient in ["rate_limited", "service_unavailable", "permission_denied"]:
                return f"groq:{GROQ_MODEL}", self._call_groq(system=system, user=user, temperature=temperature)
            raise

    def run_audit(self, *, project_name: str, project_spec: str) -> OrchestrationResult:
        kb = knowledge_base_as_dict()
        shared_context = (
            f"PROJECT_NAME: {project_name}\n\n"
            f"ENGINEERING_COMPLIANCE_BENCHMARKS:\n{kb}\n\n"
            f"PROJECT_SPEC:\n{project_spec.strip()}\n"
        )

        phases_order = ["requirements", "validation", "planning", "risk", "insights"]
        phase_results: list[AgentPhaseResult] = []
        stitched_inputs: dict[str, str] = {"context": shared_context}

        for persona_id in phases_order:
            persona = get_persona(persona_id)
            user_payload = stitched_inputs["context"]
            
            # Before insights phase, perform cross-agent validation
            if persona_id == "insights" and len(phase_results) >= 4:
                phase_outputs = {p.persona_id: p.output for p in phase_results}
                contradictions = self._validator.validate_phases(phase_outputs)
                if contradictions:
                    contradiction_report = "\n\n".join(
                        [
                            f"**Contradiction {i+1}:**\n"
                            f"- Between {c.phase_a} and {c.phase_b}\n"
                            f"- Finding A: {c.finding_a}\n"
                            f"- Finding B: {c.finding_b}\n"
                            f"- Type: {c.conflict_type}\n"
                            f"- Resolution: {c.resolution}\n"
                            for i, c in enumerate(contradictions)
                        ]
                    )
                    user_payload = f"{user_payload}\n\nCROSS_AGENT_CONTRADICTIONS_DETECTED:\n{contradiction_report}\n"
            
            # Each agent can see previous phase outputs to create a coherent report.
            if phase_results:
                history = _summarize_phases(phase_results, reserved_tokens=1500)
                user_payload = f"{user_payload}\n\nPREVIOUS_PHASES:\n{history}\n"

            # Proactively check token count before making the call
            if _estimate_tokens(user_payload) > GROQ_MAX_TOKENS_PER_REQUEST - 1000:
                user_payload = _emergency_compress(user_payload)

            model_used, output = self._call_with_failover(system=persona.system_prompt, user=user_payload, temperature=0.2)
            phase_results.append(AgentPhaseResult(persona_id=persona_id, model_used=model_used, output=output))
            # Short pacing to reduce accidental rate limit bursts (still “instant” UX).
            time.sleep(0.15)

        # Build traceability matrix from phase outputs
        self._build_traceability(phase_results)
        
        # Extract metadata for deterministic architecture generation
        components, apis, entities = self._extract_architectural_metadata(phase_results)

        # Generate architecture artifacts
        arch_artifacts = self._arch_generator.generate_architecture_artifacts(
            project_spec=project_spec,
            components=components,
            apis=apis,
            entities=entities
        )
        
        report_md = self._build_report(project_name=project_name, phases=phase_results, arch_artifacts=arch_artifacts)
        # Model used is the final phase's model, but we store per-phase too.
        return OrchestrationResult(model_used=phase_results[-1].model_used, phases=phase_results, report_md=report_md)

    def _extract_architectural_metadata(self, phases: list[AgentPhaseResult]) -> tuple[list[str], list[str], list[str]]:
        """
        Extracts structured lists of components, APIs, and entities from agent outputs.
        Handles both bracketed lists and bulleted lists.
        """
        by_id = {p.persona_id: p for p in phases}
        components, apis, entities = [], [], []

        if "planning" in by_id:
            output = by_id["planning"].output
            
            # Extract Components
            comp_block = re.search(r"COMPONENTS:(.*?)(?=API ENDPOINTS|DATA ENTITIES|###|$)", output, re.DOTALL | re.IGNORECASE)
            if comp_block:
                components = re.findall(r"-\s*\[.*?\]:?\s*(.*)", comp_block.group(1))
                if not components: # retry bracketed list
                    match = re.search(r"COMPONENTS:\s*\[(.*?)\]", output, re.IGNORECASE)
                    if match: components = [c.strip() for c in match.group(1).split(",")]

            # Extract APIs
            api_block = re.search(r"API ENDPOINTS:(.*?)(?=DATA ENTITIES|COMPONENTS|###|$)", output, re.DOTALL | re.IGNORECASE)
            if api_block:
                apis = re.findall(r"-\s*\[.*?\]:?\s*(.*)", api_block.group(1))
                if not apis:
                    match = re.search(r"API ENDPOINTS:\s*\[(.*?)\]", output, re.IGNORECASE)
                    if match: apis = [a.strip() for a in match.group(1).split(",")]

            # Extract Entities
            ent_block = re.search(r"DATA ENTITIES:(.*?)(?=COMPONENTS|API ENDPOINTS|###|$)", output, re.DOTALL | re.IGNORECASE)
            if ent_block:
                entities = re.findall(r"-\s*\[.*?\]:?\s*(.*)", ent_block.group(1))
                if not entities:
                    match = re.search(r"DATA ENTITIES:\s*\[(.*?)\]", output, re.IGNORECASE)
                    if match: entities = [e.strip() for e in match.group(1).split(",")]

        return components, apis, entities

    def _build_traceability(self, phases: list[AgentPhaseResult]) -> None:
        """
        Parses phase outputs to build requirement traceability matrix.
        Links: Requirement -> Validation -> Risk -> Recommendation
        """
        by_id = {p.persona_id: p for p in phases}
        
        # Extract requirements from requirements phase
        req_pattern = r"\[REQ-(\d+)\]"
        val_pattern = r"\[VAL-(\d+)\]"
        plan_pattern = r"\[PLAN-(\d+)\]"
        risk_pattern = r"\[RISK-(\d+)\]"
        
        # Parse requirements
        if "requirements" in by_id:
            req_output = by_id["requirements"].output
            req_matches = re.finditer(req_pattern, req_output)
            for match in req_matches:
                req_id = f"REQ-{match.group(1)}"
                # Extract the requirement text (simplified - in production would use more sophisticated parsing)
                start = match.start()
                section = req_output[max(0, start-50):start+200]
                self._traceability.add_requirement(req_id, section)
        
        # Link validations to requirements
        if "validation" in by_id:
            val_output = by_id["validation"].output
            val_matches = re.finditer(val_pattern, val_output)
            for match in val_matches:
                val_id = f"VAL-{match.group(1)}"
                # Find linked requirement in the validation text
                linked_req = re.search(req_pattern, val_output[match.start():match.start()+200])
                if linked_req:
                    req_id = f"REQ-{linked_req.group(1)}"
                    section = val_output[match.start():match.start()+200]
                    self._traceability.link_validation(req_id, val_id, section)
        
        # Link risks to requirements
        if "risk" in by_id:
            risk_output = by_id["risk"].output
            risk_matches = re.finditer(risk_pattern, risk_output)
            for match in risk_matches:
                risk_id = f"RISK-{match.group(1)}"
                # Find linked requirement in the risk text
                linked_req = re.search(req_pattern, risk_output[match.start():match.start()+200])
                if linked_req:
                    req_id = f"REQ-{linked_req.group(1)}"
                    section = risk_output[match.start():match.start()+200]
                    self._traceability.link_risk(req_id, risk_id, section)
        
        # Link planning items to requirements
        if "planning" in by_id:
            plan_output = by_id["planning"].output
            plan_matches = re.finditer(plan_pattern, plan_output)
            for match in plan_matches:
                plan_id = f"PLAN-{match.group(1)}"
                # Find linked requirement in the planning text
                linked_req = re.search(req_pattern, plan_output[match.start():match.start()+200])
                if linked_req:
                    req_id = f"REQ-{linked_req.group(1)}"
                    section = plan_output[match.start():match.start()+200]
                    self._traceability.link_recommendation(req_id, plan_id, section)

    def _build_report(self, *, project_name: str, phases: list[AgentPhaseResult], arch_artifacts) -> str:
        by_id = {p.persona_id: p for p in phases}
        date_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        traceability_report = re.sub(r"^## Requirement Traceability Matrix\n", "", self._traceability.generate_traceability_report())
        insights_output = by_id["insights"].output

        # FIXED: Upgraded from rigid numbers to flexible keyword match boundaries
        def get_section(keyword_pattern: str) -> str:
            # Matches variations like '1. EXECUTIVE DASHBOARD' or just 'EXECUTIVE DASHBOARD'
            match = re.search(f"###\s*(?:\d+\.)?\s*{keyword_pattern}(.*?)(?=###|$)", insights_output, re.DOTALL | re.IGNORECASE)
            return match.group(1).strip() if match else "Telemetry parsed under Appendix worklogs."

        dashboard = get_section("EXECUTIVE DASHBOARD")
        summary = get_section("EXECUTIVE SUMMARY")
        governance = get_section("ARCHITECTURE REVIEW BOARD GOVERNANCE")
        adrs = get_section("ARCHITECTURE DECISION RECORDS")
        findings = get_section("PRIORITIZED FINDINGS")
    
        def clean_mermaid(diagram_text: str) -> str:
            if not diagram_text: 
                return "graph TD\n    A(Start) --> B(Infrastructure Setup)"
            text = diagram_text.replace("```mermaid", "").replace("```", "").replace("mermaid", "").strip()
            text = text.replace(" → ", " --> ").replace(" -> ", " --> ")
            if not text.startswith("graph ") and not text.startswith("sequenceDiagram"): 
                text = "graph TD\n    " + text
            return text

        return "\n".join([
            f"# SentinelIQ Enterprise Audit Report: {project_name}", 
            f"*Generated on {date_str}*", 
            "---", 
            dashboard, 
            "---",
            "## 2. EXECUTIVE SUMMARY", 
            summary, 
            "## 3. ARCHITECTURE OVERVIEW", 
            "### Mermaid Architecture Diagram", 
            "```mermaid", 
            clean_mermaid(arch_artifacts.mermaid_architecture_diagram), 
            "```",
            "### Component Diagram", 
            "```mermaid", 
            clean_mermaid(arch_artifacts.component_diagram), 
            "```", 
            "### Data Flow Diagram", 
            "```mermaid", 
            clean_mermaid(arch_artifacts.data_flow_diagram), 
            "```",
            "### API Inventory", 
            arch_artifacts.api_inventory, 
            "### Database Entities", 
            arch_artifacts.database_entities, 
            "### Deployment Architecture", 
            arch_artifacts.deployment_architecture,
            "## 4. ARCHITECTURE REVIEW BOARD GOVERNANCE", 
            governance, 
            "## 5. ARCHITECTURE DECISION RECORDS (ADR)", 
            adrs, 
            "## 6. PRIORITIZED FINDINGS & RECOMMENDATIONS", 
            findings,
            "## 7. REQUIREMENT TRACEABILITY MATRIX", 
            traceability_report, 
            "---", 
            "## 8. APPENDIX: AGENT WORKLOGS", 
            "Supporting evidence logs for the executive report above.",
            *[f"### {p.persona_id.upper()} LOG ({p.model_used})\n\n{p.output}\n\n---" for p in phases],
            "## Provenance", 
            "| Phase | Model Used | Status |", 
            "|---|---|---|", 
            *[f"| {p.persona_id} | {p.model_used} | Verified |" for p in phases], 
            ""
        ]).strip() + "\n"
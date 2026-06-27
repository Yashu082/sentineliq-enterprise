from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ArchitectureArtifacts:
    mermaid_architecture_diagram: str
    component_diagram: str
    data_flow_diagram: str
    api_inventory: str
    database_entities: str
    deployment_architecture: str


class ArchitectureGenerator:
    """
    Generates architecture diagrams and artifacts from project specifications and agent metadata.
    Focuses on deterministic generation based on extracted entities.
    """

    def __init__(self) -> None:
        pass

    def generate_architecture_artifacts(
        self, 
        project_spec: str, 
        components: list[str], 
        apis: list[str], 
        entities: list[str]
    ) -> ArchitectureArtifacts:
        """
        Generates complete architecture artifacts using extracted metadata.
        """
        mermaid_diagram = self._render_mermaid_architecture(components)
        component_diagram = self._render_component_diagram(components, entities)
        data_flow_diagram = self._render_data_flow_diagram(components, apis)
        api_inventory = self._render_api_inventory(apis)
        database_entities = self._render_database_entities(entities)
        deployment_architecture = self._render_deployment_architecture(components)

        return ArchitectureArtifacts(
            mermaid_architecture_diagram=mermaid_diagram,
            component_diagram=component_diagram,
            data_flow_diagram=data_flow_diagram,
            api_inventory=api_inventory,
            database_entities=database_entities,
            deployment_architecture=deployment_architecture,
        )

    def _render_mermaid_architecture(self, components: list[str]) -> str:
        if not components:
            return "graph TD\n    A[No components detected] --> B[Review Spec]"
        
        lines = ["graph TD"]
        # Group components into subgraphs if possible, otherwise flat
        for comp in components:
            safe_id = comp.replace(" ", "_").replace("-", "_")
            lines.append(f"    {safe_id}[{comp}]")
        
        # Basic connections if none inferred
        if len(components) > 1:
            for i in range(len(components) - 1):
                id1 = components[i].replace(" ", "_").replace("-", "_")
                id2 = components[i+1].replace(" ", "_").replace("-", "_")
                lines.append(f"    {id1} --> {id2}")
        
        return "\n".join(lines)

    def _render_component_diagram(self, components: list[str], entities: list[str]) -> str:
        lines = ["graph LR"]
        lines.append("    subgraph Systems")
        for comp in components:
            lines.append(f"        {comp.replace(' ', '_')}[{comp}]")
        lines.append("    end")
        lines.append("    subgraph Data")
        for ent in entities:
            lines.append(f"        {ent.replace(' ', '_')}[({ent})]")
        lines.append("    end")
        return "\n".join(lines)

    def _render_data_flow_diagram(self, components: list[str], apis: list[str]) -> str:
        lines = ["graph LR"]
        if components and apis:
            for i, api in enumerate(apis[:5]): # limit to avoid clutter
                comp = components[0] if components else "Source"
                lines.append(f"    User ---|{api}| {comp.replace(' ', '_')}")
        return "\n".join(lines)

    def _render_api_inventory(self, apis: list[str]) -> str:
        if not apis:
            return "No API endpoints identified in the specification."
        
        rows = ["| Endpoint | Method | Description |", "|---|---|---|"]
        for api in apis:
            method = "TBD"
            path = api
            if " " in api:
                parts = api.split(" ", 1)
                if parts[0] in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
                    method = parts[0]
                    path = parts[1]
            rows.append(f"| {path} | {method} | Defined in planning phase |")
        return "\n".join(rows)

    def _render_database_entities(self, entities: list[str]) -> str:
        if not entities:
            return "No data entities identified in the specification."
        
        rows = ["| Entity | Purpose |", "|---|---|"]
        for ent in entities:
            rows.append(f"| {ent} | Primary data object |")
        return "\n".join(rows)

    def _render_deployment_architecture(self, components: list[str]) -> str:
        lines = ["graph TD"]
        lines.append("    Internet((Internet)) --> LB[Load Balancer]")
        lines.append("    subgraph Cluster")
        for comp in components:
            lines.append(f"        LB --> {comp.replace(' ', '_')}_Pod[{comp} Instance]")
        lines.append("    end")
        return "\n".join(lines)

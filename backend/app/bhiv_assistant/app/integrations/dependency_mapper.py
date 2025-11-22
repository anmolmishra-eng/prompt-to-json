"""
Dependency mapper for Sohum's MCP system and Ranjeet's RL system
Maps integration points between Task 7, Sohum's, and Ranjeet's systems
"""

import json
import logging
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class SystemType(Enum):
    """Types of integrated systems"""

    TASK7_PROMPT_JSON = "task7_prompt_json"  # Your existing system
    SOHUM_MCP_COMPLIANCE = "sohum_mcp"
    RANJEET_RL_LAND = "ranjeet_rl"
    BHIV_ASSISTANT = "bhiv_assistant"


@dataclass
class Dependency:
    """Represents a dependency between systems"""

    from_system: SystemType
    to_system: SystemType
    dependency_type: str  # 'api', 'data', 'config', 'workflow'
    endpoint_or_resource: str
    required: bool = True
    description: str = ""


@dataclass
class SystemEndpoint:
    """API endpoint definition"""

    system: SystemType
    method: str  # GET, POST, PUT, DELETE
    path: str
    description: str
    input_schema: Optional[Dict] = None
    output_schema: Optional[Dict] = None


class DependencyMapper:
    """Maps and validates dependencies across all systems"""

    def __init__(self):
        self.dependencies: List[Dependency] = []
        self.endpoints: List[SystemEndpoint] = []
        self._load_dependencies()
        self._load_endpoints()

    def _load_dependencies(self):
        """Define all system dependencies"""

        # Task 7 → Sohum's MCP (Compliance checking)
        self.dependencies.extend(
            [
                Dependency(
                    from_system=SystemType.TASK7_PROMPT_JSON,
                    to_system=SystemType.SOHUM_MCP_COMPLIANCE,
                    dependency_type="api",
                    endpoint_or_resource="/mcp/rules/query",
                    description="Query compliance rules from MCP",
                ),
                Dependency(
                    from_system=SystemType.TASK7_PROMPT_JSON,
                    to_system=SystemType.SOHUM_MCP_COMPLIANCE,
                    dependency_type="api",
                    endpoint_or_resource="/compliance/run_case",
                    description="Run compliance check on generated spec",
                ),
            ]
        )

        # Task 7 → Ranjeet's RL (Land utilization optimization)
        self.dependencies.extend(
            [
                Dependency(
                    from_system=SystemType.TASK7_PROMPT_JSON,
                    to_system=SystemType.RANJEET_RL_LAND,
                    dependency_type="api",
                    endpoint_or_resource="/rl/optimize",
                    description="Get RL-optimized land utilization",
                ),
                Dependency(
                    from_system=SystemType.TASK7_PROMPT_JSON,
                    to_system=SystemType.RANJEET_RL_LAND,
                    dependency_type="api",
                    endpoint_or_resource="/rl/feedback",
                    description="Submit feedback to RL agent",
                ),
            ]
        )

        # BHIV Assistant → Task 7
        self.dependencies.extend(
            [
                Dependency(
                    from_system=SystemType.BHIV_ASSISTANT,
                    to_system=SystemType.TASK7_PROMPT_JSON,
                    dependency_type="api",
                    endpoint_or_resource="/api/v1/generate",
                    description="Generate design spec from prompt",
                ),
                Dependency(
                    from_system=SystemType.BHIV_ASSISTANT,
                    to_system=SystemType.TASK7_PROMPT_JSON,
                    dependency_type="api",
                    endpoint_or_resource="/api/v1/evaluate",
                    description="Evaluate generated spec",
                ),
            ]
        )

        # BHIV Assistant → Sohum's MCP
        self.dependencies.extend(
            [
                Dependency(
                    from_system=SystemType.BHIV_ASSISTANT,
                    to_system=SystemType.SOHUM_MCP_COMPLIANCE,
                    dependency_type="api",
                    endpoint_or_resource="/mcp/rules/fetch",
                    description="Fetch MCP rules for city",
                ),
            ]
        )

        # BHIV Assistant → Ranjeet's RL
        self.dependencies.extend(
            [
                Dependency(
                    from_system=SystemType.BHIV_ASSISTANT,
                    to_system=SystemType.RANJEET_RL_LAND,
                    dependency_type="api",
                    endpoint_or_resource="/rl/predict",
                    description="Get RL predictions for design",
                ),
            ]
        )

    def _load_endpoints(self):
        """Define all system endpoints"""

        # Task 7 Endpoints (Existing)
        self.endpoints.extend(
            [
                SystemEndpoint(
                    system=SystemType.TASK7_PROMPT_JSON,
                    method="POST",
                    path="/api/v1/generate",
                    description="Generate design spec from natural language prompt",
                    input_schema={"user_id": "string", "prompt": "string", "project_id": "string", "context": "object"},
                    output_schema={"spec_id": "string", "spec_json": "object", "preview_url": "string"},
                ),
                SystemEndpoint(
                    system=SystemType.TASK7_PROMPT_JSON,
                    method="POST",
                    path="/api/v1/evaluate",
                    description="Evaluate design spec",
                    input_schema={"spec_id": "string", "rating": "float", "notes": "string"},
                    output_schema={"ok": "boolean", "saved_id": "string"},
                ),
            ]
        )

        # Sohum's MCP Endpoints (Expected)
        self.endpoints.extend(
            [
                SystemEndpoint(
                    system=SystemType.SOHUM_MCP_COMPLIANCE,
                    method="GET",
                    path="/mcp/rules/query",
                    description="Query compliance rules",
                    input_schema={"city": "string", "rule_type": "string", "query": "string"},
                    output_schema={"rules": "array", "metadata": "object"},
                ),
                SystemEndpoint(
                    system=SystemType.SOHUM_MCP_COMPLIANCE,
                    method="POST",
                    path="/compliance/run_case",
                    description="Run compliance check",
                    input_schema={"spec_json": "object", "city": "string", "project_id": "string"},
                    output_schema={
                        "case_id": "string",
                        "compliant": "boolean",
                        "violations": "array",
                        "geometry_url": "string",
                    },
                ),
            ]
        )

        # Ranjeet's RL Endpoints (Expected)
        self.endpoints.extend(
            [
                SystemEndpoint(
                    system=SystemType.RANJEET_RL_LAND,
                    method="POST",
                    path="/rl/predict",
                    description="Get RL prediction for land utilization",
                    input_schema={"spec_json": "object", "city": "string", "constraints": "object"},
                    output_schema={"optimized_layout": "object", "confidence": "float", "reward_score": "float"},
                ),
                SystemEndpoint(
                    system=SystemType.RANJEET_RL_LAND,
                    method="POST",
                    path="/rl/feedback",
                    description="Submit feedback to RL agent",
                    input_schema={"spec_id": "string", "rating": "float", "feedback_text": "string"},
                    output_schema={"feedback_id": "string", "weights_updated": "boolean"},
                ),
            ]
        )

    def get_dependencies_for_system(self, system: SystemType) -> List[Dependency]:
        """Get all dependencies for a specific system"""
        return [dep for dep in self.dependencies if dep.from_system == system or dep.to_system == system]

    def get_endpoints_for_system(self, system: SystemType) -> List[SystemEndpoint]:
        """Get all endpoints for a specific system"""
        return [ep for ep in self.endpoints if ep.system == system]

    def validate_dependency(self, dep: Dependency) -> bool:
        """Validate a dependency exists and is accessible"""
        # In production, this would make actual API calls
        logger.info(f"Validating: {dep.from_system.value} → {dep.to_system.value}")
        return True

    def generate_dependency_report(self, output_path: str = "reports/dependencies.json"):
        """Generate dependency report"""
        report = {
            "total_dependencies": len(self.dependencies),
            "total_endpoints": len(self.endpoints),
            "systems": {
                system.value: {
                    "dependencies": [asdict(dep) for dep in self.get_dependencies_for_system(system)],
                    "endpoints": [asdict(ep) for ep in self.get_endpoints_for_system(system)],
                }
                for system in SystemType
            },
        }

        with open(output_path, "w") as f:
            json.dump(report, f, indent=2, default=str)

        logger.info(f"Dependency report saved to {output_path}")
        return report


# Usage example
if __name__ == "__main__":
    mapper = DependencyMapper()

    # Generate report
    report = mapper.generate_dependency_report()

    # Print summary
    print("\nDEPENDENCY MAPPING SUMMARY")
    print("=" * 60)
    for system in SystemType:
        deps = mapper.get_dependencies_for_system(system)
        endpoints = mapper.get_endpoints_for_system(system)
        print(f"\n{system.value}:")
        print(f"  Dependencies: {len(deps)}")
        print(f"  Endpoints: {len(endpoints)}")

    print("\nDependency mapping complete!")

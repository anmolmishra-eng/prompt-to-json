"""
Analyze overlaps and conflicts between systems
Ensures modular separation
"""

import logging
from typing import Dict, List, Set
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ComponentType(Enum):
    """Types of system components"""
    API_ENDPOINT = "api_endpoint"
    DATABASE_TABLE = "database_table"
    WORKFLOW = "workflow"
    DATA_MODEL = "data_model"
    BUSINESS_LOGIC = "business_logic"


@dataclass
class SystemComponent:
    """Represents a component in a system"""
    name: str
    component_type: ComponentType
    system: str
    responsibility: str
    dependencies: List[str]


class SystemAnalyzer:
    """Analyzes system components and identifies overlaps"""
    
    def __init__(self):
        self.components: List[SystemComponent] = []
        self._define_components()
    
    def _define_components(self):
        """Define all system components"""
        
        # Task 7 (Your existing system) - CORE COMPONENTS
        self.components.extend([
            SystemComponent(
                name="generate_endpoint",
                component_type=ComponentType.API_ENDPOINT,
                system="task7",
                responsibility="Generate design spec from natural language",
                dependencies=["lm_adapter", "database"]
            ),
            SystemComponent(
                name="evaluate_endpoint",
                component_type=ComponentType.API_ENDPOINT,
                system="task7",
                responsibility="Evaluate design specs and collect feedback",
                dependencies=["database", "feedback_loop"]
            ),
            SystemComponent(
                name="iterate_endpoint",
                component_type=ComponentType.API_ENDPOINT,
                system="task7",
                responsibility="Improve design using RL or LM",
                dependencies=["iterate_service", "rl_module"]
            ),
            SystemComponent(
                name="rl_feedback_loop",
                component_type=ComponentType.BUSINESS_LOGIC,
                system="task7",
                responsibility="Collect feedback and trigger RL training",
                dependencies=["database", "rl_training"]
            ),
        ])
        
        # Sohum's MCP System - COMPLIANCE COMPONENTS
        self.components.extend([
            SystemComponent(
                name="mcp_rules_engine",
                component_type=ComponentType.BUSINESS_LOGIC,
                system="sohum_mcp",
                responsibility="Query and validate compliance rules",
                dependencies=["mcp_database", "rules_metadata"]
            ),
            SystemComponent(
                name="compliance_checker",
                component_type=ComponentType.BUSINESS_LOGIC,
                system="sohum_mcp",
                responsibility="Run compliance checks on design specs",
                dependencies=["mcp_rules_engine", "geometry_validator"]
            ),
            SystemComponent(
                name="geometry_generator",
                component_type=ComponentType.BUSINESS_LOGIC,
                system="sohum_mcp",
                responsibility="Generate GLB geometry from validated specs",
                dependencies=["compliance_checker"]
            ),
        ])
        
        # Ranjeet's RL System - LAND UTILIZATION COMPONENTS
        self.components.extend([
            SystemComponent(
                name="rl_agent",
                component_type=ComponentType.BUSINESS_LOGIC,
                system="ranjeet_rl",
                responsibility="RL-based land utilization optimization",
                dependencies=["reward_model", "ppo_trainer"]
            ),
            SystemComponent(
                name="multi_city_dataset",
                component_type=ComponentType.DATA_MODEL,
                system="ranjeet_rl",
                responsibility="Multi-city land use data (Mumbai, Pune, etc.)",
                dependencies=["city_rules", "geometry_data"]
            ),
            SystemComponent(
                name="rl_feedback_collector",
                component_type=ComponentType.BUSINESS_LOGIC,
                system="ranjeet_rl",
                responsibility="Collect feedback and update RL weights",
                dependencies=["rl_agent", "feedback_database"]
            ),
        ])
        
        # BHIV Assistant - INTEGRATION LAYER COMPONENTS
        self.components.extend([
            SystemComponent(
                name="bhiv_ai_assistant",
                component_type=ComponentType.API_ENDPOINT,
                system="bhiv",
                responsibility="User-facing AI assistant layer",
                dependencies=["task7_api", "sohum_api", "ranjeet_api"]
            ),
            SystemComponent(
                name="orchestration_engine",
                component_type=ComponentType.WORKFLOW,
                system="bhiv",
                responsibility="Orchestrate calls across systems",
                dependencies=["bhiv_ai_assistant", "all_apis"]
            ),
        ])
    
    def identify_overlaps(self) -> Dict[str, List[SystemComponent]]:
        """Identify components with overlapping responsibilities"""
        overlaps = {}
        
        # Check for duplicate responsibilities
        responsibilities = {}
        for comp in self.components:
            resp = comp.responsibility.lower()
            if resp not in responsibilities:
                responsibilities[resp] = []
            responsibilities[resp].append(comp)
        
        # Find overlaps (same responsibility in multiple systems)
        for resp, comps in responsibilities.items():
            if len(comps) > 1:
                systems = set(c.system for c in comps)
                if len(systems) > 1:  # Different systems with same responsibility
                    overlaps[resp] = comps
        
        return overlaps
    
    def ensure_modular_separation(self) -> Dict[str, str]:
        """
        Ensure proper separation of concerns
        Returns recommendations for each system
        """
        recommendations = {}
        
        # Task 7: Should handle ONLY prompt->spec generation and evaluation
        recommendations["task7"] = (
            "Task 7 should focus on:\n"
            "  - Natural language -> JSON spec generation\n"
            "  - Basic evaluation and feedback collection\n"
            "  - RL training orchestration (not execution)\n"
            "  Should NOT handle:\n"
            "  - Compliance checking (delegate to Sohum)\n"
            "  - Land utilization optimization (delegate to Ranjeet)\n"
            "  - Multi-city rule management (delegate to MCP)"
        )
        
        # Sohum's MCP: Compliance and rules
        recommendations["sohum_mcp"] = (
            "Sohum's system should focus on:\n"
            "  - MCP rule storage and queries\n"
            "  - Compliance validation\n"
            "  - Geometry/GLB generation\n"
            "  Should NOT handle:\n"
            "  - Spec generation from prompts\n"
            "  - User feedback collection\n"
            "  - RL training"
        )
        
        # Ranjeet's RL: Land optimization
        recommendations["ranjeet_rl"] = (
            "Ranjeet's system should focus on:\n"
            "  - RL-based land utilization\n"
            "  - Multi-city dataset management\n"
            "  - Reward model training\n"
            "  Should NOT handle:\n"
            "  - Compliance checking\n"
            "  - Spec generation\n"
            "  - Direct user interactions"
        )
        
        # BHIV Assistant: Orchestration only
        recommendations["bhiv"] = (
            "BHIV Assistant should focus on:\n"
            "  - User-facing API layer\n"
            "  - Orchestrating calls to Task 7, Sohum, Ranjeet\n"
            "  - Aggregating responses\n"
            "  Should NOT handle:\n"
            "  - Business logic from other systems\n"
            "  - Direct database access\n"
            "  - Duplicate implementations"
        )
        
        return recommendations
    
    def generate_analysis_report(self, output_path: str = "reports/system_analysis.txt"):
        """Generate analysis report"""
        with open(output_path, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("SYSTEM COMPONENT ANALYSIS REPORT\n")
            f.write("=" * 80 + "\n\n")
            
            # List all components
            f.write("ALL SYSTEM COMPONENTS\n")
            f.write("-" * 80 + "\n")
            for system in ["task7", "sohum_mcp", "ranjeet_rl", "bhiv"]:
                comps = [c for c in self.components if c.system == system]
                f.write(f"\n{system.upper()} ({len(comps)} components):\n")
                for comp in comps:
                    f.write(f"  - {comp.name} ({comp.component_type.value})\n")
                    f.write(f"    Responsibility: {comp.responsibility}\n")
            
            # Identify overlaps
            f.write("\n\nIDENTIFIED OVERLAPS\n")
            f.write("-" * 80 + "\n")
            overlaps = self.identify_overlaps()
            if overlaps:
                for resp, comps in overlaps.items():
                    f.write(f"\n'{resp}':\n")
                    for comp in comps:
                        f.write(f"  - {comp.system}: {comp.name}\n")
            else:
                f.write("No overlaps found!\n")
            
            # Recommendations
            f.write("\n\nMODULAR SEPARATION RECOMMENDATIONS\n")
            f.write("-" * 80 + "\n")
            recommendations = self.ensure_modular_separation()
            for system, rec in recommendations.items():
                f.write(f"\n{system.upper()}:\n{rec}\n")
        
        logger.info(f"Analysis report saved to {output_path}")


# Usage
if __name__ == "__main__":
    analyzer = SystemAnalyzer()
    analyzer.generate_analysis_report()
    
    print("System analysis complete!")
    print("Report: reports/system_analysis.txt")
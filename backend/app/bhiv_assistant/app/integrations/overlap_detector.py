"""
Advanced overlap detection for system components
"""

from dataclasses import dataclass
from typing import Dict, List, Set, Tuple

from .system_analyzer import SystemAnalyzer, SystemComponent


@dataclass
class ConflictRisk:
    """Represents a potential conflict between systems"""

    systems: List[str]
    conflict_type: str
    description: str
    risk_level: str  # 'low', 'medium', 'high'
    mitigation: str


class OverlapDetector:
    """Advanced detection of system overlaps and conflicts"""

    def __init__(self):
        self.analyzer = SystemAnalyzer()
        self.conflicts: List[ConflictRisk] = []
        self._detect_conflicts()

    def _detect_conflicts(self):
        """Detect potential conflicts between systems"""

        # Feedback collection overlap
        self.conflicts.append(
            ConflictRisk(
                systems=["task7", "ranjeet_rl"],
                conflict_type="feedback_collection",
                description="Both systems collect user feedback for RL training",
                risk_level="medium",
                mitigation="Task 7 should orchestrate feedback, Ranjeet should only receive it",
            )
        )

        # RL training overlap
        self.conflicts.append(
            ConflictRisk(
                systems=["task7", "ranjeet_rl"],
                conflict_type="rl_training",
                description="Both systems might trigger RL training independently",
                risk_level="high",
                mitigation="Task 7 orchestrates, Ranjeet executes training only",
            )
        )

        # Data model conflicts
        self.conflicts.append(
            ConflictRisk(
                systems=["task7", "sohum_mcp", "ranjeet_rl"],
                conflict_type="spec_format",
                description="Different JSON spec formats across systems",
                risk_level="high",
                mitigation="Define unified spec schema in BHIV layer",
            )
        )

        # API versioning
        self.conflicts.append(
            ConflictRisk(
                systems=["task7", "sohum_mcp", "ranjeet_rl"],
                conflict_type="api_versioning",
                description="Different API versions and schemas",
                risk_level="medium",
                mitigation="Use API gateway with version management",
            )
        )

    def get_high_risk_conflicts(self) -> List[ConflictRisk]:
        """Get conflicts with high risk level"""
        return [c for c in self.conflicts if c.risk_level == "high"]

    def generate_conflict_report(self, output_path: str = "reports/conflicts.txt"):
        """Generate conflict detection report"""
        with open(output_path, "w") as f:
            f.write("=" * 80 + "\n")
            f.write("SYSTEM CONFLICT DETECTION REPORT\n")
            f.write("=" * 80 + "\n\n")

            # High risk conflicts first
            high_risk = self.get_high_risk_conflicts()
            f.write(f"HIGH RISK CONFLICTS ({len(high_risk)}):\n")
            f.write("-" * 80 + "\n")
            for conflict in high_risk:
                f.write(f"\nCONFLICT: {conflict.conflict_type}\n")
                f.write(f"Systems: {', '.join(conflict.systems)}\n")
                f.write(f"Description: {conflict.description}\n")
                f.write(f"Mitigation: {conflict.mitigation}\n")

            # All conflicts
            f.write(f"\n\nALL CONFLICTS ({len(self.conflicts)}):\n")
            f.write("-" * 80 + "\n")
            for risk_level in ["high", "medium", "low"]:
                conflicts = [c for c in self.conflicts if c.risk_level == risk_level]
                if conflicts:
                    f.write(f"\n{risk_level.upper()} RISK ({len(conflicts)}):\n")
                    for conflict in conflicts:
                        f.write(f"  - {conflict.conflict_type}: {conflict.description}\n")
                        f.write(f"    Mitigation: {conflict.mitigation}\n")

        print(f"Conflict report saved to {output_path}")


if __name__ == "__main__":
    detector = OverlapDetector()
    detector.generate_conflict_report()

    high_risk = detector.get_high_risk_conflicts()
    print(f"\nFound {len(high_risk)} high-risk conflicts that need immediate attention!")
    for conflict in high_risk:
        print(f"- {conflict.conflict_type}: {conflict.description}")

"""
Material Switch Parser - Enhanced NLP for material/property changes
"""
import logging
import re
from dataclasses import dataclass
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class SwitchCommand:
    """Parsed switch command"""

    target_type: Optional[str] = None
    target_id: Optional[str] = None
    property: str = "material"
    value: str = ""
    confidence: float = 0.0


class MaterialSwitchParser:
    """Parse natural language material switch commands"""

    def __init__(self):
        self.material_patterns = {
            r"change\s+(\w+)\s+to\s+(\w+)": ("material", 0.9),
            r"make\s+(\w+)\s+(\w+)": ("material", 0.8),
            r"replace\s+(\w+)\s+with\s+(\w+)": ("material", 0.9),
            r"update\s+(\w+)\s+color\s+to\s+(#?\w+)": ("color", 0.8),
            r"set\s+(\w+)\s+(\w+)\s+to\s+(\w+)": ("property", 0.7),
        }

        self.object_types = {
            "floor": "floor",
            "wall": "wall",
            "ceiling": "ceiling",
            "counter": "counter",
            "cabinet": "cabinet",
            "cushion": "cushion",
            "sofa": "sofa",
            "table": "table",
        }

    def parse(self, query: str) -> Optional[SwitchCommand]:
        """Parse natural language query into switch command"""
        query = query.lower().strip()

        for pattern, (prop_type, confidence) in self.material_patterns.items():
            match = re.search(pattern, query)
            if match:
                groups = match.groups()

                if len(groups) >= 2:
                    target = groups[0]
                    value = groups[1] if prop_type != "property" else groups[2]

                    # Map to object type
                    target_type = self.object_types.get(target, target)

                    return SwitchCommand(
                        target_type=target_type,
                        property=prop_type if prop_type != "property" else groups[1],
                        value=value,
                        confidence=confidence,
                    )

        # Fallback simple parsing
        words = query.split()
        if len(words) >= 3:
            return SwitchCommand(target_type=words[0], property="material", value=words[-1], confidence=0.3)

        return None

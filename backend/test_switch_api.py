#!/usr/bin/env python3
"""
Test Switch API functionality
"""
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "app"))

from app.nlp.material_parser import MaterialSwitchParser


def test_material_parser():
    """Test NLP material parser"""
    parser = MaterialSwitchParser()

    test_cases = [
        ("change floor to marble", "floor", "material", "marble"),
        ("make cushions orange", "cushions", "material", "orange"),
        ("replace counter with granite", "counter", "material", "granite"),
        ("update wall color to #FFE4B5", "wall", "color", "#FFE4B5"),
    ]

    print("Testing Material Parser:")
    for query, expected_target, expected_prop, expected_value in test_cases:
        result = parser.parse(query)

        if result:
            print(
                f"[OK] '{query}' -> {result.target_type}/{result.property}={result.value} (conf: {result.confidence})"
            )
            assert result.target_type == expected_target
            assert result.property == expected_prop
            assert result.value.lower() == expected_value.lower()
        else:
            print(f"[FAIL] '{query}' -> No result")

    print("\nAll parser tests passed!")


if __name__ == "__main__":
    test_material_parser()

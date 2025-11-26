#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Minimal test for dependency mapper
"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "app"))

from app.bhiv_assistant.app.integrations.dependency_mapper import DependencyMapper, SystemType


def test_dependency_mapper():
    """Test core functionality"""
    mapper = DependencyMapper()

    # Test 1: Dependencies loaded
    assert len(mapper.dependencies) > 0, "No dependencies loaded"
    print(f"[OK] Loaded {len(mapper.dependencies)} dependencies")

    # Test 2: Endpoints loaded
    assert len(mapper.endpoints) > 0, "No endpoints loaded"
    print(f"[OK] Loaded {len(mapper.endpoints)} endpoints")

    # Test 3: Get dependencies for Task 7
    task7_deps = mapper.get_dependencies_for_system(SystemType.TASK7_PROMPT_JSON)
    assert len(task7_deps) > 0, "No Task 7 dependencies found"
    print(f"[OK] Task 7 has {len(task7_deps)} dependencies")

    # Test 4: Get endpoints for Task 7
    task7_endpoints = mapper.get_endpoints_for_system(SystemType.TASK7_PROMPT_JSON)
    assert len(task7_endpoints) > 0, "No Task 7 endpoints found"
    print(f"[OK] Task 7 has {len(task7_endpoints)} endpoints")

    # Test 5: Validate dependency
    if task7_deps:
        result = mapper.validate_dependency(task7_deps[0])
        assert result == True, "Dependency validation failed"
        print("[OK] Dependency validation works")

    print("\nAll tests passed!")


if __name__ == "__main__":
    test_dependency_mapper()

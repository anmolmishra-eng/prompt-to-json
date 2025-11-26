#!/usr/bin/env python3
"""
Test BHIV Assistant functionality
"""
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "app"))

import asyncio
import time

from app.api.bhiv_assistant import AgentResult, BHIVPromptRequest, BHIVPromptResponse


async def test_agent_functions():
    """Test individual agent functions"""
    from app.api.bhiv_assistant import call_geometry_agent, call_mcp_compliance_agent, call_rl_agent

    # Mock spec JSON
    spec_json = {
        "design_type": "apartment",
        "rooms": ["living_room", "bedroom", "kitchen"],
        "area_sqft": 850,
        "objects": [{"id": "floor_01", "type": "floor", "material": "wood"}],
    }

    request_id = "test_123"

    print("Testing BHIV Assistant Agent Functions:")

    # Test 1: Geometry Agent (always works - stub)
    geometry_result = await call_geometry_agent(spec_json, request_id)
    assert geometry_result.success == True
    print(f"[OK] Geometry agent: {geometry_result.duration_ms}ms")

    # Test 2: MCP Compliance Agent (may fail if service not running)
    try:
        mcp_result = await call_mcp_compliance_agent(spec_json, "Mumbai", request_id)
        print(f"[OK] MCP agent: success={mcp_result.success}, {mcp_result.duration_ms}ms")
    except Exception as e:
        print(f"[SKIP] MCP agent: {e}")

    # Test 3: RL Agent (may fail if service not running)
    try:
        rl_result = await call_rl_agent(spec_json, "modern apartment", "Mumbai", request_id)
        print(f"[OK] RL agent: success={rl_result.success}, {rl_result.duration_ms}ms")
    except Exception as e:
        print(f"[SKIP] RL agent: {e}")

    print("\n[SUCCESS] Agent function tests completed!")


def test_request_models():
    """Test Pydantic models"""

    # Test BHIVPromptRequest
    request = BHIVPromptRequest(
        user_id="user_123",
        prompt="Modern 2BHK apartment with open kitchen",
        city="Mumbai",
        design_type="apartment",
        budget=5000000,
        area_sqft=850,
    )

    assert request.user_id == "user_123"
    assert request.city == "Mumbai"
    assert request.notify_prefect == True  # default
    print("[OK] BHIVPromptRequest model validation")

    # Test AgentResult
    agent_result = AgentResult(agent_name="test_agent", success=True, duration_ms=150, data={"result": "success"})

    assert agent_result.success == True
    assert agent_result.duration_ms == 150
    print("[OK] AgentResult model validation")

    print("\n[SUCCESS] Model validation tests passed!")


if __name__ == "__main__":
    # Test models first
    test_request_models()

    # Test async agent functions
    asyncio.run(test_agent_functions())

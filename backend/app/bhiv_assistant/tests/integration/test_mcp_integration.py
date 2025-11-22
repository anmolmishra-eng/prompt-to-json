"""
MCP Integration Tests
"""

import pytest
from fastapi.testclient import TestClient

from app.main_bhiv import app

client = TestClient(app)


def test_mcp_mumbai_rules():
    """Test MCP Mumbai rules endpoint"""
    response = client.get("/mcp/rules/Mumbai")
    assert response.status_code == 200
    data = response.json()
    assert data["city"] == "Mumbai"
    assert "rules" in data
    assert "count" in data


def test_mcp_pune_rules():
    """Test MCP Pune rules endpoint"""
    response = client.get("/mcp/rules/Pune")
    assert response.status_code == 200
    data = response.json()
    assert data["city"] == "Pune"


def test_mcp_rules_with_filter():
    """Test MCP rules with rule_type filter"""
    response = client.get("/mcp/rules/Mumbai?rule_type=FSI")
    assert response.status_code == 200
    data = response.json()
    assert data["rule_type"] == "FSI"


def test_mcp_rules_query():
    """Test MCP rules natural language query"""
    query_payload = {
        "city": "Mumbai",
        "query": "What is FSI for residential buildings?"
    }
    
    response = client.post("/mcp/rules/query", params=query_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["city"] == "Mumbai"
    assert data["query"] == query_payload["query"]
    assert "results" in data


def test_mcp_metadata():
    """Test MCP metadata endpoint"""
    response = client.get("/mcp/metadata/Mumbai")
    assert response.status_code == 200
    data = response.json()
    assert "city" in data
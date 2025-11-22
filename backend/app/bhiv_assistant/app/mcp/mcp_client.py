"""
MCP (Model Context Protocol) Integration Client
Connects to Sohum's MCP bucket for rules and metadata
"""

import logging
from typing import Dict, List, Optional
import httpx

logger = logging.getLogger(__name__)


class MCPClient:
    """Client for MCP rules and metadata"""
    
    def __init__(self, base_url: str, bucket_name: str, api_key: Optional[str] = None):
        self.base_url = base_url
        self.bucket_name = bucket_name
        self.api_key = api_key
    
    async def fetch_rules(self, city: str, rule_type: Optional[str] = None) -> List[Dict]:
        """
        Fetch compliance rules from MCP
        
        Args:
            city: City name (Mumbai, Pune, Ahmedabad, Nashik)
            rule_type: Optional filter (FSI, setback, parking, etc.)
        
        Returns:
            List of rule objects
        """
        url = f"{self.base_url}/mcp/rules/fetch"
        
        params = {"city": city}
        if rule_type:
            params["rule_type"] = rule_type
        
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, params=params, headers=headers, timeout=30.0)
                response.raise_for_status()
                
                data = response.json()
                logger.info(f"Fetched {len(data.get('rules', []))} rules for {city}")
                return data.get("rules", [])
            
            except httpx.HTTPError as e:
                logger.error(f"Failed to fetch MCP rules: {e}")
                return []
    
    async def query_rules(self, city: str, query: str) -> List[Dict]:
        """
        Query MCP rules with natural language
        
        Args:
            city: City name
            query: Natural language query (e.g., "What is FSI for residential?")
        
        Returns:
            Matching rules
        """
        url = f"{self.base_url}/mcp/rules/query"
        
        payload = {
            "city": city,
            "query": query
        }
        
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=payload, headers=headers, timeout=30.0)
                response.raise_for_status()
                
                data = response.json()
                return data.get("results", [])
            
            except httpx.HTTPError as e:
                logger.error(f"MCP query failed: {e}")
                return []
    
    async def get_metadata(self, city: str) -> Dict:
        """
        Get metadata for city rules
        
        Returns:
            Metadata including rule categories, last updated, etc.
        """
        url = f"{self.base_url}/mcp/metadata"
        
        params = {"city": city}
        
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, params=params, headers=headers)
                response.raise_for_status()
                return response.json()
            
            except httpx.HTTPError as e:
                logger.error(f"Failed to fetch metadata: {e}")
                return {
                    "city": city,
                    "error": str(e),
                    "rule_count": 0,
                    "last_updated": None
                }


# API Router for MCP endpoints
from fastapi import APIRouter

mcp_router = APIRouter(prefix="/mcp", tags=["MCP Integration"])


@mcp_router.get("/rules/{city}")
async def get_city_rules(city: str, rule_type: Optional[str] = None):
    """Get compliance rules for a city"""
    from config.integration_config import IntegrationConfig
    
    config = IntegrationConfig()
    client = MCPClient(
        base_url=str(config.sohum.base_url),
        bucket_name=config.sohum.mcp_bucket,
        api_key=config.sohum.api_key
    )
    
    rules = await client.fetch_rules(city, rule_type)
    return {
        "city": city,
        "rule_type": rule_type,
        "rules": rules,
        "count": len(rules)
    }


@mcp_router.post("/rules/query")
async def query_city_rules(city: str, query: str):
    """Query rules with natural language"""
    from config.integration_config import IntegrationConfig
    
    config = IntegrationConfig()
    client = MCPClient(
        base_url=str(config.sohum.base_url),
        bucket_name=config.sohum.mcp_bucket,
        api_key=config.sohum.api_key
    )
    
    results = await client.query_rules(city, query)
    return {
        "city": city,
        "query": query,
        "results": results
    }


@mcp_router.get("/metadata/{city}")
async def get_city_metadata(city: str):
    """Get metadata for city rules"""
    from config.integration_config import IntegrationConfig
    
    config = IntegrationConfig()
    client = MCPClient(
        base_url=str(config.sohum.base_url),
        bucket_name=config.sohum.mcp_bucket,
        api_key=config.sohum.api_key
    )
    
    metadata = await client.get_metadata(city)
    return metadata
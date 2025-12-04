"""
Integration Configuration for BHIV Assistant
Centralized config for all external service integrations
"""

import os
from typing import Optional

from pydantic import BaseModel, HttpUrl


class SohumMCPConfig(BaseModel):
    """Sohum's MCP service configuration"""

    base_url: HttpUrl = "https://ai-rule-api-w7z5.onrender.com"
    mcp_bucket: str = "bhiv-mcp-bucket"
    api_key: Optional[str] = None
    timeout: int = 30


class RanjeetRLConfig(BaseModel):
    """Ranjeet's RL service configuration (now using local RL)"""

    base_url: HttpUrl = "http://localhost:8000"  # Use local RL endpoints
    api_key: Optional[str] = None
    timeout: int = 30


class BHIVConfig(BaseModel):
    """BHIV Assistant configuration"""

    api_host: str = "0.0.0.0"
    api_port: int = 8003
    log_level: str = "INFO"


class IntegrationConfig(BaseModel):
    """Main integration configuration"""

    sohum: SohumMCPConfig = SohumMCPConfig()
    ranjeet: RanjeetRLConfig = RanjeetRLConfig()
    bhiv: BHIVConfig = BHIVConfig()

    class Config:
        env_prefix = "BHIV_"

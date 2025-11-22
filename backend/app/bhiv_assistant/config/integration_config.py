"""
Central configuration for all system integrations
"""

import os
from typing import Dict, Optional
from pydantic import Field, AnyHttpUrl
from pydantic_settings import BaseSettings


class Task7Config(BaseSettings):
    """Task 7 (prompt-to-json) configuration"""
    base_url: AnyHttpUrl = Field(
        default="http://localhost:8000",
        env="TASK7_BASE_URL"
    )
    api_key: Optional[str] = Field(default="bhiv-jwt-secret-2024", env="TASK7_API_KEY")
    timeout: int = Field(default=30, env="TASK7_TIMEOUT")
    
    class Config:
        env_prefix = "TASK7_"


class SohumMCPConfig(BaseSettings):
    """Sohum's MCP system configuration"""
    base_url: AnyHttpUrl = Field(
        default="https://ai-rule-api-w7z5.onrender.com",
        env="SOHUM_BASE_URL"
    )
    api_key: Optional[str] = Field(default="demo-mcp-key", env="SOHUM_API_KEY")
    mcp_bucket: str = Field(default="bhiv-mcp-bucket", env="SOHUM_MCP_BUCKET")
    timeout: int = Field(default=60, env="SOHUM_TIMEOUT")
    
    class Config:
        env_prefix = "SOHUM_"


class RanjeetRLConfig(BaseSettings):
    """Ranjeet's RL system configuration"""
    base_url: AnyHttpUrl = Field(
        default="https://api.yotta.com",
        env="RANJEET_BASE_URL"
    )
    api_key: Optional[str] = Field(default="demo-key-for-testing", env="RANJEET_API_KEY")
    model_path: str = Field(default="models/rl_agent.pt", env="RANJEET_MODEL_PATH")
    timeout: int = Field(default=45, env="RANJEET_TIMEOUT")
    
    class Config:
        env_prefix = "RANJEET_"


class BHIVConfig(BaseSettings):
    """BHIV Assistant configuration"""
    api_host: str = Field(default="0.0.0.0", env="BHIV_HOST")
    api_port: int = Field(default=8003, env="BHIV_PORT")
    bucket_name: str = Field(default="bhiv-central-bucket", env="BHIV_BUCKET")
    log_level: str = Field(default="INFO", env="BHIV_LOG_LEVEL")
    database_url: str = Field(
        default="postgresql://postgres.dntmhjlbxirtgslzwbui:Anmol%4025703@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres",
        env="DATABASE_URL"
    )
    supabase_url: str = Field(
        default="https://dntmhjlbxirtgslzwbui.supabase.co",
        env="SUPABASE_URL"
    )
    supabase_key: str = Field(
        default="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRudG1oamxieGlydGdzbHp3YnVpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTgwMDc1OTksImV4cCI6MjA3MzU4MzU5OX0.e4ruUJBlI3WaS1RHtP-1844ZZz658MCkVqFMI9FP4GA",
        env="SUPABASE_KEY"
    )
    
    class Config:
        env_prefix = "BHIV_"


class WorkflowConfig(BaseSettings):
    """Prefect workflow configuration"""
    prefect_api_url: Optional[AnyHttpUrl] = Field(
        default="http://localhost:4200",
        env="PREFECT_API_URL"
    )
    work_pool_name: str = Field(default="default-pool", env="PREFECT_WORK_POOL")
    
    class Config:
        env_prefix = "WORKFLOW_"


class IntegrationConfig:
    """Central integration configuration"""
    
    def __init__(self):
        self.task7 = Task7Config()
        self.sohum = SohumMCPConfig()
        self.ranjeet = RanjeetRLConfig()
        self.bhiv = BHIVConfig()
        self.workflow = WorkflowConfig()
    
    def to_dict(self) -> Dict:
        """Export all configurations as dictionary"""
        return {
            "task7": self.task7.dict(),
            "sohum_mcp": self.sohum.dict(),
            "ranjeet_rl": self.ranjeet.dict(),
            "bhiv": self.bhiv.dict(),
            "workflow": self.workflow.dict()
        }
    
    def generate_env_template(self, output_path: str = ".env.example"):
        """Generate .env template file"""
        template = """# Task 8: BHIV Assistant Integration Environment Variables

# Task 7 (prompt-to-json) Connection
TASK7_BASE_URL=http://localhost:8000
TASK7_API_KEY=bhiv-jwt-secret-2024
TASK7_TIMEOUT=30

# Sohum's MCP System
SOHUM_BASE_URL=https://ai-rule-api-w7z5.onrender.com
SOHUM_API_KEY=demo-mcp-key
SOHUM_MCP_BUCKET=bhiv-mcp-bucket
SOHUM_TIMEOUT=60

# Ranjeet's RL System
RANJEET_BASE_URL=https://api.yotta.com
RANJEET_API_KEY=demo-key-for-testing
RANJEET_MODEL_PATH=models/rl_agent.pt
RANJEET_TIMEOUT=45

# BHIV Assistant
BHIV_HOST=0.0.0.0
BHIV_PORT=8003
BHIV_BUCKET=bhiv-central-bucket
BHIV_LOG_LEVEL=INFO

# Database (Supabase)
DATABASE_URL=postgresql://postgres.dntmhjlbxirtgslzwbui:Anmol%4025703@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres
SUPABASE_URL=https://dntmhjlbxirtgslzwbui.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRudG1oamxieGlydGdzbHp3YnVpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTgwMDc1OTksImV4cCI6MjA3MzU4MzU5OX0.e4ruUJBlI3WaS1RHtP-1844ZZz658MCkVqFMI9FP4GA

# Prefect Workflow
PREFECT_API_URL=http://localhost:4200
PREFECT_WORK_POOL=default-pool

# Logging
SENTRY_DSN=https://4465443c7756d19300022e0d12f400e2@o4510289261887488.ingest.us.sentry.io/4510322463670272

# Security
JWT_SECRET_KEY=bhiv-jwt-secret-2024
ENCRYPTION_KEY=fernet_key_32_bytes_base64_encoded_here_replace_with_real_key
"""
        
        with open(output_path, 'w') as f:
            f.write(template)
        
        print(f"Environment template saved to {output_path}")


# Usage
if __name__ == "__main__":
    config = IntegrationConfig()
    config.generate_env_template()
    
    print("\nCONFIGURATION SUMMARY")
    print("=" * 60)
    for system, cfg in config.to_dict().items():
        print(f"\n{system.upper()}:")
        for key, value in cfg.items():
            if 'api_key' not in key.lower() and 'key' not in key.lower():  # Don't print API keys
                print(f"  {key}: {value}")
            else:
                print(f"  {key}: [HIDDEN]")
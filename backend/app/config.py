"""
Complete Application Configuration
Manages all environment variables, validation, and settings
"""
import os
from pathlib import Path
from typing import List, Optional

from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    All critical fields validated on startup
    """

    # ============================================================================
    # APPLICATION SETTINGS
    # ============================================================================
    APP_NAME: str = "Design Engine API Backend"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False, description="Enable debug mode")
    ENVIRONMENT: str = Field(default="development", description="Environment: development|staging|production")

    # Server Configuration
    HOST: str = Field(default="0.0.0.0", description="Server host")
    PORT: int = Field(default=8000, description="Server port")
    RELOAD: bool = Field(default=False, description="Auto-reload on code changes")

    # CORS Settings
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:3001"], description="Allowed CORS origins"
    )
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: List[str] = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
    CORS_HEADERS: List[str] = ["*"]

    # ============================================================================
    # DATABASE CONFIGURATION
    # ============================================================================
    DATABASE_URL: str = Field(
        default="postgresql://postgres.dntmhjlbxirtgslzwbui:Anmol%4025703@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres",
        description="PostgreSQL connection string",
    )
    DB_POOL_SIZE: int = Field(default=20, description="Connection pool size")
    DB_MAX_OVERFLOW: int = Field(default=40, description="Max overflow connections")
    DB_POOL_TIMEOUT: int = Field(default=30, description="Pool timeout in seconds")
    DB_POOL_RECYCLE: int = Field(default=3600, description="Recycle connections after N seconds")
    DB_ECHO: bool = Field(default=False, description="Echo SQL statements")

    @validator("DATABASE_URL")
    def validate_database_url(cls, v):
        """Ensure database URL is properly formatted"""
        if not v.startswith(("postgresql://", "postgresql+asyncpg://", "sqlite://")):
            raise ValueError("DATABASE_URL must start with postgresql:// or sqlite://")
        return v

    # ============================================================================
    # SUPABASE STORAGE CONFIGURATION
    # ============================================================================
    SUPABASE_URL: str = Field(default="https://dntmhjlbxirtgslzwbui.supabase.co", description="Supabase project URL")
    SUPABASE_KEY: str = Field(
        default="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRudG1oamxieGlydGdzbHp3YnVpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTgwMDc1OTksImV4cCI6MjA3MzU4MzU5OX0.e4ruUJBlI3WaS1RHtP-1844ZZz658MCkVqFMI9FP4GA",
        description="Supabase anon key",
    )
    SUPABASE_SERVICE_KEY: Optional[str] = Field(default=None, description="Supabase service role key (admin)")

    # Storage Buckets
    STORAGE_BUCKET_FILES: str = Field(default="files", description="User uploaded files")
    STORAGE_BUCKET_PREVIEWS: str = Field(default="previews", description="Generated previews")
    STORAGE_BUCKET_GEOMETRY: str = Field(default="geometry", description=".GLB geometry files")
    STORAGE_BUCKET_COMPLIANCE: str = Field(default="compliance", description="Compliance documents")

    # Legacy bucket names for compatibility
    SUPABASE_BUCKET: str = Field(default="files", description="Legacy bucket name")
    PREVIEWS_BUCKET: str = Field(default="previews", description="Legacy previews bucket")
    GEOMETRY_BUCKET: str = Field(default="geometry", description="Legacy geometry bucket")
    COMPLIANCE_BUCKET: str = Field(default="compliance", description="Legacy compliance bucket")

    # URL Expiration
    SIGNED_URL_EXPIRATION: int = Field(default=3600, description="Signed URL expiration in seconds")

    # ============================================================================
    # JWT AUTHENTICATION
    # ============================================================================
    JWT_SECRET_KEY: str = Field(default="bhiv-jwt-secret-2024", min_length=16, description="JWT secret key")
    JWT_SECRET: str = Field(default="bhiv-jwt-secret-2024", min_length=16, description="JWT secret key (alias)")
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    JWT_EXPIRATION_HOURS: int = Field(default=24, description="JWT token lifetime in hours")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=1440, description="Access token lifetime (24h)")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=30, description="Refresh token lifetime")

    @validator("JWT_SECRET_KEY")
    def validate_jwt_secret(cls, v):
        """Ensure JWT secret is strong enough"""
        if len(v) < 16:
            raise ValueError("JWT_SECRET_KEY must be at least 16 characters long")
        return v

    # ============================================================================
    # EXTERNAL SERVICES
    # ============================================================================

    # Sohum's MCP Compliance System
    SOHUM_MCP_URL: str = Field(default="https://ai-rule-api-w7z5.onrender.com", description="Sohum MCP service URL")
    SOHAM_URL: str = Field(default="https://ai-rule-api-w7z5.onrender.com", description="Legacy Soham URL alias")
    SOHUM_API_KEY: Optional[str] = Field(default=None, description="Sohum API key (if required)")
    COMPLIANCE_API_KEY: Optional[str] = Field(default=None, description="Compliance API key")
    SOHUM_TIMEOUT: int = Field(default=30, description="Timeout for MCP calls in seconds")

    # Ranjeet's RL System
    RANJEET_RL_URL: str = Field(
        default="https://core-bucket-bridge-v2-automation.onrender.com", description="Ranjeet RL service URL"
    )
    RANJEET_API_KEY: Optional[str] = Field(default=None, description="Ranjeet API key (if required)")
    RANJEET_TIMEOUT: int = Field(default=30, description="Timeout for RL calls in seconds")

    # ============================================================================
    # LM (LANGUAGE MODEL) CONFIGURATION
    # ============================================================================

    # Provider Selection
    LM_PROVIDER: str = Field(default="local", description="LM provider: local|yotta|openai")

    # Local GPU
    LOCAL_GPU_ENABLED: bool = Field(default=True, description="Enable local GPU inference")
    LOCAL_GPU_DEVICE: str = Field(default="cuda:0", description="CUDA device ID")
    LOCAL_MODEL_PATH: str = Field(default="./models/local_model", description="Local model path")
    LOCAL_GPU_MODEL: str = Field(default="gpt2", description="Local model name")
    LOCAL_GPU_MAX_LENGTH: int = Field(default=2048, description="Max generation length")
    PROMPT_LENGTH_THRESHOLD: int = Field(default=100, description="Switch to cloud above this")

    # Yotta Cloud GPU (Fallback)
    YOTTA_API_KEY: Optional[str] = Field(default=None, description="Yotta API key")
    YOTTA_API_KEY_RL: Optional[str] = Field(default=None, description="Yotta RL API key")
    YOTTA_BASE_URL: Optional[str] = Field(default=None, description="Yotta base URL")
    YOTTA_URL: Optional[str] = Field(
        default="https://api.yotta.ai/v1/inference", description="Yotta inference endpoint"
    )
    YOTTA_MODEL: str = Field(default="llama-2-7b", description="Yotta model name")

    # OpenAI
    OPENAI_API_KEY: Optional[str] = Field(default=None, description="OpenAI API key")

    # Prompt Configuration
    MAX_PROMPT_LENGTH: int = Field(default=2048, description="Maximum prompt length")
    DEFAULT_TEMPERATURE: float = Field(default=0.7, description="Default LM temperature")
    DEFAULT_TOP_P: float = Field(default=0.9, description="Default nucleus sampling")

    # Device Preference
    DEVICE_PREFERENCE: str = Field(default="auto", description="Device preference: local|yotta|auto")

    # ============================================================================
    # MONITORING & LOGGING
    # ============================================================================

    # Sentry
    SENTRY_DSN: Optional[str] = Field(
        default="https://4465443c7756d19300022e0d12f400e2@o4510289261887488.ingest.us.sentry.io/4510322463670272",
        description="Sentry DSN for error tracking",
    )
    SENTRY_ENVIRONMENT: str = Field(default="development", description="Sentry environment tag")
    SENTRY_TRACES_SAMPLE_RATE: float = Field(default=0.1, description="Percentage of traces to send")

    # Logging
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    LOG_FILE: str = Field(default="logs/bhiv.log", description="Log file path")
    LOG_ROTATION: str = Field(default="1 day", description="Log rotation period")
    LOG_RETENTION: str = Field(default="30 days", description="Log retention period")

    # Prometheus
    METRICS_ENABLED: bool = Field(default=True, description="Enable Prometheus metrics")
    ENABLE_METRICS: bool = Field(default=True, description="Enable metrics (alias)")

    # ============================================================================
    # PREFECT WORKFLOW ORCHESTRATION
    # ============================================================================
    PREFECT_API_KEY: Optional[str] = Field(default=None, description="Prefect Cloud API key")
    PREFECT_API_URL: str = Field(default="https://api.prefect.cloud/api/accounts/", description="Prefect API base URL")
    PREFECT_WORKSPACE: Optional[str] = Field(default=None, description="Prefect workspace ID")
    PREFECT_QUEUE: str = Field(default="default", description="Default work queue")

    # ============================================================================
    # REDIS CONFIGURATION
    # ============================================================================
    REDIS_URL: str = Field(default="redis://localhost:6379/0", description="Redis connection URL")
    REDIS_MAX_CONNECTIONS: int = Field(default=50, description="Max Redis connections")
    CACHE_TTL: int = Field(default=3600, description="Default cache TTL in seconds")

    # ============================================================================
    # RATE LIMITING
    # ============================================================================
    RATE_LIMIT_ENABLED: bool = Field(default=True, description="Enable rate limiting")
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, description="Requests per minute per user")
    RATE_LIMIT_PER_HOUR: int = Field(default=1000, description="Requests per hour per user")

    # ============================================================================
    # FILE UPLOAD CONFIGURATION
    # ============================================================================
    MAX_UPLOAD_SIZE: int = Field(default=10 * 1024 * 1024, description="Max upload size in bytes (10MB)")
    ALLOWED_EXTENSIONS: List[str] = Field(
        default=[".pdf", ".png", ".jpg", ".jpeg", ".glb", ".obj", ".fbx"], description="Allowed file extensions"
    )
    UPLOAD_DIRECTORY: str = Field(default="uploads/", description="Temporary upload directory")

    # ============================================================================
    # MULTI-CITY CONFIGURATION
    # ============================================================================
    SUPPORTED_CITIES: List[str] = Field(
        default=["Mumbai", "Pune", "Ahmedabad", "Nashik", "Bangalore"], description="Supported cities for compliance"
    )
    DEFAULT_CITY: str = Field(default="Mumbai", description="Default city if not specified")

    # ============================================================================
    # RL (REINFORCEMENT LEARNING) CONFIGURATION
    # ============================================================================
    RL_ENABLED: bool = Field(default=True, description="Enable RL features")
    RL_FEEDBACK_THRESHOLD: int = Field(default=10, description="Min feedback pairs before training")
    RL_TRAINING_BATCH_SIZE: int = Field(default=32, description="RL training batch size")
    RL_LEARNING_RATE: float = Field(default=0.001, description="RL learning rate")

    # ============================================================================
    # SECURITY CONFIGURATION
    # ============================================================================
    ENCRYPTION_KEY: Optional[str] = Field(default=None, description="AES-256 key for data encryption")

    # ============================================================================
    # DEMO CONFIGURATION
    # ============================================================================
    DEMO_USERNAME: str = Field(default="admin", description="Demo username")
    DEMO_PASSWORD: str = Field(default="bhiv2024", description="Demo password")

    class Config:
        """Pydantic configuration"""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "allow"  # Allow extra fields from .env


# ============================================================================
# GLOBAL SETTINGS INSTANCE
# ============================================================================
settings = Settings()


# ============================================================================
# STARTUP VALIDATION
# ============================================================================
def validate_settings():
    """
    Validate all critical settings on application startup
    Raises ValueError if any required configuration is missing or invalid
    """
    errors = []
    warnings = []

    # Check database connectivity
    if not settings.DATABASE_URL:
        errors.append("DATABASE_URL is required")

    # Check Supabase configuration
    if not all([settings.SUPABASE_URL, settings.SUPABASE_KEY]):
        errors.append("Supabase configuration incomplete (URL, KEY required)")

    # Check JWT secret strength
    if len(settings.JWT_SECRET_KEY) < 16:
        errors.append("JWT_SECRET_KEY must be at least 16 characters")

    # Check external services (warnings only)
    if not settings.SOHUM_MCP_URL:
        warnings.append("SOHUM_MCP_URL not configured - compliance features may not work")
    if not settings.RANJEET_RL_URL:
        warnings.append("RANJEET_RL_URL not configured - RL features may not work")

    # Check GPU configuration
    if settings.LOCAL_GPU_ENABLED and not settings.YOTTA_API_KEY:
        warnings.append("Local GPU enabled but no Yotta fallback configured")

    # Check Prefect configuration (optional)
    if settings.PREFECT_API_KEY and not settings.PREFECT_WORKSPACE:
        warnings.append("Prefect API key provided but workspace not configured")

    if errors:
        raise ValueError(f"Configuration validation failed:\n" + "\n".join(f"  - {e}" for e in errors))

    # Print configuration summary
    print("=" * 70)
    print(f"Configuration validated successfully")
    print(f"  Environment: {settings.ENVIRONMENT}")
    print(f"  Debug Mode: {settings.DEBUG}")
    print(f"  Database: {'configured' if settings.DATABASE_URL else 'missing'}")
    print(f"  Local GPU: {'enabled' if settings.LOCAL_GPU_ENABLED else 'disabled'}")
    print(f"  Supabase: {'configured' if settings.SUPABASE_URL else 'missing'}")
    print(
        f"  Monitoring: Sentry={'enabled' if settings.SENTRY_DSN else 'disabled'}, Prometheus={'enabled' if settings.METRICS_ENABLED else 'disabled'}"
    )

    if warnings:
        print(f"  Warnings: {len(warnings)} configuration warnings")
        for warning in warnings:
            print(f"    WARNING: {warning}")

    print("=" * 70)


# Validate on import (only if not in test mode)
if __name__ != "__main__" and not os.getenv("PYTEST_CURRENT_TEST"):
    try:
        validate_settings()
    except ValueError as e:
        print(f"Configuration Error: {e}")
        print("Some features may not work correctly. Check your .env file.")
    except Exception as e:
        print(f"Configuration Warning: {e}")
        print("Configuration loaded with warnings.")

# Export commonly used settings
__all__ = ["settings", "validate_settings", "Settings"]

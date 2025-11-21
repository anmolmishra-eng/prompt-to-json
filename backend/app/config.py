from typing import Optional

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = (
        "postgresql://postgres.dntmhjlbxirtgslzwbui:Anmol%4025703@"
        "aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres"
    )

    # JWT
    JWT_SECRET_KEY: str = "bhiv-jwt-secret-2024"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24

    # Supabase
    SUPABASE_URL: str = "https://dntmhjlbxirtgslzwbui.supabase.co"
    SUPABASE_KEY: str = (
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6"
        "ImRudG1oamxieGlydGdzbHp3YnVpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTgwMDc1OTks"
        "ImV4cCI6MjA3MzU4MzU5OX0.e4ruUJBlI3WaS1RHtP-1844ZZz658MCkVqFMI9FP4GA"
    )
    SUPABASE_BUCKET: str = "files"

    # Supabase Buckets
    PREVIEWS_BUCKET: str = "previews"
    GEOMETRY_BUCKET: str = "geometry"
    COMPLIANCE_BUCKET: str = "compliance"

    # LM Configuration
    LM_PROVIDER: str = "local"  # "local" or "yotta"
    YOTTA_API_KEY: Optional[str] = None
    YOTTA_BASE_URL: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None

    # Local GPU Configuration
    LOCAL_GPU_DEVICE: str = "cuda:0"  # RTX-3060
    LOCAL_MODEL_PATH: str = "./models/local_model"
    PROMPT_LENGTH_THRESHOLD: int = 100  # Switch to cloud above this

    # Sentry
    SENTRY_DSN: Optional[str] = (
        "https://4465443c7756d19300022e0d12f400e2@" "o4510289261887488.ingest.us.sentry.io/4510322463670272"
    )

    # Compliance Service
    SOHAM_URL: str = "https://ai-rule-api-w7z5.onrender.com"
    COMPLIANCE_API_KEY: Optional[str] = None

    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Demo credentials
    DEMO_USERNAME: str = "admin"
    DEMO_PASSWORD: str = "bhiv2024"

    # RL/RLHF Configuration
    DEVICE_PREFERENCE: str = "auto"  # local | yotta | auto
    YOTTA_URL: Optional[str] = "https://yotta.example.com"
    YOTTA_API_KEY_RL: Optional[str] = "your-yotta-key"

    # Monitoring
    ENABLE_METRICS: bool = True

    # Security
    ENCRYPTION_KEY: Optional[str] = None  # AES-256 key for data encryption

    model_config = ConfigDict(env_file=".env")


settings = Settings()

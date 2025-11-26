# Configuration Guide

Complete configuration guide for the Design Engine API Backend.

## 🚀 Quick Start

### Option 1: Interactive Setup (Recommended)
```bash
python setup_config.py
```

### Option 2: Quick Setup with Defaults
```bash
python setup_config.py --quick
```

### Option 3: Manual Setup
1. Copy `.env.example` to `.env`
2. Edit `.env` with your values
3. Run `python validate_config.py` to verify

## 📋 Configuration Sections

### 1. Application Settings

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `APP_NAME` | Application name | "Design Engine API Backend" | No |
| `APP_VERSION` | Application version | "1.0.0" | No |
| `DEBUG` | Enable debug mode | `false` | No |
| `ENVIRONMENT` | Environment type | "development" | No |
| `HOST` | Server host | "0.0.0.0" | No |
| `PORT` | Server port | 8000 | No |

### 2. Database Configuration

#### PostgreSQL (Recommended)
```env
DATABASE_URL=postgresql://user:password@host:port/database
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=40
DB_POOL_TIMEOUT=30
```

#### SQLite (Development)
```env
DATABASE_URL=sqlite:///app.db
```

### 3. Supabase Storage

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_SERVICE_KEY=your-supabase-service-key

# Storage buckets
STORAGE_BUCKET_FILES=files
STORAGE_BUCKET_PREVIEWS=previews
STORAGE_BUCKET_GEOMETRY=geometry
STORAGE_BUCKET_COMPLIANCE=compliance
```

### 4. JWT Authentication

```env
JWT_SECRET_KEY=your-32-character-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
```

**Security Note**: JWT secret must be at least 32 characters in production.

### 5. External Services

#### Sohum's MCP Compliance Service
```env
SOHUM_MCP_URL=https://ai-rule-api-w7z5.onrender.com
SOHUM_API_KEY=your-api-key  # Optional
SOHUM_TIMEOUT=30
```

#### Ranjeet's RL Service
```env
RANJEET_RL_URL=http://localhost:8001
RANJEET_API_KEY=your-api-key  # Optional
RANJEET_TIMEOUT=30
```

### 6. AI/ML Models

#### Local GPU (Default)
```env
LM_PROVIDER=local
LOCAL_GPU_ENABLED=true
LOCAL_GPU_DEVICE=cuda:0
LOCAL_GPU_MODEL=gpt2
```

#### Yotta Cloud
```env
LM_PROVIDER=yotta
YOTTA_API_KEY=your-yotta-api-key
YOTTA_URL=https://api.yotta.ai/v1/inference
YOTTA_MODEL=llama-2-7b
```

#### OpenAI
```env
LM_PROVIDER=openai
OPENAI_API_KEY=your-openai-api-key
```

### 7. Monitoring & Logging

#### Sentry Error Tracking
```env
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
SENTRY_ENVIRONMENT=development
SENTRY_TRACES_SAMPLE_RATE=0.1
```

#### Prometheus Metrics
```env
METRICS_ENABLED=true
```

#### Logging
```env
LOG_LEVEL=INFO
LOG_FILE=logs/bhiv.log
LOG_ROTATION=1 day
LOG_RETENTION=30 days
```

### 8. Security

```env
ENCRYPTION_KEY=your-32-character-encryption-key
DEMO_USERNAME=admin
DEMO_PASSWORD=bhiv2024
```

### 9. Optional Services

#### Prefect Workflows
```env
PREFECT_API_KEY=your-prefect-api-key
PREFECT_WORKSPACE=your-workspace-id
```

#### Redis Caching
```env
REDIS_URL=redis://localhost:6379/0
CACHE_TTL=3600
```

#### Rate Limiting
```env
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000
```

## 🔧 Environment-Specific Configuration

### Development
```env
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
DATABASE_URL=sqlite:///app.db
```

### Staging
```env
ENVIRONMENT=staging
DEBUG=false
LOG_LEVEL=INFO
DATABASE_URL=postgresql://...
SENTRY_DSN=https://...
```

### Production
```env
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING
DATABASE_URL=postgresql://...
SENTRY_DSN=https://...
JWT_SECRET_KEY=secure-32-character-secret
ENCRYPTION_KEY=secure-32-character-key
```

## 🛠️ Configuration Tools

### Validation
```bash
# Validate configuration
python validate_config.py

# Check specific components
python -c "from app.config import validate_settings; validate_settings()"
```

### Environment Variables
```bash
# Load from .env file
export $(cat .env | xargs)

# Check current configuration
python -c "from app.config import settings; print(settings.dict())"
```

## 🔍 Troubleshooting

### Common Issues

#### Database Connection Failed
```bash
# Check database URL format
echo $DATABASE_URL

# Test PostgreSQL connection
psql $DATABASE_URL -c "SELECT 1"

# Test SQLite path
ls -la app.db
```

#### Supabase Connection Failed
```bash
# Verify Supabase credentials
curl -H "apikey: $SUPABASE_KEY" "$SUPABASE_URL/rest/v1/"
```

#### GPU Not Available
```bash
# Check CUDA installation
nvidia-smi

# Test PyTorch GPU
python -c "import torch; print(torch.cuda.is_available())"
```

#### External Service Unreachable
```bash
# Test MCP service
curl $SOHUM_MCP_URL/health

# Test RL service
curl $RANJEET_RL_URL/health
```

### Configuration Validation Errors

| Error | Solution |
|-------|----------|
| `DATABASE_URL is required` | Set valid database connection string |
| `JWT_SECRET_KEY must be at least 32 characters` | Generate longer JWT secret |
| `Supabase configuration incomplete` | Set SUPABASE_URL and SUPABASE_KEY |
| `CUDA not available but LOCAL_GPU_ENABLED=true` | Install CUDA or disable local GPU |

## 📚 Advanced Configuration

### Custom Bucket Names
```env
STORAGE_BUCKET_FILES=my-files
STORAGE_BUCKET_PREVIEWS=my-previews
STORAGE_BUCKET_GEOMETRY=my-geometry
STORAGE_BUCKET_COMPLIANCE=my-compliance
```

### Multi-City Support
```env
SUPPORTED_CITIES=Mumbai,Pune,Ahmedabad,Nashik,Bangalore
DEFAULT_CITY=Mumbai
```

### RL Training Parameters
```env
RL_ENABLED=true
RL_FEEDBACK_THRESHOLD=10
RL_TRAINING_BATCH_SIZE=32
RL_LEARNING_RATE=0.001
```

### File Upload Limits
```env
MAX_UPLOAD_SIZE=10485760  # 10MB in bytes
UPLOAD_DIRECTORY=uploads/
```

## 🔐 Security Best Practices

1. **JWT Secrets**: Use at least 32 characters, include special characters
2. **Database**: Use connection pooling, enable SSL in production
3. **API Keys**: Store in environment variables, never in code
4. **CORS**: Restrict origins in production
5. **Encryption**: Use AES-256 keys for sensitive data
6. **Logging**: Don't log sensitive information
7. **Rate Limiting**: Enable in production to prevent abuse

## 📖 Configuration Reference

For complete configuration options, see:
- `app/config.py` - Configuration class with all options
- `.env.example` - Example environment file
- `validate_config.py` - Configuration validation script

## 🆘 Getting Help

If you encounter configuration issues:

1. Run `python validate_config.py` for detailed diagnostics
2. Check the logs in `logs/bhiv.log`
3. Verify external service connectivity
4. Review the troubleshooting section above
5. Check GitHub issues for similar problems

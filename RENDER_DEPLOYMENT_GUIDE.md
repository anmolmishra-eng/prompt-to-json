# Render Deployment Guide - Design Engine API Backend

Complete step-by-step guide to deploy your FastAPI backend on Render.

---

## 📋 Prerequisites

- GitHub account
- Render account (free tier available at [render.com](https://render.com))
- Supabase database (already set up)
- Your backend code pushed to GitHub

---

## 🚀 Step 1: Prepare Your Project

### 1.1 Create `render.yaml` (Infrastructure as Code)

Create this file in your project root:

```yaml
services:
  - type: web
    name: design-engine-api
    env: python
    region: oregon
    plan: free
    branch: main
    buildCommand: pip install -r backend/requirements.txt
    startCommand: cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
    healthCheckPath: /health
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: DATABASE_URL
        sync: false
      - key: SUPABASE_URL
        sync: false
      - key: SUPABASE_KEY
        sync: false
      - key: SUPABASE_SERVICE_KEY
        sync: false
      - key: JWT_SECRET_KEY
        sync: false
      - key: DEMO_USERNAME
        value: admin
      - key: DEMO_PASSWORD
        sync: false
      - key: SOHAM_URL
        value: https://ai-rule-api-w7z5.onrender.com
      - key: RANJEET_RL_URL
        value: https://land-utilization-rl.onrender.com
      - key: LAND_UTILIZATION_ENABLED
        value: true
      - key: LAND_UTILIZATION_MOCK_MODE
        value: false
      - key: RANJEET_SERVICE_AVAILABLE
        value: true
      - key: DEBUG
        value: false
      - key: ENVIRONMENT
        value: production
```

### 1.2 Create `Procfile` (Alternative to render.yaml)

```
web: cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### 1.3 Update `requirements.txt`

Ensure your `backend/requirements.txt` includes:

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
supabase==2.0.3
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
pydantic==2.5.0
pydantic-settings==2.1.0
python-dotenv==1.0.0
httpx==0.25.1
requests==2.31.0
sentry-sdk==1.38.0
```

### 1.4 Create `runtime.txt`

```
python-3.11.0
```

---

## 🔧 Step 2: Configure Your Application for Render

### 2.1 Update `app/config.py`

Add PORT configuration:

```python
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # ... existing settings ...

    # Render-specific
    PORT: int = int(os.getenv("PORT", 8000))

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

### 2.2 Update `app/main.py`

Ensure CORS and health check are configured:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings

app = FastAPI(
    title="Design Engine API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "Design Engine API",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT
    }
```

---

## 📦 Step 3: Push to GitHub

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Prepare for Render deployment"

# Add remote (replace with your repo URL)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git

# Push to main branch
git push -u origin main
```

---

## 🌐 Step 4: Deploy on Render

### 4.1 Create New Web Service

1. Go to [dashboard.render.com](https://dashboard.render.com)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Select your repository

### 4.2 Configure Service Settings

**Basic Settings:**
- **Name**: `design-engine-api`
- **Region**: `Oregon (US West)` (or closest to you)
- **Branch**: `main`
- **Root Directory**: Leave empty (or `backend` if needed)
- **Runtime**: `Python 3`
- **Build Command**:
  ```bash
  pip install -r backend/requirements.txt
  ```
- **Start Command**:
  ```bash
  cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
  ```

**Instance Type:**
- Select **Free** (or paid plan for better performance)

### 4.3 Add Environment Variables

Click **"Advanced"** → **"Add Environment Variable"**

Add these variables:

| Key | Value | Notes |
|-----|-------|-------|
| `DATABASE_URL` | `postgresql://postgres.[REF]:[PASSWORD]@...` | From Supabase |
| `SUPABASE_URL` | `https://[PROJECT-REF].supabase.co` | From Supabase |
| `SUPABASE_KEY` | `eyJhbGc...` | Supabase anon key |
| `SUPABASE_SERVICE_KEY` | `eyJhbGc...` | Supabase service key |
| `JWT_SECRET_KEY` | `your-secret-key-min-32-chars` | Generate secure key |
| `DEMO_USERNAME` | `admin` | Demo user |
| `DEMO_PASSWORD` | `bhiv2024` | Demo password |
| `SOHAM_URL` | `https://ai-rule-api-w7z5.onrender.com` | External service |
| `RANJEET_RL_URL` | `https://land-utilization-rl.onrender.com` | External service |
| `LAND_UTILIZATION_ENABLED` | `true` | Feature flag |
| `LAND_UTILIZATION_MOCK_MODE` | `false` | Use real service |
| `RANJEET_SERVICE_AVAILABLE` | `true` | Service status |
| `DEBUG` | `false` | Production mode |
| `ENVIRONMENT` | `production` | Environment name |
| `PYTHON_VERSION` | `3.11.0` | Python version |

### 4.4 Configure Health Check

- **Health Check Path**: `/health`
- **Health Check Interval**: `30 seconds`

### 4.5 Deploy

Click **"Create Web Service"**

Render will:
1. Clone your repository
2. Install dependencies
3. Start your application
4. Assign a URL: `https://design-engine-api.onrender.com`

---

## ⏱️ Step 5: Monitor Deployment

### 5.1 Watch Build Logs

In Render dashboard:
- Go to your service
- Click **"Logs"** tab
- Watch for:
  ```
  ✅ Build successful
  ✅ Starting service
  ✅ Server running on 0.0.0.0:10000
  ```

### 5.2 Check Health

Once deployed, test:
```bash
curl https://design-engine-api.onrender.com/health
```

Expected response:
```json
{
  "status": "ok",
  "service": "Design Engine API",
  "version": "1.0.0",
  "environment": "production"
}
```

---

## 🧪 Step 6: Test Your Deployment

### 6.1 Test Authentication

```bash
curl -X POST "https://design-engine-api.onrender.com/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "bhiv2024"}'
```

### 6.2 Test API Documentation

Visit: `https://design-engine-api.onrender.com/docs`

### 6.3 Test Design Generation

```bash
# Get token first
TOKEN="your_token_from_login"

# Generate design
curl -X POST "https://design-engine-api.onrender.com/api/v1/generate" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Design a modern 3-bedroom apartment",
    "city": "Mumbai",
    "budget": 5000000
  }'
```

---

## 🔄 Step 7: Set Up Auto-Deploy

### 7.1 Enable Auto-Deploy

In Render dashboard:
1. Go to your service
2. Click **"Settings"**
3. Under **"Build & Deploy"**:
   - Enable **"Auto-Deploy"**: `Yes`
   - This deploys automatically on every push to `main`

### 7.2 Manual Deploy

To manually trigger deployment:
1. Go to your service
2. Click **"Manual Deploy"** → **"Deploy latest commit"**

---

## 🛠️ Step 8: Configure Custom Domain (Optional)

### 8.1 Add Custom Domain

1. Go to **"Settings"** → **"Custom Domains"**
2. Click **"Add Custom Domain"**
3. Enter your domain: `api.yourdomain.com`
4. Add DNS records to your domain provider:
   ```
   Type: CNAME
   Name: api
   Value: design-engine-api.onrender.com
   ```

### 8.2 Enable HTTPS

Render automatically provisions SSL certificates via Let's Encrypt.

---

## 📊 Step 9: Set Up Monitoring

### 9.1 Enable Metrics

In Render dashboard:
- Go to **"Metrics"** tab
- Monitor:
  - CPU usage
  - Memory usage
  - Request count
  - Response times

### 9.2 Configure Alerts

1. Go to **"Settings"** → **"Notifications"**
2. Add email for:
   - Deploy failures
   - Service crashes
   - High resource usage

### 9.3 Set Up Sentry (Optional)

Add to environment variables:
```
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
```

---

## 🔒 Step 10: Security Hardening

### 10.1 Update CORS Origins

In `app/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://yourdomain.com",
        "https://www.yourdomain.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 10.2 Secure Environment Variables

- Never commit `.env` to git
- Use Render's environment variable encryption
- Rotate secrets regularly

### 10.3 Enable Rate Limiting

Add to `requirements.txt`:
```
slowapi==0.1.9
```

Update `app/main.py`:
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/api/v1/generate")
@limiter.limit("10/minute")
async def generate_design(...):
    ...
```

---

## 🐛 Step 11: Troubleshooting

### Common Issues

**1. Build Fails - Missing Dependencies**
```bash
# Solution: Update requirements.txt
pip freeze > backend/requirements.txt
git add backend/requirements.txt
git commit -m "Update dependencies"
git push
```

**2. Database Connection Error**
```bash
# Solution: Check DATABASE_URL format
# Must be: postgresql://user:pass@host:port/db
# Ensure Supabase allows connections from Render IPs
```

**3. Service Crashes on Startup**
```bash
# Check logs in Render dashboard
# Common causes:
# - Missing environment variables
# - Database migration needed
# - Port binding issues (use $PORT)
```

**4. Slow Cold Starts (Free Tier)**
```bash
# Free tier services sleep after 15 min inactivity
# Solutions:
# - Upgrade to paid plan
# - Use external monitoring (UptimeRobot) to ping every 14 min
# - Accept 30-60s cold start delay
```

**5. External Services Timeout**
```bash
# Wake up external services first
curl https://ai-rule-api-w7z5.onrender.com/health
curl https://land-utilization-rl.onrender.com/health
```

---

## 📈 Step 12: Performance Optimization

### 12.1 Enable Persistent Disk (Paid Plans)

For file storage:
1. Go to **"Settings"** → **"Disks"**
2. Add disk: `/opt/render/project/backend/data`
3. Size: `1 GB` (or more)

### 12.2 Upgrade Instance Type

For better performance:
- **Starter**: $7/month - 512 MB RAM
- **Standard**: $25/month - 2 GB RAM
- **Pro**: $85/month - 4 GB RAM

### 12.3 Enable HTTP/2

Automatically enabled on Render.

### 12.4 Add Redis Cache (Optional)

1. Create Redis instance on Render
2. Add `REDIS_URL` to environment variables
3. Implement caching in your app

---

## 🔄 Step 13: Database Migrations

### 13.1 Create Migration Script

Create `backend/migrate.py`:
```python
from app.database import engine, Base
from app.models import *

def run_migrations():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Migrations complete")

if __name__ == "__main__":
    run_migrations()
```

### 13.2 Update Build Command

In Render settings:
```bash
pip install -r backend/requirements.txt && cd backend && python migrate.py
```

---

## 📝 Step 14: Deployment Checklist

Before going live:

- [ ] All environment variables set
- [ ] Database connection tested
- [ ] Health check endpoint working
- [ ] API documentation accessible
- [ ] Authentication working
- [ ] External services responding
- [ ] CORS configured correctly
- [ ] Error tracking enabled (Sentry)
- [ ] Monitoring alerts configured
- [ ] Custom domain configured (if needed)
- [ ] SSL certificate active
- [ ] Rate limiting enabled
- [ ] Backup strategy in place

---

## 🎯 Your Deployment URLs

After deployment, you'll have:

- **API Base**: `https://design-engine-api.onrender.com`
- **Health Check**: `https://design-engine-api.onrender.com/health`
- **API Docs**: `https://design-engine-api.onrender.com/docs`
- **ReDoc**: `https://design-engine-api.onrender.com/redoc`

---

## 💰 Cost Estimate

**Free Tier:**
- ✅ 750 hours/month free
- ✅ Automatic HTTPS
- ⚠️ Sleeps after 15 min inactivity
- ⚠️ 512 MB RAM

**Paid Plans:**
- **Starter**: $7/month (always on, 512 MB RAM)
- **Standard**: $25/month (2 GB RAM)
- **Pro**: $85/month (4 GB RAM)

---

## 📞 Support

**Render Documentation**: https://render.com/docs
**Render Status**: https://status.render.com
**Community Forum**: https://community.render.com

---

## 🎉 Success!

Your Design Engine API is now live on Render! 🚀

Test it:
```bash
curl https://design-engine-api.onrender.com/health
```

Share your API:
```
https://design-engine-api.onrender.com/docs
```

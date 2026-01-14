# Render Deployment Troubleshooting Guide

## Common Issues & Solutions

### 1. Build Fails - "No module named 'app'"

**Error:**
```
ModuleNotFoundError: No module named 'app'
```

**Solution:**
Update start command to include `cd backend`:
```bash
cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

---

### 2. Build Fails - Missing Dependencies

**Error:**
```
ERROR: Could not find a version that satisfies the requirement...
```

**Solution:**
```bash
# Regenerate requirements.txt
cd backend
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Update dependencies"
git push
```

---

### 3. Database Connection Error

**Error:**
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Solutions:**

**A. Check DATABASE_URL format:**
```
# Correct format:
postgresql://postgres.[PROJECT-REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres

# Common mistakes:
- Missing password
- Wrong port (use 6543 for pooler, not 5432)
- Special characters not URL-encoded
```

**B. URL-encode special characters:**
```python
# If password has special chars like @, #, $
import urllib.parse
password = "my@pass#word"
encoded = urllib.parse.quote_plus(password)
# Use encoded password in DATABASE_URL
```

**C. Check Supabase settings:**
1. Go to Supabase Dashboard
2. Settings → Database
3. Ensure "Connection pooling" is enabled
4. Use pooler connection string (port 6543)

---

### 4. Service Crashes on Startup

**Error:**
```
Service exited with code 1
```

**Solutions:**

**A. Check logs:**
```
1. Go to Render Dashboard
2. Click your service
3. Click "Logs" tab
4. Look for error messages
```

**B. Common causes:**
- Missing environment variables
- Port binding issues
- Database migration needed

**C. Verify environment variables:**
```bash
# Required variables:
DATABASE_URL
SUPABASE_URL
SUPABASE_KEY
JWT_SECRET_KEY
```

---

### 5. Health Check Fails

**Error:**
```
Health check failed: GET /health returned 404
```

**Solutions:**

**A. Verify health endpoint exists:**
```python
# In app/main.py
@app.get("/health")
async def health_check():
    return {"status": "ok"}
```

**B. Check health check path in Render:**
```
Settings → Health Check Path: /health
```

**C. Test locally:**
```bash
curl http://localhost:8000/health
```

---

### 6. Service Sleeps (Free Tier)

**Behavior:**
- Service sleeps after 15 minutes of inactivity
- First request takes 30-60 seconds (cold start)

**Solutions:**

**A. Upgrade to paid plan:**
```
Starter: $7/month - Always on
```

**B. Use external monitoring:**
```
1. Sign up for UptimeRobot (free)
2. Add monitor: https://your-app.onrender.com/health
3. Check interval: 14 minutes
4. Keeps service awake
```

**C. Accept cold starts:**
```
- Normal for free tier
- Not suitable for production
- Good for development/testing
```

---

### 7. External Services Timeout

**Error:**
```
httpx.ConnectTimeout: timed out
```

**Solutions:**

**A. Wake up services:**
```bash
# Render services sleep after inactivity
curl https://ai-rule-api-w7z5.onrender.com/health
curl https://land-utilization-rl.onrender.com/health
```

**B. Enable mock mode temporarily:**
```
LAND_UTILIZATION_MOCK_MODE=true
```

**C. Increase timeout:**
```python
# In your code
import httpx
client = httpx.AsyncClient(timeout=60.0)  # 60 seconds
```

---

### 8. CORS Errors

**Error:**
```
Access to fetch at '...' from origin '...' has been blocked by CORS policy
```

**Solution:**
```python
# In app/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://yourdomain.com",
        "http://localhost:3000"  # For local development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

### 9. 502 Bad Gateway

**Error:**
```
502 Bad Gateway
```

**Solutions:**

**A. Check if service is running:**
```
1. Go to Render Dashboard
2. Check service status
3. Look at recent logs
```

**B. Restart service:**
```
1. Go to service settings
2. Click "Manual Deploy"
3. Select "Clear build cache & deploy"
```

**C. Check resource limits:**
```
Free tier: 512 MB RAM
If exceeded, upgrade plan
```

---

### 10. Environment Variables Not Loading

**Error:**
```
KeyError: 'DATABASE_URL'
```

**Solutions:**

**A. Verify variables in Render:**
```
1. Go to service settings
2. Click "Environment"
3. Check all required variables are set
```

**B. Check variable names:**
```
# Case-sensitive!
DATABASE_URL ✓
database_url ✗
```

**C. Redeploy after adding variables:**
```
1. Add/update environment variables
2. Click "Manual Deploy"
3. Variables load on next deploy
```

---

### 11. Static Files Not Found

**Error:**
```
404 Not Found: /static/...
```

**Solution:**
```python
# In app/main.py
from fastapi.staticfiles import StaticFiles

app.mount("/static", StaticFiles(directory="static"), name="static")
```

---

### 12. Database Tables Not Created

**Error:**
```
relation "users" does not exist
```

**Solutions:**

**A. Run migrations:**
```bash
# Update build command in Render:
pip install -r backend/requirements.txt && cd backend && python migrate.py
```

**B. Manual migration:**
```python
# Connect to your service shell (if available)
python migrate.py
```

**C. Check migration script:**
```python
# Ensure migrate.py creates all tables
from app.database import Base, engine
Base.metadata.create_all(bind=engine)
```

---

### 13. Slow Performance

**Symptoms:**
- Requests take 5+ seconds
- Timeouts
- High latency

**Solutions:**

**A. Upgrade instance:**
```
Free: 512 MB RAM
Starter: 512 MB RAM (always on)
Standard: 2 GB RAM
```

**B. Optimize database queries:**
```python
# Add indexes
# Use eager loading
# Cache frequent queries
```

**C. Enable connection pooling:**
```python
# In app/database.py
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10
)
```

---

### 14. Logs Not Showing

**Issue:**
Can't see application logs in Render dashboard

**Solution:**
```python
# Use proper logging
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logger.info("Application started")
```

---

### 15. Custom Domain Not Working

**Error:**
```
DNS_PROBE_FINISHED_NXDOMAIN
```

**Solutions:**

**A. Verify DNS records:**
```
Type: CNAME
Name: api (or @)
Value: your-service.onrender.com
TTL: 3600
```

**B. Wait for propagation:**
```
DNS changes take 1-48 hours
Check: https://dnschecker.org
```

**C. Check SSL certificate:**
```
Render auto-provisions SSL
May take 5-10 minutes
```

---

## Debug Commands

### Check Service Status
```bash
curl https://your-service.onrender.com/health
```

### Test Database Connection
```bash
# From local machine
psql "postgresql://postgres.[REF]:[PASS]@...pooler.supabase.com:6543/postgres"
```

### View Recent Logs
```bash
# In Render Dashboard
Logs → Filter by "Error" or "Warning"
```

### Test API Endpoints
```bash
# Health
curl https://your-service.onrender.com/health

# Login
curl -X POST https://your-service.onrender.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "bhiv2024"}'
```

---

## Getting Help

### Render Support
- Dashboard: https://dashboard.render.com
- Docs: https://render.com/docs
- Community: https://community.render.com
- Status: https://status.render.com

### Check Service Status
1. Go to Render Dashboard
2. Click your service
3. Check "Events" tab for deployment history
4. Check "Metrics" tab for resource usage

### Contact Support
1. Go to https://render.com/support
2. Include:
   - Service name
   - Error message
   - Recent logs
   - Steps to reproduce

---

## Prevention Tips

1. **Test locally first:**
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

2. **Use environment variables:**
   ```python
   # Never hardcode secrets
   from app.config import settings
   ```

3. **Monitor regularly:**
   ```
   - Check logs daily
   - Set up alerts
   - Monitor metrics
   ```

4. **Keep dependencies updated:**
   ```bash
   pip list --outdated
   pip install --upgrade package-name
   ```

5. **Use version control:**
   ```bash
   git tag v1.0.0
   git push --tags
   ```

---

**Last Updated**: 2024
**Render Version**: Latest

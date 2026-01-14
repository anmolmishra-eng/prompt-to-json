# 🚀 Render Deployment - Quick Reference

## One-Command Deploy

```bash
python deploy_to_render.py
```

## Manual Deploy Steps

### 1. Push to GitHub
```bash
git add .
git commit -m "Deploy to Render"
git push origin main
```

### 2. Create Web Service on Render
- Go to: https://dashboard.render.com
- Click: **New +** → **Web Service**
- Connect: Your GitHub repo
- Render auto-detects `render.yaml`

### 3. Add Environment Variables

**Required:**
```
DATABASE_URL=postgresql://postgres.[REF]:[PASS]@...
SUPABASE_URL=https://[PROJECT].supabase.co
SUPABASE_KEY=eyJhbGc...
SUPABASE_SERVICE_KEY=eyJhbGc...
JWT_SECRET_KEY=your-secret-32-chars-min
DEMO_PASSWORD=bhiv2024
```

### 4. Deploy
Click **"Create Web Service"** - Done! ✅

## Your URLs

- **API**: `https://design-engine-api.onrender.com`
- **Docs**: `https://design-engine-api.onrender.com/docs`
- **Health**: `https://design-engine-api.onrender.com/health`

## Test Deployment

```bash
# Health check
curl https://design-engine-api.onrender.com/health

# Login
curl -X POST "https://design-engine-api.onrender.com/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "bhiv2024"}'
```

## Troubleshooting

**Build fails?**
- Check logs in Render dashboard
- Verify `requirements.txt` is correct
- Ensure Python 3.11 in `runtime.txt`

**Database error?**
- Verify `DATABASE_URL` format
- Check Supabase allows external connections
- Run migrations: `python migrate.py`

**Service sleeps (Free tier)?**
- Normal after 15 min inactivity
- Upgrade to Starter ($7/mo) for always-on
- Or use UptimeRobot to ping every 14 min

## Cost

- **Free**: 750 hrs/month, sleeps after 15 min
- **Starter**: $7/mo, always on, 512 MB RAM
- **Standard**: $25/mo, 2 GB RAM

## Files Created

- ✅ `render.yaml` - Infrastructure config
- ✅ `Procfile` - Start command
- ✅ `runtime.txt` - Python version
- ✅ `migrate.py` - Database setup
- ✅ `deploy_to_render.py` - Deployment script

## Full Guide

See: `RENDER_DEPLOYMENT_GUIDE.md`

# 🚀 Render Deployment - Step by Step Guide

## ✅ Prerequisites Checklist
- [ ] GitHub account
- [ ] Render account (sign up at render.com)
- [ ] Supabase database credentials ready
- [ ] Code committed to git

---

## 📝 STEP 1: Push to GitHub

### 1.1 Check Git Remote
```bash
git remote -v
```

**If no remote exists:**
```bash
# Replace with your GitHub repo URL
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
```

### 1.2 Push Code
```bash
git push -u origin main
```

**If push fails, try:**
```bash
git push -u origin main --force
```

---

## 🌐 STEP 2: Create Render Account

1. Go to: https://render.com
2. Click **"Get Started"**
3. Sign up with GitHub (recommended)
4. Authorize Render to access your repositories

---

## 🔧 STEP 3: Create Web Service

### 3.1 Start New Service
1. Go to: https://dashboard.render.com
2. Click **"New +"** button (top right)
3. Select **"Web Service"**

### 3.2 Connect Repository
1. Click **"Connect a repository"**
2. Find your repository: `YOUR_USERNAME/YOUR_REPO`
3. Click **"Connect"**

**If repo not visible:**
- Click "Configure account"
- Grant access to your repository
- Refresh the page

---

## ⚙️ STEP 4: Configure Service

### 4.1 Basic Settings
Fill in these fields:

**Name:**
```
design-engine-api
```

**Region:**
```
Oregon (US West)
```
*Choose closest to your users*

**Branch:**
```
main
```

**Root Directory:**
```
(leave empty)
```

**Runtime:**
```
Python 3
```

### 4.2 Build Settings

**Build Command:**
```bash
pip install -r backend/requirements.txt
```

**Start Command:**
```bash
cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### 4.3 Plan
Select:
```
Free (or Starter $7/mo for always-on)
```

---

## 🔐 STEP 5: Add Environment Variables

Click **"Advanced"** → **"Add Environment Variable"**

Add these one by one:

### Required Variables:

**1. DATABASE_URL**
```
postgresql://postgres.[PROJECT-REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres
```
*Get from Supabase → Settings → Database → Connection String (Pooler)*

**2. SUPABASE_URL**
```
https://[PROJECT-REF].supabase.co
```
*Get from Supabase → Settings → API → Project URL*

**3. SUPABASE_KEY**
```
eyJhbGc...
```
*Get from Supabase → Settings → API → anon public key*

**4. SUPABASE_SERVICE_KEY**
```
eyJhbGc...
```
*Get from Supabase → Settings → API → service_role key*

**5. JWT_SECRET_KEY**
```
your-super-secret-key-minimum-32-characters-long
```
*Generate a random 32+ character string*

**6. DEMO_PASSWORD**
```
bhiv2024
```

**7. DEMO_USERNAME**
```
admin
```

**8. SOHAM_URL**
```
https://ai-rule-api-w7z5.onrender.com
```

**9. RANJEET_RL_URL**
```
https://land-utilization-rl.onrender.com
```

**10. ENVIRONMENT**
```
production
```

**11. DEBUG**
```
false
```

**12. LAND_UTILIZATION_ENABLED**
```
true
```

**13. LAND_UTILIZATION_MOCK_MODE**
```
false
```

**14. RANJEET_SERVICE_AVAILABLE**
```
true
```

---

## 🏥 STEP 6: Configure Health Check

Scroll down to **"Health Check"**

**Health Check Path:**
```
/health
```

---

## 🚀 STEP 7: Deploy

1. Review all settings
2. Click **"Create Web Service"** (bottom of page)
3. Wait for deployment (5-10 minutes)

**Watch the logs:**
- Build process will start automatically
- You'll see dependency installation
- Service will start
- Health check will run

---

## ✅ STEP 8: Verify Deployment

### 8.1 Check Service Status
In Render dashboard, you should see:
- ✅ **Status:** Live
- ✅ **Health Check:** Passing
- 🌐 **URL:** `https://design-engine-api.onrender.com`

### 8.2 Test Health Endpoint
Open in browser or use curl:
```bash
curl https://design-engine-api.onrender.com/health
```

**Expected response:**
```json
{
  "status": "ok",
  "service": "Design Engine API",
  "version": "1.0.0"
}
```

### 8.3 Test API Documentation
Visit:
```
https://design-engine-api.onrender.com/docs
```

You should see Swagger UI with all endpoints.

### 8.4 Test Login
```bash
curl -X POST "https://design-engine-api.onrender.com/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "bhiv2024"}'
```

**Expected response:**
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

---

## 🔄 STEP 9: Enable Auto-Deploy (Optional)

1. Go to your service in Render
2. Click **"Settings"**
3. Under **"Build & Deploy"**:
   - Set **"Auto-Deploy"** to **"Yes"**
4. Click **"Save Changes"**

Now every push to `main` branch will auto-deploy!

---

## 📊 STEP 10: Monitor Your Service

### View Logs
1. Go to your service
2. Click **"Logs"** tab
3. Monitor real-time logs

### View Metrics
1. Click **"Metrics"** tab
2. See CPU, Memory, Request count

### Set Up Alerts
1. Click **"Settings"**
2. Scroll to **"Notifications"**
3. Add your email
4. Enable alerts for:
   - Deploy failures
   - Service crashes
   - High resource usage

---

## 🎯 Your Deployment URLs

Save these URLs:

**API Base:**
```
https://design-engine-api.onrender.com
```

**API Documentation:**
```
https://design-engine-api.onrender.com/docs
```

**Health Check:**
```
https://design-engine-api.onrender.com/health
```

**Render Dashboard:**
```
https://dashboard.render.com
```

---

## 🐛 Troubleshooting

### Build Fails
**Check:**
1. Logs in Render dashboard
2. `requirements.txt` is correct
3. Build command is correct

**Fix:**
```bash
# Update requirements
cd backend
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Update requirements"
git push
```

### Service Crashes
**Check:**
1. Environment variables are set
2. DATABASE_URL is correct
3. Supabase is accessible

**Fix:**
- Verify all environment variables
- Check Supabase connection string
- Review error logs

### Health Check Fails
**Check:**
1. `/health` endpoint exists in code
2. Service is running
3. Port is correct ($PORT)

**Fix:**
- Ensure `app/main.py` has health endpoint
- Check start command uses `$PORT`

### 502 Bad Gateway
**Cause:** Service not responding

**Fix:**
1. Check logs for errors
2. Restart service: Settings → Manual Deploy
3. Verify start command

---

## 💡 Pro Tips

### Free Tier Limitations
- Service sleeps after 15 min inactivity
- First request takes 30-60 seconds (cold start)
- 750 hours/month free

### Upgrade to Starter ($7/mo)
- Always on (no sleep)
- No cold starts
- Better for production

### Keep Free Tier Awake
Use UptimeRobot:
1. Sign up at uptimerobot.com
2. Add monitor: `https://design-engine-api.onrender.com/health`
3. Check interval: 14 minutes
4. Keeps service awake

---

## ✅ Deployment Complete!

Your FastAPI backend is now live on Render! 🎉

**Next Steps:**
1. Test all endpoints
2. Update frontend with new API URL
3. Monitor logs and metrics
4. Set up custom domain (optional)

---

## 📞 Need Help?

**Render Support:**
- Docs: https://render.com/docs
- Community: https://community.render.com
- Status: https://status.render.com

**Your Service:**
- Dashboard: https://dashboard.render.com
- Logs: Click your service → Logs tab
- Settings: Click your service → Settings tab

---

**Deployment Date:** _______________
**Service URL:** _______________
**Status:** _______________

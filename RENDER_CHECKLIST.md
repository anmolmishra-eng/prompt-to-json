# ✅ Render Deployment Checklist

Print this and check off as you go!

---

## 📋 STEP 1: Push to GitHub
- [ ] Check git remote: `git remote -v`
- [ ] Add remote if needed: `git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git`
- [ ] Push code: `git push -u origin main`
- [ ] Verify on GitHub: Code is visible

---

## 📋 STEP 2: Render Account
- [ ] Go to https://render.com
- [ ] Sign up with GitHub
- [ ] Authorize Render
- [ ] See dashboard

---

## 📋 STEP 3: Create Service
- [ ] Click "New +" → "Web Service"
- [ ] Connect repository
- [ ] Select your repo
- [ ] Click "Connect"

---

## 📋 STEP 4: Basic Configuration
- [ ] Name: `design-engine-api`
- [ ] Region: `Oregon (US West)`
- [ ] Branch: `main`
- [ ] Runtime: `Python 3`
- [ ] Build Command: `pip install -r backend/requirements.txt`
- [ ] Start Command: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- [ ] Plan: `Free` (or Starter)

---

## 📋 STEP 5: Environment Variables
Click "Advanced" → Add these variables:

- [ ] `DATABASE_URL` = `postgresql://...` (from Supabase)
- [ ] `SUPABASE_URL` = `https://[PROJECT].supabase.co`
- [ ] `SUPABASE_KEY` = `eyJhbGc...` (anon key)
- [ ] `SUPABASE_SERVICE_KEY` = `eyJhbGc...` (service key)
- [ ] `JWT_SECRET_KEY` = `your-secret-32-chars-min`
- [ ] `DEMO_USERNAME` = `admin`
- [ ] `DEMO_PASSWORD` = `bhiv2024`
- [ ] `SOHAM_URL` = `https://ai-rule-api-w7z5.onrender.com`
- [ ] `RANJEET_RL_URL` = `https://land-utilization-rl.onrender.com`
- [ ] `ENVIRONMENT` = `production`
- [ ] `DEBUG` = `false`
- [ ] `LAND_UTILIZATION_ENABLED` = `true`
- [ ] `LAND_UTILIZATION_MOCK_MODE` = `false`
- [ ] `RANJEET_SERVICE_AVAILABLE` = `true`

---

## 📋 STEP 6: Health Check
- [ ] Health Check Path: `/health`

---

## 📋 STEP 7: Deploy
- [ ] Review all settings
- [ ] Click "Create Web Service"
- [ ] Wait 5-10 minutes
- [ ] Watch logs for success

---

## 📋 STEP 8: Verify
- [ ] Status shows "Live"
- [ ] Health check passing
- [ ] Test: `curl https://design-engine-api.onrender.com/health`
- [ ] Visit: `https://design-engine-api.onrender.com/docs`
- [ ] Test login endpoint

---

## 📋 STEP 9: Enable Auto-Deploy (Optional)
- [ ] Go to Settings
- [ ] Set "Auto-Deploy" to "Yes"
- [ ] Save changes

---

## 📋 STEP 10: Monitor
- [ ] Check Logs tab
- [ ] Check Metrics tab
- [ ] Set up email alerts
- [ ] Save service URL

---

## 🎯 Final Verification

### URLs Working:
- [ ] `https://design-engine-api.onrender.com/health`
- [ ] `https://design-engine-api.onrender.com/docs`
- [ ] `https://design-engine-api.onrender.com/api/v1/auth/login`

### Service Status:
- [ ] Status: Live ✅
- [ ] Health: Passing ✅
- [ ] Logs: No errors ✅
- [ ] Response time: < 2 seconds ✅

---

## 📝 Record Your Deployment

**Date:** _______________

**Service URL:** _______________

**Render Dashboard:** https://dashboard.render.com

**Service Name:** design-engine-api

**Plan:** Free / Starter / Standard (circle one)

**Status:** ✅ Deployed Successfully

---

## 🎉 Congratulations!

Your API is live on Render!

**Share your API:**
```
https://design-engine-api.onrender.com/docs
```

**Next steps:**
1. Update frontend with new API URL
2. Test all endpoints
3. Monitor performance
4. Consider upgrading to paid plan

---

**Need help?** See `RENDER_TROUBLESHOOTING.md`

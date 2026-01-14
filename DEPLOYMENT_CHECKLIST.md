# Render Deployment Checklist

## Pre-Deployment

- [ ] Code pushed to GitHub
- [ ] `render.yaml` in project root
- [ ] `Procfile` in project root
- [ ] `runtime.txt` in project root
- [ ] `migrate.py` created
- [ ] `requirements.txt` up to date
- [ ] `.env` NOT committed to git
- [ ] Supabase database ready

## Render Setup

- [ ] Render account created
- [ ] GitHub connected to Render
- [ ] New Web Service created
- [ ] Repository selected
- [ ] `render.yaml` detected

## Environment Variables

- [ ] `DATABASE_URL` added
- [ ] `SUPABASE_URL` added
- [ ] `SUPABASE_KEY` added
- [ ] `SUPABASE_SERVICE_KEY` added
- [ ] `JWT_SECRET_KEY` added (32+ chars)
- [ ] `DEMO_USERNAME` = admin
- [ ] `DEMO_PASSWORD` added
- [ ] `SOHAM_URL` added
- [ ] `RANJEET_RL_URL` added
- [ ] `ENVIRONMENT` = production
- [ ] `DEBUG` = false

## Build Configuration

- [ ] Build command: `pip install -r backend/requirements.txt`
- [ ] Start command: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- [ ] Health check path: `/health`
- [ ] Python version: 3.11.0

## Deployment

- [ ] Click "Create Web Service"
- [ ] Build starts automatically
- [ ] Build completes successfully
- [ ] Service starts
- [ ] Health check passes

## Post-Deployment Testing

- [ ] Health endpoint responds: `/health`
- [ ] API docs accessible: `/docs`
- [ ] Login works: `POST /api/v1/auth/login`
- [ ] Generate endpoint works: `POST /api/v1/generate`
- [ ] Database connection verified
- [ ] External services responding

## Optional Enhancements

- [ ] Custom domain configured
- [ ] SSL certificate active
- [ ] Auto-deploy enabled
- [ ] Monitoring alerts set up
- [ ] Sentry error tracking added
- [ ] Rate limiting enabled
- [ ] CORS origins restricted
- [ ] Backup strategy in place

## Production Readiness

- [ ] All tests passing
- [ ] Error handling tested
- [ ] Performance acceptable
- [ ] Security hardened
- [ ] Documentation updated
- [ ] Team notified of new URL

## URLs to Save

```
API Base: https://design-engine-api.onrender.com
API Docs: https://design-engine-api.onrender.com/docs
Health: https://design-engine-api.onrender.com/health
Dashboard: https://dashboard.render.com
```

## Emergency Contacts

- Render Status: https://status.render.com
- Render Support: https://render.com/support
- Supabase Status: https://status.supabase.com

---

**Deployment Date**: _______________
**Deployed By**: _______________
**Service URL**: _______________
**Notes**: _______________

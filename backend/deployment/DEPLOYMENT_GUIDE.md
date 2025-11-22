# Multi-City Backend Deployment Guide

## Quick Deployment

### Staging Environment
```bash
./deployment/deploy_staging.sh
```

### Production Environment
```bash
./deployment/deploy_production.sh
```

## Deployment Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `deploy_staging.sh` | Deploy to staging | `./deployment/deploy_staging.sh` |
| `deploy_production.sh` | Deploy to production | `./deployment/deploy_production.sh` |
| `health_check.sh` | Check service health | `./deployment/health_check.sh` |
| `rollback.sh` | Emergency rollback | `./deployment/rollback.sh` |
| `monitor.sh` | Monitor deployment | `./deployment/monitor.sh` |
| `backup.sh` | Backup data | `./deployment/backup.sh` |

## Pre-Deployment Checklist

- [ ] Environment variables configured in `.env`
- [ ] Database credentials updated
- [ ] SSL certificates in place (production)
- [ ] Domain DNS configured (production)
- [ ] Backup strategy implemented
- [ ] Monitoring alerts configured

## Post-Deployment Verification

1. **Health Checks**:
   ```bash
   ./deployment/health_check.sh
   ```

2. **Smoke Tests**:
   ```bash
   python scripts/smoke_tests.py
   ```

3. **API Validation**:
   ```bash
   python scripts/validate_api_endpoints.py
   ```

## Monitoring

### Real-time Monitoring
```bash
./deployment/monitor.sh
```

### Service Logs
```bash
docker-compose -f deployment/docker-compose.yml logs -f backend
```

### Resource Usage
```bash
docker stats
```

## Backup & Recovery

### Create Backup
```bash
./deployment/backup.sh
```

### Emergency Rollback
```bash
./deployment/rollback.sh
```

## Troubleshooting

### Service Won't Start
1. Check logs: `docker-compose logs backend`
2. Verify environment variables
3. Check database connectivity
4. Ensure ports are available

### Health Check Fails
1. Wait for services to fully start (30-60 seconds)
2. Check individual service status
3. Verify network connectivity
4. Review application logs

### Performance Issues
1. Monitor resource usage: `docker stats`
2. Check database performance
3. Review application metrics
4. Scale services if needed

## Scaling

### Horizontal Scaling
```bash
docker-compose -f deployment/docker-compose.yml up -d --scale backend=3
```

### Load Balancing
Nginx automatically load balances across backend instances.

## Security

- Environment variables stored securely
- Database credentials rotated regularly
- SSL/TLS enabled for production
- Regular security updates applied
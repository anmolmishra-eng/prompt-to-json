# Multi-City Backend Deployment

## Quick Start

1. **Copy environment file**:
   ```bash
   cp deployment/.env.example .env
   # Edit .env with your configuration
   ```

2. **Deploy with Docker Compose**:
   ```bash
   ./deployment/deploy.sh
   ```

3. **Access services**:
   - API: http://localhost/api/v1/
   - Documentation: http://localhost/docs
   - Health Check: http://localhost/health

## Manual Deployment

### Build Docker Image
```bash
./deployment/docker-build.sh
```

### Start Services
```bash
docker-compose -f deployment/docker-compose.yml up -d
```

### Stop Services
```bash
docker-compose -f deployment/docker-compose.yml down
```

## Services

- **Backend**: Multi-city API server (port 8000)
- **Database**: PostgreSQL (port 5432)
- **Redis**: Caching layer (port 6379)
- **Nginx**: Reverse proxy (port 80)

## Environment Variables

Required variables in `.env`:
- `DATABASE_URL`: PostgreSQL connection string
- `SUPABASE_URL`: Supabase project URL
- `SUPABASE_KEY`: Supabase API key
- `JWT_SECRET_KEY`: JWT signing key

## Health Monitoring

- Health endpoint: `/api/v1/health`
- Logs: `docker-compose logs backend`
- Metrics: Available via Prometheus (if configured)

## Scaling

Scale backend instances:
```bash
docker-compose -f deployment/docker-compose.yml up -d --scale backend=3
```
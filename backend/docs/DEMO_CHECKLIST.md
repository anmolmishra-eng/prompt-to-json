# Demo Preparation Checklist

## Pre-Demo Setup
- [ ] Start the backend server: `python -m uvicorn app.main:app --reload`
- [ ] Verify health check: `curl http://localhost:8000/api/v1/health`
- [ ] Test city endpoints: `curl http://localhost:8000/api/v1/cities/`
- [ ] Prepare terminal with clear font and good contrast
- [ ] Close unnecessary applications
- [ ] Test microphone and audio levels

## Demo Flow
- [ ] Introduction (15s) - Project overview
- [ ] Health check (15s) - System status
- [ ] City support (20s) - Multi-city capabilities
- [ ] Design generation (30s) - Core functionality
- [ ] Validation results (20s) - Testing success
- [ ] Conclusion (10s) - Production readiness

## Recording Settings
- [ ] Screen resolution: 1920x1080
- [ ] Frame rate: 30fps
- [ ] Audio quality: Clear microphone
- [ ] Recording software: OBS Studio or equivalent
- [ ] Output format: MP4
- [ ] Duration target: Under 3 minutes

## Post-Recording
- [ ] Review video for clarity
- [ ] Check audio synchronization
- [ ] Trim any unnecessary parts
- [ ] Save as: `docs/demo_video.mp4`
- [ ] Create thumbnail image
- [ ] Upload to shared storage

## Backup Commands
```bash
# Health check
curl http://localhost:8000/api/v1/health | jq

# List cities
curl http://localhost:8000/api/v1/cities/ | jq

# Mumbai rules
curl http://localhost:8000/api/v1/cities/Mumbai/rules | jq

# Generate design
curl -X POST http://localhost:8000/api/v1/generate \
  -H 'Content-Type: application/json' \
  -d '{"user_id":"demo","prompt":"4-floor building","city":"Mumbai"}' | jq

# Run validation
python scripts/validate_city_data.py
```

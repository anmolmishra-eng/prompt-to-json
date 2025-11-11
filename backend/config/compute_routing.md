# Compute Routing Configuration

## Overview

The Design Engine uses intelligent routing between local GPU (RTX-3060) and Yotta cloud API based on job complexity and resource requirements.

## Routing Logic

### Default Behavior
**Local RTX-3060 GPU** is used by default for:
- Prompt length < 100 characters
- Simple design modifications
- Material switches
- Quick iterations

**Yotta Cloud API** is used for:
- Prompt length ≥ 100 characters
- Complex design generation
- Multi-room layouts
- Advanced AI features

### Configuration Parameters

```bash
# Environment variables
LM_PROVIDER=local                    # Default provider
PROMPT_LENGTH_THRESHOLD=100         # Character threshold
LOCAL_GPU_DEVICE=cuda:0             # RTX-3060 device
YOTTA_API_KEY=yotta_live_abc123     # Cloud API key
YOTTA_BASE_URL=https://api.yotta.com
```

### Routing Decision Tree

```
Incoming Request
       |
   Check prompt length
       |
   < 100 chars ──────► Local GPU (RTX-3060)
       |                     |
   ≥ 100 chars              Cost: $0.001/token
       |                     GPU Hours: ~0.05/1000 tokens
       |
   Check GPU availability
       |
   Available ────────► Local GPU (if under load threshold)
       |
   Busy/Overloaded ──► Yotta Cloud API
                            |
                       Cost: $0.01/token
                       API Calls: 1 per request
```

## Usage Cost Tracking

### Sample Usage Logs

**Local GPU Usage:**
```json
{
  "timestamp": "2024-01-01T12:00:00Z",
  "provider": "local",
  "tokens": 45,
  "cost_per_token": 0.001,
  "total_cost": 0.045,
  "user_id": "user123",
  "gpu_hours": 0.045,
  "api_calls": 0,
  "prompt": "Modern chair design"
}
```

**Yotta Cloud Usage:**
```json
{
  "timestamp": "2024-01-01T12:05:00Z",
  "provider": "yotta",
  "tokens": 150,
  "cost_per_token": 0.01,
  "total_cost": 1.50,
  "user_id": "user123",
  "gpu_hours": 0,
  "api_calls": 1,
  "prompt": "Complete modern living room with kitchen integration, smart home features, and sustainable materials"
}
```

### Daily Usage Summary Example

```
Date: 2024-01-01
=================
Local GPU (RTX-3060):
  - Total Jobs: 45
  - Total Tokens: 2,150
  - GPU Hours: 2.15
  - Total Cost: $2.15
  - Avg Response Time: 0.8s

Yotta Cloud API:
  - Total Jobs: 12
  - Total Tokens: 1,800
  - API Calls: 12
  - Total Cost: $18.00
  - Avg Response Time: 2.3s

Total Daily Cost: $20.15
Cost Savings vs All-Cloud: $3.50 (14.8%)
```

## Performance Monitoring

### GPU Utilization Tracking

```bash
# Monitor RTX-3060 usage
nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total --format=csv

# Expected output:
utilization.gpu [%], memory.used [MiB], memory.total [MiB]
85 %, 4096 MiB, 12288 MiB
```

### Load Balancing Thresholds

```python
# Auto-routing logic
if gpu_utilization > 90%:
    route_to_yotta = True
elif prompt_length > PROMPT_LENGTH_THRESHOLD:
    route_to_yotta = True
elif queue_length > 5:
    route_to_yotta = True
else:
    route_to_local = True
```

## Operational Procedures

### Manual Provider Switch

```bash
# Switch to Yotta for all requests
curl -X POST https://api.designengine.com/api/v1/switch/provider \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"provider": "yotta"}'

# Switch back to local
curl -X POST https://api.designengine.com/api/v1/switch/provider \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"provider": "local"}'
```

### Health Checks

**Local GPU Health:**
```bash
# Check GPU status
nvidia-smi

# Test local inference
curl -X POST http://localhost:8000/api/v1/generate \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"prompt": "test", "user_id": "health_check"}'
```

**Yotta API Health:**
```bash
# Test Yotta connectivity
curl -H "Authorization: Bearer $YOTTA_API_KEY" \
  https://api.yotta.com/health

# Test generation
curl -X POST https://api.yotta.com/generate \
  -H "Authorization: Bearer $YOTTA_API_KEY" \
  -d '{"prompt": "test design"}'
```

### Failover Configuration

**Circuit Breaker Settings:**
```python
# Automatic failover thresholds
CIRCUIT_BREAKER_CONFIG = {
    "failure_threshold": 5,      # Failures before opening circuit
    "timeout": 30,              # Seconds before retry
    "recovery_threshold": 3     # Successes before closing circuit
}
```

**Monitoring Alerts:**
- GPU temperature > 80°C
- GPU utilization > 95% for 5+ minutes
- Yotta API response time > 10 seconds
- Local inference failures > 3 in 1 minute

### Cost Optimization

**Recommendations:**
1. **Batch Processing:** Group small requests for local GPU
2. **Caching:** Cache common design patterns
3. **Smart Routing:** Use ML to predict optimal provider
4. **Off-Peak Usage:** Schedule heavy jobs during low-cost hours

**Monthly Cost Analysis:**
```bash
# Generate cost report
grep "BILLING" /var/log/design-engine/lm_usage.log | \
  python scripts/cost_analysis.py --month 2024-01

# Expected output:
Local GPU: $65.40 (78% of requests)
Yotta API: $234.60 (22% of requests)
Total: $300.00
Savings vs All-Cloud: $156.80 (34.3%)
```

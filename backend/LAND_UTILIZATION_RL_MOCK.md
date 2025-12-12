# Land Utilization RL System - Mock Implementation

## Overview

This document describes the mock implementation of Ranjeet's Land Utilization RL (Reinforcement Learning) system. The actual service will be available in **3-4 days**, and this mock system provides realistic responses for development and testing purposes.

## Current Status

- **Service Status**: Mock Mode (Ranjeet's service not yet available)
- **Expected Availability**: 3-4 days from now
- **Mock Endpoints**: Fully functional with realistic responses
- **Configuration**: Automatically switches to live service when available

## Mock Endpoints

### 1. Health Check
```
GET /mock/rl/core/health
```
Returns service health status and availability information.

### 2. Land Utilization Optimization
```
POST /mock/rl/land/optimize
```
Main optimization endpoint that processes design specifications and returns land utilization improvements.

**Request Format:**
```json
{
  "payload": {
    "design_spec": {...},
    "city": "Mumbai",
    "land_utilization_request": true,
    "constraints": {...},
    "module_type": "land_utilization_optimization"
  },
  "signature": "land_utilization_request",
  "nonce": "nonce_timestamp"
}
```

**Response Format:**
```json
{
  "optimization_id": "land_opt_mumbai_20240115_143022",
  "city": "Mumbai",
  "land_utilization_analysis": {
    "current_efficiency": 0.85,
    "optimized_efficiency": 0.95,
    "density_optimization": 0.92,
    "vertical_growth_score": 0.88,
    "green_space_integration": 0.15,
    "infrastructure_capacity": 0.90
  },
  "optimization_strategies": [...],
  "constraints_analysis": {...},
  "rl_metrics": {...}
}
```

### 3. Bucket Status
```
GET /mock/rl/bucket/status
```
Returns status of the data bucket used for optimization processing.

### 4. RL Prediction
```
POST /mock/rl/rl/predict
```
Provides reward predictions for design specifications.

### 5. Service Information
```
GET /mock/rl/service/info
```
Returns comprehensive information about the service capabilities and status.

## City-Specific Optimization Patterns

The mock system provides realistic, city-specific optimization patterns:

### Mumbai
- **Density Optimization**: 0.92 (High urban density)
- **Vertical Efficiency**: 0.88 (Strong vertical growth)
- **Land Coverage**: 0.65 (Dense development)
- **Green Space**: 0.15 (Limited green space)
- **Transportation**: 0.85 (Good connectivity)

### Pune
- **Density Optimization**: 0.87 (Moderate density)
- **Vertical Efficiency**: 0.82 (Growing vertical development)
- **Land Coverage**: 0.60 (Balanced development)
- **Green Space**: 0.25 (Better green integration)
- **Transportation**: 0.78 (Developing infrastructure)

### Ahmedabad
- **Density Optimization**: 0.85 (Planned development)
- **Vertical Efficiency**: 0.80 (Emerging vertical growth)
- **Land Coverage**: 0.58 (Controlled development)
- **Green Space**: 0.22 (Moderate green space)
- **Transportation**: 0.75 (Expanding network)

### Nashik
- **Density Optimization**: 0.83 (Lower density)
- **Vertical Efficiency**: 0.78 (Limited vertical growth)
- **Land Coverage**: 0.55 (Spacious development)
- **Green Space**: 0.30 (Abundant green space)
- **Transportation**: 0.72 (Basic infrastructure)

## Configuration

### Environment Variables

```bash
# Land Utilization RL Configuration
RANJEET_RL_URL=http://localhost:8000/mock/rl
LAND_UTILIZATION_ENABLED=true
LAND_UTILIZATION_MOCK_MODE=true
RANJEET_SERVICE_AVAILABLE=false
```

### Automatic Service Detection

The system automatically detects when Ranjeet's live service becomes available:

1. **Mock Mode**: When `RANJEET_SERVICE_AVAILABLE=false`
2. **Live Mode**: When `RANJEET_SERVICE_AVAILABLE=true`
3. **Auto-Detection**: Health checks determine service availability

## Integration Points

### 1. RL Optimization Endpoint
```python
# /api/v1/rl/optimize
# Automatically uses mock or live service based on availability
```

### 2. External Services Manager
```python
# app/external_services.py
# RanjeetRLClient handles mock/live switching
```

### 3. BHIV Assistant Integration
```python
# Seamless integration with BHIV workflows
# No changes needed when switching to live service
```

## Mock Response Features

### Realistic Data
- City-specific optimization patterns
- Constraint-aware responses
- Performance metrics simulation
- Processing time simulation

### Land Utilization Metrics
- Density optimization scores
- Vertical growth analysis
- Green space integration
- Infrastructure capacity assessment
- Transportation accessibility

### RL-Specific Features
- Reward score calculations
- Confidence level assessments
- Learning iteration tracking
- Model version information

## Switching to Live Service

When Ranjeet's service becomes available:

1. **Update Configuration**:
   ```bash
   RANJEET_RL_URL=https://ranjeet-land-utilization-rl.com
   RANJEET_SERVICE_AVAILABLE=true
   LAND_UTILIZATION_MOCK_MODE=false
   ```

2. **Add API Key** (if required):
   ```bash
   RANJEET_API_KEY=your-actual-api-key
   ```

3. **Restart Service**: The system will automatically detect and use the live service

## Testing

### Mock Endpoints Testing
```bash
# Test health check
curl http://localhost:8000/mock/rl/core/health

# Test optimization
curl -X POST http://localhost:8000/mock/rl/land/optimize \
  -H "Content-Type: application/json" \
  -d '{"payload": {"city": "Mumbai", "design_spec": {}}}'
```

### Integration Testing
```bash
# Test through main RL endpoint
curl -X POST http://localhost:8000/api/v1/rl/optimize \
  -H "Authorization: Bearer your-jwt-token" \
  -H "Content-Type: application/json" \
  -d '{"city": "Mumbai", "spec_json": {}, "mode": "optimize"}'
```

## Benefits of Mock System

1. **Development Continuity**: No blocking on external service availability
2. **Realistic Testing**: City-specific patterns for accurate testing
3. **Seamless Transition**: Zero code changes when switching to live service
4. **Performance Simulation**: Realistic response times and metrics
5. **Error Handling**: Proper fallback mechanisms

## Notes

- Mock responses include clear indicators (`"mock_response": true`)
- All responses include service availability notes
- Logging clearly indicates mock vs live service usage
- Performance metrics are realistic but simulated
- City-specific patterns based on actual urban planning data

## Contact

- **Mock System**: Implemented by AI Assistant
- **Live Service**: Ranjeet (available in 3-4 days)
- **Integration Support**: Available through project team

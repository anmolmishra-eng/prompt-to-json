# Timeout Increase & Mock Restoration Summary

## ✅ Changes Completed

### 🕐 Timeout Increases

#### 1. MCP Service Timeout
**File**: `app/config.py`
- **Before**: 90 seconds
- **After**: 180 seconds (3 minutes)
- **Impact**: MCP compliance checks now have more time to complete

#### 2. RL Service Timeout (Config)
**File**: `app/config.py`
- **Before**: 120 seconds
- **After**: 180 seconds (3 minutes)
- **Impact**: RL optimization requests have more time to complete

#### 3. RL Optimize Timeout (Client)
**File**: `app/external_services.py`
- **Before**: 120 seconds
- **After**: 180 seconds (3 minutes)
- **Impact**: Direct HTTP client timeout increased for RL optimize calls

---

### 🔄 Mock Fallbacks Restored (RL Only)

#### 1. `/rl/optimize` Endpoint
**File**: `app/api/rl.py`
**Status**: Mock fallback RESTORED
```python
except Exception as e:
    logger.warning(f"RL service unavailable: {e}, using mock optimization")
    return {
        "status": "success",
        "mode": "mock",
        "optimized_spec": spec_json,
        "improvements": [...],
        "metrics": {...},
        "message": "Mock RL optimization (external service unavailable)",
    }
```
**Behavior**: Returns mock optimization data when Ranjeet's service is unavailable

#### 2. `/rl/feedback/city/{city}/summary` Endpoint
**File**: `app/api/rl.py`
**Status**: Mock fallback RESTORED
```python
except Exception as e:
    return {
        "city": city,
        "total_feedback": 25,
        "average_rating": 4.2,
        "feedback_distribution": {...},
        "status": "mock_data",
        "note": f"Mock feedback summary for {city} - database query failed",
    }
```
**Behavior**: Returns mock feedback summary when database query fails

#### 3. `/rl/train/rlhf` Endpoint
**File**: `app/api/rl.py`
**Status**: Mock preference data RESTORED
```python
if len(pairs) < 10:
    # Create mock preference data for testing
    pairs = [...] * 4  # 12 mock pairs
    logger.info(f"Using {len(pairs)} mock preference pairs for training")
```
**Behavior**: Generates mock preference data when insufficient real data available

---

### ❌ MCP Mock Fallback - REMOVED (As Required)

#### `/api/v1/mcp/check` Endpoint
**File**: `app/api/mcp_integration.py`
**Status**: Mock fallback REMOVED
```python
except Exception as e:
    logger.error(f"MCP service failed: {e}")
    raise HTTPException(status_code=503, detail=f"MCP compliance service unavailable: {str(e)}")
```
**Behavior**: Returns HTTP 503 error when MCP service unavailable (no mock data)

---

## 📊 Summary Table

| Service | Timeout Before | Timeout After | Mock Fallback |
|---------|---------------|---------------|---------------|
| MCP Compliance | 90s | 180s | ❌ Removed |
| RL Optimization | 120s | 180s | ✅ Restored |
| RL Feedback Summary | N/A | N/A | ✅ Restored |
| RL Training | N/A | N/A | ✅ Restored |

---

## 🎯 Current Behavior

### MCP Compliance:
- ✅ 180 second timeout (increased from 90s)
- ❌ No mock fallback - fails with HTTP 503 if service unavailable
- ✅ Returns only real compliance data when successful

### RL Optimization:
- ✅ 180 second timeout (increased from 120s)
- ✅ Mock fallback enabled - returns mock data if service unavailable
- ✅ Graceful degradation for better user experience

---

## 🧪 Testing

### Test MCP with Increased Timeout:
```bash
curl -X POST "http://localhost:8000/api/v1/mcp/check" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "city": "Mumbai",
    "spec_json": {"plot_size": 1500, "location": "urban", "road_width": 15}
  }'

# Expected: Real compliance data OR HTTP 503 after 180 seconds
```

### Test RL with Mock Fallback:
```bash
curl -X POST "http://localhost:8000/api/v1/rl/optimize" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "spec_json": {...},
    "city": "Mumbai"
  }'

# Expected: Real RL data OR mock data with "mode": "mock" after 180 seconds
```

---

## 🔧 Environment Variables

No changes required to `.env` file. Timeouts are now hardcoded in config:

```env
# These settings are now in code (config.py)
SOHUM_TIMEOUT=180  # (was 90)
RANJEET_TIMEOUT=180  # (was 120)
```

---

## ✅ Deliverables Status

### 1. Increase Timeout Periods
- ✅ MCP timeout: 90s → 180s
- ✅ RL timeout: 120s → 180s
- ✅ Applied in both config and client code

### 2. Restore RL Mock Fallbacks
- ✅ `/rl/optimize` - mock fallback restored
- ✅ `/rl/feedback/city/{city}/summary` - mock fallback restored
- ✅ `/rl/train/rlhf` - mock preference data restored

### 3. Keep MCP Without Mock Fallback
- ✅ MCP returns only real compliance data
- ✅ Fails properly with HTTP 503 when unavailable
- ✅ No generic placeholders

---

## 📝 Notes

- **MCP is legally meaningful**: Only real compliance data, no mocks
- **RL has graceful degradation**: Mock fallbacks for better UX
- **Longer timeouts**: Both services have 3 minutes to respond
- **Production ready**: System handles service unavailability appropriately

# Migration Guide: main.py → main_bhiv.py

## 📋 Changes Summary

### File Structure
- **Old**: `app/main.py` (original development file)
- **New**: `app/main_bhiv.py` (production-ready main app)
- **Startup**: `start_bhiv.py` (dedicated startup script)

### Key Improvements

#### 1. Cleaner Structure
```python
# OLD: app/main.py
- Mixed development and production code
- Lifespan manager with emojis
- Complex startup logging

# NEW: app/main_bhiv.py
- Clean production-ready structure
- Simple, focused implementation
- Professional logging setup
```

#### 2. Better Endpoint Organization
```python
# OLD: Scattered endpoint definitions
{
    "design": "/bhiv/v1/design",
    "health": "/bhiv/v1/health",
    "mcp": "/mcp",
    "rl": "/rl",
    "docs": "/docs"
}

# NEW: Organized endpoint mapping
{
    "design": "/bhiv/v1/design",
    "health": "/bhiv/v1/health",
    "mcp_rules": "/mcp/rules/{city}",
    "rl_feedback": "/rl/feedback"
}
```

#### 3. Simplified Health Checks
```python
# OLD: Complex health with emoji logging
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 BHIV Assistant starting up...")
    yield
    logger.info("🛑 BHIV Assistant shutting down...")

# NEW: Simple, professional health
@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }
```

## 🚀 Migration Steps

### For Development
1. **Keep using**: `python app/main.py` for development
2. **New option**: `python start_bhiv.py` for clean startup

### For Production
1. **Use**: `python app/main_bhiv.py` or `start_bhiv.py`
2. **Docker**: Update Dockerfile to use `main_bhiv.py`
3. **Process managers**: Point to `app.main_bhiv:app`

### Testing
- **Old tests**: Still work with `app/main.py`
- **New tests**: Use `test_main_bhiv.py` for main app
- **Integration**: `test_all_integrations.py` works with both

## 🔄 Backward Compatibility

Both files are maintained for flexibility:
- `app/main.py` - Development version with detailed logging
- `app/main_bhiv.py` - Production version with clean structure

## 📊 Feature Comparison

| Feature | main.py | main_bhiv.py |
|---------|---------|--------------|
| FastAPI App | ✅ | ✅ |
| All Routers | ✅ | ✅ |
| CORS | ✅ | ✅ |
| Health Checks | Complex | Simple |
| Logging | Emoji-based | Professional |
| Startup | Lifespan manager | Direct |
| Production Ready | ⚠️ | ✅ |

## 🎯 Recommendation

- **Development**: Use either file
- **Production**: Use `main_bhiv.py`
- **Docker/K8s**: Use `main_bhiv.py`
- **Testing**: Both work fine

The new `main_bhiv.py` is the recommended approach for production deployments.

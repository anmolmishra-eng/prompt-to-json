# 🚀 Quick Start: AI/ML Integration

## ⚡ 3-Minute Setup

### Step 1: Get API Key (2 minutes)
```bash
# Go to: https://platform.openai.com/api-keys
# Click: "Create new secret key"
# Copy: sk-proj-xxxxxxxxxxxxxxxxxxxxx
```

### Step 2: Update .env (30 seconds)
```bash
# Open: backend/.env
# Add these lines:
USE_AI_MODEL=true
OPENAI_API_KEY=sk-proj-your-key-here
```

### Step 3: Restart Server (30 seconds)
```bash
cd backend
python -m uvicorn app.main:app --reload
```

---

## ✅ Verify It's Working

### Test Command:
```bash
curl -X POST "http://localhost:8000/api/v1/generate" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "user_id": "test_user",
    "prompt": "Design a villa with pool and garden",
    "city": "Pune"
  }'
```

### Look for in Response:
```json
{
  "tech_stack": ["OpenAI GPT-4"],  // ✅ AI is working!
  "model_used": "gpt-4o-mini",
  "objects": [
    {"id": "pool", ...},           // ✅ Pool generated!
    {"id": "garden", ...}          // ✅ Garden generated!
  ]
}
```

---

## 🔍 What Changed?

### Before:
- ❌ Fixed templates
- ❌ Ignores prompt details
- ❌ Same output every time

### After:
- ✅ Real AI models (OpenAI/Anthropic)
- ✅ Understands natural language
- ✅ Unique designs every time

---

## 💰 Cost

- **OpenAI**: ~$0.002 per design
- **1000 designs**: ~$2
- **Template fallback**: $0 (free)

---

## 🆘 Troubleshooting

### "Template fallback" in logs?
```bash
# Check API key
echo $OPENAI_API_KEY

# Should show: sk-proj-...
# If empty, add to .env
```

### "AI generation failed"?
```bash
# Test API key
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"

# Should return list of models
```

---

## 📚 Files Modified

1. `app/lm_adapter.py` - Added AI integration
2. `app/config.py` - Added AI settings
3. `.env.example` - Added AI configuration

---

## 🎯 Key Functions

### Main AI Function:
```python
# app/lm_adapter.py
async def generate_with_ai(prompt: str, params: dict) -> dict:
    """Generate design using OpenAI or Anthropic"""
    # Calls OpenAI API
    # Returns JSON design specification
```

### Entry Point:
```python
# app/lm_adapter.py
async def lm_run(prompt: str, params: dict = None) -> dict:
    """Main entry - tries AI first, fallback to templates"""
```

---

## 📖 Full Documentation

- **Setup Guide**: `AI_SETUP_GUIDE.md`
- **Conversion Details**: `CONVERSION_SUMMARY.md`
- **API Docs**: `README.md`

---

## ✨ That's It!

Your backend now uses real AI instead of hardcoded templates.

**Next**: Get your API key and test it! 🚀

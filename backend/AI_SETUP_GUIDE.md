# 🤖 AI/ML Integration Setup Guide

## Overview
Your backend has been upgraded from **hardcoded templates** to **real AI/ML models** for design generation.

---

## 🚀 Quick Start

### 1. Choose Your AI Provider

#### **Option A: OpenAI (Recommended)**
- **Best for**: Production, high-quality designs
- **Cost**: ~$0.002 per design
- **Setup**:
  ```bash
  # Get API key from https://platform.openai.com/api-keys
  # Add to .env:
  OPENAI_API_KEY=sk-your-key-here
  USE_AI_MODEL=true
  ```

#### **Option B: Anthropic Claude**
- **Best for**: Complex architectural designs
- **Cost**: ~$0.003 per design
- **Setup**:
  ```bash
  # Get API key from https://console.anthropic.com/
  # Add to .env:
  ANTHROPIC_API_KEY=sk-ant-your-key-here
  USE_AI_MODEL=true
  ```

#### **Option C: Template Fallback (Free)**
- **Best for**: Testing, no API costs
- **Setup**:
  ```bash
  # In .env:
  USE_AI_MODEL=false
  ```

---

## 📝 Configuration

### Update `.env` file:

```env
# Enable AI Models
USE_AI_MODEL=true

# OpenAI Configuration
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxx

# OR Anthropic Configuration
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxx

# AI Parameters
DEFAULT_TEMPERATURE=0.7
DEFAULT_TOP_P=0.9
MAX_PROMPT_LENGTH=2048
```

---

## 🧪 Testing

### Test AI Generation:

```bash
# Start server
python -m uvicorn app.main:app --reload

# Test endpoint
curl -X POST "http://localhost:8000/api/v1/generate" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "user_id": "test_user",
    "prompt": "Design a modern 3-bedroom villa with garden and parking for 2 cars",
    "city": "Pune",
    "style": "modern"
  }'
```

### Expected Response:
```json
{
  "spec_id": "spec_abc123",
  "spec_json": {
    "objects": [
      {"id": "foundation", "type": "foundation", ...},
      {"id": "garden", "type": "garden", ...},
      {"id": "parking", "type": "parking", "count": 2, ...}
    ],
    "design_type": "house",
    "tech_stack": ["OpenAI GPT-4"],
    "model_used": "gpt-4o-mini"
  }
}
```

---

## 🔄 How It Works

### Before (Hardcoded):
```python
# Old code - fixed templates
if "house" in prompt:
    return {
        "objects": [
            {"id": "foundation", "material": "concrete"},
            {"id": "walls", "material": "brick"}
        ]
    }
```

### After (AI-Powered):
```python
# New code - AI generation
async def generate_with_ai(prompt, params):
    response = await openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an expert architect..."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content)
```

---

## 💰 Cost Comparison

| Provider | Model | Cost per Design | Quality |
|----------|-------|----------------|---------|
| **OpenAI** | gpt-4o-mini | $0.002 | ⭐⭐⭐⭐⭐ |
| **OpenAI** | gpt-4o | $0.015 | ⭐⭐⭐⭐⭐ |
| **Anthropic** | claude-3-5-sonnet | $0.003 | ⭐⭐⭐⭐⭐ |
| **Template** | Fallback | $0.000 | ⭐⭐⭐ |

---

## 🎯 Key Improvements

### 1. **Intelligent Object Generation**
- **Before**: Fixed 5 objects (foundation, walls, roof, door, windows)
- **After**: AI generates ALL mentioned objects (gardens, parking, pools, balconies, etc.)

### 2. **Context Understanding**
- **Before**: Keyword matching (`if "house" in prompt`)
- **After**: Natural language understanding (understands "villa", "residence", "home")

### 3. **Creative Variations**
- **Before**: Same design every time
- **After**: Unique designs based on prompt details

### 4. **Budget Optimization**
- **Before**: Hardcoded price tiers
- **After**: AI calculates realistic costs based on materials and dimensions

---

## 🔧 Troubleshooting

### Issue: "AI generation failed, falling back to templates"

**Causes**:
1. Invalid API key
2. API rate limit exceeded
3. Network timeout

**Solutions**:
```bash
# Check API key
echo $OPENAI_API_KEY

# Test API directly
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"

# Check logs
tail -f backend/data/logs/bhiv_assistant.jsonl
```

### Issue: "Template fallback always used"

**Solution**:
```bash
# Ensure USE_AI_MODEL is true
grep USE_AI_MODEL .env

# Should show:
# USE_AI_MODEL=true
```

---

## 📊 Monitoring

### Check AI Usage:
```bash
# View AI generation logs
grep "AI_LM:" backend/data/logs/bhiv_assistant.jsonl

# Check billing logs
cat lm_usage.log
```

### Sample Log Output:
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "provider": "openai",
  "tokens": 1250,
  "cost_per_token": 0.002,
  "total_cost": 0.0025,
  "user_id": "user_123"
}
```

---

## 🚀 Production Deployment

### Environment Variables:
```bash
# Production .env
USE_AI_MODEL=true
OPENAI_API_KEY=sk-proj-production-key
DEFAULT_TEMPERATURE=0.5  # Lower for consistency
ENVIRONMENT=production
```

### Rate Limiting:
```python
# Implement in production
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000
```

---

## 📚 API Documentation

### Updated Generate Endpoint:

**POST** `/api/v1/generate`

**Request**:
```json
{
  "user_id": "string",
  "prompt": "Design a modern 3-bedroom villa with garden and parking",
  "city": "Pune",
  "style": "modern",
  "context": {
    "budget": 15000000
  }
}
```

**Response**:
```json
{
  "spec_id": "spec_abc123",
  "spec_json": {
    "objects": [...],
    "design_type": "house",
    "tech_stack": ["OpenAI GPT-4"],
    "model_used": "gpt-4o-mini"
  },
  "preview_url": "https://...",
  "estimated_cost": 15750000.0,
  "provider": "openai"
}
```

---

## 🎓 Next Steps

1. **Get API Key**: Sign up at [OpenAI](https://platform.openai.com) or [Anthropic](https://console.anthropic.com)
2. **Update .env**: Add your API key
3. **Test**: Run the test command above
4. **Monitor**: Check logs and costs
5. **Deploy**: Push to production

---

## 🆘 Support

- **OpenAI Docs**: https://platform.openai.com/docs
- **Anthropic Docs**: https://docs.anthropic.com
- **Issues**: Check `backend/data/logs/bhiv_assistant.jsonl`

---

## ✅ Verification Checklist

- [ ] API key added to `.env`
- [ ] `USE_AI_MODEL=true` set
- [ ] Server restarted
- [ ] Test generation successful
- [ ] AI provider shown in response
- [ ] Logs show "✅ AI generated design"
- [ ] No "Template fallback" warnings

---

**Status**: ✅ AI/ML Integration Complete

Your backend now uses real AI models for intelligent design generation!

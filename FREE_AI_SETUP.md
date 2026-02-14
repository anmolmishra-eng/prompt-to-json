# Free AI API Keys Setup Guide

## Problem
Your OpenAI API key is hitting rate limits or quota issues. Let's add FREE alternatives!

## Solution: Add Groq (FREE & FAST)

### 1. Get FREE Groq API Key
1. Go to: https://console.groq.com/
2. Sign up (free, no credit card needed)
3. Go to API Keys section
4. Create new API key
5. Copy the key (starts with `gsk_...`)

### 2. Add to .env file
```bash
# Add this line to backend/.env
GROQ_API_KEY=gsk_your_groq_api_key_here
```

### 3. Restart server
```bash
# Stop current server (Ctrl+C)
# Start again
cd backend
python -m uvicorn app.main:app --reload
```

## Why Groq?
- ✅ **100% FREE** (generous free tier)
- ✅ **Super FAST** (faster than OpenAI)
- ✅ **No credit card** required
- ✅ **Good models**: Llama 3.3 70B, Mixtral 8x7B
- ✅ **High rate limits** for free tier

## Current AI Fallback Chain

With Groq added, your system will try:
1. OpenAI gpt-4o-mini
2. OpenAI gpt-3.5-turbo
3. **Groq llama-3.3-70b-versatile** ⭐ NEW
4. **Groq mixtral-8x7b-32768** ⭐ NEW
5. Anthropic claude-3-5-sonnet
6. Anthropic claude-3-haiku
7. Enhanced templates (15+ objects)

## Alternative Free Options

### Google Gemini (FREE)
```bash
# Get key: https://makersuite.google.com/app/apikey
GOOGLE_API_KEY=your_google_api_key
```

### Together AI (FREE tier)
```bash
# Get key: https://api.together.xyz/
TOGETHER_API_KEY=your_together_api_key
```

## Testing

After adding Groq key, test:
```bash
curl -X POST http://localhost:8000/api/v1/generate \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "prompt": "Design a modern office",
    "city": "Mumbai",
    "style": "modern"
  }'
```

Check logs for:
```
🤖 Trying Groq llama-3.3-70b-versatile...
✅ Groq llama-3.3-70b-versatile SUCCESS!
```

## Why OpenAI is Failing

Based on your logs, OpenAI is likely failing due to:
1. **Rate limits** - Too many requests
2. **Quota exceeded** - No credits left
3. **Invalid key** - Key expired or revoked

Check your OpenAI usage: https://platform.openai.com/usage

## Recommended Setup

For production, use this combination:
```bash
# Primary (FREE)
GROQ_API_KEY=gsk_...

# Backup (if you have credits)
OPENAI_API_KEY=sk-...

# Optional backup
GOOGLE_API_KEY=...
```

This gives you FREE, reliable AI generation! 🚀

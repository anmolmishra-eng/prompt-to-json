# Multi-City Backend Demo Guide

## Sample API Requests

### Mumbai 4-floor residential building

**Request:**
```json
{
  "user_id": "demo_user",
  "prompt": "Design a 4-floor residential building with parking",
  "project_id": "demo_mumbai_001",
  "city": "Mumbai"
}
```

**cURL Command:**
```bash
curl -X POST http://localhost:8000/api/v1/generate \
  -H 'Content-Type: application/json' \
  -d '{
    "user_id": "demo_user",
    "prompt": "Design a 4-floor residential building with parking",
    "project_id": "demo_mumbai_001",
    "city": "Mumbai"
  }' | jq
```

### Pune IT office park

**Request:**
```json
{
  "user_id": "demo_user",
  "prompt": "Create an IT office campus with 3 buildings",
  "project_id": "demo_pune_001",
  "city": "Pune"
}
```

**cURL Command:**
```bash
curl -X POST http://localhost:8000/api/v1/generate \
  -H 'Content-Type: application/json' \
  -d '{
    "user_id": "demo_user",
    "prompt": "Create an IT office campus with 3 buildings",
    "project_id": "demo_pune_001",
    "city": "Pune"
  }' | jq
```

### Get city DCR rules

**cURL Command:**
```bash
curl http://localhost:8000/api/v1/cities/Mumbai/rules | jq
```

### Get city context

**cURL Command:**
```bash
curl http://localhost:8000/api/v1/cities/Ahmedabad/context | jq
```


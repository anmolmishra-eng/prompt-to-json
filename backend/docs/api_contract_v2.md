# API Contract v2

## Base URL
`https://api.designengine.com/api/v1`

## Authentication

### POST /auth/login
**Description:** Authenticate user and receive JWT token

**Request (Form Data):**
```
username=user
password=pass
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

**Authentication Required:** All endpoints below require `Authorization: Bearer <token>` header

---

## Core Endpoints

### POST /generate
**Description:** Generate a design specification from natural language prompt

**Request:**
```json
{
  "user_id": "user123",
  "prompt": "A modern living room with comfortable seating and natural lighting",
  "context": {
    "style": "modern",
    "budget": "medium",
    "room_size": "large"
  },
  "project_id": "proj_001"
}
```

**Response:**
```json
{
  "spec_id": "spec_a1b2c3d4",
  "spec_json": {
    "components": ["sofa", "coffee_table", "floor_lamp"],
    "materials": ["fabric_gray", "wood_oak", "metal_chrome"],
    "dimensions": {
      "room": {"width": 4.5, "length": 6.0, "height": 2.8}
    },
    "lighting": {
      "natural": ["large_window_south"],
      "artificial": ["floor_lamp", "ceiling_spots"]
    }
  },
  "preview_url": "https://storage.supabase.co/previews/spec_a1b2c3d4.glb?signed=...",
  "created_at": "2024-01-01T12:00:00Z"
}
```

### POST /switch
**Description:** Change material/property of specific object in existing spec

**Request:**
```json
{
  "spec_id": "spec_a1b2c3d4",
  "target": "sofa_1",
  "material": "leather_brown"
}
```

**Response:**
```json
{
  "spec_id": "spec_a1b2c3d4",
  "updated_spec_json": {
    "components": ["sofa", "coffee_table", "floor_lamp"],
    "materials": ["leather_brown", "wood_oak", "metal_chrome"]
  },
  "preview_url": "https://storage.supabase.co/previews/spec_a1b2c3d4_v2.glb?signed=...",
  "iteration_id": "iter_x1y2z3w4",
  "changed": {
    "object_id": "sofa_1",
    "before": "fabric_gray",
    "after": "leather_brown"
  },
  "updated_at": "2024-01-01T12:15:00Z"
}
```

### POST /evaluate
**Description:** Record user evaluation of a design spec

**Request:**
```json
{
  "spec_id": "spec_a1b2c3d4",
  "user_id": "user123",
  "rating": 5,
  "notes": "Excellent design, love the material choice"
}
```

**Response:**
```json
{
  "ok": true,
  "saved_id": "eval_m5n6o7p8"
}
```

### POST /iterate
**Description:** Generate improved spec based on strategy

**Request:**
```json
{
  "spec_id": "spec_a1b2c3d4",
  "strategy": "improve_materials",
  "user_id": "user123"
}
```

**Response:**
```json
{
  "before": {
    "components": ["sofa", "coffee_table"],
    "materials": ["fabric_gray", "wood_pine"]
  },
  "after": {
    "components": ["sofa", "coffee_table"],
    "materials": ["leather_premium", "wood_walnut"]
  },
  "feedback": "Upgraded materials for better durability and aesthetics. Replaced fabric with premium leather and pine with walnut for enhanced quality."
}
```

---

## Compliance Endpoints

### POST /compliance/run_case
**Description:** Run compliance check via external service

**Request:**
```json
{
  "case_params": {
    "design_type": "interior",
    "safety_level": "commercial",
    "materials": ["leather", "wood", "metal"],
    "room_type": "living_room"
  },
  "geometry_data": "base64_encoded_3d_model_data",
  "compliance_rules": ["fire_safety", "accessibility", "building_code"]
}
```

**Response:**
```json
{
  "case_id": "case_c9d8e7f6",
  "status": "completed",
  "compliance_score": 0.92,
  "violations": [],
  "geometry_zip_bytes": "base64_encoded_zip_file",
  "report_url": "https://storage.supabase.co/compliance/case_c9d8e7f6.zip?signed=..."
}
```

### POST /compliance/feedback
**Description:** Submit feedback on compliance results

**Request:**
```json
{
  "case_id": "case_c9d8e7f6",
  "feedback_type": "correction",
  "message": "The accessibility check missed the door width requirement",
  "user_id": "user123"
}
```

**Response:**
```json
{
  "feedback_id": "fb_q1w2e3r4",
  "status": "received",
  "message": "Feedback submitted successfully"
}
```

---

## Orchestration Endpoints

### POST /core/run
**Description:** Execute multiple operations in sequence

**Request:**
```json
{
  "pipeline": ["generate", "evaluate", "iterate"],
  "input": {
    "user_id": "user123",
    "prompt": "Modern office space",
    "project_id": "proj_002",
    "rating": 4,
    "notes": "Good start",
    "strategy": "optimize_lighting"
  }
}
```

**Response:**
```json
{
  "generate": {
    "spec_id": "spec_b2c3d4e5",
    "spec_json": {...},
    "preview_url": "https://...",
    "created_at": "2024-01-01T13:00:00Z"
  },
  "evaluate": {
    "ok": true,
    "saved_id": "eval_t5y6u7i8"
  },
  "iterate": {
    "before": {...},
    "after": {...},
    "feedback": "Optimized lighting layout for better workspace illumination"
  }
}
```

---

## Reporting Endpoints

### GET /reports/{spec_id}
**Description:** Retrieve complete history of a design spec

**Response:**
```json
{
  "spec": {
    "components": ["desk", "chair", "bookshelf"],
    "materials": ["wood_oak", "fabric_blue", "metal_steel"],
    "current_version": 3
  },
  "iterations": [
    {
      "components": ["desk", "chair"],
      "materials": ["wood_pine", "fabric_gray"]
    },
    {
      "components": ["desk", "chair", "lamp"],
      "materials": ["wood_oak", "fabric_blue", "metal_chrome"]
    }
  ],
  "evaluations": [
    {
      "score": 3,
      "notes": "Good start but needs more lighting"
    },
    {
      "score": 5,
      "notes": "Perfect after adding the lamp"
    }
  ],
  "preview_urls": [
    "https://storage.supabase.co/previews/spec_b2c3d4e5_v1.glb?signed=...",
    "https://storage.supabase.co/previews/spec_b2c3d4e5_v2.glb?signed=...",
    "https://storage.supabase.co/previews/spec_b2c3d4e5_v3.glb?signed=..."
  ]
}
```

---

## Monitoring Endpoints

### GET /health
**Description:** Service health check (no authentication required)

**Response:**
```json
{
  "status": "ok",
  "uptime": 3600.5,
  "service": "Design Engine API",
  "version": "1.0.0"
}
```

### GET /metrics
**Description:** Prometheus metrics (no authentication required)

**Response:** (Plain text)
```
# HELP http_requests_total Total number of HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="POST",handler="/api/v1/generate",status="200"} 42

# HELP app_uptime_seconds Application uptime in seconds
# TYPE app_uptime_seconds gauge
app_uptime_seconds 3600.5
```

---

## Error Responses

All endpoints may return these error formats:

**401 Unauthorized:**
```json
{
  "detail": "Invalid authentication credentials"
}
```

**404 Not Found:**
```json
{
  "detail": "Spec not found"
}
```

**422 Validation Error:**
```json
{
  "detail": [
    {
      "loc": ["body", "user_id"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Internal server error"
}
```

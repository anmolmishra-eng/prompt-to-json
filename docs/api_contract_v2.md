# API Contract v2.0 - Design Engine Integration

## Overview
This document specifies the exact API contract for the Design Engine Backend, including all request/response schemas, error handling, and integration patterns.

**Last Updated**: 2025-11-15  
**API Version**: v2.0  
**Base URL**: `/api/v1`

## 1. Authentication

### Login Endpoint
**POST** `/auth/login`

**Request (Form Data)**:
```
username=demo&password=demo123
```

**Response (200 OK)**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

All subsequent requests must include:
```
Authorization: Bearer <access_token>
```

## 2. Core Design Engine Endpoints

### 2.1 Generate Spec
**POST** `/generate`

**Purpose**: Convert natural language prompt into structured design specification

**Request Headers**:
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body**:
```json
{
  "user_id": "u123",
  "prompt": "Design a modern living room with marble floor and grey sofa",
  "context": {
    "style": "modern",
    "dimensions": {
      "length": 20.0,
      "width": 15.0,
      "height": 3.0
    },
    "user_preferences": {
      "preferred_materials": ["marble", "wood"],
      "avoid": ["plastic"]
    }
  },
  "project_id": "proj_456"
}
```

**Response (200 OK)**:
```json
{
  "spec_id": "spec_abc123",
  "spec_version": 1,
  "spec_json": {
    "objects": [
      {
        "id": "floor_1",
        "type": "floor",
        "material": "marble_white",
        "dimensions": {
          "length": 20.0,
          "width": 15.0,
          "height": 0.05
        },
        "metadata": {
          "editable": true,
          "layer": "base"
        }
      },
      {
        "id": "sofa_1",
        "type": "sofa",
        "material": "fabric_grey",
        "position": {
          "x": 5.0,
          "y": 0.0,
          "z": 3.0
        },
        "rotation": {
          "x": 0,
          "y": 90,
          "z": 0
        },
        "metadata": {
          "editable": true
        }
      }
    ],
    "scene": {
      "units": "meters",
      "bounding_box": {
        "l": 20.0,
        "w": 15.0,
        "h": 3.0
      }
    }
  },
  "preview_url": "https://bucket.bhiv.ai/previews/spec_abc123.glb?signature=...",
  "created_at": "2025-11-15T12:00:00Z"
}
```

### 2.2 Switch Material
**POST** `/switch`

**Purpose**: Update material/property of an object in existing spec

**Request Body**:
```json
{
  "user_id": "u123",
  "spec_id": "spec_abc123",
  "target": {
    "object_id": "sofa_1"
  },
  "update": {
    "material": "leather_brown",
    "color_hex": "#8B4513"
  },
  "note": "User prefers leather for sofa"
}
```

**Response (200 OK)**:
```json
{
  "spec_id": "spec_abc123",
  "spec_version": 2,
  "iteration_id": "iter_xyz789",
  "updated_spec_json": {
    "objects": [
      {
        "id": "floor_1",
        "type": "floor",
        "material": "marble_white"
      },
      {
        "id": "sofa_1",
        "type": "sofa",
        "material": "leather_brown",
        "color_hex": "#8B4513",
        "position": {
          "x": 5.0,
          "y": 0.0,
          "z": 3.0
        }
      }
    ]
  },
  "preview_url": "https://bucket.bhiv.ai/previews/spec_abc123_v2.glb?signature=...",
  "changed": {
    "object_id": "sofa_1",
    "field": "material",
    "before": "fabric_grey",
    "after": "leather_brown"
  },
  "saved_at": "2025-11-15T13:00:00Z"
}
```

### 2.3 Evaluate Design
**POST** `/evaluate`

**Purpose**: Submit user evaluation/rating for a design

**Request Body**:
```json
{
  "user_id": "u123",
  "spec_id": "spec_abc123",
  "rating": 4.5,
  "notes": "Great design, nice color combinations"
}
```

**Response (200 OK)**:
```json
{
  "ok": true,
  "saved_id": "eval_123456",
  "message": "Evaluation recorded successfully",
  "timestamp": "2025-11-15T13:30:00Z"
}
```

### 2.4 Iterate Design
**POST** `/iterate`

**Purpose**: Request LM to improve design based on strategy

**Request Body**:
```json
{
  "user_id": "u123",
  "spec_id": "spec_abc123",
  "strategy": "improve_materials"
}
```

**Supported strategies**:
- `improve_materials` - Suggest better materials
- `improve_layout` - Optimize spatial arrangement
- `improve_aesthetics` - Enhance visual appeal
- `auto_optimize` - Use RL model for optimization

**Response (200 OK)**:
```json
{
  "before": {
    "objects": [...],
    "scene": {...}
  },
  "after": {
    "objects": [...],
    "scene": {...}
  },
  "feedback": "Improved material selection for better durability and aesthetics",
  "iteration_id": "iter_456789",
  "timestamp": "2025-11-15T14:00:00Z"
}
```

## 3. Error Responses

**400 Bad Request**:
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "field_errors": [
      {
        "field": "prompt",
        "message": "Field is required",
        "value": null
      }
    ],
    "request_id": "req_abc123",
    "timestamp": "2025-11-15T12:00:00Z"
  }
}
```

**401 Unauthorized**:
```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Invalid or missing token",
    "request_id": "req_def456",
    "timestamp": "2025-11-15T12:00:00Z"
  }
}
```

**500 Internal Server Error**:
```json
{
  "error": {
    "code": "INTERNAL_ERROR",
    "message": "An unexpected error occurred. Please contact support.",
    "details": {
      "error_type": "LMError"
    },
    "request_id": "req_ghi789",
    "timestamp": "2025-11-15T12:00:00Z"
  }
}
```

## 4. Rate Limits
- **Default**: 100 requests per minute per client IP
- **Authenticated**: 500 requests per minute per user
- **Headers**: `X-RateLimit-Limit`, `X-RateLimit-Remaining`
- **Response**: 429 Too Many Requests when exceeded

## 5. Integration Guidelines

### Frontend (Yash)
- **Token Management**: Store JWT securely, implement refresh logic
- **Preview Loading**: Use GLTFLoader for GLB files, handle signed URL expiry
- **Error Handling**: Parse structured errors, implement retry logic
- **Rate Limiting**: Check headers, implement client-side queuing

### Backend Developers
- **Validation**: Validate inputs, return 422 with field errors
- **Error Handling**: Always return structured responses with request_id
- **Security**: Verify JWT, check permissions, log access
- **Performance**: Use async/await, return 202 for long operations
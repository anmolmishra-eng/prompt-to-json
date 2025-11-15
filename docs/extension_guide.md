# Extension Guide - Adding Features and Schemas

This guide explains how to extend the Design Engine with new features, endpoints, and schemas.

## Table of Contents
1. [Adding New Schemas](#adding-new-schemas)
2. [Creating New Endpoints](#creating-new-endpoints)
3. [Integrating with Feedback Loop](#integrating-with-feedback-loop)
4. [UI/Data Layer Separation](#uidata-layer-separation)
5. [Best Practices](#best-practices)

## Adding New Schemas

### Step 1: Define Your Schema
Create a new Pydantic model in `app/schemas/`:

```python
# app/schemas/custom_schemas.py
from pydantic import BaseModel, Field
from typing import Optional, List

class CustomObjectRequest(BaseModel):
    """Request model for custom object creation"""
    object_type: str = Field(..., description="Type of object (wall, furniture, etc.)")
    material: str = Field(..., description="Material identifier")
    dimensions: Optional[dict] = Field(None, description="Object dimensions")
    
    class Config:
        schema_extra = {
            "example": {
                "object_type": "wall",
                "material": "concrete",
                "dimensions": {"height": 3.0, "width": 5.0}
            }
        }

class CustomObjectResponse(BaseModel):
    """Response model for custom object"""
    object_id: str
    object_type: str
    material: str
    created_at: str
```

### Step 2: Register Schema
Add to `app/schemas/__init__.py`:

```python
from .custom_schemas import CustomObjectRequest, CustomObjectResponse

__all__ = [
    "CustomObjectRequest",
    "CustomObjectResponse",
    # ... other schemas
]
```

## Creating New Endpoints

### Step 1: Create Router Module
Create a new file in `app/api/`:

```python
# app/api/my_feature.py
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_current_user, get_db
from app.error_handler import APIException
from app.schemas.error_schemas import ErrorCode

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/my-endpoint")
async def my_endpoint(
    request_data: dict,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Endpoint description for API docs
    """
    
    try:
        # 1. Validate input
        if not request_data.get("required_field"):
            raise APIException(
                status_code=status.HTTP_400_BAD_REQUEST,
                error_code=ErrorCode.INVALID_INPUT,
                message="required_field is required"
            )
        
        # 2. Process request
        # ... your business logic ...
        
        # 3. Log important actions
        logger.info(f"Processed request for user {current_user}")
        
        # 4. Return response
        return {"status": "success", "data": {}}
    
    except ValueError as e:
        logger.error(f"Value error: {e}")
        raise APIException(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code=ErrorCode.INVALID_INPUT,
            message=str(e)
        )
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        raise APIException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code=ErrorCode.INTERNAL_ERROR,
            message="An unexpected error occurred"
        )
```

### Step 2: Register Router
In `app/main.py`:

```python
from app.api import my_feature

# Add to router registration section
app.include_router(
    my_feature.router, 
    prefix="/api/v1", 
    tags=["🎨 My Feature"]
)
```

## Integrating with Feedback Loop

### Connect Your Endpoint to Feedback System
```python
# In your endpoint that accepts user feedback
from app.feedback_loop import IterativeFeedbackCycle

@router.post("/my-feature/rate")
async def rate_feature(
    spec_id: str,
    rating: float,
    notes: str,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Rate a feature - this feeds into RL training"""
    
    # Process rating
    # ... your code ...
    
    # Integrate with feedback loop
    feedback_cycle = IterativeFeedbackCycle(db)
    
    result = await feedback_cycle.process_evaluation_feedback(
        user_id=current_user,
        spec_id=spec_id,
        rating=rating,
        notes=notes
    )
    
    return {
        "ok": True,
        "feedback_status": result,
        "training_triggered": result.get("training_triggered", False)
    }
```

## UI/Data Layer Separation

### Architecture Pattern
```
┌─────────────────────────────────┐
│         React UI Layer          │
│  (Components, State Management) │
├─────────────────────────────────┤
│     API Client Layer            │
│  (Axios/Fetch wrappers)        │
├─────────────────────────────────┤
│  Backend API Endpoints          │
│  (FastAPI routers)              │
├─────────────────────────────────┤
│  Business Logic Layer           │
│  (Services, Use Cases)          │
├─────────────────────────────────┤
│  Data Access Layer              │
│  (SQLAlchemy ORM, Queries)      │
└─────────────────────────────────┘
```

### Separating Concerns
**❌ BAD - Mixed concerns:**
```javascript
function MyComponent() {
    function load_data() {
        response = fetch("/api/v1/spec")
        setSpecs(response.data)
        renderUI(response.data)
    }
    
    return <div>{specs}</div>
}
```

**✅ GOOD - Separated concerns:**
```javascript
// 1. API Client (api/client.ts)
export const specClient = {
    getSpec: (id) => fetch(`/api/v1/spec/${id}`),
    generateSpec: (prompt) => fetch("/api/v1/generate", {...})
}

// 2. Data/State Management (hooks/useSpec.ts)
export function useSpec(specId) {
    const [spec, setSpec] = useState(null)
    useEffect(() => {
        specClient.getSpec(specId)
            .then(data => setSpec(data))
    }, [specId])
    return { spec, loading, error }
}

// 3. UI Component (components/SpecViewer.tsx)
export function SpecViewer({ specId }) {
    const { spec, loading } = useSpec(specId)
    if (loading) return <Spinner/>
    return <Viewer spec={spec}/>
}
```

## Best Practices

### 1. Error Handling Checklist
- ✅ Validate all inputs at endpoint level
- ✅ Use structured error responses
- ✅ Include field-level validation errors
- ✅ Log errors with appropriate severity
- ✅ Send errors to Sentry with context
- ✅ Return user-friendly messages

### 2. Documentation Checklist
- ✅ Add docstring to endpoint function
- ✅ Document request/response schemas
- ✅ Include error scenarios
- ✅ Provide example requests/responses
- ✅ Document any side effects (DB writes, async jobs)

### 3. Security Checklist
- ✅ Verify user authentication
- ✅ Check user permissions
- ✅ Validate user input (types, length, format)
- ✅ Sanitize user input
- ✅ Log sensitive operations
- ✅ Use HTTPS/TLS for all endpoints

### 4. Performance Checklist
- ✅ Use async/await for I/O operations
- ✅ Implement database query optimization
- ✅ Add caching where appropriate
- ✅ Return 202 for long-running operations (>2s)
- ✅ Implement pagination for list endpoints

### 5. Testing Checklist
- ✅ Write unit tests for business logic
- ✅ Write integration tests for endpoints
- ✅ Test error scenarios
- ✅ Test edge cases
- ✅ Test with different user permissions
- ✅ Test rate limiting

## Example: Complete Feature Addition

Let's add a "Material Suggestions" endpoint:

```python
# 1. Schema
# app/schemas/material_schemas.py
class MaterialSuggestionRequest(BaseModel):
    spec_id: str
    object_id: str
    context: Optional[str] = None

class MaterialSuggestion(BaseModel):
    material_id: str
    name: str
    reason: str
    preview_url: Optional[str]

class MaterialSuggestionResponse(BaseModel):
    suggestions: List[MaterialSuggestion]
    timestamp: str

# 2. Service
# app/services/material_service.py
class MaterialService:
    def __init__(self, db: Session, lm_adapter):
        self.db = db
        self.lm = lm_adapter
    
    async def suggest_materials(self, spec_id: str, object_id: str) -> List[dict]:
        """Generate material suggestions using LM"""
        spec = self.db.query(Spec).filter(Spec.spec_id == spec_id).first()
        if not spec:
            raise ValueError(f"Spec {spec_id} not found")
        
        # Use LM to generate suggestions
        prompt = f"Suggest 3 alternative materials for {object_id} in spec..."
        suggestions = await self.lm.run(prompt)
        
        return suggestions

# 3. Endpoint
# app/api/materials.py
@router.post("/materials/suggest", response_model=MaterialSuggestionResponse)
async def suggest_materials(
    request: MaterialSuggestionRequest,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        service = MaterialService(db, lm_adapter)
        suggestions = await service.suggest_materials(
            request.spec_id,
            request.object_id
        )
        
        return MaterialSuggestionResponse(
            suggestions=suggestions,
            timestamp=datetime.utcnow().isoformat()
        )
    except ValueError as e:
        raise APIException(
            status_code=400,
            error_code=ErrorCode.NOT_FOUND,
            message=str(e)
        )

# 4. Tests
# tests/test_materials.py
def test_suggest_materials(auth_headers):
    response = client.post(
        "/api/v1/materials/suggest",
        headers=auth_headers,
        json={"spec_id": "spec_123", "object_id": "wall_1"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "suggestions" in data
    assert len(data["suggestions"]) > 0
```

## Additional Resources
- [Pydantic Documentation](https://docs.pydantic.dev)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org)
- [React Best Practices](https://react.dev/learn)

## Questions?
Contact the backend team or refer to the API Contract v2.0 for detailed specifications.
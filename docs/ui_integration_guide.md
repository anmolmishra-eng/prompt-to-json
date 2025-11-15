# UI Integration Guide

## Frontend Setup

### 1. Authentication

```typescript
// services/auth.ts
export async function login(username: string, password: string) {
  const response = await fetch('/api/v1/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({ username, password })
  })
  
  const data = await response.json()
  localStorage.setItem('token', data.access_token)
  return data
}

export function getAuthHeaders() {
  const token = localStorage.getItem('token')
  return {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
}
```

### 2. Spec Generation
```typescript
// services/specClient.ts
export async function generateSpec(prompt: string) {
  const response = await fetch('/api/v1/generate', {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({
      user_id: getCurrentUserId(),
      prompt,
      context: { style: 'modern' }
    })
  })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.error.message)
  }
  
  return response.json()
}
```

### 3. Error Handling
```typescript
// utils/errorHandler.ts
export function handleApiError(error: any) {
  if (error.error?.code === 'VALIDATION_ERROR') {
    return {
      type: 'validation',
      fields: error.error.field_errors,
      message: error.error.message
    }
  }
  
  if (error.error?.code === 'UNAUTHORIZED') {
    // Redirect to login
    window.location.href = '/login'
  }
  
  return {
    type: 'error',
    message: error.error?.message || 'Unknown error'
  }
}
```

### 4. React Hooks
```typescript
// hooks/useSpec.ts
export function useSpec(specId: string) {
  const [spec, setSpec] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  
  useEffect(() => {
    const fetchSpec = async () => {
      try {
        const data = await fetch(`/api/v1/reports/${specId}`, {
          headers: getAuthHeaders()
        }).then(r => r.json())
        
        setSpec(data)
      } catch (err) {
        setError(err)
      } finally {
        setLoading(false)
      }
    }
    
    fetchSpec()
  }, [specId])
  
  return { spec, loading, error }
}
```

### 5. 3D Preview Loading
```typescript
// components/SpecViewer.tsx
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader'
import { Canvas } from '@react-three/fiber'

export function SpecViewer({ previewUrl }: { previewUrl: string }) {
  const [model, setModel] = useState(null)
  const [loading, setLoading] = useState(true)
  
  useEffect(() => {
    const loader = new GLTFLoader()
    loader.load(
      previewUrl,
      (gltf) => {
        setModel(gltf.scene)
        setLoading(false)
      },
      undefined,
      (error) => {
        console.error('Error loading GLB:', error)
        setLoading(false)
      }
    )
  }, [previewUrl])
  
  if (loading) return <div>Loading 3D preview...</div>
  
  return (
    <Canvas>
      <ambientLight intensity={0.5} />
      <pointLight position={[10, 10, 10]} />
      {model && <primitive object={model} />}
    </Canvas>
  )
}
```

### 6. Rate Limiting Handling
```typescript
// utils/rateLimiter.ts
export class RateLimitHandler {
  private queue: Array<() => Promise<any>> = []
  private processing = false
  
  async makeRequest(requestFn: () => Promise<Response>) {
    return new Promise((resolve, reject) => {
      this.queue.push(async () => {
        try {
          const response = await requestFn()
          
          // Check rate limit headers
          const remaining = response.headers.get('X-RateLimit-Remaining')
          if (remaining && parseInt(remaining) < 5) {
            // Slow down requests when approaching limit
            await new Promise(resolve => setTimeout(resolve, 1000))
          }
          
          if (response.status === 429) {
            // Rate limited - retry after delay
            await new Promise(resolve => setTimeout(resolve, 60000))
            return this.makeRequest(requestFn)
          }
          
          resolve(response)
        } catch (error) {
          reject(error)
        }
      })
      
      this.processQueue()
    })
  }
  
  private async processQueue() {
    if (this.processing || this.queue.length === 0) return
    
    this.processing = true
    while (this.queue.length > 0) {
      const request = this.queue.shift()!
      await request()
      await new Promise(resolve => setTimeout(resolve, 100)) // Small delay between requests
    }
    this.processing = false
  }
}
```

## Best Practices

### Security
- **Never store JWT tokens in localStorage in production** - use secure, httpOnly cookies
- **Implement token refresh logic** - refresh tokens 5 minutes before expiry
- **Validate all user inputs** - sanitize before sending to API
- **Use HTTPS in production** - never send tokens over HTTP

### Performance
- **Implement request caching** - cache GET requests for specs and history
- **Use React.memo** - prevent unnecessary re-renders of 3D components
- **Lazy load 3D models** - only load GLB files when needed
- **Implement pagination** - for design history and large lists

### Error Handling
- **Always handle network errors** - show user-friendly messages
- **Implement retry logic** - with exponential backoff for failed requests
- **Log errors with context** - include request IDs for debugging
- **Show loading states** - for all async operations

### User Experience
- **Show progress indicators** - for long-running operations (generate, iterate)
- **Handle 202 Accepted responses** - poll status endpoints for completion
- **Implement optimistic updates** - update UI immediately, rollback on error
- **Cache preview images** - avoid re-downloading GLB files

## Example: Complete Component Integration

```typescript
// components/DesignGenerator.tsx
import React, { useState } from 'react'
import { generateSpec, switchMaterial } from '../services/specClient'
import { handleApiError } from '../utils/errorHandler'
import { SpecViewer } from './SpecViewer'

export function DesignGenerator() {
  const [prompt, setPrompt] = useState('')
  const [spec, setSpec] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  
  const handleGenerate = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const result = await generateSpec(prompt)
      setSpec(result)
    } catch (err) {
      const errorInfo = handleApiError(err)
      setError(errorInfo.message)
    } finally {
      setLoading(false)
    }
  }
  
  const handleMaterialSwitch = async (objectId: string, newMaterial: string) => {
    try {
      const result = await switchMaterial(spec.spec_id, objectId, newMaterial)
      setSpec(prev => ({ ...prev, ...result }))
    } catch (err) {
      const errorInfo = handleApiError(err)
      setError(errorInfo.message)
    }
  }
  
  return (
    <div className="design-generator">
      <div className="input-section">
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Describe your design..."
          maxLength={5000}
        />
        <button onClick={handleGenerate} disabled={loading || !prompt}>
          {loading ? 'Generating...' : 'Generate Design'}
        </button>
      </div>
      
      {error && (
        <div className="error-message">
          {error}
        </div>
      )}
      
      {spec && (
        <div className="spec-viewer">
          <SpecViewer previewUrl={spec.preview_url} />
          <div className="spec-controls">
            {/* Material switching controls */}
            {spec.spec_json.objects.map(obj => (
              <MaterialSelector
                key={obj.id}
                object={obj}
                onMaterialChange={(material) => 
                  handleMaterialSwitch(obj.id, material)
                }
              />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
```

## Testing Frontend Integration

```typescript
// tests/specClient.test.ts
import { generateSpec, switchMaterial } from '../services/specClient'

// Mock fetch for testing
global.fetch = jest.fn()

describe('Spec Client', () => {
  beforeEach(() => {
    fetch.mockClear()
  })
  
  test('generateSpec handles success response', async () => {
    const mockResponse = {
      spec_id: 'spec_123',
      spec_json: { objects: [] },
      preview_url: 'https://example.com/preview.glb'
    }
    
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse
    })
    
    const result = await generateSpec('test prompt')
    expect(result).toEqual(mockResponse)
  })
  
  test('generateSpec handles error response', async () => {
    const mockError = {
      error: {
        code: 'VALIDATION_ERROR',
        message: 'Prompt is required'
      }
    }
    
    fetch.mockResolvedValueOnce({
      ok: false,
      json: async () => mockError
    })
    
    await expect(generateSpec('')).rejects.toThrow('Prompt is required')
  })
})
```

## Deployment Checklist

### Environment Variables
```bash
# .env.production
REACT_APP_API_BASE_URL=https://api.yourapp.com
REACT_APP_SENTRY_DSN=your-sentry-dsn
REACT_APP_VERSION=1.0.0
```

### Build Configuration
```json
// package.json
{
  "scripts": {
    "build": "react-scripts build",
    "build:staging": "REACT_APP_API_BASE_URL=https://staging-api.yourapp.com npm run build",
    "build:prod": "REACT_APP_API_BASE_URL=https://api.yourapp.com npm run build"
  }
}
```

### Performance Monitoring
```typescript
// utils/monitoring.ts
import * as Sentry from '@sentry/react'

export function trackApiCall(endpoint: string, duration: number, success: boolean) {
  Sentry.addBreadcrumb({
    category: 'api',
    message: `${endpoint} - ${success ? 'success' : 'error'}`,
    data: { duration, endpoint },
    level: success ? 'info' : 'error'
  })
}
```

## Questions?
Contact the backend team or refer to the API Contract v2.0 for detailed specifications.
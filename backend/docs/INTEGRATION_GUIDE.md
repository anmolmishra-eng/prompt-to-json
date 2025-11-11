# Integration Guide for Yash & Bhavesh

## 🔐 Authorization (JWT)

### Backend Implementation ✅
- All endpoints require `Authorization: Bearer <JWT>` header
- JWT tokens expire in 24 hours (configurable)
- Login endpoint: `POST /api/v1/auth/login`

### Frontend Implementation Required
```javascript
// Login flow
const response = await fetch('/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  body: 'username=admin&password=bhiv2024'
});
const { access_token } = await response.json();

// Store token securely (mobile: Keychain/Keystore)
localStorage.setItem('jwt_token', access_token);

// Use in all API calls
const apiCall = await fetch('/api/v1/generate', {
  headers: { 'Authorization': `Bearer ${access_token}` }
});
```

## 🌐 CORS Configuration

### Current Status ⚠️
```javascript
// main.py - Currently allows all origins
allow_origins=["*"]
```

### Action Required
**Yash**: Provide frontend origin URLs to Anmol ASAP:
- Development: `http://localhost:3000`
- Staging: `https://staging.bhiv.com`
- Production: `https://app.bhiv.com`

## 🎨 Preview Loading (GLB/GLTF)

### Backend Response ✅
```json
{
  "preview_url": "https://signed-url-to-file.glb",
  "spec_id": "spec_123"
}
```

### Frontend Implementation Required
```javascript
// React Three Fiber
import { useGLTF } from '@react-three/drei';

function Preview({ previewUrl }) {
  const { scene } = useGLTF(previewUrl);
  return <primitive object={scene} />;
}

// Or vanilla Three.js
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader';
const loader = new GLTFLoader();
loader.load(previewUrl, (gltf) => {
  scene.add(gltf.scene);
});
```

## ⏰ Signed URLs & Expiry

### Backend Implementation ✅
- All preview URLs expire in 10 minutes (600s)
- Fresh URLs generated on each request

### Frontend Implementation Required
```javascript
// Treat preview_url as ephemeral
const refreshPreview = async (specId) => {
  const response = await fetch(`/api/v1/specs/${specId}`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  const { preview_url } = await response.json();
  return preview_url;
};

// Refresh on 403/404 errors
if (response.status === 403 || response.status === 404) {
  const newUrl = await refreshPreview(specId);
  // Retry with new URL
}
```

## ⚠️ Conflict Handling (409)

### Backend Implementation ✅
- Returns 409 Conflict when spec version mismatch occurs
- Includes latest spec version in error response

### Frontend Implementation Required
```javascript
const handleConflict = async (response) => {
  if (response.status === 409) {
    const error = await response.json();

    // Show friendly message
    const userChoice = await showConflictDialog({
      message: "Someone else modified this design. What would you like to do?",
      options: ["Merge Changes", "Override", "Cancel"]
    });

    if (userChoice === "merge") {
      // Fetch latest version and merge
      const latest = await fetch(`/api/v1/specs/${specId}`);
      // Implement merge logic
    } else if (userChoice === "override") {
      // Force update with current changes
      return fetch(url, { ...options, headers: { ...headers, 'X-Force-Update': 'true' }});
    }
  }
};
```

## 🔄 Async Previews (202 Accepted)

### Backend Implementation ✅
- `/switch` endpoint may return 202 with `status_url`
- Poll status URL for completion

### Frontend Implementation Required
```javascript
const handleAsyncPreview = async (response) => {
  if (response.status === 202) {
    const { status_url } = await response.json();

    // Poll status URL
    const pollStatus = async () => {
      const statusResponse = await fetch(status_url, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (statusResponse.status === 200) {
        const { preview_url } = await statusResponse.json();
        return preview_url; // Ready!
      } else if (statusResponse.status === 202) {
        // Still processing, poll again
        setTimeout(pollStatus, 2000);
      }
    };

    return pollStatus();
  }
};
```

## 📱 Mobile Security

### Token Storage
```javascript
// React Native - Use secure storage
import * as SecureStore from 'expo-secure-store';

// Store token
await SecureStore.setItemAsync('jwt_token', access_token);

// Retrieve token
const token = await SecureStore.getItemAsync('jwt_token');
```

## 🚀 Quick Start Checklist

### For Yash (Frontend)
- [ ] Implement JWT login flow with secure token storage
- [ ] Add Authorization header to all API calls
- [ ] Provide CORS origin URLs to Anmol
- [ ] Implement GLB preview loading with Three.js/R3F
- [ ] Handle signed URL expiry and refresh logic
- [ ] Add 409 conflict resolution UI
- [ ] Implement 202 async preview polling

### For Bhavesh (Mobile)
- [ ] Use secure storage (Keychain/Keystore) for JWT tokens
- [ ] Implement same authorization patterns as web
- [ ] Handle network errors and token refresh
- [ ] Test GLB loading on mobile devices

### For Anmol (Backend)
- [ ] Update CORS origins once Yash provides URLs
- [ ] Monitor Sentry for integration issues
- [ ] Verify signed URL expiry handling

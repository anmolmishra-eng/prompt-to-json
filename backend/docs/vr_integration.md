# VR/AR Integration Guide

## Overview

The Design Engine API provides VR/AR bridge endpoints for immersive design visualization. These endpoints integrate with Bhavesh's VR rendering system and provide optimized 3D content delivery.

## VR Endpoints

### Preview Access

Get VR-optimized preview URLs for design specs:

```javascript
// Get VR preview
const getVRPreview = async (specId, token) => {
  const response = await fetch(`https://api.designengine.com/api/v1/vr/preview/${specId}`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });

  return await response.json();
};

// Response format:
{
  "spec_id": "spec_a1b2c3d4",
  "preview_url": "https://storage.supabase.co/previews/spec_a1b2c3d4.glb?signed=...",
  "format": "glb",
  "expires_in": 600,
  "vr_optimized": true
}
```

### VR Rendering

Request high-quality VR renders:

```javascript
// Request VR render
const requestVRRender = async (specId, quality, token) => {
  const response = await fetch(`https://api.designengine.com/api/v1/vr/render/${specId}?quality=${quality}`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });

  return await response.json();
};

// Response format:
{
  "spec_id": "spec_a1b2c3d4",
  "render_status": "queued",
  "quality": "high",
  "estimated_time": "30s",
  "render_id": "vr_render_spec_a1b2c3d4_high"
}
```

### Render Status Tracking

Check VR render progress:

```javascript
// Check render status
const checkRenderStatus = async (renderId, token) => {
  const response = await fetch(`https://api.designengine.com/api/v1/vr/status/${renderId}`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });

  return await response.json();
};

// Response format:
{
  "render_id": "vr_render_spec_a1b2c3d4_high",
  "status": "completed",
  "progress": 100,
  "vr_url": "https://storage.supabase.co/vr/vr_render_spec_a1b2c3d4_high.glb?signed=..."
}
```

## Unity Integration Example

Complete Unity C# integration for VR applications:

```csharp
using System;
using System.Collections;
using UnityEngine;
using UnityEngine.Networking;

public class DesignEngineVR : MonoBehaviour
{
    private string apiBase = "https://api.designengine.com/api/v1";
    private string authToken;

    [System.Serializable]
    public class VRPreviewResponse
    {
        public string spec_id;
        public string preview_url;
        public string format;
        public int expires_in;
        public bool vr_optimized;
    }

    [System.Serializable]
    public class VRRenderResponse
    {
        public string spec_id;
        public string render_status;
        public string quality;
        public string estimated_time;
        public string render_id;
    }

    // Login and get JWT token
    public IEnumerator Login(string username, string password)
    {
        WWWForm form = new WWWForm();
        form.AddField("username", username);
        form.AddField("password", password);

        using (UnityWebRequest request = UnityWebRequest.Post($"{apiBase}/auth/login", form))
        {
            yield return request.SendWebRequest();

            if (request.result == UnityWebRequest.Result.Success)
            {
                var response = JsonUtility.FromJson<LoginResponse>(request.downloadHandler.text);
                authToken = response.access_token;
                Debug.Log("VR Login successful");
            }
            else
            {
                Debug.LogError($"VR Login failed: {request.error}");
            }
        }
    }

    // Get VR preview for spec
    public IEnumerator GetVRPreview(string specId, System.Action<VRPreviewResponse> callback)
    {
        using (UnityWebRequest request = UnityWebRequest.Get($"{apiBase}/vr/preview/{specId}"))
        {
            request.SetRequestHeader("Authorization", $"Bearer {authToken}");

            yield return request.SendWebRequest();

            if (request.result == UnityWebRequest.Result.Success)
            {
                var response = JsonUtility.FromJson<VRPreviewResponse>(request.downloadHandler.text);
                callback?.Invoke(response);
            }
            else
            {
                Debug.LogError($"VR Preview failed: {request.error}");
            }
        }
    }

    // Load GLB model in VR scene
    public IEnumerator LoadVRModel(string glbUrl)
    {
        using (UnityWebRequest request = UnityWebRequest.Get(glbUrl))
        {
            yield return request.SendWebRequest();

            if (request.result == UnityWebRequest.Result.Success)
            {
                // Use GLTFast or similar library to load GLB
                byte[] glbData = request.downloadHandler.data;
                yield return LoadGLBIntoScene(glbData);
            }
        }
    }

    // Request high-quality VR render
    public IEnumerator RequestVRRender(string specId, string quality = "high")
    {
        using (UnityWebRequest request = UnityWebRequest.Get($"{apiBase}/vr/render/{specId}?quality={quality}"))
        {
            request.SetRequestHeader("Authorization", $"Bearer {authToken}");

            yield return request.SendWebRequest();

            if (request.result == UnityWebRequest.Result.Success)
            {
                var response = JsonUtility.FromJson<VRRenderResponse>(request.downloadHandler.text);
                Debug.Log($"VR Render queued: {response.render_id}");

                // Start polling for completion
                StartCoroutine(PollRenderStatus(response.render_id));
            }
        }
    }

    // Poll render status until complete
    private IEnumerator PollRenderStatus(string renderId)
    {
        while (true)
        {
            yield return new WaitForSeconds(5f); // Poll every 5 seconds

            using (UnityWebRequest request = UnityWebRequest.Get($"{apiBase}/vr/status/{renderId}"))
            {
                request.SetRequestHeader("Authorization", $"Bearer {authToken}");
                yield return request.SendWebRequest();

                if (request.result == UnityWebRequest.Result.Success)
                {
                    var status = JsonUtility.FromJson<RenderStatusResponse>(request.downloadHandler.text);

                    if (status.status == "completed")
                    {
                        Debug.Log("VR Render completed!");
                        yield return LoadVRModel(status.vr_url);
                        break;
                    }
                    else if (status.status == "failed")
                    {
                        Debug.LogError("VR Render failed");
                        break;
                    }
                }
            }
        }
    }

    // Submit VR experience feedback
    public IEnumerator SubmitVRFeedback(string specId, int rating, string comments)
    {
        var feedback = new
        {
            spec_id = specId,
            rating = rating,
            comments = comments,
            platform = "unity_vr",
            device_type = "vr_headset"
        };

        string jsonData = JsonUtility.ToJson(feedback);

        using (UnityWebRequest request = UnityWebRequest.PostWwwForm($"{apiBase}/vr/feedback", ""))
        {
            request.SetRequestHeader("Authorization", $"Bearer {authToken}");
            request.SetRequestHeader("Content-Type", "application/json");
            request.uploadHandler = new UploadHandlerRaw(System.Text.Encoding.UTF8.GetBytes(jsonData));

            yield return request.SendWebRequest();

            if (request.result == UnityWebRequest.Result.Success)
            {
                Debug.Log("VR Feedback submitted successfully");
            }
        }
    }
}
```

## WebXR Integration

For web-based VR/AR experiences:

```javascript
// WebXR VR Session
class DesignEngineWebXR {
  constructor(apiToken) {
    this.token = apiToken;
    this.apiBase = 'https://api.designengine.com/api/v1';
  }

  async startVRSession(specId) {
    // Get VR preview
    const preview = await this.getVRPreview(specId);

    // Initialize WebXR session
    if (navigator.xr) {
      const session = await navigator.xr.requestSession('immersive-vr');

      // Load GLB model
      await this.loadModelInVR(session, preview.preview_url);

      return session;
    }
  }

  async getVRPreview(specId) {
    const response = await fetch(`${this.apiBase}/vr/preview/${specId}`, {
      headers: {
        'Authorization': `Bearer ${this.token}`
      }
    });

    return await response.json();
  }

  async loadModelInVR(session, glbUrl) {
    // Use Three.js or A-Frame to load GLB in VR
    const loader = new THREE.GLTFLoader();

    return new Promise((resolve) => {
      loader.load(glbUrl, (gltf) => {
        // Add model to VR scene
        scene.add(gltf.scene);
        resolve(gltf);
      });
    });
  }
}

// Usage
const vrEngine = new DesignEngineWebXR(authToken);
await vrEngine.startVRSession('spec_a1b2c3d4');
```

## AR Integration (ARCore/ARKit)

Mobile AR integration example:

```javascript
// React Native AR integration
import { ViroARScene, ViroARSceneNavigator, Viro3DObject } from '@viro-community/react-viro';

const ARDesignViewer = ({ specId, authToken }) => {
  const [modelUrl, setModelUrl] = useState(null);

  useEffect(() => {
    // Get AR-optimized model
    fetch(`https://api.designengine.com/api/v1/vr/preview/${specId}`, {
      headers: { 'Authorization': `Bearer ${authToken}` }
    })
    .then(response => response.json())
    .then(data => setModelUrl(data.preview_url));
  }, [specId]);

  return (
    <ViroARSceneNavigator
      initialScene={{
        scene: () => (
          <ViroARScene>
            {modelUrl && (
              <Viro3DObject
                source={{ uri: modelUrl }}
                position={[0, 0, -2]}
                scale={[0.1, 0.1, 0.1]}
                type="GLB"
              />
            )}
          </ViroARScene>
        )
      }}
    />
  );
};
```

## Quality Settings

VR render quality options:

- **low**: Fast preview (< 10s render time)
- **medium**: Balanced quality (< 30s render time)
- **high**: Production quality (< 60s render time)
- **ultra**: Maximum quality (< 120s render time)

## Performance Optimization

1. **LOD Models**: Use level-of-detail for VR performance
2. **Texture Compression**: Optimize textures for VR platforms
3. **Polygon Reduction**: Reduce geometry complexity for mobile VR
4. **Occlusion Culling**: Implement frustum culling for large scenes
5. **Async Loading**: Load models asynchronously to prevent frame drops

## Bhavesh Integration Notes

The VR endpoints serve as bridges to Bhavesh's rendering system:

- Preview URLs point to Supabase-hosted GLB files
- Render requests queue jobs in Bhavesh's pipeline
- Status polling tracks render progress
- Final VR URLs provide optimized models for immersive viewing

This architecture allows seamless integration between the Design Engine API and specialized VR rendering infrastructure.

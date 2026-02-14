# 🎨 Testing /api/v1/generate Endpoint with CURL

## Step 1: Login and Get Token

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/login" ^
  -H "Content-Type: application/x-www-form-urlencoded" ^
  -d "username=admin&password=admin"
```

**Save the `access_token` from the response!**

---

## Step 2: Test Generate Endpoint

Replace `YOUR_TOKEN_HERE` with the actual token from Step 1:

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/generate" ^
  -H "Content-Type: application/json" ^
  -H "Authorization: Bearer YOUR_TOKEN_HERE" ^
  -d "{\"user_id\":\"admin\",\"prompt\":\"Design a 3-bedroom residential building in Mumbai with 2000 sq ft area\",\"project_id\":\"proj_001\",\"context\":{\"city\":\"Mumbai\",\"plot_area\":2000,\"building_type\":\"residential\"}}"
```

**Save the `spec_id` from the response!**

---

## Step 3: Verify Database Storage

Replace `YOUR_SPEC_ID` with the spec_id from Step 2:

```bash
psql -U postgres -d bhiv_db -c "SELECT id, user_id, prompt, city, estimated_cost, created_at FROM specs WHERE id = 'YOUR_SPEC_ID';"
```

---

## Step 4: Verify Local File Storage

Replace `YOUR_SPEC_ID` with the spec_id from Step 2:

```bash
dir backend\data\specs\YOUR_SPEC_ID.json
dir backend\data\geometry_outputs\YOUR_SPEC_ID.glb
```

---

## Step 5: Retrieve Spec via API

Replace `YOUR_TOKEN_HERE` and `YOUR_SPEC_ID`:

```bash
curl -X GET "http://127.0.0.1:8000/api/v1/specs/YOUR_SPEC_ID" ^
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## Complete Example (Copy-Paste Ready)

### 1. Login
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/login" -H "Content-Type: application/x-www-form-urlencoded" -d "username=admin&password=admin"
```

### 2. Generate (replace TOKEN)
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/generate" -H "Content-Type: application/json" -H "Authorization: Bearer YOUR_TOKEN" -d "{\"user_id\":\"admin\",\"prompt\":\"Design a 3-bedroom residential building in Mumbai with 2000 sq ft area\",\"project_id\":\"proj_001\",\"context\":{\"city\":\"Mumbai\",\"plot_area\":2000,\"building_type\":\"residential\"}}"
```

### 3. Check Database (replace SPEC_ID)
```bash
psql -U postgres -d bhiv_db -c "SELECT * FROM specs WHERE id = 'YOUR_SPEC_ID';"
```

### 4. Check Files (replace SPEC_ID)
```bash
dir backend\data\specs\YOUR_SPEC_ID.json
dir backend\data\geometry_outputs\YOUR_SPEC_ID.glb
```

### 5. Retrieve Spec (replace TOKEN and SPEC_ID)
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/specs/YOUR_SPEC_ID" -H "Authorization: Bearer YOUR_TOKEN"
```

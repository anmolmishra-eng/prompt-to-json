# Authentication Runbook

## JWT Secret Management

### Initial Setup
```bash
# Generate a secure JWT secret (run once)
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Example output
# rB9_Mh-5K_L4pQ_8tU-1vW_2xY_3zA_4bC_5dE_6fG

# Add to .env file
JWT_SECRET_KEY=rB9_Mh-5K_L4pQ_8tU-1vW_2xY_3zA_4bC_5dE_6fG
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### Secret Rotation (Every 90 days)
1. Generate new secret
2. Update JWT_SECRET_KEY in .env
3. All existing tokens remain valid for their 60-minute lifetime
4. After 1 hour, all users must re-login
5. Old secret becomes invalid for new tokens

## API Keys for Service-to-Service
```bash
# Create API key (admin only)
curl -X POST http://localhost:8000/api/v1/auth/api-key \
  -H "Authorization: Bearer {admin_token}" \
  -H "Content-Type: application/json" \
  -d '{"service": "compliance_check", "permissions": ["run_case"]}'

# Response:
# {
#   "api_key_id": "ak_xyz123",
#   "secret": "sk_...full key...",
#   "permissions": ["run_case"],
#   "created_at": "2025-11-15T14:30:00"
# }

# Revoke API key
curl -X DELETE http://localhost:8000/api/v1/auth/api-key/ak_xyz123 \
  -H "Authorization: Bearer {admin_token}"
```

## Login Flow
```python
import httpx

async def login():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/v1/auth/login",
            json={"username": "user@example.com", "password": "secure_password"}
        )

        if response.status_code == 200:
            token = response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            # Use headers for all subsequent requests
```

## Token Refresh
Tokens expire after 60 minutes. To refresh:

```python
response = await client.post(
    "http://localhost:8000/api/v1/auth/refresh",
    headers={"Authorization": f"Bearer {old_token}"}
)

new_token = response.json()["access_token"]
```

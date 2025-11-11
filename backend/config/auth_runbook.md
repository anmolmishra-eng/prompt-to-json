# Authentication Runbook

## JWT Secret Management

### Initial Setup
1. **Generate Strong Secret:**
   ```bash
   openssl rand -hex 32
   # Output: a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456
   ```

2. **Set Environment Variable:**
   ```bash
   export JWT_SECRET_KEY="a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456"
   ```

3. **Verify Configuration:**
   ```bash
   curl -X POST http://localhost:8000/api/v1/auth/login \
     -d "username=user&password=pass"
   ```

### Key Rotation Procedure

**Monthly Rotation (Recommended):**

1. **Generate New Secret:**
   ```bash
   NEW_SECRET=$(openssl rand -hex 32)
   echo "New secret: $NEW_SECRET"
   ```

2. **Update Environment:**
   ```bash
   # Update .env file
   sed -i "s/JWT_SECRET_KEY=.*/JWT_SECRET_KEY=$NEW_SECRET/" .env

   # Or update in secrets manager
   aws secretsmanager update-secret \
     --secret-id "design-engine/jwt-secret" \
     --secret-string "$NEW_SECRET"
   ```

3. **Rolling Deployment:**
   ```bash
   # Deploy with new secret
   kubectl set env deployment/design-engine JWT_SECRET_KEY="$NEW_SECRET"
   kubectl rollout restart deployment/design-engine
   ```

4. **Verify Rotation:**
   ```bash
   # Test new token generation
   curl -X POST https://api.designengine.com/api/v1/auth/login \
     -d "username=test&password=test"
   ```

### API Key Management

**Yotta API Key Setup:**
```bash
# Store in environment
export YOTTA_API_KEY="yotta_live_abc123def456"
export YOTTA_BASE_URL="https://api.yotta.com"

# Test connection
curl -H "Authorization: Bearer $YOTTA_API_KEY" \
  https://api.yotta.com/health
```

**Compliance API Key Setup:**
```bash
# Store Soham's compliance service key
export COMPLIANCE_API_KEY="comp_key_xyz789"
export SOHAM_URL="https://ai-rule-api-w7z5.onrender.com"

# Test connection
curl -H "Authorization: Bearer $COMPLIANCE_API_KEY" \
  $SOHAM_URL/health
```

### Token Configuration

**Current Settings:**
- **Algorithm:** HS256 (HMAC with SHA-256)
- **Expiration:** 24 hours (configurable)
- **Payload:** `{"sub": "username", "exp": timestamp}`

**Production Recommendations:**
- Use RS256 for distributed systems
- Implement refresh tokens for long-lived sessions
- Set shorter expiration (1-4 hours) for sensitive operations

### Emergency Procedures

**Compromised Secret Response:**
1. **Immediate Actions:**
   ```bash
   # Generate emergency secret
   EMERGENCY_SECRET=$(openssl rand -hex 32)

   # Update all instances immediately
   kubectl set env deployment/design-engine JWT_SECRET_KEY="$EMERGENCY_SECRET"

   # Force all users to re-authenticate
   kubectl rollout restart deployment/design-engine
   ```

2. **Audit & Investigation:**
   ```bash
   # Check recent token usage
   grep "JWT" /var/log/design-engine/audit.log | tail -100

   # Review Sentry for suspicious activity
   # Check access logs for unusual patterns
   ```

### Monitoring & Alerts

**Set up alerts for:**
- Failed authentication attempts > 10/minute
- JWT validation errors > 5/minute
- API key usage anomalies
- Secret rotation due dates

**Log Monitoring:**
```bash
# Monitor auth events
tail -f /var/log/design-engine/audit.log | grep "auth"

# Check token validation errors
grep "Invalid token" /var/log/design-engine/app.log
```

# Security Checklist

## ✅ Pre-Production Security Requirements

### Authentication & Authorization
- [ ] **JWT Secret Rotation:** Generate cryptographically secure JWT secret (32+ bytes)
  ```bash
  openssl rand -hex 32 > jwt_secret.key
  ```
- [ ] **API Key Security:** Store all API keys in secure vault (AWS Secrets Manager/HashiCorp Vault)
- [ ] **Token Expiration:** Set JWT expiration to 4 hours maximum for production
- [ ] **Rate Limiting:** Implement auth endpoint rate limiting (5 attempts/minute)
  ```nginx
  limit_req_zone $binary_remote_addr zone=auth:10m rate=5r/m;
  ```

### HTTPS & Transport Security
- [ ] **Force HTTPS:** Redirect all HTTP traffic to HTTPS
  ```nginx
  return 301 https://$server_name$request_uri;
  ```
- [ ] **TLS Configuration:** Use TLS 1.2+ with strong cipher suites
- [ ] **HSTS Headers:** Enable HTTP Strict Transport Security
  ```
  Strict-Transport-Security: max-age=31536000; includeSubDomains
  ```
- [ ] **Certificate Management:** Use automated certificate renewal (Let's Encrypt/ACM)

### Supabase Storage Security
- [ ] **AES-256 Encryption:** Enable encryption at rest for all buckets
  ```sql
  -- Verify encryption status
  SELECT bucket_id, encryption FROM storage.buckets;
  ```
- [ ] **Bucket ACLs:** Restrict bucket access to authenticated users only
- [ ] **Signed URLs Only:** Disable public access, use signed URLs exclusively
  ```javascript
  // Correct: Signed URL with expiration
  const { signedURL } = await supabase.storage
    .from('previews')
    .createSignedUrl('file.glb', 600); // 10 min expiry
  ```
- [ ] **File Type Validation:** Whitelist allowed file extensions (.glb, .stl, .zip)
- [ ] **File Size Limits:** Enforce maximum file sizes (50MB for geometry, 10MB for previews)

### Database Security
- [ ] **Connection Encryption:** Use SSL/TLS for all database connections
- [ ] **Least Privilege:** Database user has minimal required permissions
- [ ] **SQL Injection Prevention:** Use parameterized queries exclusively
- [ ] **Connection Pooling:** Implement secure connection pooling
- [ ] **Backup Encryption:** Encrypt database backups at rest

### API Security
- [ ] **Input Validation:** Validate all request payloads with Pydantic schemas
- [ ] **CORS Configuration:** Restrict origins to known domains
  ```python
  allow_origins=["https://app.designengine.com", "https://admin.designengine.com"]
  ```
- [ ] **Request Size Limits:** Limit request body size (10MB maximum)
- [ ] **SQL Injection Protection:** Use ORM exclusively, no raw SQL
- [ ] **XSS Prevention:** Sanitize all user inputs

### Monitoring & Alerting
- [ ] **Sentry Integration:** Configure error tracking with sensitive data filtering
  ```python
  sentry_sdk.init(
      dsn="your-dsn",
      before_send=filter_sensitive_data
  )
  ```
- [ ] **Security Alerts:** Set up alerts for:
  - Failed authentication attempts > 10/minute
  - Unusual API usage patterns
  - File upload anomalies
  - Database connection failures

### Compliance & Audit
- [ ] **Audit Logging:** Log all security-relevant events
  ```python
  # Required audit events
  - User authentication (success/failure)
  - File uploads/downloads
  - API key usage
  - Admin actions
  - Data access patterns
  ```
- [ ] **Log Retention:** Store security logs for minimum 90 days
- [ ] **Access Reviews:** Monthly review of user access and permissions
- [ ] **Vulnerability Scanning:** Weekly dependency vulnerability scans

## ⚠️ Production Deployment Checklist

### Environment Configuration
- [ ] **Secrets Management:** No hardcoded secrets in code/config
- [ ] **Environment Separation:** Separate dev/staging/prod environments
- [ ] **Debug Mode:** Disable debug mode in production (`DEBUG=false`)
- [ ] **Error Handling:** Generic error messages (no stack traces to users)

### Infrastructure Security
- [ ] **Firewall Rules:** Restrict inbound traffic to necessary ports only
- [ ] **VPC Configuration:** Deploy in private subnets with NAT gateway
- [ ] **Load Balancer:** Use ALB/NLB with SSL termination
- [ ] **Auto-scaling:** Configure secure auto-scaling policies

### Container Security (if using Docker/K8s)
- [ ] **Base Images:** Use minimal, security-patched base images
- [ ] **Non-root User:** Run containers as non-root user
- [ ] **Resource Limits:** Set CPU/memory limits
- [ ] **Security Context:** Configure security contexts appropriately

## 🔍 Security Testing

### Automated Testing
- [ ] **SAST Scanning:** Static application security testing in CI/CD
- [ ] **Dependency Scanning:** Automated vulnerability scanning
  ```bash
  pip-audit --requirement requirements.txt
  ```
- [ ] **Container Scanning:** Scan container images for vulnerabilities
- [ ] **API Security Testing:** Automated API security tests

### Manual Testing
- [ ] **Penetration Testing:** Annual third-party security assessment
- [ ] **Authentication Testing:** Test JWT validation, session management
- [ ] **Authorization Testing:** Verify access controls work correctly
- [ ] **Input Validation Testing:** Test for injection vulnerabilities

## 🚨 Incident Response

### Preparation
- [ ] **Incident Response Plan:** Document security incident procedures
- [ ] **Contact List:** Maintain updated security contact information
- [ ] **Backup Procedures:** Test backup and recovery procedures monthly
- [ ] **Communication Plan:** Define internal/external communication protocols

### Detection & Response
- [ ] **Monitoring Dashboard:** Real-time security monitoring dashboard
- [ ] **Alert Escalation:** Define alert severity levels and escalation paths
- [ ] **Forensic Logging:** Ensure sufficient logging for incident investigation
- [ ] **Recovery Procedures:** Document system recovery procedures

## 📅 Regular Security Maintenance

### Weekly Tasks
- [ ] Review security alerts and logs
- [ ] Update dependencies with security patches
- [ ] Verify backup integrity
- [ ] Check SSL certificate expiration dates

### Monthly Tasks
- [ ] Rotate API keys and secrets
- [ ] Review user access and permissions
- [ ] Analyze security metrics and trends
- [ ] Update security documentation

### Quarterly Tasks
- [ ] Conduct security training for development team
- [ ] Review and update security policies
- [ ] Perform security architecture review
- [ ] Test incident response procedures

## 📝 Compliance Requirements

### Data Protection
- [ ] **GDPR Compliance:** Implement data subject rights (if applicable)
- [ ] **Data Minimization:** Collect only necessary user data
- [ ] **Data Retention:** Define and implement data retention policies
- [ ] **Privacy Policy:** Maintain updated privacy policy

### Industry Standards
- [ ] **SOC 2 Type II:** Consider SOC 2 compliance for enterprise customers
- [ ] **ISO 27001:** Implement information security management system
- [ ] **OWASP Top 10:** Address all OWASP Top 10 vulnerabilities
- [ ] **Security Framework:** Adopt NIST Cybersecurity Framework

---

**⚠️ Critical:** All items marked as "Critical" must be completed before production deployment.

**📄 Documentation:** Maintain security documentation and update this checklist quarterly.

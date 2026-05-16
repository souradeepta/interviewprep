# Security Best Practices: Protecting Systems and Data

Master security fundamentals for building secure systems.

---

## OWASP Top 10 (2021)

### 1. Broken Access Control

**Problem:** Users access data/features they shouldn't.

```python
# ❌ Bad: No access check
@app.get("/users/{user_id}")
def get_user(user_id: int):
    return db.get_user(user_id)  # Anyone can read anyone's data!

# ✓ Good: Verify ownership
@app.get("/users/{user_id}")
def get_user(user_id: int, current_user = Depends(get_current_user)):
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(403, "Not authorized")
    return db.get_user(user_id)
```

### 2. Cryptographic Failures

**Problem:** Sensitive data transmitted/stored unencrypted.

```python
# ❌ Bad: Plain password
user.password = request.password
db.save(user)

# ✓ Good: Hash password
from werkzeug.security import generate_password_hash
user.password = generate_password_hash(request.password)
db.save(user)

# ✓ Good: Encrypt in transit
# Use HTTPS for all traffic
# Use TLS 1.3+
```

### 3. Injection

**Problem:** Attacker inputs malicious code interpreted as code.

```python
# ❌ Bad: SQL injection
query = f"SELECT * FROM users WHERE email = '{email}'"

# ✓ Good: Parameterized query
query = "SELECT * FROM users WHERE email = %s"
db.execute(query, (email,))

# ❌ Bad: XSS injection
<div>{{ user_input }}</div>

# ✓ Good: Escape HTML
<div>{{ user_input | escape }}</div>
```

### 4. Insecure Design

**Problem:** Security not built in from start.

**Solutions:**
- Threat modeling at design time
- Security review before development
- Defense in depth (multiple layers)

### 5. Security Misconfiguration

**Problem:** Default passwords, unnecessary features enabled, outdated dependencies.

```python
# ❌ Bad: Default AWS credentials
aws.configure(
    aws_access_key_id="AKIAIOSFODNN7EXAMPLE",
    aws_secret_access_key="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
)

# ✓ Good: Use IAM roles
session = boto3.Session()  # Uses instance IAM role

# ❌ Bad: Debug mode on production
app.config['DEBUG'] = True

# ✓ Good: Debug only in development
app.config['DEBUG'] = os.getenv('ENVIRONMENT') == 'development'
```

---

## Authentication & Authorization

### Password Security

```python
# Requirements:
# - Min 12 characters
# - Mix of upper, lower, numbers, special chars
# - No common patterns (123456, qwerty)
# - Hash with bcrypt/Argon2 (not MD5/SHA1)

from bcrypt import hashpw, checkpw

password_hash = hashpw(password.encode(), bcrypt.gensalt())
if checkpw(password.encode(), password_hash):
    # Valid
```

### OAuth 2.0 / OpenID Connect

```
User → Login with Google
   ↓
Google authenticates user
   ↓
Google returns token
   ↓
App uses token to access user data
```

**Benefits:** No password storage, user controls data

---

## API Security

### API Key Management

```python
# ❌ Bad: API key in code
API_KEY = "sk_live_abcd1234efgh5678"

# ✓ Good: API key in environment
import os
API_KEY = os.getenv('API_KEY')

# ✓ Good: Rotate keys regularly
# ✓ Good: Use separate keys per environment
# ✓ Good: Rate limit per key
```

### CORS (Cross-Origin Resource Sharing)

```python
# ❌ Bad: Allow all origins
@app.middleware("http")
async def cors_middleware(request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response

# ✓ Good: Whitelist origins
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://example.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"]
)
```

---

## Data Protection

### Encryption in Transit

```
# Use HTTPS/TLS for all traffic
# Minimum: TLS 1.2
# Better: TLS 1.3
```

### Encryption at Rest

```python
# Encrypt sensitive fields before storing
from cryptography.fernet import Fernet

cipher = Fernet(key)
encrypted = cipher.encrypt(social_security_number.encode())
db.save(encrypted)

# Decrypt when needed
decrypted = cipher.decrypt(encrypted).decode()
```

### PII (Personally Identifiable Information)

```python
# ✓ Good: Hash PII for anonymization
import hashlib

hashed_email = hashlib.sha256(email.encode()).hexdigest()
# Can use hashed email as lookup without revealing actual email
```

---

## Security Headers

```
# HTTP Response Headers
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Content-Security-Policy: default-src 'self'
X-XSS-Protection: 1; mode=block
Referrer-Policy: strict-origin-when-cross-origin
```

---

## Logging & Monitoring

```python
# ✓ Log security events
logger.info(f"User {user_id} failed login attempt")
logger.warning(f"Excessive failed logins from {ip_address}")
logger.error(f"Unauthorized access attempt to {resource}")

# ❌ Don't log sensitive data
logger.debug(f"Password: {password}")  # ❌ Never!
logger.debug(f"Credit card: {cc_number}")  # ❌ Never!

# ✓ Alert on suspicious activity
if failed_logins > 5:
    alert_security_team()
```

---

## Security Checklist

- ✓ HTTPS/TLS for all traffic
- ✓ Passwords hashed (bcrypt/Argon2)
- ✓ Access control on all endpoints
- ✓ Input validation and sanitization
- ✓ Parameterized queries (prevent SQL injection)
- ✓ HTML escaping (prevent XSS)
- ✓ Rate limiting on login/APIs
- ✓ No default credentials
- ✓ Dependencies up-to-date
- ✓ Security headers configured
- ✓ Sensitive data not logged
- ✓ Encryption at rest for PII
- ✓ Regular security audits
- ✓ Incident response plan


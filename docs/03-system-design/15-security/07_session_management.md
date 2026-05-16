# Session Management Security

## Problem Statement

### Functional Requirements
- Create secure session tokens
- Track session activity and timeout
- Support session revocation
- Detect and prevent session hijacking
- Enable concurrent session limits

### Non-Functional Requirements
- Latency: Session lookup < 10ms p99
- Security: Cryptographic session IDs
- Timeout: Idle > 30 minutes logout
- Availability: 99.99% session availability
- Scalability: Support 1B+ concurrent sessions

## System Overview

**Scale Metrics:**
- Throughput: Millions of security operations per second
- Latency: Milliseconds for security processing
- Data volume: Petabytes of security logs
- User population: Billions of users
- Availability: 99.99%+ uptime SLA

**Key Components:**
- Identity and authentication
- Encryption and key management
- Access control and authorization
- Threat detection and prevention
- Audit and compliance tracking

## Architecture Diagrams

### Security Architecture Layers

```mermaid
graph TB
    subgraph "Perimeter"
        P1["DDoS Protection"]
        P2["WAF"]
        P3["IDS/IPS"]
    end

    subgraph "Authentication"
        A1["Authentication"]
        A2["MFA"]
        A3["Session Management"]
    end

    subgraph "Application"
        AP1["Authorization"]
        AP2["Input Validation"]
        AP3["Encryption"]
    end

    subgraph "Data"
        D1["Encryption at Rest"]
        D2["Access Logging"]
        D3["Audit Trail"]
    end

    P1 --> P2
    P2 --> P3
    P3 --> A1
    A1 --> A2
    A2 --> A3
    A3 --> AP1
    AP1 --> AP2
    AP2 --> AP3
    AP3 --> D1
    D1 --> D2
    D2 --> D3

    style P1 fill:#ffcdd2
    style A1 fill:#fff9c4
    style AP1 fill:#c8e6c9
    style D1 fill:#bbdefb
```

### Authentication Flow

```mermaid
graph LR
    A["User"] --> B["Authenticate"]
    B --> C["Verify Credentials"]
    C --> D["MFA Check"]
    D --> E["Issue Token"]
    E --> F["Access Granted"]

    style B fill:#fff9c4
    style D fill:#ffccbc
    style F fill:#c8e6c9
```

### Encryption and Key Management

```mermaid
graph TB
    D["Data"] --> E["Encrypt"]
    E --> K["Key Manager"]
    K --> S["Secure Storage"]
    S --> R["Retrieve Data"]
    R --> DE["Decrypt"]
    DE --> O["Output"]

    style E fill:#ffccbc
    style K fill:#fff9c4
    style S fill:#c8e6c9
```

### Threat Detection Pipeline

```mermaid
graph LR
    T["Traffic"] --> A["Analyze"]
    A --> D["Detect Threats"]
    D --> R["Report"]
    R --> M["Mitigate"]
    M --> L["Log"]

    style A fill:#ffccbc
    style D fill:#ffcdd2
    style M fill:#c8e6c9
```

### Audit and Compliance

```mermaid
graph TB
    E["Security Event"] --> L["Log"]
    L --> A["Aggregate"]
    A --> M["Monitor"]
    M --> R["Report"]
    R --> C["Compliance Check"]

    style E fill:#fff9c4
    style M fill:#bbdefb
    style C fill:#c8e6c9
```

## Data Flow Scenarios

### Scenario 1: Secure Authentication
1. User submits credentials
2. Hash password and compare
3. If match, generate MFA challenge
4. User provides MFA code
5. Issue signed security token
6. Grant authenticated access

### Scenario 2: Encryption and Decryption
1. Plaintext data arrives
2. Generate random IV
3. Encrypt with session key
4. Store encrypted data
5. On retrieval, get IV
6. Decrypt with session key
7. Return plaintext

### Scenario 3: Threat Detection
1. Monitor incoming traffic
2. Analyze packet patterns
3. Check against threat rules
4. If match detected, alert
5. Activate mitigation rules
6. Log security event

## Security Best Practices

### Defense in Depth
- **Multiple layers**: Never rely on single defense
- **Redundancy**: Multiple detection mechanisms
- **Isolation**: Minimize blast radius
- **Monitoring**: Detect at each layer

### Principle of Least Privilege
- **Minimal access**: Grant only needed permissions
- **Role-based**: Use roles not individuals
- **Time-limited**: Revoke access after use
- **Auditable**: Track all access

### Security by Design
- **Early**: Integrate security from start
- **Default secure**: Secure defaults, explicit to weaken
- **Testing**: Security testing in CI/CD
- **Review**: Regular security reviews

## Back-of-Envelope Calculations

### User Authentication Scale
```
Daily active users: 100M
Auth requests per user: 5
Daily auth: 500M requests
RPS: 500M / 86400 ≈ 5,787 RPS
Peak hour (10x): 57,870 RPS
Auth servers: 57,870 / 10K per server ≈ 6 servers
```

### Encryption Operations
```
Data per transaction: 1 KB
Daily transactions: 10B
Daily encryption: 10B × 1 KB = 10 TB
Encryption throughput: 100 MB/s
Hours needed: 10TB / 100MB/s = 100K seconds ≈ 28 hours
Requires parallel: 10 concurrent processes
```

### Audit Log Storage
```
Log entries per day: 100B
Bytes per entry: 500 bytes
Daily log: 100B × 500 = 50 TB
Storage per year: 50 TB × 365 = 18.25 PB
Retention: 7 years = 127.75 PB
Compression: 10x → 12.8 PB
```

## Interview Questions & Answers

### Q1: Design authentication system for 1B users

**Answer:**
1. **Architecture**: Distributed auth servers across regions
2. **Password storage**: Bcrypt with salt, not plaintext
3. **MFA**: Support TOTP, SMS, push notifications
4. **Tokens**: Short-lived access, long-lived refresh
5. **Session**: Track across services with JWT
6. **Recovery**: Backup codes, email verification

### Q2: Implement end-to-end encryption

**Answer:**
- **Client-side**: Encrypt before sending
- **Key management**: User controls keys
- **Server**: Cannot decrypt even with access
- **Key exchange**: ECDH for secure sharing
- **Forward secrecy**: Derive keys per message
- **Compliance**: Support key recovery for legal

### Q3: Prevent common web vulnerabilities

**Answer:**
- **SQL injection**: Parameterized queries always
- **XSS**: Sanitize and escape output
- **CSRF**: Token validation on state changes
- **Clickjacking**: X-Frame-Options header
- **Insecure deserialization**: Validate input
- **Weak crypto**: AES-256, TLS 1.2+

### Q4: Design DDoS protection system

**Answer:**
- **Detection**: Monitor traffic patterns
- **Filtering**: Block at CDN/ISP level
- **Rate limiting**: Per IP or user
- **Captcha**: Challenge suspicious traffic
- **Scaling**: Absorb attack with capacity
- **Failover**: Automatic to mitigation

### Q5: Ensure data privacy and compliance

**Answer:**
- **Encryption**: At rest and in transit
- **Anonymization**: Remove PII when possible
- **Access control**: RBAC for data access
- **Audit**: Log all access and changes
- **Retention**: Delete per policy
- **Compliance**: GDPR, CCPA, HIPAA

### Q6: Implement secure API design

**Answer:**
- **Authentication**: OAuth 2.0 or mutual TLS
- **Authorization**: Scope-based permissions
- **Rate limiting**: Prevent abuse
- **Input validation**: Strict validation rules
- **Output encoding**: Prevent injection
- **Logging**: Complete audit trail

## Technology Stack

| Component | Technology | Why |
|-----------|-----------|-----|
| Authentication | OAuth 2.0, OpenID Connect | Industry standard |
| Encryption | TLS 1.3, AES-256-GCM | Strong, fast |
| Key Management | AWS KMS, HashiCorp Vault | Secure, managed |
| Identity | LDAP, Active Directory | Enterprise standard |
| Monitoring | SIEM, ELK Stack | Threat detection |
| Compliance | Keycloak, Okta | Centralized identity |
| WAF | ModSecurity, WAF rules | Attack prevention |

## Lessons Learned

1. **Security is not optional**: Build in from start, not after
2. **Assume breach**: Design for recovery, not prevention alone
3. **People matter**: Training prevents more attacks than technology
4. **Measure security**: Track metrics, improve continuously
5. **Keep it simple**: Complex systems have more flaws

## Related Topics

- Cryptography and encryption algorithms
- Identity and access management (IAM)
- Threat detection and response
- Incident management and forensics
- Security compliance and standards
- Secure software development
- Cloud security and multi-tenancy


## Code Implementation

### Python
```python
import hashlib, hmac, secrets, time
import jwt                        # pip install PyJWT
from cryptography.fernet import Fernet
from typing import Optional

SECRET_KEY = secrets.token_bytes(32)

# ── Password hashing ────────────────────────────────────────────────────────
def hash_password(password: str) -> str:
    """Argon2 / bcrypt preferable in production; PBKDF2 shown here."""
    salt = secrets.token_bytes(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 260_000)
    return f"{salt.hex()}:{dk.hex()}"

def verify_password(stored: str, provided: str) -> bool:
    salt_hex, dk_hex = stored.split(":")
    salt = bytes.fromhex(salt_hex)
    dk = hashlib.pbkdf2_hmac("sha256", provided.encode(), salt, 260_000)
    return hmac.compare_digest(dk.hex(), dk_hex)  # constant-time comparison

# ── JWT tokens ──────────────────────────────────────────────────────────────
def create_token(user_id: int, roles: list[str], ttl_seconds: int = 3600) -> str:
    payload = {
        "sub": user_id,
        "roles": roles,
        "iat": time.time(),
        "exp": time.time() + ttl_seconds,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def verify_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return None

# ── Symmetric encryption ────────────────────────────────────────────────────
key = Fernet.generate_key()
fernet = Fernet(key)
encrypted = fernet.encrypt(b"sensitive data")
print(fernet.decrypt(encrypted))   # b"sensitive data"
```

### Java
```java
import io.jsonwebtoken.*;
import io.jsonwebtoken.security.Keys;
import javax.crypto.SecretKey;
import java.security.MessageDigest;
import java.security.SecureRandom;
import java.util.*;

public class SecurityUtils {
    private static final SecureRandom RANDOM = new SecureRandom();
    private static final SecretKey JWT_KEY = Keys.secretKeyFor(SignatureAlgorithm.HS256);

    // ── Password hashing ─────────────────────────────────────────────────
    public static String hashPassword(String password) throws Exception {
        byte[] salt = new byte[16];
        RANDOM.nextBytes(salt);
        MessageDigest md = MessageDigest.getInstance("SHA-256");
        md.update(salt);
        byte[] hash = md.digest(password.getBytes());
        return Base64.getEncoder().encodeToString(salt) + ":" +
               Base64.getEncoder().encodeToString(hash);
    }

    public static boolean verifyPassword(String stored, String provided) throws Exception {
        String[] parts = stored.split(":");
        byte[] salt = Base64.getDecoder().decode(parts[0]);
        MessageDigest md = MessageDigest.getInstance("SHA-256");
        md.update(salt);
        byte[] expected = Base64.getDecoder().decode(parts[1]);
        byte[] actual = md.digest(provided.getBytes());
        return MessageDigest.isEqual(expected, actual); // constant-time
    }

    // ── JWT ──────────────────────────────────────────────────────────────
    public static String createToken(long userId, List<String> roles) {
        return Jwts.builder()
            .subject(String.valueOf(userId))
            .claim("roles", roles)
            .issuedAt(new Date())
            .expiration(new Date(System.currentTimeMillis() + 3_600_000)) // 1h
            .signWith(JWT_KEY)
            .compact();
    }

    public static Claims verifyToken(String token) {
        return Jwts.parser().verifyWith(JWT_KEY).build()
               .parseSignedClaims(token).getPayload();
    }
}
```

## Back-of-the-Envelope Calculations

**Crypto Performance:**
- AES-256-GCM: 3GB/sec throughput (hardware accelerated)
- RSA-2048 sign: 5ms; verify: 0.3ms
- bcrypt (cost=12): 250ms per hash — good for login, too slow for API
- PBKDF2 (260K iterations): 100ms — balance of security and speed
- JWT verify (HS256): <1ms — suitable for every request

**Token Storage:**
- 1M active sessions × 256 bytes = 256MB in Redis
- 100K logins/day × 256 bytes = 25MB new tokens/day
- TTL 1 hour → ~4% of tokens expire per minute → cleanup manageable
## Follow-up Questions

1. **How would you handle this at 10x the scale described?**
   - What breaks first? (typically: single DB, single cache node, single region)
   - What architectural changes are required?

2. **What are the consistency vs. availability trade-offs in your design?**
   - Where did you accept eventual consistency?
   - Which operations require strong consistency and why?

3. **How would you debug a sudden latency spike in production?**
   - What metrics would you look at first?
   - What's your runbook for the top 3 likely causes?

4. **How does your design handle partial failures?**
   - What happens if one component is slow (not down)?
   - How do you prevent cascading failures?

5. **What would you change if you had to build this in one week vs. six months?**
   - What corners can safely be cut initially?
   - What must be right from day one?

6. **How would you migrate from the current design to a better one without downtime?**
   - What's the strangler-fig or blue-green strategy here?
   - How do you validate correctness during migration?
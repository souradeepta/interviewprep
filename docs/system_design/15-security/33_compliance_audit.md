# Compliance and Auditing

## Problem Statement

### Functional Requirements
- Track security events
- Maintain audit logs
- Support compliance reporting
- Enable security assessments
- Document security controls

### Non-Functional Requirements
- Logging: 100% event capture
- Retention: 7+ years archive
- Query: Search logs < 5 seconds
- Compliance: SOC 2, ISO 27001
- Immutability: Tamper-proof logs

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
import asyncio
import aiohttp
from dataclasses import dataclass
from typing import Optional, List
import time, logging

logger = logging.getLogger(__name__)

@dataclass
class ServiceConfig:
    host: str = "localhost"
    port: int = 8080
    timeout_seconds: float = 5.0
    max_retries: int = 3

class ServiceClient:
    """Generic service client with retry and circuit breaker."""
    def __init__(self, config: ServiceConfig):
        self.config = config
        self.base_url = f"http://{config.host}:{config.port}"
        self._failures = 0
        self._circuit_open = False
        self._last_failure: Optional[float] = None

    def _is_circuit_open(self) -> bool:
        if not self._circuit_open:
            return False
        # Half-open after 60s — allow one request through
        if time.time() - self._last_failure > 60:
            self._circuit_open = False
            return False
        return True

    async def call(self, endpoint: str, payload: dict) -> Optional[dict]:
        if self._is_circuit_open():
            logger.warning("Circuit open — fast fail")
            return None

        timeout = aiohttp.ClientTimeout(total=self.config.timeout_seconds)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            for attempt in range(self.config.max_retries):
                try:
                    async with session.post(
                        f"{self.base_url}{endpoint}", json=payload
                    ) as resp:
                        resp.raise_for_status()
                        self._failures = 0              # reset on success
                        return await resp.json()
                except Exception as e:
                    logger.warning(f"Attempt {attempt+1} failed: {e}")
                    if attempt < self.config.max_retries - 1:
                        await asyncio.sleep(2 ** attempt)  # exponential backoff
            # All retries exhausted
            self._failures += 1
            if self._failures >= 5:                     # open circuit
                self._circuit_open = True
                self._last_failure = time.time()
            return None
```

### Java
```java
import java.net.http.*;
import java.net.URI;
import java.time.Duration;
import java.util.concurrent.atomic.*;
import java.util.concurrent.CompletableFuture;

/** Generic resilient service client with circuit breaker + retry. */
public class ServiceClient {
    private final String baseUrl;
    private final HttpClient http;
    private final AtomicInteger failures = new AtomicInteger(0);
    private final AtomicBoolean circuitOpen = new AtomicBoolean(false);
    private volatile long lastFailureTime;

    public ServiceClient(String host, int port) {
        this.baseUrl = "http://" + host + ":" + port;
        this.http = HttpClient.newBuilder()
            .connectTimeout(Duration.ofSeconds(5))
            .build();
    }

    private boolean isCircuitOpen() {
        if (!circuitOpen.get()) return false;
        // Half-open after 60s
        if (System.currentTimeMillis() - lastFailureTime > 60_000) {
            circuitOpen.set(false);
            return false;
        }
        return true;
    }

    public CompletableFuture<String> call(String path, String jsonBody) {
        if (isCircuitOpen())
            return CompletableFuture.failedFuture(
                new RuntimeException("Circuit open"));

        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create(baseUrl + path))
            .header("Content-Type", "application/json")
            .POST(HttpRequest.BodyPublishers.ofString(jsonBody))
            .timeout(Duration.ofSeconds(5))
            .build();

        return http.sendAsync(request, HttpResponse.BodyHandlers.ofString())
            .thenApply(resp -> {
                if (resp.statusCode() >= 500) throw new RuntimeException("Server error");
                failures.set(0);  // reset on success
                return resp.body();
            })
            .exceptionally(ex -> {
                if (failures.incrementAndGet() >= 5) {
                    circuitOpen.set(true);
                    lastFailureTime = System.currentTimeMillis();
                }
                return null;
            });
    }
}
```

## Back-of-the-Envelope Calculations

**System Load Estimation:**
- 1M daily active users × 10 requests/day = 10M requests/day
- Peak QPS = 10M / 86400 × 3 (peak factor) ≈ 350 QPS
- API server capacity: 1000 QPS/server → 1 server sufficient at peak
- With 2x redundancy: 2 servers minimum

**Storage Estimation:**
- 1M users × 10KB average data = 10GB structured data
- Annual growth: 10GB × 365 = 3.65TB/year
- With 3x replication: 11TB/year
- SSD cost ($0.10/GB): $1,100/year

**Bandwidth:**
- 350 QPS × 10KB response = 3.5MB/sec outbound
- Monthly egress: 3.5MB × 86400 × 30 = 9TB/month
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
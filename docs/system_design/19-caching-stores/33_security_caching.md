# Security in Caching Systems

## Problem Statement

### Functional Requirements
- Encrypt sensitive data in cache
- Control access to cache entries
- Prevent cache poisoning
- Audit cache access
- Support TTL for sensitive data

### Non-Functional Requirements
- Encryption: AES-256 minimum
- Latency: Encryption < 1ms overhead
- Compliance: SOC 2, HIPAA support
- Audit: Complete access logs
- Confidentiality: No data leakage

## System Overview

**Scale Metrics:**
- Throughput: Millions of cache operations per second
- Latency: Microseconds to milliseconds
- Data volume: Terabytes to Petabytes
- Concurrent connections: Millions
- Availability: 99.99%+ uptime SLA

**Key Components:**
- Data storage and retrieval
- Cache management and eviction
- Replication and durability
- Monitoring and performance
- Recovery and high availability

## Architecture Diagrams

### Cache System Architecture

```mermaid
graph TB
    subgraph "Clients"
        C1["Client 1"]
        C2["Client 2"]
        C3["Client N"]
    end

    subgraph "Cache Layer"
        CA1["Cache Node 1"]
        CA2["Cache Node 2"]
        CA3["Cache Node 3"]
    end

    subgraph "Storage"
        S1["Primary DB"]
        S2["Replicas"]
    end

    C1 --> CA1
    C2 --> CA2
    C3 --> CA3
    CA1 --> S1
    CA2 --> S1
    CA3 --> S1
    S1 --> S2

    style C1 fill:#e1f5ff
    style CA1 fill:#f3e5f5
    style S1 fill:#e8f5e9
```

### Data Flow in Cache

```mermaid
graph LR
    A["Request"] --> B["Check Cache"]
    B --> C["Cache Hit"]
    C --> D["Return Data"]
    B --> E["Cache Miss"]
    E --> F["Query DB"]
    F --> G["Update Cache"]
    G --> D

    style C fill:#c8e6c9
    style E fill:#ffccbc
    style D fill:#fff9c4
```

### Replication and Failover

```mermaid
graph TB
    P["Primary"] -->|Replicate| R1["Replica 1"]
    P -->|Replicate| R2["Replica 2"]
    P -->|Heartbeat| H["Health Check"]
    H -->|Failure| F["Failover"]
    F -->|Promote| R1
    R1 -->|New Primary| N["Clients"]

    style P fill:#e1f5ff
    style R1 fill:#c8e6c9
    style F fill:#fff9c4
```

### Multi-Level Caching

```mermaid
graph TB
    R["Request"] --> L1["L1 Cache"]
    L1 --> H1["Hit"]
    L1 --> M1["Miss"]
    M1 --> L2["L2 Cache"]
    L2 --> H2["Hit"]
    L2 --> M2["Miss"]
    M2 --> DB["Database"]
    DB --> U1["Update L2"]
    U1 --> U2["Update L1"]

    style H1 fill:#c8e6c9
    style H2 fill:#bbdefb
    style DB fill:#ffccbc
```

### Performance Monitoring

```mermaid
graph TB
    O["Operations"] --> M["Metrics"]
    M --> A["Analysis"]
    A --> D["Dashboard"]
    A --> AL["Alerts"]
    AL --> OPT["Optimization"]

    style M fill:#bbdefb
    style D fill:#c8e6c9
    style OPT fill:#fff9c4
```

## Data Flow Scenarios

### Scenario 1: Cache Hit
1. Request arrives at cache layer
2. Hash key to find cache partition
3. Lookup in local cache
4. Found in cache (hit)
5. Return data to client
6. Update access time

### Scenario 2: Cache Miss
1. Request arrives at cache layer
2. Cache miss detected
3. Query underlying storage
4. Data returned from storage
5. Store in cache for future
6. Return to client

### Scenario 3: Failover
1. Primary cache node fails
2. Health check detects failure
3. Promote replica to primary
4. Redirect traffic to new primary
5. Sync other replicas
6. Recovery of failed node

## Performance Optimization

### Cache Efficiency
- **Hit rate**: Optimize for > 90% hit rate
- **Eviction**: LRU, LFU, or custom policies
- **Warming**: Pre-load hot data
- **Batching**: Group operations

### Resource Optimization
- **Memory**: Compress, deduplicate data
- **CPU**: Reduce hashing, optimize structures
- **Network**: Batch updates, use compression
- **Storage**: Tiered storage, archival

### Cost Optimization
- **Reserved instances**: Baseline capacity
- **Spot instances**: Flexible workloads
- **Auto-scaling**: Match demand
- **Cleanup**: Remove unused data

## Back-of-Envelope Calculations

### Cache Scale
```
Daily active users: 100M
Requests per user: 50
Daily requests: 5B
Peak RPS: 57,870
Cache servers (10K RPS each): 6 servers
Data per user: 10 KB
Total cache: 100M × 10 KB = 1 TB
```

### Hit Rate Impact
```
Without cache: 100M users × 50 req × 10ms DB = 50M seconds = 579 days
With 90% hit rate: 10% × 579 = 58 days
Speedup: 10x faster response times
```

### Replication Overhead
```
Primary data: 1 TB
Replicas: 3 copies
Total: 4 TB storage
Replication bandwidth: 1TB per day
Network: 1TB / 86400 = 11.5 MB/s
```

## Interview Questions & Answers

### Q1: Design a distributed cache system for 100M users

**Answer:**
1. **Architecture**: Distributed cache with replication
2. **Sharding**: Consistent hashing for scaling
3. **Replication**: 3-way for durability
4. **Eviction**: LRU for memory management
5. **Monitoring**: Real-time metrics and alerting
6. **Recovery**: Automatic failover and rebuild

### Q2: Handle cache invalidation at scale

**Answer:**
- **TTL-based**: Automatic expiration by time
- **Event-based**: Invalidate on data change
- **Broadcast**: Propagate across all nodes
- **Selective**: Invalidate only affected keys
- **Stampede**: Use locks to prevent queries

### Q3: Optimize cache hit rate

**Answer:**
- **Prefetch**: Load predictable data
- **Warm-up**: Pre-populate at startup
- **Eviction**: Better policy (LFU vs LRU)
- **TTL tuning**: Balance freshness vs hits
- **Analysis**: Monitor and adjust

### Q4: Design failover for caching system

**Answer:**
- **Detection**: Health checks < 10 seconds
- **Promotion**: Replica becomes primary
- **Redirect**: Route to new primary
- **Consistency**: Sync remaining replicas
- **Testing**: Regular failover drills

### Q5: Multi-level caching strategy

**Answer:**
- **L1**: Local app cache (milliseconds)
- **L2**: Distributed cache (tens of ms)
- **L3**: Database cache (hundreds of ms)
- **Miss**: Query database if all miss
- **Propagate**: Populate all levels

### Q6: Cost-optimize caching infrastructure

**Answer:**
- **Reserved**: Baseline capacity commitment
- **Spot**: Flexible non-critical workloads
- **Auto-scale**: Adjust to demand
- **Cleanup**: Remove unused data
- **Monitoring**: Track cost per operation

## Technology Stack

| Component | Technology | Why |
|-----------|-----------|-----|
| Cache | Redis, Memcached | Fast, distributed |
| Store | PostgreSQL, MongoDB | Durable storage |
| Replication | Streaming replication | Real-time sync |
| Monitoring | Prometheus, Datadog | Metrics & alerts |
| Failover | Sentinel, etcd | Automatic recovery |
| Compression | Snappy, ZSTD | Reduce footprint |

## Lessons Learned

1. **Cache is critical**: Even small improvements 10x impact
2. **Measure everything**: Can't optimize what you don't measure
3. **Consistency matters**: Stale cache causes hard bugs
4. **Failures happen**: Design for recovery, not prevention
5. **Simplicity wins**: Complex caching = debugging nightmare

## Related Topics

- Memory management and garbage collection
- Distributed systems consistency
- Replication and durability
- Performance monitoring and tuning
- Cost optimization strategies
- High availability architecture
- Security in distributed systems


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
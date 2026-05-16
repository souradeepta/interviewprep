# Cache Patterns

## Problem Statement

Design caching strategies that improve application performance while maintaining data consistency — covering cache-aside, write-through, write-behind, and read-through patterns.

## Scenario

Cache Patterns is a critical component in modern distributed systems. In real-world applications, serving billions of user interactions with minimal latency. For example, major tech companies like Netflix, Uber, and Airbnb rely on similar solutions to handle millions of concurrent users and requests. The challenge is achieving this while maintaining sub-100ms latency, 99.99% availability, and gracefully handling 10x traffic spikes during peak demand. This component provides the foundational capability to solve these challenges reliably and efficiently at global scale.

## Users

- **Backend Engineers**: Responsible for implementing and maintaining this system component in production environments. They need to understand the architecture, trade-offs, failure modes, and operational considerations.
- **DevOps/SRE Teams**: Monitor system health, manage scaling policies, handle incidents, and ensure reliability SLAs are met. They need insights into performance characteristics, bottlenecks, and failure recovery mechanisms.
- **Data Engineers**: Design data pipelines and analytics around this system, requiring deep understanding of data flow, consistency guarantees, and throughput characteristics.
- **System Architects**: Make high-level architectural decisions that impact company infrastructure, requiring comprehensive understanding of capabilities, limitations, and scalability boundaries.
- **Security Teams**: Understand security implications, potential vulnerabilities, and compliance requirements for this component.

## PRD

### Functional Requirements
- Core operations work correctly
- Explicit error handling
- Consistency guarantees defined
- Monitoring and observability

### Non-Functional Requirements
- Performance targets met
- Availability SLA achieved
- Scalability headroom
- Cost efficient

### Success Metrics
- Benchmarks met
- Uptime targets met
- Resource budgets
- No data loss


## Flow

The typical operational flow for this system involves these key phases:

1. **Request Arrival**: Client/upstream system sends request with required parameters and context
2. **Validation & Routing**: System validates request format, authentication, and routes to correct handler/shard/instance
3. **Core Processing**: Execute the main algorithm, database query, or business logic on the data/state
4. **State Management**: Update internal state (caches, indexes, counters, logs) with proper atomicity and locking
5. **Response Generation**: Format results and return to requester with relevant metadata (timing, version info)
6. **Observability**: Record metrics (latency, throughput, errors), logs (for debugging), and traces (for performance analysis)

This flow repeats thousands or millions of times per second in production. Each operation's efficiency compounds across the entire system, making careful optimization essential. Bottlenecks at any phase can cascade to impact overall system performance.


## Code Explanation (Detailed)

### Implementation Approach
The code demonstrates core patterns and trade-offs.

### Key Operations
Each operation shows algorithm and performance characteristics.

### Concurrency and Atomicity
Locking strategies, race condition prevention.

### Edge Cases
Boundary conditions and error handling.

### Performance Optimization
Techniques for reducing latency and throughput.

## Architecture Diagram

```mermaid
graph LR
    subgraph Patterns["Cache Patterns"]
        subgraph CacheAside["Cache-Aside (Lazy Loading)"]
            CA_APP["App"] -->|1. GET| CA_C["Cache\nMISS"]
            CA_APP -->|2. SELECT| CA_DB["DB"]
            CA_APP -->|3. SET| CA_C
        end

        subgraph WriteThrough["Write-Through"]
            WT_APP["App"] -->|write| WT_C["Cache"]
            WT_C -->|sync write| WT_DB["DB"]
        end

        subgraph WriteBehind["Write-Behind (Write-Back)"]
            WB_APP["App"] -->|write| WB_C["Cache"]
            WB_C -->|async batch write| WB_DB["DB"]
        end
    end
```

## Flow Diagram

```mermaid
sequenceDiagram
    participant A as Application
    participant C as Cache (Redis)
    participant D as Database

    Note over A,D: Cache-Aside (most common)

    A->>C: GET user:1
    C-->>A: MISS (nil)
    A->>D: SELECT * FROM users WHERE id=1
    D-->>A: {id:1, name:Alice, email:...}
    A->>C: SET user:1 {data} EX 3600
    A->>C: GET user:1 (next request)
    C-->>A: HIT: {id:1, name:Alice, email:...}

    Note over A,D: Cache invalidation on write
    A->>D: UPDATE users SET name=Bob WHERE id=1
    A->>C: DEL user:1 (invalidate)
```

## Design

### Cache-Aside (Lazy Loading)

```
Algorithm:
  Read:
    1. Check cache
    2. If HIT: return cached value
    3. If MISS: fetch from DB, populate cache, return
  
  Write:
    1. Write to DB
    2. Invalidate (DEL) cache key
    Note: Set + invalidate order matters (see race conditions)

Pros:
  - Only cache what's actually read
  - Cache failures don't break reads (just slower)
  - Easy to implement

Cons:
  - Cold start: first request always hits DB
  - Race condition: two concurrent reads may both query DB
  - Stale data: if invalidation fails

Race condition (thundering herd):
  Multiple requests miss cache simultaneously
  All query DB -> N queries for same key
  Fix: lock/singleflight pattern (only 1 fetches, others wait)
```

### Write-Through

```
Algorithm:
  Write:
    1. Write to cache
    2. Synchronously write to DB
    3. Return success only when both succeed
  
  Read:
    Cache always up-to-date -> simple GET

Pros:
  - Cache always consistent with DB
  - Reads always hit cache (warm cache)

Cons:
  - Write latency = cache + DB (double write)
  - Writes cache data that may never be read (wasteful)
  - Complex: cache must understand DB write protocol

Use: Read-heavy workloads with high consistency requirement
```

### Write-Behind (Write-Back)

```
Algorithm:
  Write:
    1. Write to cache immediately (fast)
    2. Add to write-back queue
    3. Background: batch flush queue to DB
  
  Consistency:
    Cache is authoritative (not DB)
    DB may be behind by seconds-minutes

Pros:
  - Lowest write latency (just cache write)
  - Batch DB writes = higher throughput
  - DB load smoothing

Cons:
  - Data loss if cache fails before flushing to DB
  - Complex recovery (which writes reached DB?)
  - DB temporarily inconsistent

Use: High-write workloads where DB write is bottleneck
     (gaming leaderboards, counters, analytics)
```

### Cache Warming

```
Problem: Cold start after deployment or cache flush

Solutions:
  1. Proactive warming: pre-populate cache before traffic
     Read most popular keys from DB -> cache
     Useful: CDN cache warming, page cache warming

  2. Gradual rollout: canary traffic first to warm cache
     5% of traffic -> wait -> cache warm -> full rollout

  3. Cache seeding: import last snapshot of cache on startup
     Redis: RDB file loaded on startup
     
  4. Lazy warming: accept cold start, cache naturally fills
     Works when cold start impact is acceptable
```

## Back-of-Envelope Calculations

```
Cache hit ratio impact:
  DB query: 10ms, Cache read: 0.5ms
  1000 req/s, 90% hit rate:
    900 * 0.5ms = 450ms cache reads
    100 * 10ms = 1000ms DB reads
    Total: 1450ms total latency work
  
  Without cache: 1000 * 10ms = 10,000ms
  Speedup: 6.9x on latency work

Cache size planning:
  Top 20% of keys get 80% of traffic (Pareto)
  10M keys, cache 2M (20%) = 80% hit rate
  Each key 1KB: 2GB cache
  
  Adding more: diminishing returns

Thundering herd:
  10K req/s, TTL=60s, 1 key
  Every 60s: all 600K next-minute requests -> 1 miss
  With singleflight: 1 DB query per expiry
  Without: up to 10K concurrent DB queries at second of expiry

Write-behind batch efficiency:
  10K writes/s to cache, batch to DB every 100ms
  10K * 0.1 = 1000 writes per batch
  DB: 1000/0.1 = 10K writes/s (same rate but batched)
  With deduplication (same key): 1000 unique keys/batch = fewer DB writes
```

## Design Choices

| Pattern | Consistency | Read Perf | Write Perf | Failure Risk |
|---|---|---|---|---|
| Cache-Aside | Eventual | High (after warm) | Same as DB | Low (DB is truth) |
| Read-Through | Strong | Always cached | Same as DB | Low |
| Write-Through | Strong | Always cached | 2x latency | Low |
| Write-Behind | Eventual | Always cached | Low latency | Data loss risk |
| Refresh-Ahead | Eventual | Always cached | Background | Stale data risk |

## Python Implementation

```python
import time
import threading
from typing import Any, Callable, Dict, Optional
from dataclasses import dataclass, field
import random

@dataclass
class CacheEntry:
    value: Any
    expires_at: Optional[float] = None

    def is_expired(self) -> bool:
        return self.expires_at is not None and time.time() > self.expires_at

class SimpleCache:
    def __init__(self):
        self._store: Dict[str, CacheEntry] = {}
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Optional[Any]:
        entry = self._store.get(key)
        if entry is None or entry.is_expired():
            if entry:
                del self._store[key]
            self._misses += 1
            return None
        self._hits += 1
        return entry.value

    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        expires_at = time.time() + ttl if ttl else None
        self._store[key] = CacheEntry(value, expires_at)

    def delete(self, key: str):
        self._store.pop(key, None)

    def stats(self) -> dict:
        total = self._hits + self._misses
        return {
            "hits": self._hits, "misses": self._misses,
            "hit_rate": f"{self._hits/max(1,total)*100:.1f}%"
        }

class DatabaseSimulator:
    def __init__(self, latency_ms: float = 10.0):
        self.latency = latency_ms / 1000
        self._data = {f"user:{i}": {"id": i, "name": f"User{i}"} for i in range(1, 101)}
        self._query_count = 0

    def find(self, key: str) -> Optional[Any]:
        self._query_count += 1
        time.sleep(self.latency)  # Simulate DB latency
        return self._data.get(key)

    def update(self, key: str, value: Any):
        self._data[key] = value
        self._query_count += 1

    @property
    def queries(self) -> int:
        return self._query_count

class CacheAsideRepository:
    def __init__(self, cache: SimpleCache, db: DatabaseSimulator, ttl: int = 3600):
        self.cache = cache
        self.db = db
        self.ttl = ttl
        self._fetch_lock = threading.Lock()
        self._inflight: Dict[str, threading.Event] = {}

    def find(self, key: str) -> Optional[Any]:
        cached = self.cache.get(key)
        if cached is not None:
            return cached
        # Singleflight: prevent thundering herd
        with self._fetch_lock:
            # Check again (another thread may have fetched)
            cached = self.cache.get(key)
            if cached is not None:
                return cached
            if key in self._inflight:
                evt = self._inflight[key]
        if key not in self._inflight:
            with self._fetch_lock:
                evt = threading.Event()
                self._inflight[key] = evt

            # Fetch from DB (outside lock)
            value = self.db.find(key)
            if value is not None:
                self.cache.set(key, value, ttl=self.ttl)
            else:
                # Cache negative result
                self.cache.set(key, "NOT_FOUND", ttl=60)

            with self._fetch_lock:
                del self._inflight[key]
            evt.set()
            return value
        else:
            evt.wait(timeout=5.0)
            return self.cache.get(key)

    def update(self, key: str, value: Any):
        self.db.update(key, value)
        self.cache.delete(key)  # Invalidate cache

class WriteBehindCache:
    def __init__(self, cache: SimpleCache, db: DatabaseSimulator,
                 flush_interval_s: float = 0.1, max_batch: int = 100):
        self.cache = cache
        self.db = db
        self._dirty: Dict[str, Any] = {}
        self._lock = threading.Lock()
        self._running = True
        self._flush_interval = flush_interval_s
        self._flushed_count = 0
        # Background flush thread
        self._thread = threading.Thread(target=self._background_flush, daemon=True)
        self._thread.start()

    def write(self, key: str, value: Any):
        self.cache.set(key, value)
        with self._lock:
            self._dirty[key] = value  # Overwrite: only latest value matters

    def _background_flush(self):
        while self._running:
            time.sleep(self._flush_interval)
            with self._lock:
                if self._dirty:
                    batch = dict(self._dirty)
                    self._dirty.clear()
            if "batch" in dir() and batch:
                for k, v in batch.items():
                    self.db.update(k, v)
                self._flushed_count += len(batch)

    def stop(self):
        self._running = False
        self._thread.join()

# Demo: Cache-Aside
print("=== Cache-Aside Pattern ===")
cache = SimpleCache()
db = DatabaseSimulator(latency_ms=5)
repo = CacheAsideRepository(cache, db, ttl=3600)

# First access: DB hit
for i in range(1, 6):
    start = time.time()
    user = repo.find(f"user:{i}")
    elapsed = (time.time() - start) * 1000
    print(f"  user:{i}: {'MISS' if elapsed > 2 else 'HIT'} ({elapsed:.1f}ms): {user['name'] if user else None}")

# Second access: cache hit
print("\nSecond round (all cache hits):")
for i in range(1, 4):
    start = time.time()
    user = repo.find(f"user:{i}")
    elapsed = (time.time() - start) * 1000
    print(f"  user:{i}: HIT ({elapsed:.2f}ms)")

print(f"\nCache stats: {cache.stats()}, DB queries: {db.queries}")

# Update + invalidation
print("\n=== Cache Invalidation on Write ===")
repo.update("user:1", {"id": 1, "name": "Alice Updated"})
user = repo.find("user:1")  # Re-fetches from DB
print(f"After update: {user}")

print("\n=== Write-Behind Cache ===")
cache2 = SimpleCache()
db2 = DatabaseSimulator(latency_ms=0)
wb = WriteBehindCache(cache2, db2, flush_interval_s=0.05)

for i in range(10):
    wb.write(f"counter:{i}", i * 100)

print(f"Wrote 10 keys to cache (instant)")
time.sleep(0.2)  # Wait for flush
print(f"DB queries after async flush: {db2.queries}")
wb.stop()
```

## Java Implementation

```java
import java.util.*;
import java.util.concurrent.*;
import java.util.function.*;

public class CachePatterns {
    record CacheEntry(Object value, long expiresAt) {
        boolean isExpired() { return expiresAt > 0 && System.currentTimeMillis() > expiresAt; }
    }

    static class SimpleCache {
        Map<String, CacheEntry> store = new ConcurrentHashMap<>();
        int hits, misses;

        Optional<Object> get(String key) {
            CacheEntry e = store.get(key);
            if (e == null || e.isExpired()) { misses++; store.remove(key); return Optional.empty(); }
            hits++;
            return Optional.of(e.value());
        }

        void set(String key, Object val, int ttlMs) {
            store.put(key, new CacheEntry(val, ttlMs > 0 ? System.currentTimeMillis() + ttlMs : -1));
        }

        void del(String key) { store.remove(key); }
    }

    static class CacheAsideRepo {
        SimpleCache cache; Map<String, Object> db;
        CacheAsideRepo(SimpleCache c, Map<String, Object> db) { this.cache = c; this.db = db; }

        Optional<Object> find(String key) {
            return cache.get(key).or(() -> {
                Object v = db.get(key);
                if (v != null) cache.set(key, v, 3600_000);
                return Optional.ofNullable(v);
            });
        }

        void update(String key, Object value) { db.put(key, value); cache.del(key); }
    }

    public static void main(String[] args) {
        SimpleCache cache = new SimpleCache();
        Map<String, Object> db = Map.of("user:1", "Alice", "user:2", "Bob");
        CacheAsideRepo repo = new CacheAsideRepo(cache, new HashMap<>(db));

        System.out.println(repo.find("user:1")); // MISS -> loads
        System.out.println(repo.find("user:1")); // HIT
        System.out.printf("hits=%d, misses=%d%n", cache.hits, cache.misses);
        repo.update("user:1", "Alice Updated");
        System.out.println(repo.find("user:1")); // MISS -> reloads
    }
}
```

## Complexity

| Pattern | Read | Write | Consistency |
|---|---|---|---|
| Cache-Aside | O(1) hit, O(DB) miss | O(DB) + O(1) del | Eventual |
| Write-Through | O(1) | O(cache) + O(DB) | Strong |
| Write-Behind | O(1) | O(1) | Eventual |
| Read-Through | O(1) | O(DB) | Strong |

## Common Questions & Answers

**Q: What is caching and why do we need it?**

A: Caching stores frequently accessed data in fast storage (memory) to reduce latency and load on slower backends (database). Trade space (cache) for speed (latency). Critical for systems serving millions of requests per second.

**Q: What are the main cache eviction policies?**

A: LRU (least recently used), LFU (least frequently used), FIFO (first in first out), TTL (time-based), Random, and ARC (adaptive replacement). Choose based on access patterns: LRU for temporal, LFU for frequency, TTL for time-sensitive data.

**Q: What is cache hit rate and cache miss rate?**

A: Hit rate = successful_finds / total_accesses. Miss rate = 1 - hit rate. P(hit) = hits / (hits + misses). Target 80%+ hit rates for effective caching. Too-small cache gives low hit rate (wasted resources). Too-large cache uses more memory than needed.

**Q: How do you handle cache invalidation when backend data changes?**

A: Use TTL (time-based expiration), active invalidation (notify cache on write), cache-aside pattern (client checks backend), or write-through (update both). Active invalidation is fastest but complex. TTL is simplest but has stale data window.

**Q: What is the cache-aside pattern?**

A: Application checks cache first. On miss, fetch from backend, update cache, then return. Simple to implement. Risk: race condition where multiple threads fetch same miss simultaneously (thundering herd problem).

**Q: What is write-through caching?**

A: Writes go to both cache and backend simultaneously (synchronously). Ensures consistency: read always gets latest. Cost: write latency includes backend write. Safer than write-back but slower.

**Q: What is write-back (write-behind) caching?**

A: Writes go to cache only; backend updated asynchronously later (batch or periodic). Fast writes. Risk: data loss if cache fails before flushing. Need durability guarantees (persistence, replication).

**Q: How do you choose cache size?**

A: Estimate working set (frequently accessed data volume). Add 20-30% buffer for margin. Monitor hit rate: if < 80%, increase size. If > 95%, might be oversized (waste). Use tools like cachegrind to profile.

**Q: What's the difference between client-side and server-side caching?**

A: Client cache (browser): reduces network round-trips, entirely controlled by client. Server cache (memory, Redis): shared across clients, controlled by server. Multi-level caching often best.

**Q: How do you measure cache effectiveness?**

A: Hit rate (primary metric), latency reduction (P99 latency with vs. without cache), backend load reduction, and memory cost per cache entry. Calculate ROI: cost of cache vs. benefit (reduced latency, backend load).

## Follow-up Questions & Answers

**Q: How do you prevent the thundering herd problem in caches?**

A: When popular key expires, many threads fetch from backend simultaneously causing spike. Solutions: probabilistic early expiration (refresh before TTL), request coalescing (single thread rebuilds, others wait), or bloom filters (detect non-existent keys fast).

**Q: How would you implement multi-level cache hierarchy?**

A: Use L1 (fast, small, in-process), L2 (medium, local machine), L3 (large, remote, Redis). Check L1, miss→L2, miss→L3, miss→backend. On write: update all levels. Trade space for speed across levels.

**Q: Can you implement read-through caching (automatic population)?**

A: Yes, cache loader/resolver called on miss. Transparent to application. Backend automatically uses cache layer. More complex than cache-aside but cleaner separation.

**Q: How do you handle hot keys in distributed caches?**

A: Hot key = key accessed by many threads/clients. Replicate hot keys on multiple cache nodes. Use local in-process caches for very hot keys. Monitor and detect hot keys automatically.

**Q: What's the difference between warm and cold cache startup?**

A: Cold cache: empty at start, misses until populated (slow ramp-up). Warm cache: pre-loaded from previous state (RDB/snapshot). Warm startup is critical for production (instant performance).

**Q: How would you measure cache effectiveness for business metrics?**

A: Track hit rate, P99 latency (with/without cache), backend QPS reduction, revenue impact. Calculate cache size vs. cost savings. A/B test to prove business value.

**Q: What happens when cache size is insufficient for working set?**

A: Constant evictions = high miss rate = ineffective cache. Solution: increase cache size, improve eviction policy, reduce working set, or use better hardware (faster storage).

**Q: How do you debug cache issues in production?**

A: Monitor hit rate continuously. Profile cache keys (which keys are accessed). Check for cache stampedes (sudden miss spike). Use distributed tracing to see cache path.

**Q: How would you implement a persistent cache?**

A: Combine memory cache (fast) with persistent backend (database, RocksDB, LevelDB). Write-back pattern: batch updates to persistent store. Trade latency for durability.

**Q: Can you use caching for write-heavy workloads?**

A: Write caching is risky (consistency issues). Use carefully: write-through for safety, write-back for speed. Good for batch writes (aggregate before writing). Monitor durability guarantees.


## System Overview

**Scale Metrics:**
- Throughput: Millions of operations per second
- Latency: Sub-millisecond to sub-second response times
- Data volume: Gigabytes to Petabytes
- Concurrent users: Millions to billions
- Availability: 99.99% to 99.999% uptime SLA

**Key Components:**
- Request handling and routing
- Data processing and storage
- Replication and consistency
- Failure detection and recovery
- Monitoring and alerting

## Architecture Diagrams

### System Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        C1["Client"]
        LB["Load Balancer"]
    end

    subgraph "Service Layer"
        S1["Service 1"]
        S2["Service 2"]
        S3["Service N"]
    end

    subgraph "Cache"
        CACHE["Redis/Memcached"]
    end

    subgraph "Storage"
        DB["Primary DB"]
        REP["Replicas"]
    end

    C1 --> LB
    LB --> S1
    LB --> S2
    LB --> S3
    S1 --> CACHE
    S2 --> CACHE
    S3 --> CACHE
    CACHE --> DB
    DB --> REP

    style C1 fill:#e1f5ff
    style S1 fill:#f3e5f5
    style CACHE fill:#fff3e0
    style DB fill:#e8f5e9
```

### Data Flow

```mermaid
graph LR
    A["Request"] --> B["Parse"]
    B --> C["Validate"]
    C --> D["Process"]
    D --> E["Cache"]
    E --> F["Store"]
    F --> G["Response"]

    style A fill:#c8e6c9
    style B fill:#ffccbc
    style C fill:#bbdefb
    style D fill:#f8bbd0
    style E fill:#ffe0b2
    style F fill:#d1c4e9
    style G fill:#c8e6c9
```

### Failover Mechanism

```mermaid
graph TB
    A["Primary Node"] -->|heartbeat| B["Health Checker"]
    C["Replica 1"] -->|heartbeat| B
    D["Replica 2"] -->|heartbeat| B
    B -->|failure detected| E["Coordinator"]
    E -->|elect new primary| F["New Primary"]
    F -->|start accepting| G["Clients"]

    style A fill:#ffcdd2
    style F fill:#c8e6c9
    style G fill:#fff9c4
```

### Consistency Models

```mermaid
graph TB
    subgraph "Strong Consistency"
        A1["Quorum Write"] --> A2["Read Latest"]
    end

    subgraph "Eventual Consistency"
        B1["Write Async"] --> B2["Replicate"]
        B2 --> B3["Read May Stale"]
    end

    subgraph "Causal Consistency"
        C1["Track Causality"] --> C2["Enforce Order"]
    end

    style A1 fill:#c8e6c9
    style B1 fill:#ffccbc
    style C1 fill:#bbdefb
```

### Scaling Strategy

```mermaid
graph TB
    subgraph "Vertical Scaling"
        V1["Bigger CPU"] --> V2["More RAM"]
        V2 --> V3["Faster Disk"]
    end

    subgraph "Horizontal Scaling"
        H1["Add Replicas"] --> H2["Shard Data"]
        H2 --> H3["Distributed Cache"]
    end

    subgraph "Result"
        R["Increased Capacity"]
    end

    V3 --> R
    H3 --> R

    style V1 fill:#bbdefb
    style H1 fill:#f8bbd0
    style R fill:#c8e6c9
```

## Implementation Examples

### Python Implementation

```python
# Python Implementation

from typing import Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)

@dataclass
class Config:
    """Configuration for the system."""
    timeout_ms: int = 5000
    retry_count: int = 3
    batch_size: int = 100
    max_connections: int = 1000

class Handler:
    """Main handler class for operations."""

    def __init__(self, config: Config):
        self.config = config
        self.metrics = {"success": 0, "failure": 0, "latency_ms": []}

    async def process(self, data: Any) -> Any:
        """Process request with error handling."""
        try:
            # Validate input
            self._validate(data)

            # Execute operation
            result = await self._execute(data)

            # Track metrics
            self.metrics["success"] += 1
            return result

        except Exception as e:
            logger.error(f"Processing failed: {e}")
            self.metrics["failure"] += 1
            raise

    def _validate(self, data: Any) -> None:
        """Validate input data."""
        if data is None:
            raise ValueError("Data cannot be None")

    async def _execute(self, data: Any) -> Any:
        """Execute core logic."""
        # Implement actual logic here
        return {"status": "success", "timestamp": datetime.now().isoformat()}

    def get_metrics(self) -> dict:
        """Return collected metrics."""
        return self.metrics

# Usage example
async def main():
    config = Config(timeout_ms=5000, batch_size=100)
    handler = Handler(config)
    result = await handler.process({"key": "value"})
    print(f"Result: {result}")
    print(f"Metrics: {handler.get_metrics()}")
```

### Java Implementation

```java
// Java Implementation

import java.util.*;
import java.util.concurrent.*;
import java.time.Instant;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SystemHandler {
    private static final Logger logger = LoggerFactory.getLogger(SystemHandler.class);

    private final Config config;
    private final Map<String, Long> metrics = new ConcurrentHashMap<>();
    private final ExecutorService executor;

    public static class Config {
        public int timeoutMs = 5000;
        public int retryCount = 3;
        public int batchSize = 100;
        public int maxConnections = 1000;

        public Config withTimeoutMs(int timeout) {
            this.timeoutMs = timeout;
            return this;
        }
    }

    public SystemHandler(Config config) {
        this.config = config;
        this.executor = Executors.newFixedThreadPool(
            Math.min(config.maxConnections, 10)
        );
        metrics.put("success", 0L);
        metrics.put("failure", 0L);
    }

    public <T> T process(Object data) throws Exception {
        try {
            // Validate input
            validate(data);

            // Execute operation
            Object result = execute(data);

            // Track metrics
            metrics.put("success", metrics.get("success") + 1);
            return (T) result;

        } catch (Exception e) {
            logger.error("Processing failed: {}", e.getMessage());
            metrics.put("failure", metrics.get("failure") + 1);
            throw e;
        }
    }

    private void validate(Object data) throws IllegalArgumentException {
        if (data == null) {
            throw new IllegalArgumentException("Data cannot be null");
        }
    }

    private Object execute(Object data) throws Exception {
        // Implement core logic
        return Map.of(
            "status", "success",
            "timestamp", Instant.now().toString()
        );
    }

    public Map<String, Long> getMetrics() {
        return new HashMap<>(metrics);
    }

    public void shutdown() {
        executor.shutdown();
    }

    public static void main(String[] args) throws Exception {
        Config config = new Config()
            .withTimeoutMs(5000);

        SystemHandler handler = new SystemHandler(config);
        Object result = handler.process(Map.of("key", "value"));
        System.out.println("Result: " + result);
        System.out.println("Metrics: " + handler.getMetrics());
        handler.shutdown();
    }
}
```

## Back-of-Envelope Calculations

### Traffic & Throughput
**Assumptions:**
- Daily active users: 100 million (100M)
- Requests per user per day: 50
- Peak hour traffic: 10% of daily (concentrated)
- Request distribution: 70% read, 30% write

**Calculations:**
```
Total daily requests = 100M users × 50 requests = 5 billion requests/day
Average RPS = 5B requests / 86400 seconds ≈ 57,870 RPS
Peak hour RPS = (5B / 86400) × (100 / 10) ≈ 578,700 RPS
Peak minute RPS = 578,700 / 60 ≈ 9,645 RPS

Read operations = 57,870 × 0.7 ≈ 40,509 RPS (average)
Write operations = 57,870 × 0.3 ≈ 17,361 RPS (average)
```

### Storage Requirements
**Assumptions:**
- Data per user: 1 KB (profile, settings)
- Data per transaction: 500 bytes
- Data retention: 3 years

**Calculations:**
```
User profile storage = 100M × 1 KB = 100 GB
Transaction data = 5B requests/day × 500 bytes × 365 × 3 = 2.74 PB
Total storage ≈ 2.75 PB
Replication factor: 3× → 8.25 PB raw storage

Backup storage (weekly snapshots): 8.25 PB × 52 weeks = 429 PB
```

### Network Bandwidth
**Assumptions:**
- Average request size: 2 KB
- Average response size: 5 KB
- Replication overhead: 2× (write to replicas)

**Calculations:**
```
Inbound bandwidth = 57,870 RPS × 2 KB = 115.74 MB/s
Outbound bandwidth = 57,870 RPS × 5 KB = 289.35 MB/s
Replication bandwidth = 17,361 RPS × 2 KB × 2 = 69.44 MB/s
Total peak bandwidth ≈ 474 MB/s ≈ 3.8 Tbps (peak hour)
```

### Compute Requirements
**Assumptions:**
- Processing time per request: 10 ms
- CPU efficiency: 1 core handles 50 RPS

**Calculations:**
```
CPUs needed for average traffic = 57,870 RPS / 50 = 1,158 cores
CPUs needed for peak traffic = 578,700 RPS / 50 = 11,574 cores
Overprovisioning factor: 1.5× → 17,361 cores total

Using 16 cores per server = 17,361 / 16 ≈ 1,085 servers
With 3:1 replication = 3,255 servers needed
Regional redundancy (3 regions) = 9,765 servers
```

### Latency Analysis (p99)
**Components:**
- Network latency: 5 ms
- Processing: 10 ms
- Storage access: 50 ms (disk), 1 ms (cache)
- Replication write: 20 ms

**Path Analysis:**
```
Cache hit path: 5 + 1 + 5 = 11 ms
Database read path: 5 + 10 + 50 + 5 = 70 ms
Write path: 5 + 10 + 20 + 5 = 40 ms
```

### Cost Estimation
**Monthly costs (approximate):**
```
Compute: 9,765 servers × $1,000/month = $9.765M
Storage: 8.25 PB × $10/GB/month = $82.5M
Bandwidth: 3.8 Tbps × $0.12/GB = $456M
Personnel: 100 engineers × $200K = $20M
Total: ~$568M/month
Cost per user: $5.68/month
```


## Interview Questions & Answers

### Q1: Design the System from Scratch

**Question:** Design a system that can handle 1 billion requests per day with sub-100ms latency.

**Answer Structure:**
1. **Clarify requirements**: DAU, request types, geographic distribution, consistency needs
2. **Back-of-envelope**: Calculate RPS (11.5K avg, 115K peak), storage, bandwidth
3. **High-level design**: Load balancing → services → cache → storage
4. **Deep dive**:
   - Horizontal scaling with sharding
   - Multi-region active-active with eventual consistency
   - Caching strategy (write-through for critical data)
   - Monitoring: metrics, logging, tracing
5. **Bottlenecks**: Identify and address each
6. **Trade-offs**: Consistency vs. availability, latency vs. cost

### Q2: Scaling Challenges

**Question:** You're growing from 10M to 1B users (100x). What breaks and how do you fix it?

**Answer:**
- **Database bottleneck**: Sharding by user ID, consistent hashing, shard rebalancing
- **Cache hit rate drops**: Larger working set, tiered caching (L1: local, L2: distributed)
- **Replication lag**: Write-through for consistency-critical data, eventual consistency elsewhere
- **Operational complexity**: Infrastructure-as-code, auto-scaling, chaos engineering
- **Cost**: Optimize resource utilization, use reserved instances, spot instances for batch

### Q3: Failure Scenarios

**Question:** Your primary database goes down. What happens? How do you recover?

**Answer:**
- **Detection**: Health check timeout (3-5 seconds)
- **Failover**: Automatic promotion of replica using Raft consensus
- **Impact**: Write requests fail for ~10 seconds, reads use replicas
- **Recovery**: Background sync of failed node, re-add to cluster
- **Lessons**: Circuit breakers prevent cascade, bulkhead limits blast radius

### Q4: Consistency Requirements

**Question:** Do you need strong or eventual consistency? Why?

**Answer:**
- **Strong consistency**: Critical for financial transactions, inventory, user auth
  - Implementation: Quorum writes, read-after-write
  - Cost: Higher latency (p99 100ms+), lower throughput

- **Eventual consistency**: Fine for user feeds, recommendations, analytics
  - Implementation: Async replication, read-repair
  - Benefit: Lower latency (p99 <10ms), higher throughput

- **Hybrid approach**: Consistency per operation type, not global

### Q5: Performance Optimization

**Question:** How would you reduce p99 latency from 100ms to 20ms?

**Answer:**
1. **Profile** (measure first): Identify bottleneck (storage, network, compute)
2. **Caching**: Multi-tier (L1 local, L2 distributed), bloom filters for misses
3. **Batching**: Group operations, reduce RPC overhead
4. **Connection pooling**: Reuse TCP connections, reduce handshake latency
5. **Async I/O**: Non-blocking operations, increase parallelism
6. **Database optimization**: Indexing, query optimization, read replicas
7. **Code optimization**: Reduce allocations, use faster algorithms
8. **Hardware**: SSD for storage, faster network interconnects

### Q6: Operational Concerns

**Question:** How do you deploy a new version with zero downtime?

**Answer:**
1. **Canary deployment**: Roll out to 1% of servers, monitor metrics
2. **Gradual rollout**: 1% → 10% → 50% → 100% as confidence increases
3. **Health checks**: Automated rollback if error rate exceeds threshold
4. **Database migration**: Schema changes with backward compatibility
5. **Feature flags**: Toggle features independently of deployment
6. **Monitoring**: Enhanced alerting during rollout, easy incident response


## Technology Stack Recommendations

| Layer | Technology | Why |
|-------|-----------|-----|
| Load Balancing | Nginx, HAProxy, AWS ALB | Distribute traffic, health checks |
| Service Framework | FastAPI (Python), Spring Boot (Java) | Async, built-in monitoring |
| Caching | Redis, Memcached | Sub-millisecond latency, distributed |
| Primary Storage | PostgreSQL, MySQL | ACID, complex queries, reliability |
| Analytics | Elasticsearch, Data Warehouse | Full-text search, time-series analysis |
| Streaming | Kafka, AWS Kinesis | Event processing, real-time |
| Observability | Prometheus, ELK Stack, Jaeger | Metrics, logs, traces |

## Lessons Learned

1. **Premature optimization kills projects**: Start simple, measure, then optimize
2. **Consistency is hard**: Eventually consistent systems are tricky to reason about
3. **Monitoring is non-negotiable**: You can't fix what you can't see
4. **Failure is not rare**: Plan for it, test it, automate recovery
5. **Cost grows with complexity**: Each component adds operational overhead

## Related Topics

- Database design and optimization
- Distributed consensus algorithms
- Load balancing strategies
- Caching mechanisms and patterns
- Monitoring and alerting systems
- Security and compliance

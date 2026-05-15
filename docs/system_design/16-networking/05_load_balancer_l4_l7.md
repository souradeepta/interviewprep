# Load Balancer: Layer 4 vs Layer 7

## Problem Statement

Design a load balancer that distributes incoming traffic across multiple backend servers to maximize availability and throughput.

**Requirements:**
- Distribute requests evenly across healthy backends
- Detect and route around unhealthy backends
- Support sticky sessions, SSL termination, content routing
- Handle 1M+ connections/sec

## Scenario

Load Balancer: Layer 4 vs Layer 7 is a critical component in modern distributed systems. In real-world applications, distributing traffic evenly across multiple backend servers. For example, major tech companies like Netflix, Uber, and Airbnb rely on similar solutions to handle millions of concurrent users and requests. The challenge is achieving this while maintaining sub-100ms latency, 99.99% availability, and gracefully handling 10x traffic spikes during peak demand. This component provides the foundational capability to solve these challenges reliably and efficiently at global scale.

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
graph TB
    Client[Clients]
    L4[L4 Load Balancer TCP level]
    L7[L7 Load Balancer HTTP level]
    S1[Server 1]
    S2[Server 2]
    S3[Server 3]

    Client -->|TCP SYN| L4
    L4 -->|Forward TCP stream| L7
    L7 -->|Route by URL/Header| S1
    L7 -->|Route by Cookie| S2
    L7 -->|Route by Path| S3
```

## Flow Diagram

```mermaid
sequenceDiagram
    participant C as Client
    participant LB as L7 LB nginx
    participant B1 as Backend 1
    participant B2 as Backend 2

    C->>LB: POST /api/orders (HTTP)
    LB->>LB: Parse URL, headers, cookie
    LB->>LB: Select backend (round-robin)
    LB->>B1: Forward request + X-Forwarded-For
    B1-->>LB: 201 Created
    LB-->>C: 201 Created

    Note over LB: Health check every 5s
    LB->>B2: GET /health
    B2-->>LB: 200 OK
```

## Design

### L4 vs L7 Comparison

| Feature | L4 (Transport) | L7 (Application) |
|---|---|---|
| Protocol | TCP/UDP | HTTP/HTTPS/gRPC |
| Visibility | IP + port only | URL, headers, cookies |
| SSL | Pass-through | Terminate + re-encrypt |
| Routing granularity | IP/port hash | Content-based |
| Performance | Higher (less parsing) | Slightly lower |
| Sticky sessions | IP-hash | Cookie-based |
| Use case | Raw TCP, databases | Web APIs |

### Balancing Algorithms

```
Round Robin       - Even distribution, O(1), simple
Weighted RR       - Server capacity-aware
Least Connections - Route to backend with fewest active connections
IP Hash           - Same client IP always hits same backend (sticky)
Random            - Surprisingly effective at scale (power of two choices)
Least Response    - Route to fastest responding backend
Consistent Hash   - Minimize remapping when backends change
```

### Health Checks

```
Active:  LB sends probe to /health every N seconds
Passive: Monitor real traffic errors, mark down on N failures
Thresholds:
  Mark down: 2-3 consecutive failures
  Mark up:   3 consecutive successes
Protocols: TCP connect, HTTP 200, gRPC health check
```

## Back-of-Envelope Calculations

```
Load balancer capacity:
  Nginx: ~50K concurrent connections per core
  HAProxy: ~100K connections/sec per core
  AWS NLB: millions of connections/sec (managed)

Health check overhead:
  100 backends x 1 check/5s = 20 checks/sec (negligible)

Latency added by L7 LB:
  HTTP header parsing: ~0.1ms
  Backend selection: ~0.01ms
  Total LB overhead: ~0.5ms

Bandwidth for L7 LB (both directions flow through):
  1M req/sec x 10KB avg = 10 GB/s through single LB
  DSR eliminates outbound, reducing to ~1 GB/s
```

## Design Choices

| Approach | Pros | Cons |
|---|---|---|
| L4 (NLB) | Ultra-high throughput | No content routing |
| L7 (ALB) | Smart routing, WAF | More CPU overhead |
| DSR | Saves LB bandwidth | Complex network config |
| Active health checks | Proactive failover | False positives possible |
| Consistent hashing | Minimize cache misses | Rebalancing on change |

## Python Implementation

```python
from typing import List, Optional
import itertools
import time

class Backend:
    def __init__(self, host: str, port: int, weight: int = 1):
        self.host = host
        self.port = port
        self.weight = weight
        self.healthy = True
        self.active_conns = 0
        self.failures = 0

    def address(self) -> str:
        return f"{self.host}:{self.port}"

class LoadBalancer:
    def __init__(self, algorithm: str = "round_robin"):
        self._backends: List[Backend] = []
        self._algorithm = algorithm
        self._rr_idx = 0

    def add_backend(self, backend: Backend):
        self._backends.append(backend)

    def healthy(self) -> List[Backend]:
        return [b for b in self._backends if b.healthy]

    def select(self) -> Optional[Backend]:
        alive = self.healthy()
        if not alive:
            return None
        if self._algorithm == "round_robin":
            b = alive[self._rr_idx % len(alive)]
            self._rr_idx += 1
            return b
        if self._algorithm == "least_connections":
            return min(alive, key=lambda b: b.active_conns)
        return alive[0]

    def handle(self, path: str) -> str:
        b = self.select()
        if not b:
            return "503 Service Unavailable"
        b.active_conns += 1
        try:
            return f"200 OK from {b.address()}"
        finally:
            b.active_conns -= 1

    def mark_down(self, addr: str):
        for b in self._backends:
            if b.address() == addr:
                b.healthy = False
                print(f"[LB] {addr} marked DOWN")

# Usage
lb = LoadBalancer("least_connections")
for i in range(1, 4):
    lb.add_backend(Backend(f"10.0.0.{i}", 8080))

for _ in range(6):
    print(lb.handle("/api/data"))

lb.mark_down("10.0.0.1:8080")
print(lb.handle("/api/data"))  # routes only to 10.0.0.2 or 10.0.0.3
```

## Java Implementation

```java
import java.util.*;
import java.util.concurrent.atomic.*;

public class LoadBalancer {
    static class Backend {
        String host; int port; AtomicInteger conns = new AtomicInteger(); volatile boolean healthy = true;
        Backend(String h, int p) { host = h; port = p; }
        String addr() { return host + ":" + port; }
    }

    private List<Backend> backends = new ArrayList<>();
    private AtomicInteger idx = new AtomicInteger();

    public void add(Backend b) { backends.add(b); }

    public Optional<Backend> selectRoundRobin() {
        List<Backend> up = backends.stream().filter(b -> b.healthy).toList();
        if (up.isEmpty()) return Optional.empty();
        return Optional.of(up.get(idx.getAndIncrement() % up.size()));
    }

    public Optional<Backend> selectLeastConn() {
        return backends.stream().filter(b -> b.healthy)
            .min(Comparator.comparingInt(b -> b.conns.get()));
    }

    public String handle(String path) {
        return selectLeastConn().map(b -> {
            b.conns.incrementAndGet();
            String r = "200 OK from " + b.addr();
            b.conns.decrementAndGet();
            return r;
        }).orElse("503 Service Unavailable");
    }
}
```

## Complexity

| Operation | Time |
|---|---|
| Round robin select | O(1) |
| Least connections | O(n) |
| Health check | O(backends) |
| Request routing | O(1) after selection |

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


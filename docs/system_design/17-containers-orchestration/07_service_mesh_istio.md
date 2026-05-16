# Service Mesh and Istio

## Problem Statement

Design a service mesh that provides observability, traffic management, and security for microservices without modifying application code — using sidecar proxies (Envoy) injected alongside every pod.

## Scenario

Service Mesh and Istio is a critical component in modern distributed systems. In real-world applications, handling complex business logic at scale with high reliability. For example, major tech companies like Netflix, Uber, and Airbnb rely on similar solutions to handle millions of concurrent users and requests. The challenge is achieving this while maintaining sub-100ms latency, 99.99% availability, and gracefully handling 10x traffic spikes during peak demand. This component provides the foundational capability to solve these challenges reliably and efficiently at global scale.

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
    subgraph ControlPlane["Istio Control Plane"]
        ISO[Istiod\nPilot + Citadel + Galley]
    end

    subgraph PodA["Pod: frontend"]
        APP1[App Container]
        ENV1[Envoy Sidecar\nport 15001]
    end

    subgraph PodB["Pod: backend"]
        APP2[App Container]
        ENV2[Envoy Sidecar\nport 15001]
    end

    subgraph PodC["Pod: payments"]
        APP3[App Container]
        ENV3[Envoy Sidecar\nport 15001]
    end

    ISO -->|xDS: routes, certs, policies| ENV1
    ISO -->|xDS: routes, certs, policies| ENV2
    ISO -->|xDS: routes, certs, policies| ENV3

    ENV1 -->|mTLS + telemetry| ENV2
    ENV2 -->|mTLS + telemetry| ENV3
    ENV1 -.->|metrics, traces| ISO
```

## Flow Diagram

```mermaid
sequenceDiagram
    participant A as App (frontend)
    participant EA as Envoy (frontend)
    participant EB as Envoy (backend)
    participant B as App (backend)
    participant ISO as Istiod

    Note over EA,EB: Envoy intercepts all traffic via iptables REDIRECT

    A->>EA: HTTP GET /api/data (plain)
    EA->>ISO: Lookup route for backend.svc
    ISO-->>EA: VirtualService: 80% v1, 20% v2
    EA->>EA: Pick target: backend-v1 (80% path)
    EA->>EB: mTLS (TLS 1.3) + HTTP/2
    EB->>B: HTTP (stripped TLS, plain to app)
    B-->>EB: HTTP 200
    EB-->>EA: mTLS response
    EA-->>A: HTTP 200
    EA->>ISO: Telemetry: latency, status code, trace
```

## Design

### Data Plane (Envoy Sidecar)

```
Envoy intercepts traffic via iptables REDIRECT (init container):
  iptables -t nat -A OUTPUT -p tcp -j REDIRECT --to-port 15001

What Envoy handles:
  - mTLS: mutual authentication between all services
  - Load balancing: consistent hashing, least request, round robin
  - Circuit breaking: fail fast on unhealthy upstream
  - Retries: automatic retry with exponential backoff
  - Timeouts: per-route timeout enforcement
  - Observability: traces (Jaeger), metrics (Prometheus), logs
  - Traffic shifting: canary deployments via weights

xDS API (from Istiod):
  LDS: Listener Discovery Service (ports to listen on)
  RDS: Route Discovery Service (routing rules)
  CDS: Cluster Discovery Service (upstream service endpoints)
  EDS: Endpoint Discovery Service (pod IPs per cluster)
```

### Control Plane (Istiod)

```
Pilot: Service discovery + traffic management
  - Translates Istio config (VirtualService, DestinationRule) to Envoy xDS
  - Monitors Kubernetes Services/Endpoints for live pod IPs

Citadel (now in Istiod): Certificate authority
  - Issues SPIFFE X.509 certificates to each workload
  - Identity: spiffe://cluster.local/ns/prod/sa/frontend
  - Rotates certs every 24h (configurable)

Galley: Config validation
  - Validates Istio CRDs before applying
  - Prevents misconfigured VirtualServices
```

### Traffic Management CRDs

```yaml
VirtualService:
  http:
    - route:
      - destination: {host: backend, subset: v1}
        weight: 80
      - destination: {host: backend, subset: v2}
        weight: 20
      timeout: 5s
      retries: {attempts: 3, retryOn: "5xx"}

DestinationRule:
  subsets:
    - name: v1; labels: {version: v1}
    - name: v2; labels: {version: v2}
  trafficPolicy:
    connectionPool:
      tcp: {maxConnections: 100}
      http: {http2MaxRequests: 1000}
    outlierDetection:  # Circuit breaker
      consecutiveGatewayErrors: 5
      interval: 30s
      baseEjectionTime: 30s
```

## Back-of-Envelope Calculations

```
Sidecar overhead:
  Envoy RAM: 50MB per pod
  1000-pod cluster: 50GB just for proxies
  Envoy CPU: ~0.01 cores at 1000 req/s
  1000 pods x 0.01 = 10 cores overhead cluster-wide

Latency per hop:
  Envoy proxy (userspace): 1-5ms per call
  10 microservices in chain: +10-50ms total
  vs direct pod-to-pod: 0.1ms

Certificate rotation:
  Default: rotate every 24h
  1000 pods: ~1 cert rotation/80s (spread evenly)
  istiod handles ~50 cert ops/sec without issue

Traffic shifting update time:
  VirtualService change -> xDS push to all Envoys
  At 1000 pods: ~1-2s for full config propagation
  Old weights may apply for up to 2s during transition

Control plane memory:
  Istiod: ~1GB RAM for 1000 services/endpoints
  xDS cache size grows with cluster size
```

## Design Choices

| Feature | Istio | Linkerd | Cilium (eBPF) |
|---|---|---|---|
| Proxy | Envoy (C++) | Linkerd2-proxy (Rust) | None (kernel) |
| Latency overhead | 2-10ms | 1-3ms | <0.1ms |
| RAM per pod | 50-150MB | 10-20MB | 0 (no sidecar) |
| mTLS | Yes | Yes | Yes |
| Traffic management | Rich (weights, retries) | Basic | Basic |
| Observability | Excellent | Good | Good |

## Python Implementation

```python
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import random
import time

@dataclass
class Endpoint:
    ip: str
    port: int
    version: str
    healthy: bool = True
    consecutive_errors: int = 0
    ejected_until: float = 0.0

    def is_available(self) -> bool:
        return self.healthy and time.time() >= self.ejected_until

@dataclass
class TrafficWeight:
    subset: str
    weight: int  # 0-100

class CircuitBreaker:
    def __init__(self, threshold: int = 5, ejection_s: float = 30.0):
        self.threshold = threshold
        self.ejection_s = ejection_s

    def record_error(self, ep: Endpoint):
        ep.consecutive_errors += 1
        if ep.consecutive_errors >= self.threshold:
            ep.ejected_until = time.time() + self.ejection_s
            ep.consecutive_errors = 0
            print(f"  [CB] Ejected {ep.ip} for {self.ejection_s}s")

    def record_success(self, ep: Endpoint):
        ep.consecutive_errors = 0

class EnvoyProxy:
    def __init__(self, service_name: str):
        self.service_name = service_name
        self._clusters: Dict[str, List[Endpoint]] = {}
        self._weights: List[TrafficWeight] = []
        self._cb = CircuitBreaker(threshold=3, ejection_s=5.0)
        self._request_count = 0
        self._error_count = 0

    def update_endpoints(self, subset: str, endpoints: List[Endpoint]):
        self._clusters[subset] = endpoints
        print(f"[xDS/EDS] Updated {self.service_name}/{subset}: {len(endpoints)} endpoints")

    def update_routes(self, weights: List[TrafficWeight]):
        self._weights = weights
        total = sum(w.weight for w in weights)
        assert total == 100, "Weights must sum to 100"
        print(f"[xDS/RDS] Route {self.service_name}: {[(w.subset, w.weight) for w in weights]}")

    def _select_subset(self) -> str:
        r = random.randint(1, 100)
        cumulative = 0
        for w in self._weights:
            cumulative += w.weight
            if r <= cumulative:
                return w.subset
        return self._weights[-1].subset

    def call(self, path: str = "/", retries: int = 2) -> Tuple[int, str]:
        self._request_count += 1
        subset = self._select_subset()
        endpoints = [ep for ep in self._clusters.get(subset, []) if ep.is_available()]
        if not endpoints:
            return 503, f"No available endpoints for {self.service_name}/{subset}"

        ep = random.choice(endpoints)
        # Simulate call with retry
        for attempt in range(retries + 1):
            status, body = self._simulate_call(ep, path)
            if status < 500:
                self._cb.record_success(ep)
                return status, body
            self._cb.record_error(ep)
            if attempt < retries:
                print(f"  [Retry] {ep.ip} returned {status}, retrying ({attempt+1}/{retries})")
                endpoints = [e for e in endpoints if e.is_available() and e != ep]
                if not endpoints:
                    break
                ep = random.choice(endpoints)

        self._error_count += 1
        return 503, "All retries exhausted"

    def _simulate_call(self, ep: Endpoint, path: str) -> Tuple[int, str]:
        # Simulate error based on endpoint state
        if not ep.healthy or random.random() < 0.3 * ep.consecutive_errors:
            return 500, "Internal server error"
        return 200, f"OK from {ep.ip}:{ep.port} (v{ep.version})"

    def stats(self) -> dict:
        return {
            "total_requests": self._request_count,
            "errors": self._error_count,
            "error_rate": f"{self._error_count/max(1,self._request_count)*100:.1f}%",
        }

# Simulate Istiod pushing config to proxy
proxy = EnvoyProxy("backend")

# xDS: EDS update - register endpoints
proxy.update_endpoints("v1", [
    Endpoint("10.244.1.2", 8080, "v1"),
    Endpoint("10.244.1.3", 8080, "v1"),
])
proxy.update_endpoints("v2", [
    Endpoint("10.244.2.2", 8080, "v2"),
])

# xDS: RDS update - 80/20 canary split
proxy.update_routes([TrafficWeight("v1", 80), TrafficWeight("v2", 20)])

# Simulate traffic
print("\n--- Serving traffic ---")
v1_count = v2_count = 0
for _ in range(10):
    status, body = proxy.call("/api/data")
    if "v1" in body:
        v1_count += 1
    elif "v2" in body:
        v2_count += 1

print(f"\nTraffic split: v1={v1_count}, v2={v2_count}")
print(proxy.stats())
```

## Java Implementation

```java
import java.util.*;
import java.util.concurrent.atomic.*;

public class ServiceMesh {
    record Endpoint(String ip, int port, String version) {}
    record WeightedRoute(String subset, int weight) {}

    static class EnvoyProxy {
        private Map<String, List<Endpoint>> clusters = new HashMap<>();
        private List<WeightedRoute> routes = new ArrayList<>();
        private Random rng = new Random();
        private AtomicLong requests = new AtomicLong();
        private AtomicLong errors = new AtomicLong();

        void updateEndpoints(String subset, List<Endpoint> eps) {
            clusters.put(subset, eps);
            System.out.printf("[xDS/EDS] %s: %d endpoints%n", subset, eps.size());
        }

        void updateRoutes(List<WeightedRoute> r) { routes = r; }

        String call() {
            requests.incrementAndGet();
            int r = rng.nextInt(100);
            int cumulative = 0;
            String subset = routes.get(routes.size()-1).subset();
            for (WeightedRoute w : routes) {
                cumulative += w.weight();
                if (r < cumulative) { subset = w.subset(); break; }
            }
            List<Endpoint> eps = clusters.getOrDefault(subset, List.of());
            if (eps.isEmpty()) { errors.incrementAndGet(); return "503 No endpoints"; }
            Endpoint ep = eps.get(rng.nextInt(eps.size()));
            return String.format("200 from %s v%s", ep.ip(), ep.version());
        }

        void stats() {
            System.out.printf("Requests=%d, Errors=%d%n", requests.get(), errors.get());
        }
    }

    public static void main(String[] args) {
        EnvoyProxy proxy = new EnvoyProxy();
        proxy.updateEndpoints("v1", List.of(new Endpoint("10.0.0.1", 8080, "1"), new Endpoint("10.0.0.2", 8080, "1")));
        proxy.updateEndpoints("v2", List.of(new Endpoint("10.0.0.3", 8080, "2")));
        proxy.updateRoutes(List.of(new WeightedRoute("v1", 80), new WeightedRoute("v2", 20)));
        long v1 = 0, v2 = 0;
        for (int i = 0; i < 20; i++) {
            String r = proxy.call();
            if (r.contains("v1")) v1++; else v2++;
        }
        System.out.printf("v1=%d, v2=%d%n", v1, v2);
        proxy.stats();
    }
}
```

## Complexity

| Operation | Time |
|---|---|
| Envoy route lookup | O(routes) |
| Circuit breaker check | O(1) |
| xDS config push | O(proxies) |
| mTLS handshake | O(1) + cert validation |
| Load balancing (least request) | O(endpoints) |

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

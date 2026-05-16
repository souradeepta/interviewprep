# Kubernetes Deployments and Rolling Updates

## Problem Statement

Design and understand Kubernetes Deployments — the mechanism for declaratively managing pod lifecycle including rolling updates, rollbacks, and self-healing.

## Scenario

Kubernetes Deployments and Rolling Updates is a critical component in modern distributed systems. In real-world applications, orchestrating containers across clusters automatically. For example, major tech companies like Netflix, Uber, and Airbnb rely on similar solutions to handle millions of concurrent users and requests. The challenge is achieving this while maintaining sub-100ms latency, 99.99% availability, and gracefully handling 10x traffic spikes during peak demand. This component provides the foundational capability to solve these challenges reliably and efficiently at global scale.

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
    subgraph Deploy["Deployment: myapp"]
        RS1["ReplicaSet v1\nmyapp:v1\nreplicas=0"]
        RS2["ReplicaSet v2\nmyapp:v2\nreplicas=3"]
        RS3["ReplicaSet v3\nmyapp:v3\nreplicas=0"]
    end

    RS2 --> P1["Pod: myapp-v2-abc"]
    RS2 --> P2["Pod: myapp-v2-def"]
    RS2 --> P3["Pod: myapp-v2-ghi"]

    DC["Deployment Controller"] -->|watches| Deploy
    DC -->|reconciles| RS2
```

## Flow Diagram

```mermaid
sequenceDiagram
    participant U as kubectl
    participant API as API Server
    participant DC as Deployment Controller
    participant RS as ReplicaSet Controller

    U->>API: kubectl set image deployment/myapp app=myapp:v2
    API->>DC: Deployment spec changed
    DC->>API: Create ReplicaSet v2 (replicas=0)
    
    loop Rolling Update (maxSurge=1, maxUnavailable=0)
        DC->>API: Scale RS v2 replicas +1
        RS->>API: Create new Pod (v2)
        Note over RS: Wait for pod Ready
        DC->>API: Scale RS v1 replicas -1
        RS->>API: Terminate old Pod (v1)
    end

    DC->>API: RS v1 replicas=0 (kept for rollback)
    API-->>U: Rollout complete
```

## Design

### Deployment Strategy

```
RollingUpdate (default):
  maxSurge: 1          # Extra pods above desired during update
  maxUnavailable: 0    # No downtime; always desired count running
  
  Example (3 replicas):
    Phase 1: v1=3, v2=0 (start)
    Phase 2: v1=3, v2=1 (surge)
    Phase 3: v1=2, v2=1 (kill old)
    Phase 4: v1=2, v2=2 (surge)
    Phase 5: v1=1, v2=2 (kill old)
    Phase 6: v1=1, v2=3 (surge)
    Phase 7: v1=0, v2=3 (done)
  
  Total time: ~7 pod transitions

Recreate:
  Kills ALL old pods, then creates new ones
  Downtime during transition
  Use case: stateful apps that can't run two versions

Blue-Green (via Deployment swap):
  Maintain two full deployments
  Switch Service selector to point to new version
  Instant cutover, no incremental rollout
  Cost: 2x resources during update
```

### Rollback Mechanism

```
Revision history:
  Deployment keeps old ReplicaSets (revisionHistoryLimit: 10)
  kubectl rollout undo deployment/myapp
    -> scales RS v2 down, RS v1 back up

  kubectl rollout undo deployment/myapp --to-revision=3
    -> rolls back to specific revision

Rollout status:
  kubectl rollout status deployment/myapp
  -> watches for completion or failure

Pause/resume:
  kubectl rollout pause deployment/myapp
  kubectl set image deployment/myapp app=myapp:v3
  kubectl rollout resume deployment/myapp
  -> Batch changes before rolling update begins
```

### readinessProbe Integration

```
Rolling update waits for pod Ready before proceeding:
  1. New pod scheduled
  2. Containers start
  3. readinessProbe executes (HTTP GET /health, TCP check, or exec)
  4. Probe succeeds -> pod added to Service endpoints
  5. Deployment controller proceeds to next step

minReadySeconds: 30
  -> Pod must be ready for 30s before counted as available
  -> Prevents fast-failing pods from appearing ready

progressDeadlineSeconds: 600
  -> Deployment fails if not complete in 600s
  -> Triggers DeadlineExceeded condition
```

## Back-of-Envelope Calculations

```
Rolling update duration:
  3 replicas, 1 new pod at a time
  Pod startup (image cached): 5s + readiness probe: 10s = 15s per pod
  Total: 3 x 15s = 45s
  
  With minReadySeconds=30: 3 x (15+30) = 135s = 2.25min

Rollback speed:
  Instant (old RS just scales up, no image pull needed)
  Effective: same as rolling update to old version = 45s

ReplicaSet storage cost:
  10 old RS * 3 pod templates * ~2KB each = 60KB in etcd
  Trivial, but with 1000 deployments: 60MB just for RS metadata

maxSurge impact:
  maxSurge=25% on 100 replicas: 25 extra pods during update
  If pod = 0.5 CPU, 512MB: 25 x 0.5 = 12.5 CPU, 25 x 512MB = 12.5 GB extra
  Size your cluster with maxSurge headroom
```

## Design Choices

| Strategy | Downtime | Resource Cost | Rollback Speed | Use Case |
|---|---|---|---|---|
| RollingUpdate | None | Low (surge only) | Slow (re-roll) | Most services |
| Recreate | Yes | None | Instant | DB migrations |
| Blue-Green | None | 2x | Instant | Critical services |
| Canary (Argo) | None | Gradual | Fast | Risk-averse deploys |

## Python Implementation

```python
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum
import time

class RolloutPhase(Enum):
    IDLE = "Idle"
    PROGRESSING = "Progressing"
    COMPLETE = "Complete"
    FAILED = "Failed"

@dataclass
class PodTemplate:
    image: str
    cpu_millicores: int = 100
    memory_mb: int = 128
    readiness_delay_s: float = 1.0  # Simulated readiness check time

@dataclass
class ReplicaSet:
    name: str
    template: PodTemplate
    desired: int = 0
    ready: int = 0
    revision: int = 0

    def scale(self, n: int):
        delta = n - self.desired
        self.desired = n
        if delta > 0:
            # Simulate pod startup + readiness
            time.sleep(self.template.readiness_delay_s * delta)
            self.ready = self.desired
            print(f"  [RS {self.name}] scaled up to {self.desired} (ready={self.ready})")
        elif delta < 0:
            self.ready = self.desired
            print(f"  [RS {self.name}] scaled down to {self.desired}")

@dataclass
class Deployment:
    name: str
    replicas: int
    max_surge: int = 1
    max_unavailable: int = 0
    revision_history_limit: int = 3

    _current_rs: Optional[ReplicaSet] = field(default=None, repr=False)
    _history: List[ReplicaSet] = field(default_factory=list, repr=False)
    _revision: int = field(default=0, repr=False)

    def apply(self, template: PodTemplate):
        self._revision += 1
        new_rs = ReplicaSet(
            name=f"{self.name}-rs-{self._revision}",
            template=template,
            revision=self._revision
        )
        print(f"\n[Deployment {self.name}] Rolling update to {template.image} (rev {self._revision})")
        self._rolling_update(new_rs)
        if self._current_rs:
            self._history.append(self._current_rs)
        self._current_rs = new_rs
        # Trim history
        while len(self._history) > self.revision_history_limit:
            removed = self._history.pop(0)
            print(f"  [History] Pruned {removed.name}")

    def _rolling_update(self, new_rs: ReplicaSet):
        old_rs = self._current_rs
        if old_rs is None:
            new_rs.scale(self.replicas)
            return

        desired = self.replicas
        max_total = desired + self.max_surge
        min_available = desired - self.max_unavailable

        new_running = 0
        old_running = old_rs.ready

        while new_running < desired or old_running > 0:
            # Scale up new RS (up to max_total)
            if new_running < desired and new_running + old_running < max_total:
                step = min(self.max_surge, desired - new_running)
                new_running += step
                new_rs.scale(new_running)

            # Scale down old RS (maintain min_available)
            if old_running > 0 and new_running + old_running - 1 >= min_available:
                step = min(old_running, new_running + old_running - min_available)
                old_running -= step
                old_rs.scale(old_running)

        print(f"  [Rollout] Complete: {new_rs.name} ready={new_rs.ready}")

    def rollback(self, revision: Optional[int] = None) -> bool:
        if not self._history:
            print("[Rollback] No history available")
            return False
        if revision:
            target = next((rs for rs in self._history if rs.revision == revision), None)
        else:
            target = self._history[-1]
        if not target:
            print(f"[Rollback] Revision {revision} not found")
            return False
        print(f"\n[Deployment {self.name}] Rolling back to {target.template.image}")
        self._history.remove(target)
        self._rolling_update(target)
        if self._current_rs:
            self._history.append(self._current_rs)
        self._current_rs = target
        return True

# Usage
deploy = Deployment("myapp", replicas=3, max_surge=1, max_unavailable=0)
deploy.apply(PodTemplate("myapp:v1", readiness_delay_s=0.1))
deploy.apply(PodTemplate("myapp:v2", readiness_delay_s=0.1))
deploy.apply(PodTemplate("myapp:v3", readiness_delay_s=0.1))

print("\n--- Rollback ---")
deploy.rollback()  # Back to v2
```

## Java Implementation

```java
import java.util.*;

public class KubeDeployment {
    record PodTemplate(String image, int cpuMillicores) {}

    static class ReplicaSet {
        String name; PodTemplate template; int desired = 0, ready = 0; int revision;
        ReplicaSet(String name, PodTemplate template, int revision) {
            this.name = name; this.template = template; this.revision = revision;
        }
        void scale(int n) {
            desired = n; ready = n;
            System.out.printf("  [RS %s] replicas=%d%n", name, desired);
        }
    }

    String name; int replicas, maxSurge, maxUnavailable;
    ReplicaSet current; Deque<ReplicaSet> history = new ArrayDeque<>();
    int rev = 0;

    KubeDeployment(String name, int replicas, int maxSurge, int maxUnavailable) {
        this.name = name; this.replicas = replicas;
        this.maxSurge = maxSurge; this.maxUnavailable = maxUnavailable;
    }

    void apply(PodTemplate template) {
        ReplicaSet newRS = new ReplicaSet(name + "-rs-" + (++rev), template, rev);
        System.out.printf("%n[Deployment %s] Update to %s%n", name, template.image());
        rollingUpdate(newRS);
        if (current != null) { history.addLast(current); }
        current = newRS;
        while (history.size() > 3) history.pollFirst();
    }

    private void rollingUpdate(ReplicaSet newRS) {
        if (current == null) { newRS.scale(replicas); return; }
        int newRunning = 0, oldRunning = current.ready;
        while (newRunning < replicas || oldRunning > 0) {
            if (newRunning < replicas && newRunning + oldRunning < replicas + maxSurge) {
                newRS.scale(++newRunning);
            }
            if (oldRunning > 0 && newRunning + oldRunning - 1 >= replicas - maxUnavailable) {
                current.scale(--oldRunning);
            }
        }
    }

    void rollback() {
        if (history.isEmpty()) { System.out.println("[Rollback] No history"); return; }
        ReplicaSet target = history.pollLast();
        System.out.printf("[Rollback] to %s%n", target.template.image());
        rollingUpdate(target);
        if (current != null) history.addLast(current);
        current = target;
    }

    public static void main(String[] args) {
        KubeDeployment d = new KubeDeployment("myapp", 3, 1, 0);
        d.apply(new PodTemplate("myapp:v1", 100));
        d.apply(new PodTemplate("myapp:v2", 100));
        System.out.println("\n--- Rollback ---");
        d.rollback();
    }
}
```

## Complexity

| Operation | Time |
|---|---|
| Rolling update (N replicas, surge=1) | O(N) pod transitions |
| Rollback | O(N) (same as update) |
| Revision history lookup | O(revisionHistoryLimit) |
| Deployment controller reconcile | O(1) per loop |

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

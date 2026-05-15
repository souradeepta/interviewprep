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


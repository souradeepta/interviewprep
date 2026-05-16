# Kubernetes Architecture

## Problem Statement

Design and understand Kubernetes (K8s) — a container orchestration system that automates deployment, scaling, and management of containerized applications.

## Scenario

Kubernetes Architecture is a critical component in modern distributed systems. In real-world applications, orchestrating containers across clusters automatically. For example, major tech companies like Netflix, Uber, and Airbnb rely on similar solutions to handle millions of concurrent users and requests. The challenge is achieving this while maintaining sub-100ms latency, 99.99% availability, and gracefully handling 10x traffic spikes during peak demand. This component provides the foundational capability to solve these challenges reliably and efficiently at global scale.

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
    subgraph ControlPlane["Control Plane (Master)"]
        API[API Server kube-apiserver]
        ETCD[(etcd cluster)]
        SCHED[Scheduler kube-scheduler]
        CM[Controller Manager]
    end

    subgraph Worker1["Worker Node 1"]
        KL1[kubelet]
        KP1[kube-proxy]
        C1[Container runtime]
        Pod1[Pod: nginx]
        Pod2[Pod: app]
    end

    subgraph Worker2["Worker Node 2"]
        KL2[kubelet]
        KP2[kube-proxy]
        C2[Container runtime]
        Pod3[Pod: app]
        Pod4[Pod: postgres]
    end

    API <--> ETCD
    API --> SCHED
    API --> CM
    SCHED --> API
    CM --> API
    KL1 --> API
    KL2 --> API
    KP1 --> API
    KP2 --> API
```

## Flow Diagram

```mermaid
sequenceDiagram
    participant User as kubectl
    participant API as API Server
    participant ETCD as etcd
    participant Sched as Scheduler
    participant KL as kubelet

    User->>API: kubectl apply -f deployment.yaml
    API->>API: Authenticate + authorize
    API->>ETCD: Store desired state
    API-->>User: 200 OK

    API->>Sched: New Pod needs scheduling
    Sched->>API: Get nodes + resource usage
    Sched->>API: Bind Pod to node-1
    API->>ETCD: Update Pod.spec.nodeName=node-1

    API->>KL: Watch: new Pod assigned to this node
    KL->>KL: Pull image, create containers
    KL->>API: Update Pod status: Running
```

## Design

### Control Plane Components

```
kube-apiserver   - REST API frontend; all mutations go through here
etcd             - Distributed key-value store; source of truth for cluster state
kube-scheduler   - Watches unscheduled Pods, assigns to optimal node
                   Considers: resources, affinity, taints/tolerations
kube-controller-manager - Control loops:
  - ReplicaSet controller: ensures N replicas running
  - Deployment controller: rolling update logic
  - Node controller: detects node failures
  - Job/CronJob controllers
cloud-controller-manager - Cloud-specific: LB provisioning, storage
```

### Worker Node Components

```
kubelet          - Node agent; ensures containers run per PodSpec
                   Reads PodSpec from API, manages pod lifecycle
kube-proxy       - Network proxy; maintains iptables/ipvs rules for Services
Container runtime - containerd, CRI-O (no longer Docker)
```

### Reconciliation Loop

```
Every K8s controller runs a reconciliation loop:
  1. Observe current state (from API/etcd)
  2. Compare with desired state (from spec)
  3. Take action to converge (create/delete/update)
  4. Repeat

This makes K8s self-healing:
  Node dies -> pod rescheduled elsewhere
  Pod crashes -> ReplicaSet creates replacement
  Config changes -> rolling update begins
```

## Back-of-Envelope Calculations

```
Control plane sizing:
  etcd: 3 instances x 4GB RAM = 12GB for cluster state
  API server: 2-4 instances, ~2GB RAM each (autoscales)
  etcd max: ~8000 objects/sec write throughput
  Large cluster (5000 nodes): ~500K pods, API server needs 32GB RAM

Scheduling latency:
  Simple pod: <1s from submit to scheduled
  Complex affinity: 1-5s
  etcd write: ~5ms (local), ~50ms (cross-AZ)

Node failure recovery:
  Detection: 40s (node heartbeat timeout)
  Eviction: +5min (pod eviction timeout) = 5m40s total
  Rescheduling: <30s after eviction
  Total recovery: ~6 minutes default (tune for faster)

Cluster scale limits:
  Google recommendation: 5000 nodes, 150K pods per cluster
  etcd: 2GB storage per 100K objects
  API server: handles ~1000 writes/sec, ~5000 reads/sec
```

## Design Choices

| Decision | Option A | Option B |
|---|---|---|
| etcd size | 3 nodes (min HA) | 5 nodes (better fault tolerance) |
| Node failure response | Default 5min eviction | Tune to 30s (faster, noisy) |
| Scheduler | Default | Custom scheduler for ML workloads |
| Network plugin | Calico (BGP) | Cilium (eBPF, better performance) |
| Runtime | containerd | CRI-O (OCI-native) |

## Python Implementation

```python
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum
import time

class PodPhase(Enum):
    PENDING = "Pending"
    RUNNING = "Running"
    SUCCEEDED = "Succeeded"
    FAILED = "Failed"
    UNKNOWN = "Unknown"

@dataclass
class ResourceRequirements:
    cpu_millicores: int = 100
    memory_mb: int = 128

@dataclass
class Node:
    name: str
    cpu_millicores: int = 4000
    memory_mb: int = 8192
    labels: Dict[str, str] = field(default_factory=dict)
    ready: bool = True
    pods: List[str] = field(default_factory=list)

    def available_cpu(self, scheduled: List["Pod"]) -> int:
        used = sum(p.resources.cpu_millicores for p in scheduled if p.node == self.name)
        return self.cpu_millicores - used

    def available_memory(self, scheduled: List["Pod"]) -> int:
        used = sum(p.resources.memory_mb for p in scheduled if p.node == self.name)
        return self.memory_mb - used

@dataclass
class Pod:
    name: str
    image: str
    resources: ResourceRequirements = field(default_factory=ResourceRequirements)
    phase: PodPhase = PodPhase.PENDING
    node: Optional[str] = None
    namespace: str = "default"

class KubeScheduler:
    def schedule(self, pod: Pod, nodes: List[Node], pods: List[Pod]) -> Optional[str]:
        # Filter: nodes that can fit the pod
        feasible = [
            n for n in nodes
            if n.ready
            and n.available_cpu(pods) >= pod.resources.cpu_millicores
            and n.available_memory(pods) >= pod.resources.memory_mb
        ]
        if not feasible:
            return None
        # Score: prefer nodes with more available resources (bin packing alternative)
        best = max(feasible, key=lambda n: n.available_cpu(pods) + n.available_memory(pods))
        return best.name

class KubeAPIServer:
    def __init__(self):
        self._pods: Dict[str, Pod] = {}
        self._nodes: Dict[str, Node] = {}
        self._scheduler = KubeScheduler()

    def add_node(self, node: Node):
        self._nodes[node.name] = node
        print(f"[K8s] Node registered: {node.name}")

    def create_pod(self, pod: Pod) -> Pod:
        self._pods[pod.name] = pod
        print(f"[K8s] Pod {pod.name} created, phase=Pending")
        self._schedule_pod(pod)
        return pod

    def _schedule_pod(self, pod: Pod):
        node_name = self._scheduler.schedule(pod, list(self._nodes.values()), list(self._pods.values()))
        if node_name:
            pod.node = node_name
            pod.phase = PodPhase.RUNNING
            print(f"[K8s] Pod {pod.name} scheduled to {node_name}")
        else:
            print(f"[K8s] Pod {pod.name} Unschedulable - insufficient resources")

    def node_failure(self, node_name: str):
        node = self._nodes.get(node_name)
        if node:
            node.ready = False
            print(f"[K8s] Node {node_name} failed")
            # Reschedule pods that were on this node
            for pod in self._pods.values():
                if pod.node == node_name:
                    pod.phase = PodPhase.UNKNOWN
                    pod.node = None
                    print(f"[K8s] Evicting {pod.name}, rescheduling...")
                    self._schedule_pod(pod)

# Usage
api = KubeAPIServer()
api.add_node(Node("node-1", cpu_millicores=4000, memory_mb=8192))
api.add_node(Node("node-2", cpu_millicores=4000, memory_mb=8192))

api.create_pod(Pod("nginx-1", "nginx:alpine", ResourceRequirements(100, 64)))
api.create_pod(Pod("app-1", "myapp:v1", ResourceRequirements(500, 512)))
api.create_pod(Pod("app-2", "myapp:v1", ResourceRequirements(500, 512)))

print("\n--- Simulating node failure ---")
api.node_failure("node-1")
```

## Java Implementation

```java
import java.util.*;
import java.util.stream.*;

public class KubeScheduler {
    enum Phase { PENDING, RUNNING, FAILED }

    record Resources(int cpuMillicores, int memoryMb) {}
    record Pod(String name, String image, Resources resources, String namespace) {}

    static class Node {
        String name;
        int cpuTotal, memTotal;
        boolean ready = true;
        List<Pod> pods = new ArrayList<>();

        Node(String name, int cpu, int mem) { this.name = name; cpuTotal = cpu; memTotal = mem; }

        int freeCpu() { return cpuTotal - pods.stream().mapToInt(p -> p.resources().cpuMillicores()).sum(); }
        int freeMem() { return memTotal - pods.stream().mapToInt(p -> p.resources().memoryMb()).sum(); }

        boolean canFit(Pod p) { return ready && freeCpu() >= p.resources().cpuMillicores() && freeMem() >= p.resources().memoryMb(); }
    }

    private List<Node> nodes = new ArrayList<>();
    private Map<String, String> podToNode = new HashMap<>(); // pod -> node

    public void addNode(Node n) { nodes.add(n); }

    public Optional<String> schedule(Pod pod) {
        return nodes.stream().filter(n -> n.canFit(pod))
            .max(Comparator.comparingInt(Node::freeCpu))
            .map(n -> { n.pods.add(pod); podToNode.put(pod.name(), n.name); return n.name; });
    }

    public static void main(String[] args) {
        KubeScheduler sched = new KubeScheduler();
        sched.addNode(new Node("node-1", 4000, 8192));
        sched.addNode(new Node("node-2", 4000, 8192));
        Pod p = new Pod("web-1", "nginx:alpine", new Resources(100, 128), "default");
        System.out.println("Scheduled to: " + sched.schedule(p).orElse("Unschedulable"));
    }
}
```

## Complexity

| Operation | Time |
|---|---|
| API request processing | O(1) + etcd write O(log n) |
| Pod scheduling | O(nodes x filters) |
| Reconciliation loop | O(desired - actual) |
| etcd watch notification | O(subscribers) |

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

**Cluster Capacity:**
- Node: 16 cores, 64GB RAM
- Per pod: 0.5 CPU request, 512MB
- Max pods per node (CPU): 32; (RAM): 128 → CPU limits at 32
- 100 nodes → 3200 pods max (real-world ~70% = 2200 schedulable)

**API Server Load:**
- 1000 pods × 2 watches = 2000 open connections
- Heartbeat: 10s interval → 200 QPS steady state
- kubectl list pods: scans etcd — expensive; use field selectors

**Etcd Storage:**
- 1 pod spec: ~2KB in etcd
- 10K pods: 20MB — well within 8GB etcd limit
- Snapshot interval: every 10K revisions → ~1 min compaction

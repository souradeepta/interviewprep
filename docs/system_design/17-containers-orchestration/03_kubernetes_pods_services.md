# Kubernetes Pods and Services

## Problem Statement

Understand how Kubernetes Pods (the smallest deployable unit) and Services (stable network endpoints) work together to enable reliable inter-container communication inside a cluster.

## Scenario

Kubernetes Pods and Services is a critical component in modern distributed systems. In real-world applications, orchestrating containers across clusters automatically. For example, major tech companies like Netflix, Uber, and Airbnb rely on similar solutions to handle millions of concurrent users and requests. The challenge is achieving this while maintaining sub-100ms latency, 99.99% availability, and gracefully handling 10x traffic spikes during peak demand. This component provides the foundational capability to solve these challenges reliably and efficiently at global scale.

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
    subgraph Cluster["Kubernetes Cluster"]
        subgraph NS["Namespace: production"]
            SVC1["Service: frontend\nClusterIP: 10.96.10.1\nPort: 80"]
            SVC2["Service: backend\nClusterIP: 10.96.20.1\nPort: 8080"]
            SVC3["Service: postgres\nClusterIP: 10.96.30.1\nPort: 5432"]

            subgraph Node1["Node 1"]
                P1["Pod: frontend-abc\n172.16.0.2:80"]
                P2["Pod: frontend-def\n172.16.0.3:80"]
            end
            subgraph Node2["Node 2"]
                P3["Pod: backend-xyz\n172.16.1.2:8080"]
                P4["Pod: postgres-0\n172.16.1.3:5432"]
            end
        end
        DNS["CoreDNS\nbackend.production.svc.cluster.local"]
    end

    SVC1 --> P1
    SVC1 --> P2
    SVC2 --> P3
    SVC3 --> P4
    P1 --> DNS
    DNS --> SVC2
```

## Flow Diagram

```mermaid
sequenceDiagram
    participant P as Pod: frontend
    participant DNS as CoreDNS
    participant SVC as Service: backend
    participant KP as kube-proxy iptables
    participant B as Pod: backend-xyz

    P->>DNS: Resolve backend.production.svc.cluster.local
    DNS-->>P: 10.96.20.1 (ClusterIP)
    P->>KP: TCP connect to 10.96.20.1:8080
    KP->>KP: iptables DNAT rule match
    KP->>B: Forward to 172.16.1.2:8080 (random pod)
    B-->>P: HTTP 200 response
```

## Design

### Pod Anatomy

```
Pod = one or more containers sharing:
  - Network namespace (same IP, port space)
  - IPC namespace (can communicate via localhost)
  - Optional: shared volumes

Pod spec:
  containers:
    - name: app
      image: myapp:v1
      ports: [{containerPort: 8080}]
      resources:
        requests: {cpu: "100m", memory: "128Mi"}
        limits:   {cpu: "500m", memory: "512Mi"}
      readinessProbe:
        httpGet: {path: /health, port: 8080}
        initialDelaySeconds: 5
        periodSeconds: 10
      livenessProbe:
        httpGet: {path: /health, port: 8080}
        failureThreshold: 3
```

### Service Types

```
ClusterIP (default):
  - Stable virtual IP inside cluster
  - kube-proxy creates iptables/IPVS rules
  - DNS: <svc>.<ns>.svc.cluster.local
  - Not accessible outside cluster

NodePort:
  - Exposes port 30000-32767 on every node
  - External: <NodeIP>:<NodePort>
  - ClusterIP also created
  - Use case: dev/test, bare metal

LoadBalancer:
  - Provisions cloud LB (AWS ELB, GCP LB)
  - Routes external traffic to NodePort
  - Gets external IP from cloud provider
  - Use case: production internet-facing services

ExternalName:
  - CNAME to external DNS name
  - Use case: migrate external services into cluster
  - No proxying, just DNS alias

Headless (ClusterIP: None):
  - No VIP; DNS returns individual Pod IPs
  - Use case: StatefulSets, custom load balancing
  - Direct pod addressing via DNS
```

### Endpoints and EndpointSlices

```
Service selects pods via label selector:
  selector:
    app: backend
    version: v1

Endpoints controller:
  - Watches pods matching selector
  - Updates Endpoints object with ready pod IPs
  - kube-proxy watches Endpoints for rule updates

EndpointSlices (K8s 1.21+):
  - Shards endpoint data (max 100 pods per slice)
  - Better scalability: less etcd/API churn
  - Required for large services (>1000 pods)
```

## Back-of-Envelope Calculations

```
Service iptables scaling:
  1000 pods x 5 services each = 5000 iptables rules
  iptables rule lookup: O(n) = 5ms for 5000 rules
  IPVS rule lookup: O(1) = <0.1ms (hash table)
  Large clusters (10K pods): IPVS mandatory

Pod startup time:
  Image cached: ~1-2s (namespace + cgroup setup)
  Image pull (500MB): +10-30s
  Readiness probe delay: +5-30s
  Total first deploy: 15-60s

Service endpoint update latency:
  Pod ready -> Endpoints updated: ~1s
  kube-proxy applies new rules: ~1-5s
  Total: ~2-6s from pod ready to receiving traffic

DNS query overhead:
  Intra-cluster DNS: ~0.5ms (CoreDNS is in-cluster)
  Connection reuse: DNS only on first request
  ndots:5 setting: 5 DNS queries before short form resolves
```

## Design Choices

| Approach | Pros | Cons |
|---|---|---|
| ClusterIP + Ingress | Standard, portable | Extra hop through Ingress |
| NodePort direct | No LB dependency | Exposes all nodes, port range limited |
| LoadBalancer per service | Simple external access | $$ per LB, cloud-specific |
| iptables mode | Widely supported | O(n) rules, high-latency large clusters |
| IPVS mode | O(1) lookup, better LB algos | Requires kernel module |
| Cilium (eBPF) | Fastest, no kube-proxy | Newer, less battle-tested |

## Python Implementation

```python
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import hashlib
import random

@dataclass
class Container:
    name: str
    image: str
    port: int
    cpu_request: int = 100   # millicores
    memory_mb: int = 128
    ready: bool = False

@dataclass
class Pod:
    name: str
    namespace: str
    labels: Dict[str, str]
    containers: List[Container]
    ip: str = ""
    phase: str = "Pending"

    def is_ready(self) -> bool:
        return all(c.ready for c in self.containers) and self.phase == "Running"

@dataclass
class Service:
    name: str
    namespace: str
    selector: Dict[str, str]
    port: int
    target_port: int
    service_type: str = "ClusterIP"
    cluster_ip: str = ""

class CoreDNS:
    def __init__(self):
        self._records: Dict[str, str] = {}

    def register(self, svc: Service):
        fqdn = f"{svc.name}.{svc.namespace}.svc.cluster.local"
        self._records[fqdn] = svc.cluster_ip
        self._records[svc.name] = svc.cluster_ip  # short name

    def resolve(self, name: str, namespace: str = "default") -> Optional[str]:
        # Try FQDN first, then short name
        fqdn = f"{name}.{namespace}.svc.cluster.local"
        return self._records.get(fqdn) or self._records.get(name)

class EndpointsController:
    def __init__(self):
        self._endpoints: Dict[str, List[str]] = {}

    def reconcile(self, svc: Service, pods: List[Pod]) -> List[str]:
        ready_ips = []
        for pod in pods:
            if pod.namespace == svc.namespace and pod.is_ready():
                if all(pod.labels.get(k) == v for k, v in svc.selector.items()):
                    ready_ips.append(f"{pod.ip}:{svc.target_port}")
        self._endpoints[svc.name] = ready_ips
        return ready_ips

    def get_endpoints(self, svc_name: str) -> List[str]:
        return self._endpoints.get(svc_name, [])

class KubeProxy:
    def __init__(self, endpoints_ctrl: EndpointsController):
        self._ep = endpoints_ctrl
        self._mode = "iptables"  # or "ipvs"

    def route(self, svc_name: str, client_ip: str = "") -> Optional[str]:
        endpoints = self._ep.get_endpoints(svc_name)
        if not endpoints:
            return None
        # iptables random selection (real: DNAT rule with probability chain)
        if self._mode == "ipvs":
            # IPVS round-robin: hash by client IP for session affinity
            idx = int(hashlib.md5(client_ip.encode()).hexdigest(), 16) % len(endpoints)
            return endpoints[idx]
        return random.choice(endpoints)

# Simulation
dns = CoreDNS()
ep_ctrl = EndpointsController()
proxy = KubeProxy(ep_ctrl)

# Register services
backend_svc = Service(
    name="backend", namespace="production",
    selector={"app": "backend"}, port=8080, target_port=8080,
    cluster_ip="10.96.20.1"
)
dns.register(backend_svc)

# Create pods
pods = [
    Pod("backend-abc", "production", {"app": "backend"}, [Container("app", "myapp:v1", 8080, ready=True)], "172.16.1.2", "Running"),
    Pod("backend-def", "production", {"app": "backend"}, [Container("app", "myapp:v1", 8080, ready=True)], "172.16.1.3", "Running"),
    Pod("backend-ghi", "production", {"app": "backend"}, [Container("app", "myapp:v1", 8080, ready=False)], "172.16.1.4", "Pending"),
]

# Reconcile endpoints (only ready pods)
endpoints = ep_ctrl.reconcile(backend_svc, pods)
print(f"Active endpoints: {endpoints}")  # Only 2 ready pods

# DNS resolution
cluster_ip = dns.resolve("backend", "production")
print(f"Resolved backend -> {cluster_ip}")

# kube-proxy routes (bypassing ClusterIP -> real pod)
for i in range(4):
    target = proxy.route("backend", client_ip=f"172.16.0.{i}")
    print(f"  Request {i} -> {target}")
```

## Java Implementation

```java
import java.util.*;
import java.util.stream.*;

public class K8sServiceMesh {
    record Container(String name, String image, int port, boolean ready) {}
    record Label(String key, String value) {}

    static class Pod {
        String name, namespace, ip, phase;
        Map<String, String> labels;
        List<Container> containers;

        Pod(String name, String ns, String ip, Map<String, String> labels, List<Container> containers, String phase) {
            this.name = name; this.namespace = ns; this.ip = ip;
            this.labels = labels; this.containers = containers; this.phase = phase;
        }

        boolean isReady() {
            return "Running".equals(phase) && containers.stream().allMatch(c -> c.ready());
        }
    }

    record Service(String name, String namespace, Map<String, String> selector, int port, int targetPort, String clusterIp) {}

    static class EndpointsController {
        private Map<String, List<String>> endpoints = new HashMap<>();

        List<String> reconcile(Service svc, List<Pod> pods) {
            List<String> ready = pods.stream()
                .filter(p -> p.namespace.equals(svc.namespace()) && p.isReady())
                .filter(p -> svc.selector().entrySet().stream()
                    .allMatch(e -> e.getValue().equals(p.labels.get(e.getKey()))))
                .map(p -> p.ip + ":" + svc.targetPort())
                .collect(Collectors.toList());
            endpoints.put(svc.name(), ready);
            return ready;
        }

        List<String> get(String svcName) { return endpoints.getOrDefault(svcName, List.of()); }
    }

    static class KubeProxy {
        EndpointsController ep;
        Random rng = new Random();
        KubeProxy(EndpointsController ep) { this.ep = ep; }

        Optional<String> route(String svcName) {
            List<String> eps = ep.get(svcName);
            if (eps.isEmpty()) return Optional.empty();
            return Optional.of(eps.get(rng.nextInt(eps.size())));
        }
    }

    public static void main(String[] args) {
        Service svc = new Service("backend", "production",
            Map.of("app", "backend"), 8080, 8080, "10.96.20.1");

        List<Pod> pods = List.of(
            new Pod("backend-1", "production", "172.16.1.2",
                Map.of("app", "backend"),
                List.of(new Container("app", "myapp:v1", 8080, true)), "Running"),
            new Pod("backend-2", "production", "172.16.1.3",
                Map.of("app", "backend"),
                List.of(new Container("app", "myapp:v1", 8080, false)), "Pending")
        );

        EndpointsController epCtrl = new EndpointsController();
        List<String> eps = epCtrl.reconcile(svc, pods);
        System.out.println("Active endpoints: " + eps);

        KubeProxy proxy = new KubeProxy(epCtrl);
        for (int i = 0; i < 3; i++) {
            System.out.println("  Route -> " + proxy.route("backend").orElse("no endpoint"));
        }
    }
}
```

## Complexity

| Operation | Time |
|---|---|
| Service DNS resolution | O(1) (CoreDNS hash map) |
| kube-proxy iptables route | O(n) rules |
| kube-proxy IPVS route | O(1) |
| Endpoint reconciliation | O(pods x label_keys) |
| Pod readiness probe check | O(containers) |

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

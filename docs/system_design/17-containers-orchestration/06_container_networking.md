# Container Networking (CNI)

## Problem Statement

Understand how containers and pods communicate across nodes using the Container Network Interface (CNI), covering overlay networks, pod CIDR allocation, and network policies.

## Scenario

Container Networking (CNI) is a critical component in modern distributed systems. In real-world applications, handling complex business logic at scale with high reliability. For example, major tech companies like Netflix, Uber, and Airbnb rely on similar solutions to handle millions of concurrent users and requests. The challenge is achieving this while maintaining sub-100ms latency, 99.99% availability, and gracefully handling 10x traffic spikes during peak demand. This component provides the foundational capability to solve these challenges reliably and efficiently at global scale.

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
    subgraph Node1["Node 1 (192.168.1.10)"]
        P1["Pod A\n10.244.1.2"]
        P2["Pod B\n10.244.1.3"]
        VE1["veth pair"]
        BR1["cni0 bridge\n10.244.1.1/24"]
        FL1["flannel.1 VTEP\nVXLAN encap"]
    end
    subgraph Node2["Node 2 (192.168.1.11)"]
        P3["Pod C\n10.244.2.2"]
        VE2["veth pair"]
        BR2["cni0 bridge\n10.244.2.1/24"]
        FL2["flannel.1 VTEP"]
    end

    P1 --> VE1 --> BR1 --> FL1
    P2 --> VE1
    FL1 -->|"VXLAN UDP 8472\nouter: 192.168.1.10->192.168.1.11\ninner: 10.244.1.2->10.244.2.2"| FL2
    FL2 --> BR2 --> VE2 --> P3
```

## Flow Diagram

```mermaid
sequenceDiagram
    participant PA as Pod A (10.244.1.2)
    participant BR1 as Bridge (Node 1)
    participant VTEP1 as VTEP (Node 1)
    participant VTEP2 as VTEP (Node 2)
    participant BR2 as Bridge (Node 2)
    participant PC as Pod C (10.244.2.2)

    PA->>BR1: IP packet: src=10.244.1.2, dst=10.244.2.2
    BR1->>BR1: No local route for 10.244.2.x -> default gw
    BR1->>VTEP1: Forward to flannel.1
    VTEP1->>VTEP1: Lookup: 10.244.2.0/24 -> Node2 (192.168.1.11)
    VTEP1->>VTEP2: VXLAN: outer src=192.168.1.10, dst=192.168.1.11\ninner: original IP packet
    VTEP2->>VTEP2: Decapsulate VXLAN
    VTEP2->>BR2: Inner packet to 10.244.2.2
    BR2->>PC: Deliver to Pod C
```

## Design

### CNI Plugins

```
Flannel (simple, VXLAN overlay):
  - Assigns /24 subnet per node from larger /16
  - VXLAN tunnels between nodes (UDP port 8472)
  - Overhead: 50 bytes per packet (VXLAN header)
  - No network policy support (use with Calico NetworkPolicy)

Calico (BGP, no overlay):
  - Native IP routing via BGP between nodes
  - No encapsulation overhead (pure IP routing)
  - Full NetworkPolicy support
  - eBPF dataplane option for high performance

Cilium (eBPF):
  - Replaces kube-proxy entirely with eBPF
  - Kernel-level packet processing (no iptables)
  - Native NetworkPolicy + L7 (HTTP, gRPC) policies
  - Hubble for network observability
  - 10-30% lower latency than iptables

Weave:
  - Fast datapath + encrypted overlay
  - No configuration needed (auto-peer discovery)
  - Multicast via UDP broadcast for discovery
```

### Pod IP Assignment

```
IPAM (IP Address Management):
  Cluster CIDR: 10.244.0.0/16 (65534 pod IPs)
  Per-node: /24 subnet = 254 pods per node
  
  Node 1: 10.244.1.0/24 (10.244.1.1 - 10.244.1.254)
  Node 2: 10.244.2.0/24
  ...
  Node 255: 10.244.255.0/24

Pod lifecycle:
  1. kubelet calls CNI plugin (ADD)
  2. CNI creates veth pair: one end in pod ns, one in host ns
  3. CNI assigns IP from node subnet
  4. CNI adds routes in both namespaces
  5. Pod gets IP, default gateway

  On pod delete:
  1. kubelet calls CNI (DEL)
  2. veth pair removed, IP returned to pool
```

### Network Policy

```
Default: All pods can communicate with all pods (flat network)

NetworkPolicy example:
  spec:
    podSelector: {matchLabels: {app: backend}}
    policyTypes: [Ingress, Egress]
    ingress:
      - from:
        - podSelector: {matchLabels: {app: frontend}}
        ports: [{port: 8080}]
    egress:
      - to:
        - podSelector: {matchLabels: {app: postgres}}
        ports: [{port: 5432}]

Implementation: CNI plugin programs iptables/eBPF rules
  - Calico: iptables chains per policy
  - Cilium: eBPF maps for O(1) policy evaluation
```

## Back-of-Envelope Calculations

```
VXLAN overhead:
  Original packet: 1460 bytes (TCP MSS)
  VXLAN header: 8B + UDP: 8B + outer IP: 20B + outer Ethernet: 14B = 50B overhead
  Effective MTU: 1500 - 50 = 1450B (jumbo frames recommended)
  Overhead: 50/1460 = 3.4% bandwidth overhead

Pod density per node:
  Node subnet: /24 = 254 usable IPs
  Max 254 pods per node (default AWS EKS: 110)
  AWS VPC CNI: limited by instance type ENIs

CNI plugin add latency:
  IPAM + veth creation: ~5-10ms per pod start
  Negligible vs. image pull time (~10-30s)

Network policy at scale:
  iptables: 10K policies = 10K rules, ~5ms per packet evaluation
  Cilium eBPF: 10K policies = O(1) hash lookup, ~10 microseconds
  At 100K req/s: iptables adds 500ms/sec CPU, eBPF adds 1ms/sec CPU
```

## Design Choices

| CNI | Overhead | NetworkPolicy | Complexity | Use Case |
|---|---|---|---|---|
| Flannel | VXLAN +50B | No | Low | Simple dev/test |
| Calico (BGP) | None | Yes | Medium | Production, bare metal |
| Calico (IPIP) | +20B | Yes | Medium | Cloud (no BGP) |
| Cilium | None (eBPF) | L3-L7 | High | Performance-critical |
| AWS VPC CNI | None | No (use Calico) | Low | EKS (native VPC IPs) |

## Python Implementation

```python
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import ipaddress
import struct
import hashlib

@dataclass
class PodInterface:
    veth_host: str  # vethXXXX in host ns
    veth_pod: str   # eth0 in pod ns
    pod_ip: str
    gateway: str
    mac: str

class IPAMPool:
    def __init__(self, cluster_cidr: str = "10.244.0.0/16"):
        self._network = ipaddress.IPv4Network(cluster_cidr)
        self._subnets = list(self._network.subnets(prefixlen_diff=8))  # /24 per node
        self._node_subnets: Dict[str, ipaddress.IPv4Network] = {}
        self._allocated: Dict[str, set] = {}

    def assign_node_subnet(self, node_name: str) -> ipaddress.IPv4Network:
        idx = len(self._node_subnets)
        subnet = self._subnets[idx]
        self._node_subnets[node_name] = subnet
        self._allocated[node_name] = set()
        print(f"[IPAM] Node {node_name} assigned {subnet}")
        return subnet

    def allocate_pod_ip(self, node_name: str) -> Optional[str]:
        subnet = self._node_subnets.get(node_name)
        if not subnet:
            return None
        hosts = list(subnet.hosts())
        hosts = hosts[1:]  # Skip gateway (.1)
        for ip in hosts:
            ip_str = str(ip)
            if ip_str not in self._allocated[node_name]:
                self._allocated[node_name].add(ip_str)
                return ip_str
        return None  # Exhausted

    def release_pod_ip(self, node_name: str, ip: str):
        self._allocated[node_name].discard(ip)

    def gateway_for_node(self, node_name: str) -> str:
        subnet = self._node_subnets[node_name]
        return str(list(subnet.hosts())[0])  # .1 address

class VXLANNetwork:
    def __init__(self):
        self._node_vtep: Dict[str, str] = {}  # node -> physical IP
        self._subnet_to_node: Dict[str, str] = {}

    def register_node(self, node_name: str, node_ip: str, pod_subnet: str):
        self._node_vtep[node_name] = node_ip
        self._subnet_to_node[pod_subnet] = node_name
        print(f"[VXLAN] Registered {node_name}: {node_ip}, pod subnet: {pod_subnet}")

    def route_pod_to_pod(self, src_pod_ip: str, dst_pod_ip: str) -> dict:
        # Find which node hosts the dst pod
        dst_subnet = ".".join(dst_pod_ip.split(".")[:3]) + ".0/24"
        dst_node = self._subnet_to_node.get(dst_subnet)
        if not dst_node:
            return {"error": f"No route to {dst_pod_ip}"}
        dst_vtep = self._node_vtep[dst_node]
        return {
            "inner_src": src_pod_ip,
            "inner_dst": dst_pod_ip,
            "outer_src": "auto",  # source node's IP
            "outer_dst": dst_vtep,
            "protocol": "VXLAN",
            "vni": 1,
            "udp_port": 8472,
        }

class NetworkPolicyEngine:
    def __init__(self):
        self._policies: List[dict] = []

    def add_policy(self, namespace: str, pod_selector: Dict[str, str],
                   ingress_from: List[Dict], egress_to: List[Dict]):
        self._policies.append({
            "namespace": namespace,
            "pod_selector": pod_selector,
            "ingress": ingress_from,
            "egress": egress_to,
        })

    def _labels_match(self, pod_labels: Dict, selector: Dict) -> bool:
        return all(pod_labels.get(k) == v for k, v in selector.items())

    def is_allowed(self, src_pod_labels: Dict, dst_pod_labels: Dict,
                   dst_port: int, namespace: str) -> bool:
        applicable = [p for p in self._policies
                      if p["namespace"] == namespace
                      and self._labels_match(dst_pod_labels, p["pod_selector"])]
        if not applicable:
            return True  # No policy = allow all
        for policy in applicable:
            for rule in policy["ingress"]:
                from_sel = rule.get("from_selector", {})
                ports = rule.get("ports", [])
                if self._labels_match(src_pod_labels, from_sel):
                    if not ports or dst_port in ports:
                        return True
        return False

# Usage
ipam = IPAMPool("10.244.0.0/16")
vxlan = VXLANNetwork()

for node, ip in [("node-1", "192.168.1.10"), ("node-2", "192.168.1.11")]:
    subnet = ipam.assign_node_subnet(node)
    vxlan.register_node(node, ip, str(subnet))

pod1_ip = ipam.allocate_pod_ip("node-1")
pod2_ip = ipam.allocate_pod_ip("node-2")
print(f"\nPod IPs: node-1={pod1_ip}, node-2={pod2_ip}")

route = vxlan.route_pod_to_pod(pod1_ip, pod2_ip)
print(f"VXLAN route: {route}")

# Network policy
policy_engine = NetworkPolicyEngine()
policy_engine.add_policy(
    namespace="prod",
    pod_selector={"app": "backend"},
    ingress_from=[{"from_selector": {"app": "frontend"}, "ports": [8080]}],
    egress_to=[{"to_selector": {"app": "postgres"}, "ports": [5432]}]
)
print(f"\nFrontend -> Backend:8080 allowed: {policy_engine.is_allowed({'app':'frontend'}, {'app':'backend'}, 8080, 'prod')}")
print(f"Unknown -> Backend:8080 allowed: {policy_engine.is_allowed({'app':'unknown'}, {'app':'backend'}, 8080, 'prod')}")
```

## Java Implementation

```java
import java.util.*;
import java.util.stream.*;

public class ContainerNetworking {
    static class IPAMPool {
        private int nextNode = 1;
        private Map<String, Integer> nodeSubnets = new HashMap<>();
        private Map<String, Set<Integer>> allocated = new HashMap<>();

        String assignNodeSubnet(String node) {
            nodeSubnets.put(node, nextNode++);
            allocated.put(node, new HashSet<>());
            return "10.244." + nodeSubnets.get(node) + ".0/24";
        }

        String allocatePodIp(String node) {
            Set<Integer> used = allocated.get(node);
            for (int i = 2; i < 255; i++) {
                if (!used.contains(i)) {
                    used.add(i);
                    return "10.244." + nodeSubnets.get(node) + "." + i;
                }
            }
            return null;
        }
    }

    record VXLANPacket(String innerSrc, String innerDst, String outerDst) {}

    static VXLANPacket buildVXLAN(String srcPodIp, String dstPodIp, String dstNodeIp) {
        return new VXLANPacket(srcPodIp, dstPodIp, dstNodeIp);
    }

    public static void main(String[] args) {
        IPAMPool ipam = new IPAMPool();
        System.out.println(ipam.assignNodeSubnet("node-1"));
        System.out.println(ipam.assignNodeSubnet("node-2"));
        String pod1 = ipam.allocatePodIp("node-1");
        String pod2 = ipam.allocatePodIp("node-2");
        System.out.printf("Pod IPs: %s, %s%n", pod1, pod2);
        VXLANPacket pkt = buildVXLAN(pod1, pod2, "192.168.1.11");
        System.out.printf("VXLAN: %s -> %s via %s%n", pkt.innerSrc(), pkt.innerDst(), pkt.outerDst());
    }
}
```

## Complexity

| Operation | Time |
|---|---|
| Pod IP allocation | O(1) amortized |
| VXLAN encap/decap | O(1) |
| NetworkPolicy evaluation (iptables) | O(rules) |
| NetworkPolicy evaluation (Cilium eBPF) | O(1) |
| FDB lookup for VXLAN | O(1) hash table |

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

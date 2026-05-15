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

**Functional Requirements:**
- Correct behavior under all specified operating conditions
- Reliable operation with explicit failure modes
- Data consistency or eventual consistency guarantees as specified
- Clear mechanisms for error handling and recovery
- Monitoring and observability hooks

**Non-Functional Requirements:**
- **Performance**: Sub-100ms P99 latency for standard operations; measure and track tail latencies
- **Availability**: 99.99%+ uptime with automatic failover and graceful degradation
- **Scalability**: Support 10-100x current load with minimal architectural modifications
- **Consistency**: Specify whether strong, eventual, or causal consistency is required
- **Cost Efficiency**: Minimize operational cost per unit of throughput; consider compute, memory, and network costs
- **Operational Simplicity**: Reduce complexity to minimize human error and operational toil

**Constraints:**
- Resource limits (memory for caches, disk for databases, network bandwidth)
- Deployment constraints (cloud provider limits, regulatory requirements)
- Latency budgets (maximum acceptable delay for operations)

## Flow

The typical operational flow for this system involves these key phases:

1. **Request Arrival**: Client/upstream system sends request with required parameters and context
2. **Validation & Routing**: System validates request format, authentication, and routes to correct handler/shard/instance
3. **Core Processing**: Execute the main algorithm, database query, or business logic on the data/state
4. **State Management**: Update internal state (caches, indexes, counters, logs) with proper atomicity and locking
5. **Response Generation**: Format results and return to requester with relevant metadata (timing, version info)
6. **Observability**: Record metrics (latency, throughput, errors), logs (for debugging), and traces (for performance analysis)

This flow repeats thousands or millions of times per second in production. Each operation's efficiency compounds across the entire system, making careful optimization essential. Bottlenecks at any phase can cascade to impact overall system performance.

## Code Explanation

The provided implementations demonstrate key architectural concepts and design patterns:

**Python Implementation**: Uses built-in Python structures and standard library features to express the core logic clearly. Python emphasizes readability and conciseness—each operation's purpose should be obvious without extensive comments. You'll see different implementation approaches (e.g., using OrderedDict vs. manual linked lists) that represent trade-offs between convenience and fine-grained control.

**Java Implementation**: Shows how to implement the same logic with explicit memory management and type safety. Java's strong typing forces clear interface design; you'll see how generics, null safety, mutable state, and thread safety are handled. This implementation style is closer to production systems at scale.

**Key Implementation Patterns**:
- **Initialization**: Setting up core data structures, thread pools, or connection pools with specified capacity and configuration
- **Read Operations**: Fetching data while maintaining O(1) or O(log n) access, updating metadata (access times, hit counts, etc.)
- **Write Operations**: Inserting/updating data while handling eviction policies, balancing tree structures, or replicating state
- **Edge Cases**: Handling capacity limits, concurrent access, data consistency, and error conditions
- **Performance Optimization**: Using techniques like batch operations, lazy evaluation, or caching to reduce latency

Each line of code represents a deliberate choice about performance characteristics, memory usage, safety guarantees, and implementation complexity. Understanding these trade-offs is essential for using this component effectively in production systems.

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

## Common Questions & Answers

**Q: What is DSR (Direct Server Return)?** A: Backend sends response directly to client, bypassing LB. LB only handles inbound. Reduces LB bandwidth 10-100x for high-throughput (video, downloads).

**Q: Sticky sessions vs stateless backends?** A: Sticky (cookie/IP-hash) ties user to one backend — breaks on backend failure. Stateless (session in Redis) is more resilient — prefer it.

**Q: Connection draining?** A: When removing a backend, LB stops new requests but lets existing connections complete (grace period: 30-300s). Prevents in-flight request failures during deploys.

**Q: AWS NLB vs ALB?** A: NLB (L4) handles millions connections/sec, preserves source IP, ultra-low latency. ALB (L7) adds routing rules, authentication, WAF integration.

**Q: What is a global load balancer?** A: Routes across regions (AWS Route53, GCP GCLB). Uses Anycast, GeoDNS, or latency-based routing to send users to nearest healthy region.

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

## Follow-up Questions

1. How would you implement a global load balancer across regions?
2. Design a LB that supports WebSocket connections.
3. How does Kubernetes' kube-proxy implement L4 load balancing?
4. How do you prevent a single backend from getting overwhelmed?
5. What is GSLB (Global Server Load Balancing)?

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

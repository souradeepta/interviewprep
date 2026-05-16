# Bandwidth, Latency, and Network Performance Math

## Problem Statement

Master fundamental network performance metrics for system design back-of-envelope calculations and capacity planning.

## Scenario

Bandwidth, Latency, and Network Performance Math is a critical component in modern distributed systems. In real-world applications, handling complex business logic at scale with high reliability. For example, major tech companies like Netflix, Uber, and Airbnb rely on similar solutions to handle millions of concurrent users and requests. The challenge is achieving this while maintaining sub-100ms latency, 99.99% availability, and gracefully handling 10x traffic spikes during peak demand. This component provides the foundational capability to solve these challenges reliably and efficiently at global scale.

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
    Client["Client NYC"]
    Link["100 Mbps Link\nRTT=80ms\n0.1% loss"]
    Server["Server London"]

    Client -->|Request 1KB| Link
    Link -->|Response 50KB| Server
    Note1["Latency = propagation + transmission + queuing\nThroughput = min(BW, cwnd/RTT)"]
```

## Flow Diagram

```mermaid
sequenceDiagram
    participant C as Client
    participant S as Server

    Note over C,S: Total Latency Components

    C->>C: Processing delay: 0.1ms
    C->>S: Packet sent (transmission: 0.12ms for 1500B at 100Mbps)
    Note over C: Propagation: 40ms (NYC to London, 8000km fiber)
    Note over S: Queuing: 0-5ms (depends on congestion)
    Note over S: Server processing: 1ms
    S-->>C: Response (same path back)
    Note over C,S: RTT = 2 * (propagation + transmission + queuing) = ~83ms
```

## Design

### Latency Components

```
Total = Propagation + Transmission + Queuing + Processing

Propagation delay:
  Speed in fiber: ~200,000 km/s (66% speed of light)
  NYC to London (8,000km): 40ms one-way, 80ms RTT
  NYC to Tokyo (11,000km): 55ms one-way, 110ms RTT

Transmission delay:
  Time to push bits onto wire
  1500 byte packet at 1 Gbps: (1500 x 8) / 10^9 = 12 microseconds
  1500 byte packet at 10 Mbps: 1.2 milliseconds

Queuing delay:
  Packets waiting in router queue
  Minimal when lightly loaded, severe under congestion (bufferbloat)

Processing delay:
  Route lookup, checksum verification
  Modern hardware: <1 microsecond
```

### Bandwidth-Delay Product (BDP)

```
BDP = Bandwidth x RTT

Example - 1 Gbps transatlantic link (RTT=80ms):
  BDP = 1 Gbps x 80ms = 80 Mb = 10 MB

Meaning: 10MB of data can be "in flight" at once
For full utilization: TCP window must be >= 10MB
Default TCP window: 65535 bytes (64KB) -- bottleneck!
TCP window scaling (RFC 1323): up to 1GB window

Practical impact:
  64KB window at 80ms RTT: 64KB/0.08s = 6.4 Mbps effective throughput
  On a 1 Gbps link: 6.4/1000 = 0.64% utilization!
  With 10MB window: 10MB/0.08s = 1000 Mbps = full utilization
```

### TCP Throughput Formula

```
Mathis formula (with packet loss):
  Throughput = (MSS / RTT) x C / sqrt(p)
  MSS = 1460 bytes (max segment size)
  RTT = round-trip time
  p = packet loss rate
  C = constant (~1.22 for standard TCP)

At 1% loss, 80ms RTT:
  Throughput = (1460 / 0.08) x 1.22 / sqrt(0.01)
             = 18250 x 1.22 / 0.1
             = 222,650 bytes/sec = 1.78 Mbps
  (Even on a 1 Gbps link, 1% loss limits to ~1.78 Mbps)
```

### Network Performance Rules of Thumb

```
Speed of light in fiber: ~200,000 km/s
NYC to London RTT: ~80ms
NYC to SF RTT: ~70ms
Same coast US: ~20ms
Same datacenter: ~0.5ms
Same rack: ~0.1ms
Cross-rack (spine hop): ~0.5ms

Bandwidth units:
  1 Gbps = 125 MB/s
  1 TB/hour = 2.2 Gbps
  Netflix peak (2024): ~800 Gbps globally
```

## Back-of-Envelope Calculations

```
File transfer over internet:
  1 GB file, 100 Mbps link, 80ms RTT
  Pure transmission: 1GB x 8 / 100M = 80 seconds
  TCP slow start: ~1.5-2x slowdown for short flows
  Realistic: ~90-100 seconds

API latency budget (SLA: 100ms p99):
  Client to LB: 20ms (same region)
  LB to app: 5ms
  App to DB: 10ms
  DB query: 15ms
  Response path: 20ms
  Total: 70ms -> 30ms budget for processing overhead

Video streaming bandwidth:
  720p: 5 Mbps, 1080p: 8 Mbps, 4K HDR: 25 Mbps
  1M concurrent 1080p streams: 1M x 8 Mbps = 8 Tbps
  Netflix at peak: ~800 Gbps (100M users, avg 8 Mbps = most from CDN)

Data transfer cost (AWS):
  S3 to internet: $0.09/GB
  1PB/month: $90,000/month
  CDN (CloudFront): $0.01/GB after 10TB -> $10,000/month
  Savings: 89%!

TCP throughput at different loss rates:
  0.0% loss: ~950 Mbps (1 Gbps link, TCP overhead)
  0.1% loss: ~56 Mbps
  1.0% loss: ~1.8 Mbps
  5.0% loss: ~0.36 Mbps
  -> Even 0.1% loss is catastrophic on high-BW links
```

## Design Choices

| Optimization | Latency Impact | Bandwidth Impact |
|---|---|---|
| CDN / Edge caching | 10-100x improvement | Reduces origin traffic 90%+ |
| Connection pooling | Eliminates 2 RTT per request | No direct impact |
| TCP window scaling | No latency improvement | Enables full BW utilization |
| HTTP/2 multiplexing | Eliminates N x RTT | Reduces header overhead |
| Compression | No direct impact | 50-80% reduction |
| Binary protocols (gRPC) | Slight improvement | 3-10x reduction |
| QUIC/HTTP3 | -1 RTT (0-RTT) | Reduces HOL blocking impact |

## Python Implementation

```python
import math
from dataclasses import dataclass
from typing import Optional

FIBER_SPEED_KM_S = 200_000  # km/s (66% speed of light in fiber)

@dataclass
class NetworkLink:
    bandwidth_mbps: float
    distance_km: float
    packet_loss_pct: float = 0.0
    buffer_ms: float = 0.0  # Additional queuing delay

    @property
    def propagation_one_way_ms(self) -> float:
        return (self.distance_km / FIBER_SPEED_KM_S) * 1000

    @property
    def rtt_ms(self) -> float:
        return 2 * self.propagation_one_way_ms + 2 * self.buffer_ms

    def transmission_ms(self, size_bytes: int) -> float:
        return (size_bytes * 8) / (self.bandwidth_mbps * 1_000) * 1000

    def bdp_bytes(self) -> float:
        return (self.bandwidth_mbps * 1_000_000 / 8) * (self.rtt_ms / 1000)

    def tcp_throughput_mbps(self, window_bytes: int = 65535) -> float:
        tput = (window_bytes * 8) / (self.rtt_ms / 1000) / 1_000_000
        return min(self.bandwidth_mbps, tput)

    def tcp_throughput_with_loss_mbps(self) -> float:
        loss = self.packet_loss_pct / 100
        if loss <= 0:
            return self.bandwidth_mbps * 0.95
        mss = 1460
        rtt_s = self.rtt_ms / 1000
        return (mss * 8 / 1_000_000) * 1.22 / (rtt_s * math.sqrt(loss))

    def file_transfer_sec(self, size_gb: float) -> float:
        bits = size_gb * 8 * 1_000_000_000
        return bits / (self.bandwidth_mbps * 1_000_000)

class CapacityPlanner:
    def __init__(self, link: NetworkLink):
        self.link = link

    def required_bandwidth_mbps(self, req_per_sec: int, avg_size_kb: float) -> float:
        return req_per_sec * avg_size_kb * 8 / 1000

    def concurrent_streams(self, per_stream_mbps: float) -> int:
        return int(self.link.bandwidth_mbps / per_stream_mbps)

    def latency_budget_ms(self, total_budget_ms: float) -> dict:
        net_used = self.link.rtt_ms
        remaining = total_budget_ms - net_used
        return {
            "network_rtt_ms": round(net_used, 1),
            "remaining_ms": round(remaining, 1),
            "feasible": remaining > 10,  # At least 10ms for processing
        }

    def report(self) -> dict:
        return {
            "link_bandwidth_mbps": self.link.bandwidth_mbps,
            "rtt_ms": round(self.link.rtt_ms, 1),
            "bdp_mb": round(self.link.bdp_bytes() / 1_000_000, 2),
            "tcp_tput_default_window_mbps": round(self.link.tcp_throughput_mbps(), 1),
            "tcp_tput_scaled_8mb_window_mbps": round(self.link.tcp_throughput_mbps(8*1024*1024), 1),
            "tcp_tput_with_loss_mbps": round(self.link.tcp_throughput_with_loss_mbps(), 1),
            "1gb_file_transfer_sec": round(self.link.file_transfer_sec(1), 1),
        }

# Example 1: Transatlantic (NYC to London)
link = NetworkLink(bandwidth_mbps=1000, distance_km=8000, packet_loss_pct=0.1)
planner = CapacityPlanner(link)
print("=== NYC to London (1 Gbps, 0.1% loss) ===")
for k, v in planner.report().items():
    print(f"  {k}: {v}")

# Example 2: Video streaming capacity
print("\n=== Streaming Capacity ===")
cdn_link = NetworkLink(bandwidth_mbps=100_000, distance_km=100)  # 100Gbps CDN edge
cdn_planner = CapacityPlanner(cdn_link)
print(f"  4K streams (25Mbps): {cdn_planner.concurrent_streams(25):,}")
print(f"  1080p streams (8Mbps): {cdn_planner.concurrent_streams(8):,}")
print(f"  100ms budget remaining after network: {cdn_planner.latency_budget_ms(100)}")

# Example 3: API capacity planning
print("\n=== API Server BW Requirements ===")
for rps, size in [(1000, 10), (10_000, 1), (100_000, 0.1)]:
    bw = cdn_planner.required_bandwidth_mbps(rps, size)
    print(f"  {rps:,} req/sec x {size}KB = {bw:.0f} Mbps required")
```

## Java Implementation

```java
public class NetworkMath {
    static final double FIBER_KM_PER_S = 200_000.0;

    record Link(double bandwidthMbps, double distanceKm, double lossPercent) {
        double propagationMs() { return distanceKm / FIBER_KM_PER_S * 1000; }
        double rttMs() { return 2 * propagationMs(); }
        double bdpMb() { return (bandwidthMbps * 1e6 / 8) * (rttMs() / 1000) / 1e6; }

        double tcpThroughputMbps(int windowBytes) {
            return Math.min(bandwidthMbps, (windowBytes * 8.0) / (rttMs() / 1000) / 1e6);
        }

        double transferTimeSec(double sizeGb) {
            return sizeGb * 8 * 1e9 / (bandwidthMbps * 1e6);
        }

        double tcpThroughputWithLoss() {
            double loss = lossPercent / 100;
            if (loss <= 0) return bandwidthMbps;
            return (1460 * 8.0 / 1e6) * 1.22 / (rttMs() / 1000 * Math.sqrt(loss));
        }
    }

    public static void main(String[] args) {
        Link transatlantic = new Link(1000, 8000, 0.1);
        System.out.printf("RTT: %.0f ms%n", transatlantic.rttMs());
        System.out.printf("BDP: %.1f MB%n", transatlantic.bdpMb());
        System.out.printf("TCP throughput (64KB window): %.1f Mbps%n",
            transatlantic.tcpThroughputMbps(65535));
        System.out.printf("TCP throughput (8MB window): %.1f Mbps%n",
            transatlantic.tcpThroughputMbps(8 * 1024 * 1024));
        System.out.printf("TCP throughput (0.1%% loss): %.1f Mbps%n",
            transatlantic.tcpThroughputWithLoss());
        System.out.printf("1GB file transfer: %.1f seconds%n",
            transatlantic.transferTimeSec(1));
    }
}
```

## Complexity / Reference Formulas

| Formula | Use |
|---|---|
| Propagation = dist / fiber_speed | Physical minimum latency |
| Transmission = bits / bandwidth | Time to send packet |
| BDP = bandwidth x RTT | Required window size |
| Throughput = window / RTT | TCP performance limit |
| Throughput = 1.22 x MSS / (RTT x sqrt(loss)) | Loss impact formula |
| File time = size / bandwidth | Transfer estimation |

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

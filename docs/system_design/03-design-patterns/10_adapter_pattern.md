# Adapter Pattern

## Problem Statement

Convert the interface of a class into another interface clients expect. Adapter lets classes work together that couldn't otherwise because of incompatible interfaces.

**Use Cases:**
- Third-party library integration
- Legacy code integration
- Interface translation (USB-C to USB-A adapter)
- Incompatible libraries/APIs


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

## Design

### Class Diagram

```
        Client (expects Target interface)
             │
             ├─→ Adapter
                    │
                    └─→ delegates to Adaptee
```

### Key Components

```
Target: Interface client expects
Adapter: Implements Target, wraps Adaptee
Adaptee: Existing interface to adapt
Client: Uses Adapter through Target interface
```

### Adapter Implementation

```
class Adapter implements Target {
  private Adaptee adaptee;
  
  public void targetMethod() {
    // Translate to Adaptee's interface
    adaptee.adapteeMethod();
  }
}
```

## Types

```
Class Adapter: Uses inheritance (less flexible)
Object Adapter: Uses composition (more flexible) - preferred
```


## Scenario

Adapter Pattern is a critical component in modern distributed systems. In real-world applications, handling complex business logic at scale with high reliability. For example, major tech companies like Netflix, Uber, and Airbnb rely on similar solutions to handle millions of concurrent users and requests. The challenge is achieving this while maintaining sub-100ms latency, 99.99% availability, and gracefully handling 10x traffic spikes during peak demand. This component provides the foundational capability to solve these challenges reliably and efficiently at global scale.

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

## Architecture Diagram

```
┌─────────────────────────────────────────────┐
│      Client                                 │
│  (expects MediaPlayer interface)            │
│                                             │
│  + play(audioFile)                          │
│  + stop()                                   │
└────────────┬──────────────────────────────┘
             │ uses Target interface
             ▼
┌─────────────────────────────────────────────┐
│      MediaAdapter (Adapter)                 │
│  ┌──────────────────────────────────────┐   │
│  │  - vlcPlayer: VLCPlayer (Adaptee)    │   │
│  │  - mediaPlayer: MediaPlayer          │   │
│  │                                      │   │
│  │  + play(file) {                      │   │
│  │      vlcPlayer.playVLC(file)         │   │
│  │    }                                 │   │
│  └──────────────────────────────────────┘   │
│         delegates to Adaptee                │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│      VLCPlayer (Adaptee)                    │
│  (incompatible interface)                   │
│                                             │
│  + playVLC(vlcFile)                         │
│  + stopVLC()                                │
└─────────────────────────────────────────────┘
```

## Back-of-Envelope Calculations

For typical scenario (JSON to XML adapter, 100K requests/sec):
- Storage: Adapter class × 1KB code = 1KB, minimal instances
- Throughput: Adapter translation O(n) where n=data size, 100KB payload = 1-5ms
- Latency: Data transformation adds 1-5ms per request
- Bandwidth: Same data size (just format conversion)

Scaling: Adapter doesn't bottleneck if transformation is fast. Bottleneck is actual I/O to Adaptee.

## Design Choice Comparison

| Approach | Pros | Cons |
|----------|------|------|
| Object Adapter | Flexible, composition, no inheritance | Extra indirection |
| Class Adapter | Simple, direct inheritance | Breaks inheritance chain, inflexible |
| No Adapter (modify source) | Direct, simple | Breaks compatibility, invasive |

## Follow-up Interview Questions

1. How would you handle bidirectional adaptation (convert both directions)?
2. What if Adaptee interface changes? Adapter becomes brittle; how to handle versioning?
3. How to monitor adapter usage and transformation latency?
4. What's the bottleneck at 10x scale (1M requests)? Adapter transformation time, not invocation.
5. How would you implement lazy adaptation (only transform when needed)?

## Example Scenario Walkthrough

Scenario: Integrate legacy VLCPlayer into modern MediaPlayer system

Initial setup:
- Client expects: MediaPlayer interface (play, stop, pause)
- Existing code: VLCPlayer with (playVLC, stopVLC, pauseVLC)
- Incompatible interfaces

Step 1: Client requests to play file
- Client.play("movie.mp4")
- Client expects MediaPlayer interface

Step 2: Adapter intercepts call
- MediaAdapter receives play("movie.mp4")
- Adapter wraps VLCPlayer internally

Step 3: Adapter translates and delegates
- MediaAdapter.play("movie.mp4") {
-     vlcPlayer.playVLC("movie.mp4")
- }

Step 4: VLCPlayer executes actual work
- Loads VLC codec
- Plays movie.mp4
- Client gets expected behavior

Step 5: Client requests to stop
- Client.stop()
- MediaAdapter.stop() {
-     vlcPlayer.stopVLC()
- }

Step 6: Integration complete
- Client code unchanged (works with MediaPlayer interface)
- VLCPlayer integrated seamlessly
- No modification to VLCPlayer source code
- Adapter handles interface translation

## Trade-offs

| Pro | Con |
|-----|-----|
| Makes incompatible work | Extra indirection |
| Single Responsibility | May require multiple adapters |
| Open/Closed principle | Complexity |
| Reuses existing code | Don't overuse |

### Architecture Diagram

```mermaid
graph LR
    Client["Client"]
    Target["Target Interface"]
    Adapter["Adapter<br/>implements Target"]
    Adaptee["Adaptee<br/>incompatible"]

    Client -->|uses| Target
    Adapter -->|implements| Target
    Adapter -->|wraps| Adaptee
```

### Flow Diagram

```mermaid
sequenceDiagram
    participant C as Client
    participant A as Adapter
    participant E as Adaptee

    C->>A: request()
    A->>A: translate format
    A->>E: specificRequest()
    E-->>A: response
    A->>A: translate format
    A-->>C: response
```

## Complexity

| Operation | Time |
|-----------|------|
| adapt | O(1) |
| delegate | O(1) |

## Python Implementation

```python
class EuropeanSocket:
    def voltage(self) -> int: return 220
    def live(self) -> int: return 1
    def neutral(self) -> int: return -1

class USASocket:
    def voltage(self) -> int: return 110
    def live(self) -> int: return 1
    def neutral(self) -> int: return -1

class EuropeanToUSAAdapter:
    def __init__(self, socket: EuropeanSocket):
        self._socket = socket

    def voltage(self) -> int:
        return 110  # Convert 220V to 110V

    def live(self) -> int: return self._socket.live()
    def neutral(self) -> int: return self._socket.neutral()

class AmericanDevice:
    def charge(self, socket: USASocket):
        if socket.voltage() == 110:
            print(f"Charging at {socket.voltage()}V")
        else:
            raise ValueError("Incompatible voltage")

# Usage
eu_socket = EuropeanSocket()
adapter = EuropeanToUSAAdapter(eu_socket)
device = AmericanDevice()
device.charge(adapter)  # Charging at 110V
```

## Java Implementation

```java
public interface USSocket {
    int voltage();
    int live();
    int neutral();
}

public class EuropeanSocket {
    public int voltage() { return 220; }
    public int live() { return 1; }
    public int neutral() { return -1; }
}

public class EuropeanToUSAdapter implements USSocket {
    private EuropeanSocket socket;
    public EuropeanToUSAdapter(EuropeanSocket socket) { this.socket = socket; }
    public int voltage() { return 110; }
    public int live() { return socket.live(); }
    public int neutral() { return socket.neutral(); }
}

// Usage
EuropeanSocket eu = new EuropeanSocket();
USSocket adapter = new EuropeanToUSAdapter(eu);
System.out.println("Voltage: " + adapter.voltage()); // 110
```

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


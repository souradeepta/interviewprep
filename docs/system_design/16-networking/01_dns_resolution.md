# DNS Resolution

## Problem Statement

Design the Domain Name System (DNS) — a distributed hierarchical system that translates human-readable domain names (e.g., `www.example.com`) into IP addresses.

**Requirements:**
- Fast lookups (< 10ms for cached, < 100ms for recursive)
- Highly available (no single point of failure)
- Globally distributed
- Support millions of domains and billions of queries/day

## Scenario

DNS Resolution is a critical component in modern distributed systems. In real-world applications, translating domain names to IP addresses globally. For example, major tech companies like Netflix, Uber, and Airbnb rely on similar solutions to handle millions of concurrent users and requests. The challenge is achieving this while maintaining sub-100ms latency, 99.99% availability, and gracefully handling 10x traffic spikes during peak demand. This component provides the foundational capability to solve these challenges reliably and efficiently at global scale.

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
    Client[Client Browser]
    Cache[Local DNS Cache]
    Resolver[Recursive Resolver ISP]
    Root[Root Name Server]
    TLD[TLD Server .com]
    Auth[Authoritative Server example.com]

    Client -->|1 Query| Cache
    Cache -->|2 Miss| Resolver
    Resolver -->|3 Who handles .com?| Root
    Root -->|4 TLD Server IP| Resolver
    Resolver -->|5 Who handles example.com?| TLD
    TLD -->|6 Auth Server IP| Resolver
    Resolver -->|7 What is www.example.com?| Auth
    Auth -->|8 93.184.216.34| Resolver
    Resolver -->|9 Cache + Return| Cache
    Cache -->|10 Return IP| Client
```

## Flow Diagram

```mermaid
sequenceDiagram
    participant C as Client
    participant LC as Local Cache
    participant RR as Recursive Resolver
    participant Root as Root Server
    participant TLD as TLD (.com)
    participant Auth as Authoritative NS

    C->>LC: Lookup www.example.com
    alt Cache Hit
        LC-->>C: Return cached IP (TTL valid)
    else Cache Miss
        LC->>RR: Forward query
        RR->>Root: Query root
        Root-->>RR: .com TLD NS: 192.5.6.30
        RR->>TLD: Query .com TLD
        TLD-->>RR: example.com NS: 205.251.196.1
        RR->>Auth: Query example.com NS
        Auth-->>RR: www → 93.184.216.34, TTL=300
        RR-->>LC: Cache result
        LC-->>C: Return 93.184.216.34
    end
```

## Design

### DNS Record Types

```
A      → IPv4 address         (www.example.com → 1.2.3.4)
AAAA   → IPv6 address         (www.example.com → ::1)
CNAME  → Canonical alias      (blog.example.com → example.com)
MX     → Mail server          (example.com → mail.example.com)
TXT    → Text/verification    (SPF, DKIM records)
NS     → Name server          (who handles this domain)
SOA    → Zone authority info  (primary NS, serial, TTL)
```

### Caching Hierarchy

```
Browser cache (5-300s TTL)
  → OS cache (/etc/hosts, nscd)
    → Resolver cache (ISP/corporate)
      → Recursive resolver (Google 8.8.8.8, Cloudflare 1.1.1.1)
        → Root servers (13 clusters, anycast)
          → TLD servers (.com, .org, .net)
            → Authoritative servers (origin of truth)
```

### DNS Resolution Modes

| Mode | Description | RTT |
|------|-------------|-----|
| Recursive | Resolver does all the work | 1 RTT to client |
| Iterative | Client contacts each server | Multiple RTTs |
| Caching | Return cached answer | < 1ms |

## Back-of-Envelope Calculations

```
Google handles ~1 trillion DNS queries/day:
  1T / 86400s ≈ 11.6M queries/sec

Cache hit rate ~85%:
  Miss rate: 11.6M × 0.15 = 1.7M recursive lookups/sec

Average DNS response size: 100 bytes
Bandwidth: 11.6M × 100B = 1.16 GB/s

Root server queries (small % since resolvers cache TLD answers):
  ~1.7M × 0.001 = 1,700 root queries/sec per 13-cluster root

Recursive resolution latency:
  Root RTT: 20ms + TLD: 40ms + Auth: 30ms = ~90ms total
  Cached: <1ms
```

## Design Choices

| Approach | Pros | Cons |
|---|---|---|
| Anycast routing | Geographically close server, DDoS resilience | Harder to debug routing |
| High TTL (3600s) | Less DNS traffic, faster | Slow propagation of changes |
| Low TTL (60s) | Fast failover | More DNS load |
| Round-robin DNS | Simple LB | No health checks, stale |
| GeoDNS | Route to nearest DC | Complex setup |

## Python Implementation

```python
from typing import Dict, Optional, Tuple
import time

class DNSRecord:
    def __init__(self, record_type: str, value: str, ttl: int):
        self.record_type = record_type
        self.value = value
        self.ttl = ttl
        self.created_at = time.time()

    def is_expired(self) -> bool:
        return time.time() - self.created_at > self.ttl

class DNSCache:
    def __init__(self):
        self._cache: Dict[Tuple[str, str], DNSRecord] = {}

    def get(self, domain: str, record_type: str = "A") -> Optional[str]:
        key = (domain, record_type)
        record = self._cache.get(key)
        if record and not record.is_expired():
            return record.value
        if record:
            del self._cache[key]
        return None

    def set(self, domain: str, record_type: str, value: str, ttl: int):
        self._cache[(domain, record_type)] = DNSRecord(record_type, value, ttl)

class DNSResolver:
    def __init__(self):
        self._cache = DNSCache()
        self._zone: Dict[str, Dict[str, str]] = {
            "example.com": {"A": "93.184.216.34", "MX": "mail.example.com"},
            "www.example.com": {"A": "93.184.216.34", "CNAME": "example.com"},
            "mail.example.com": {"A": "93.184.216.100"},
        }

    def resolve(self, domain: str, record_type: str = "A") -> Optional[str]:
        cached = self._cache.get(domain, record_type)
        if cached:
            print(f"[CACHE HIT] {domain} → {cached}")
            return cached

        result = self._recursive_resolve(domain, record_type)
        if result:
            self._cache.set(domain, record_type, result, ttl=300)
        return result

    def _recursive_resolve(self, domain: str, record_type: str) -> Optional[str]:
        zone = self._zone.get(domain, {})
        if record_type in zone:
            return zone[record_type]
        if "CNAME" in zone:
            return self._recursive_resolve(zone["CNAME"], record_type)
        return None

# Usage
resolver = DNSResolver()
print(resolver.resolve("www.example.com"))       # 93.184.216.34
print(resolver.resolve("www.example.com"))       # [CACHE HIT] 93.184.216.34
print(resolver.resolve("example.com", "MX"))     # mail.example.com
```

## Java Implementation

```java
import java.util.*;

public class DNSResolver {
    record DNSRecord(String type, String value, int ttl, long createdAt) {
        boolean isExpired() { return (System.currentTimeMillis() / 1000 - createdAt) > ttl; }
    }

    private Map<String, DNSRecord> cache = new HashMap<>();
    private Map<String, Map<String, String>> zone = Map.of(
        "example.com", Map.of("A", "93.184.216.34", "MX", "mail.example.com"),
        "www.example.com", Map.of("A", "93.184.216.34")
    );

    public Optional<String> resolve(String domain, String type) {
        String key = domain + ":" + type;
        DNSRecord cached = cache.get(key);
        if (cached != null && !cached.isExpired()) {
            System.out.println("[CACHE HIT] " + domain);
            return Optional.of(cached.value());
        }
        return zone.getOrDefault(domain, Map.of()).entrySet().stream()
            .filter(e -> e.getKey().equals(type))
            .map(e -> {
                cache.put(key, new DNSRecord(type, e.getValue(), 300, System.currentTimeMillis() / 1000));
                return e.getValue();
            }).findFirst();
    }
}
```

## Complexity

| Operation | Time | Notes |
|---|---|---|
| Cache lookup | O(1) | Hash map |
| Recursive resolve | O(depth) | Typically 3 hops |
| Zone transfer | O(n) | n = number of records |
| Space | O(n) | Cached records |

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


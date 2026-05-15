# NAT and IP Routing

## Problem Statement

Understand how NAT (Network Address Translation) enables private IP networks to reach the internet, and how IP routing directs packets across networks.

## Scenario

NAT and IP Routing is a critical component in modern distributed systems. In real-world applications, handling complex business logic at scale with high reliability. For example, major tech companies like Netflix, Uber, and Airbnb rely on similar solutions to handle millions of concurrent users and requests. The challenge is achieving this while maintaining sub-100ms latency, 99.99% availability, and gracefully handling 10x traffic spikes during peak demand. This component provides the foundational capability to solve these challenges reliably and efficiently at global scale.

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
graph LR
    PC1["PC1 192.168.1.10"]
    PC2["PC2 192.168.1.11"]
    NAT["NAT Router\nPrivate: 192.168.1.1\nPublic: 203.0.113.5"]
    ISP[ISP Router]
    Server["Server 93.184.216.34"]

    PC1 -->|Private src IP| NAT
    PC2 -->|Private src IP| NAT
    NAT -->|Rewrites src to public IP| ISP
    ISP --> Server
```

## Flow Diagram

```mermaid
sequenceDiagram
    participant PC as PC 192.168.1.10:5000
    participant NAT as NAT Router
    participant S as Server 93.184.216.34:80

    PC->>NAT: SYN src=192.168.1.10:5000 dst=93.184.216.34:80
    NAT->>NAT: Add NAT entry: 192.168.1.10:5000 <-> 203.0.113.5:40001
    NAT->>S: SYN src=203.0.113.5:40001 dst=93.184.216.34:80
    S-->>NAT: SYN-ACK dst=203.0.113.5:40001
    NAT->>NAT: Lookup reverse: 203.0.113.5:40001 -> 192.168.1.10:5000
    NAT-->>PC: SYN-ACK dst=192.168.1.10:5000
    Note over PC,S: Data flows with NAT transparently rewriting addresses
```

## Design

### NAT Translation Table

```
Private IP:Port          Public IP:Port          Protocol  TTL
192.168.1.10:5000   ->  203.0.113.5:40001       TCP       300s
192.168.1.11:6000   ->  203.0.113.5:40002       TCP       300s
192.168.1.10:5001   ->  203.0.113.5:40003       UDP       30s
```

### IP Routing - Longest Prefix Match

```
Routing table entries (sorted by prefix length):
  0.0.0.0/0      -> gateway (default, lowest priority)
  10.0.0.0/8     -> eth1
  10.0.1.0/24    -> eth2   (more specific, wins for 10.0.1.x)
  192.168.0.0/16 -> eth3

Lookup for 10.0.1.5:
  Check /24: 10.0.1.0/24 matches -> route via eth2 (WINNER)
  (Does not use /8 even though it also matches)
```

### Private IP Ranges (RFC 1918)

```
10.0.0.0/8      -> 16.7M addresses (large orgs)
172.16.0.0/12   -> 1M addresses   (medium orgs)
192.168.0.0/16  -> 65K addresses  (home/small office)
127.0.0.0/8     -> Loopback (localhost)
169.254.0.0/16  -> Link-local (APIPA, no DHCP)
```

## Back-of-Envelope Calculations

```
IPv4 exhaustion math:
  Total: 2^32 = 4.29B addresses
  Reserved: ~592M (private, loopback, multicast, reserved)
  Usable public: ~3.7B
  Active internet devices: 15B+ -> NAT essential

NAT port capacity:
  Ports per public IP: 65,535 (minus reserved 0-1023 = 64,512)
  Average TCP connection duration: 60s
  Connections/sec per IP: 64,512/60 = 1,075/sec
  CGNAT with 100 users/IP: 10 connections/sec/user

Subnet planning example:
  New office: 200 employees + IoT + servers
  Needed: ~400 IPs (2x buffer)
  Use /23 = 512 IPs (255.255.254.0 mask)

BGP routing table:
  2024 full table: ~950K routes
  Memory per route: ~200 bytes
  Total per router: 950K x 200B = 190MB (manageable)
```

## Design Choices

| Approach | Pros | Cons |
|---|---|---|
| NAT44 (IPv4-IPv4) | Extends IPv4, security boundary | Breaks P2P, complex logging |
| IPv6 native | Unlimited addresses, no NAT | Legacy IPv4 compatibility |
| Dual stack (IPv4+IPv6) | Full compatibility | Operational complexity |
| CGNAT | Extends IPv4 life | Port exhaustion, no inbound |

## Python Implementation

```python
from dataclasses import dataclass
from typing import Dict, Optional, Tuple
import hashlib

@dataclass
class NATEntry:
    private_ip: str
    private_port: int
    public_ip: str
    public_port: int

class NATRouter:
    def __init__(self, public_ip: str):
        self.public_ip = public_ip
        self._table: Dict[Tuple[str, int], NATEntry] = {}
        self._reverse: Dict[Tuple[str, int], NATEntry] = {}
        self._next_port = 40000

    def outbound(self, src_ip: str, src_port: int) -> Tuple[str, int]:
        key = (src_ip, src_port)
        if key not in self._table:
            pub_port = self._next_port
            self._next_port += 1
            entry = NATEntry(src_ip, src_port, self.public_ip, pub_port)
            self._table[key] = entry
            self._reverse[(self.public_ip, pub_port)] = entry
            print(f"[NAT] New mapping: {src_ip}:{src_port} -> {self.public_ip}:{pub_port}")
        e = self._table[key]
        return e.public_ip, e.public_port

    def inbound(self, dst_ip: str, dst_port: int) -> Optional[Tuple[str, int]]:
        entry = self._reverse.get((dst_ip, dst_port))
        return (entry.private_ip, entry.private_port) if entry else None

class IPRouter:
    def __init__(self):
        self._routes: list = []  # (network_int, mask_int, prefix_len, next_hop)

    def add_route(self, network: str, prefix_len: int, next_hop: str):
        net_int = self._to_int(network)
        mask = (0xFFFFFFFF << (32 - prefix_len)) & 0xFFFFFFFF
        self._routes.append((net_int, mask, prefix_len, next_hop))
        self._routes.sort(key=lambda r: -r[2])  # Longest prefix first

    def lookup(self, dst: str) -> Optional[str]:
        dst_int = self._to_int(dst)
        for net, mask, prefix, hop in self._routes:
            if dst_int & mask == net & mask:
                return hop
        return None

    def _to_int(self, ip: str) -> int:
        parts = ip.split(".")
        return sum(int(p) << (24 - 8*i) for i, p in enumerate(parts))

# Usage
nat = NATRouter("203.0.113.5")
pub_ip, pub_port = nat.outbound("192.168.1.10", 5000)
print(f"Outbound: {pub_ip}:{pub_port}")
priv = nat.inbound(pub_ip, pub_port)
print(f"Inbound reverse: {priv[0]}:{priv[1]}")

router = IPRouter()
router.add_route("0.0.0.0", 0, "default-gateway")
router.add_route("10.0.0.0", 8, "eth1")
router.add_route("10.0.1.0", 24, "eth2")  # More specific

print(router.lookup("10.0.1.5"))   # eth2 (longest prefix match)
print(router.lookup("10.0.2.5"))   # eth1
print(router.lookup("8.8.8.8"))    # default-gateway
```

## Java Implementation

```java
import java.util.*;

public class IPRouter {
    record Route(long net, long mask, int prefix, String hop) {}

    private List<Route> routes = new ArrayList<>();

    public void addRoute(String network, int prefix, String nextHop) {
        long mask = prefix == 0 ? 0 : (-1L << (32 - prefix)) & 0xFFFFFFFFL;
        routes.add(new Route(ipToLong(network), mask, prefix, nextHop));
        routes.sort((a, b) -> b.prefix() - a.prefix());
    }

    public Optional<String> lookup(String dst) {
        long d = ipToLong(dst);
        return routes.stream()
            .filter(r -> (d & r.mask()) == (r.net() & r.mask()))
            .map(Route::hop)
            .findFirst();
    }

    private long ipToLong(String ip) {
        String[] p = ip.split("\\.");
        return (Long.parseLong(p[0]) << 24) | (Long.parseLong(p[1]) << 16)
             | (Long.parseLong(p[2]) << 8)  |  Long.parseLong(p[3]);
    }

    public static void main(String[] args) {
        IPRouter r = new IPRouter();
        r.addRoute("0.0.0.0", 0, "gateway");
        r.addRoute("10.0.0.0", 8, "eth1");
        r.addRoute("10.0.1.0", 24, "eth2");
        System.out.println(r.lookup("10.0.1.5"));  // eth2
        System.out.println(r.lookup("10.0.2.5"));  // eth1
        System.out.println(r.lookup("8.8.8.8"));   // gateway
    }
}
```

## Complexity

| Operation | Time |
|---|---|
| NAT lookup | O(1) hash map |
| NAT reverse lookup | O(1) hash map |
| LPM route lookup | O(routes) linear scan |
| Hardware TCAM lookup | O(1) |

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


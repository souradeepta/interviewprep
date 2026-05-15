# Distributed Cache Design

## Problem Statement

Design a distributed cache that scales horizontally, handles node failures gracefully, minimizes hotspot issues, and maintains consistency across cache nodes — covering consistent hashing, replication strategies, and cache coherence.

## Scenario

Distributed Cache Design is a critical component in modern distributed systems. In real-world applications, serving billions of user interactions with minimal latency. For example, major tech companies like Netflix, Uber, and Airbnb rely on similar solutions to handle millions of concurrent users and requests. The challenge is achieving this while maintaining sub-100ms latency, 99.99% availability, and gracefully handling 10x traffic spikes during peak demand. This component provides the foundational capability to solve these challenges reliably and efficiently at global scale.

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
    subgraph Clients["Client Layer"]
        C1["App Server 1"]
        C2["App Server 2"]
        C3["App Server 3"]
    end

    subgraph Router["Smart Client / Proxy"]
        CH["Consistent Hash Ring\n+ Virtual Nodes"]
        PROXY["Twemproxy / mcrouter\nor Redis Cluster"]
    end

    subgraph CacheLayer["Cache Cluster"]
        subgraph Shard1["Shard A"]
            A_M["Primary"]
            A_R["Replica"]
        end
        subgraph Shard2["Shard B"]
            B_M["Primary"]
            B_R["Replica"]
        end
        subgraph Shard3["Shard C"]
            C_M["Primary"]
            C_R["Replica"]
        end
    end

    DB["Database"]

    C1 & C2 & C3 --> Router
    Router --> Shard1 & Shard2 & Shard3
    Shard1 & Shard2 & Shard3 --> DB
```

## Flow Diagram

```mermaid
sequenceDiagram
    participant C as Client
    participant H as Hash Router
    participant P as Cache Primary
    participant R as Cache Replica
    participant D as Database

    C->>H: GET user:1234
    H->>H: hash("user:1234") -> node B
    H->>P: GET user:1234
    P-->>H: MISS
    H->>D: SELECT * FROM users WHERE id=1234
    D-->>H: {id:1234, name:Alice}
    H->>P: SET user:1234 {data} EX 3600
    P->>R: async replicate
    H-->>C: {id:1234, name:Alice}

    Note over C,R: Read scaling: reads from replica
    C->>H: GET user:1234 (read replica)
    H->>R: GET user:1234
    R-->>H: HIT: {id:1234, name:Alice}
    H-->>C: {id:1234, name:Alice}
```

## Design

### Consistent Hashing

```
Problem with simple modular hashing:
  node = hash(key) % N
  Add/remove node: ~100% keys remap -> cold cache

Consistent hashing:
  Ring: 0 to 2^32-1
  Nodes placed at hash(node_id) positions
  Key assigned to next clockwise node
  Add/remove: only keys between two adjacent nodes remap
  Average remapped: 1/N of total keys

Virtual nodes (vnodes):
  Physical node has 150-200 virtual positions
  Prevents hotspots when nodes have different capacities
  Smoother distribution even with few physical nodes

Hash ring with virtual nodes:
  Node A (32GB): 200 vnodes
  Node B (16GB): 100 vnodes (half the capacity)
  Node C (32GB): 200 vnodes
  Keys distributed proportionally
```

### Replication Strategies

```
1. Leader-Follower (Primary-Replica):
   Writes -> primary only
   Reads -> primary or replica (replica lag acceptable)
   Failover: replica promoted on primary failure
   
   Redis Sentinel / Redis Cluster approach

2. Leaderless (Dynamo-style):
   Writes -> any N nodes (quorum write)
   Reads -> any R nodes (quorum read)
   W + R > N: strong consistency
   W=1, R=1: maximum availability, possible stale reads
   
   W=2, R=2, N=3: one node can fail without data loss or stale reads

3. Write-through replication:
   Write succeeds only when all replicas ACK
   Strong consistency, higher write latency
   
4. Write-behind replication:
   Async propagation (fire-and-forget)
   Lower write latency, possible replication lag

Cache-specific strategy:
  Async replication usually sufficient (cache is not source of truth)
  Strong consistency only needed when cache + DB consistency critical
```

### Hotspot Prevention

```
Problem: "celebrity key" - one key gets 100K req/s
  e.g., viral post, game leaderboard, stock price
  
Solutions:

1. Local in-process cache (L1):
   Small LRU in each app server (1-5% of keys)
   Hot keys cached locally, never hit Redis
   TTL: very short (1-5s) for freshness
   
   app_cache = LRUCache(1000)  # 1000 hot keys

2. Key replication with suffix:
   popular_key -> N copies: key:0, key:1, ..., key:N-1
   Read: key:random(N) (round-robin read)
   Write: write all N copies (or async propagation)
   
   def get_hot_key(key, N=10):
       return cache.get(f"{key}:{random.randint(0, N-1)}")

3. Request coalescing (singleflight):
   Multiple requests for same missing key -> one DB query
   Others wait and share the result
   
4. Jitter on TTL:
   Instead of TTL=3600, use TTL=3600 + random(-60, 60)
   Prevents thundering herd at simultaneous expiry

5. Probabilistic early refresh:
   T = original TTL, t = remaining TTL
   Refresh with probability P(t) = e^(-beta * t)
   As key approaches expiry, refresh probability increases
   One request triggers refresh before expiry
```

### Cache Coherence

```
Invalidation patterns:

1. TTL-based (simplest):
   Data inconsistent for at most TTL duration
   No explicit invalidation needed
   Use when stale tolerance acceptable

2. Write-invalidate:
   On DB update: DEL cache key
   Next read: miss -> re-populate from DB
   Risk: thundering herd

3. Write-update:
   On DB update: SET cache key (with new value)
   No miss window, but race condition risk
   Two concurrent writes -> cache = older value

4. Event-driven invalidation:
   DB change event (CDC/Debezium) -> Kafka -> cache invalidator
   Subscribe to DB changes, invalidate affected keys
   Eventually consistent, no direct DB-cache coupling

5. Tagged invalidation:
   Group keys by tag: {tag:user:1234} -> [profile, sessions, orders]
   On user update: invalidate all tagged keys
   Redis: use Sets to track tags per key

Cache-aside vs write-through coherence:
  Cache-aside: invalidate after DB write (DEL key)
  Write-through: update cache atomically with DB write
  Both: eventual consistency possible in race conditions
```

## Back-of-Envelope Calculations

```
Cluster sizing:
  10M active users, 500B cache per user session
  Total data: 5GB
  With 3x replication: 15GB cache needed
  3 nodes x 8GB Redis = 24GB (with headroom)

Hit rate improvement with read replicas:
  100K req/s, 1 primary handles 80K (80% hits)
  Add 2 replicas: reads distributed 3-way
  Primary: ~27K req/s, each replica: ~27K req/s
  Primary write pressure reduced 3x

Consistent hashing remapping:
  100 nodes, 10M keys
  Remove 1 node: ~100K keys remapped (1%)
  Vs modular hashing: 10M keys remapped (100%)

Hotspot math:
  1 viral post: 500K req/s
  Single Redis node max: ~100K req/s -> saturated
  With 10 key replicas: each node handles 50K req/s (OK)
  With L1 local cache (100 app servers): 5K req/s each -> trivial

Replication lag impact:
  Async replication: <1ms intra-DC
  Acceptable for: session cache, product catalog
  Not acceptable for: payment status, inventory count
```

## Design Choices

| Strategy | Consistency | Availability | Complexity |
|---|---|---|---|
| Single node | Strong | Low (SPOF) | Minimal |
| Primary-replica | Eventual (reads) | High (replica serves) | Low |
| Quorum (W+R>N) | Strong | Medium | Medium |
| Leaderless | Tunable | High | High |
| L1+L2 (local+Redis) | Eventual | Very high | Medium |
| CDN + Redis | Eventual | Highest | High |

## Python Implementation

```python
import hashlib
import time
import random
import threading
from typing import Any, Dict, List, Optional, Tuple
from collections import OrderedDict

class CacheNode:
    def __init__(self, node_id: str, capacity: int = 1000):
        self.node_id = node_id
        self._store: Dict[str, Tuple[Any, float]] = {}
        self._capacity = capacity
        self._hits = 0
        self._misses = 0
        self.alive = True

    def get(self, key: str) -> Optional[Any]:
        entry = self._store.get(key)
        if entry is None:
            self._misses += 1
            return None
        value, expires_at = entry
        if expires_at and time.time() > expires_at:
            del self._store[key]
            self._misses += 1
            return None
        self._hits += 1
        return value

    def set(self, key: str, value: Any, ttl: int = 0) -> bool:
        if len(self._store) >= self._capacity and key not in self._store:
            return False
        expires_at = time.time() + ttl if ttl else 0
        self._store[key] = (value, expires_at)
        return True

    def delete(self, key: str) -> bool:
        return self._store.pop(key, None) is not None

    def stats(self) -> dict:
        total = self._hits + self._misses
        return {
            "node": self.node_id,
            "keys": len(self._store),
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": f"{self._hits / max(1, total) * 100:.1f}%",
        }

class ConsistentHashRing:
    def __init__(self, virtual_nodes: int = 150):
        self._ring: List[Tuple[int, str]] = []
        self._nodes: Dict[str, CacheNode] = {}
        self._vnodes = virtual_nodes

    def add_node(self, node: CacheNode):
        self._nodes[node.node_id] = node
        for i in range(self._vnodes):
            h = int(hashlib.md5(f"{node.node_id}:{i}".encode()).hexdigest(), 16)
            self._ring.append((h, node.node_id))
        self._ring.sort()

    def remove_node(self, node_id: str) -> List[str]:
        if node_id not in self._nodes:
            return []
        affected_keys = list(self._nodes[node_id]._store.keys())
        self._ring = [(h, n) for h, n in self._ring if n != node_id]
        del self._nodes[node_id]
        return affected_keys

    def get_node(self, key: str) -> Optional[CacheNode]:
        if not self._ring:
            return None
        h = int(hashlib.md5(key.encode()).hexdigest(), 16)
        for ring_hash, node_id in self._ring:
            if h <= ring_hash:
                node = self._nodes.get(node_id)
                if node and node.alive:
                    return node
        return self._nodes.get(self._ring[0][1])

    def get_n_nodes(self, key: str, n: int) -> List[CacheNode]:
        if not self._ring:
            return []
        h = int(hashlib.md5(key.encode()).hexdigest(), 16)
        seen = set()
        result = []
        start = next((i for i, (rh, _) in enumerate(self._ring) if rh >= h), 0)
        for offset in range(len(self._ring)):
            idx = (start + offset) % len(self._ring)
            _, node_id = self._ring[idx]
            if node_id not in seen and node_id in self._nodes and self._nodes[node_id].alive:
                seen.add(node_id)
                result.append(self._nodes[node_id])
                if len(result) == n:
                    break
        return result

class L1L2Cache:
    def __init__(self, ring: ConsistentHashRing, l1_size: int = 100,
                 l1_ttl: int = 5, hot_threshold: int = 10):
        self._ring = ring
        self._l1: OrderedDict = OrderedDict()
        self._l1_size = l1_size
        self._l1_ttl = l1_ttl
        self._l1_expires: Dict[str, float] = {}
        self._access_count: Dict[str, int] = {}
        self._hot_threshold = hot_threshold
        self._l1_hits = 0
        self._l2_hits = 0
        self._misses = 0

    def _l1_get(self, key: str) -> Optional[Any]:
        if key not in self._l1:
            return None
        if time.time() > self._l1_expires.get(key, 0):
            self._l1.pop(key, None)
            return None
        self._l1.move_to_end(key)
        return self._l1[key]

    def _l1_set(self, key: str, value: Any):
        if len(self._l1) >= self._l1_size:
            self._l1.popitem(last=False)
        self._l1[key] = value
        self._l1_expires[key] = time.time() + self._l1_ttl

    def get(self, key: str) -> Optional[Any]:
        # L1 check
        val = self._l1_get(key)
        if val is not None:
            self._l1_hits += 1
            return val
        # L2 check
        node = self._ring.get_node(key)
        if node:
            val = node.get(key)
            if val is not None:
                self._l2_hits += 1
                self._access_count[key] = self._access_count.get(key, 0) + 1
                if self._access_count[key] >= self._hot_threshold:
                    self._l1_set(key, val)
                return val
        self._misses += 1
        return None

    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        nodes = self._ring.get_n_nodes(key, 2)
        success = any(n.set(key, value, ttl) for n in nodes)
        if key in self._l1:
            self._l1_set(key, value)
        return success

    def invalidate(self, key: str):
        self._l1.pop(key, None)
        node = self._ring.get_node(key)
        if node:
            node.delete(key)

    def stats(self) -> dict:
        total = self._l1_hits + self._l2_hits + self._misses
        return {
            "l1_hits": self._l1_hits, "l2_hits": self._l2_hits,
            "misses": self._misses,
            "l1_hit_rate": f"{self._l1_hits / max(1, total) * 100:.1f}%",
        }

# Demo
print("=== Distributed Cache Demo ===\n")

ring = ConsistentHashRing(virtual_nodes=50)
nodes = [CacheNode(f"node-{i}", capacity=500) for i in range(3)]
for n in nodes:
    ring.add_node(n)

# Show distribution
key_distribution: Dict[str, int] = {}
for i in range(300):
    key = f"key:{i}"
    node = ring.get_node(key)
    if node:
        key_distribution[node.node_id] = key_distribution.get(node.node_id, 0) + 1

print("Key distribution across nodes:")
for node_id, count in sorted(key_distribution.items()):
    print(f"  {node_id}: {count} keys ({count/300*100:.1f}%)")

# L1+L2 cache with hot key detection
cache = L1L2Cache(ring, l1_size=50, l1_ttl=5, hot_threshold=5)

# Populate
for i in range(50):
    cache.set(f"user:{i}", {"id": i, "name": f"User{i}"}, ttl=3600)

# Simulate hot key access
print("\nSimulating hot key access for 'user:1':")
for _ in range(10):
    cache.get("user:1")

print(f"  In L1 cache after 10 hits: {'user:1' in cache._l1}")
print(f"  Cache stats: {cache.stats()}")

# Node failure + rebalancing
print("\n=== Node Failure Simulation ===")
failed_node = "node-1"
nodes[1].alive = False
affected = ring.remove_node(failed_node)
print(f"Node {failed_node} removed. {len(affected)} keys need rebalancing")

# Keys still readable from L2 (other nodes) if replicated
for key in affected[:3]:
    val = cache.get(key)
    print(f"  {key}: {'recovered' if val is not None else 'lost'}")
```

## Java Implementation

```java
import java.util.*;
import java.security.MessageDigest;

public class DistributedCache {
    static class Node {
        String id;
        Map<String, Object> store = new HashMap<>();
        boolean alive = true;

        Node(String id) { this.id = id; }

        void set(String k, Object v) { store.put(k, v); }
        Object get(String k) { return store.get(k); }
        boolean del(String k) { return store.remove(k) != null; }
    }

    static class ConsistentHashRing {
        TreeMap<Long, Node> ring = new TreeMap<>();
        Map<String, Node> nodes = new HashMap<>();

        void addNode(Node n, int vnodes) {
            nodes.put(n.id, n);
            for (int i = 0; i < vnodes; i++) {
                long h = hash(n.id + ":" + i);
                ring.put(h, n);
            }
        }

        Node getNode(String key) {
            if (ring.isEmpty()) return null;
            long h = hash(key);
            Map.Entry<Long, Node> entry = ring.ceilingEntry(h);
            if (entry == null) entry = ring.firstEntry();
            Node n = entry.getValue();
            return n.alive ? n : ring.values().stream().filter(x -> x.alive).findFirst().orElse(null);
        }

        long hash(String s) {
            try {
                MessageDigest md = MessageDigest.getInstance("MD5");
                byte[] b = md.digest(s.getBytes());
                long h = 0;
                for (int i = 0; i < 8; i++) h = (h << 8) | (b[i] & 0xFF);
                return h & Long.MAX_VALUE;
            } catch (Exception e) { return s.hashCode() & Long.MAX_VALUE; }
        }

        void set(String key, Object value) {
            Node n = getNode(key);
            if (n != null) n.set(key, value);
        }

        Object get(String key) {
            Node n = getNode(key);
            return n != null ? n.get(key) : null;
        }
    }

    public static void main(String[] args) {
        ConsistentHashRing ring = new ConsistentHashRing();
        for (int i = 0; i < 3; i++) ring.addNode(new Node("node-" + i), 100);

        // Populate and show distribution
        Map<String, Integer> dist = new HashMap<>();
        for (int i = 0; i < 300; i++) {
            String key = "key:" + i;
            Node n = ring.getNode(key);
            if (n != null) dist.merge(n.id, 1, Integer::sum);
            ring.set(key, "value-" + i);
        }
        System.out.println("Distribution: " + dist);

        // Read-write
        ring.set("user:1", Map.of("name", "Alice"));
        System.out.println("user:1 = " + ring.get("user:1"));

        // Simulate node failure
        ring.nodes.get("node-1").alive = false;
        System.out.println("After node-1 failure, user:1 = " + ring.get("user:1"));
    }
}
```

## Complexity

| Operation | Consistent Hash | Modular Hash |
|---|---|---|
| Key lookup | O(log V) V=vnodes | O(1) |
| Add node remapping | O(K/N) keys | O(K) keys (all) |
| Remove node remapping | O(K/N) keys | O(K) keys (all) |
| Hotspot mitigation | Vnodes help | None |
| Quorum read (N replicas) | O(R) reads | O(R) reads |

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


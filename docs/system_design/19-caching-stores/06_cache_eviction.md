# Cache Eviction Policies

## Problem Statement

Design cache eviction strategies that maximize hit rates within memory constraints — understanding LRU, LFU, TTL-based, and Redis-specific approximation algorithms.

## Scenario

Cache Eviction Policies is a critical component in modern distributed systems. In real-world applications, serving billions of user interactions with minimal latency. For example, major tech companies like Netflix, Uber, and Airbnb rely on similar solutions to handle millions of concurrent users and requests. The challenge is achieving this while maintaining sub-100ms latency, 99.99% availability, and gracefully handling 10x traffic spikes during peak demand. This component provides the foundational capability to solve these challenges reliably and efficiently at global scale.

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
    subgraph Cache["Cache (maxmemory=2GB)"]
        HOT["Hot Data\n(frequently accessed)"]
        WARM["Warm Data\n(occasionally accessed)"]
        COLD["Cold Data\n(rarely accessed)"]
    end

    subgraph Policies["Eviction Policies"]
        LRU["LRU\nLeast Recently Used"]
        LFU["LFU\nLeast Frequently Used"]
        TTL["Volatile-TTL\nShortest TTL first"]
        RAND["Random\nRandom eviction"]
    end

    NEW["New Key (cache full)"] -->|evict| Policies
    Policies -->|remove COLD| COLD
    COLD -->|freed space| NEW
```

## Flow Diagram

```mermaid
sequenceDiagram
    participant C as Client
    participant R as Redis
    participant MEM as Memory Manager

    C->>R: SET newkey value
    R->>MEM: Allocate memory
    MEM->>MEM: Check: current_memory > maxmemory?
    MEM->>MEM: YES: run eviction cycle
    MEM->>MEM: Sample 5 random keys (LRU approx)
    MEM->>MEM: Evict key with oldest access time
    MEM->>R: Memory freed
    R->>MEM: Allocate for newkey
    R-->>C: OK
```

## Design

### Eviction Policies

```
noeviction: Return error when memory full
  Use: critical data, operator must increase memory

allkeys-lru: Evict least recently used from all keys
  Best general-purpose policy
  Use: cache where all keys equally eligible

volatile-lru: Evict LRU from keys with TTL only
  Protects keys without TTL (permanent keys)
  Use: mix of persistent + ephemeral data

allkeys-lfu: Evict least frequently used (Redis 4.0+)
  Better than LRU for skewed access patterns
  Keeps truly hot keys regardless of recency
  Use: Pareto-distributed access patterns

volatile-lfu: LFU only on keys with TTL

allkeys-random: Random eviction
  Use: you don't care which key to evict

volatile-random: Random from keys with TTL

volatile-ttl: Evict key with shortest TTL first
  Prioritizes evicting "soon-to-expire" keys
  Use: TTL used as priority hint for eviction
```

### LRU Implementation

```
Doubly-linked list + Hash map:
  List: ordered by recency (head=most recent)
  Map: O(1) access to any node

  GET(key):
    1. Map lookup: O(1)
    2. Move node to head: O(1)
    3. Return value

  SET(key, value):
    1. If exists: update, move to head
    2. If new + capacity full: remove tail (LRU)
    3. Insert at head, add to map

  All operations: O(1)

Redis LRU approximation:
  True LRU: O(N) memory for tracking order
  Redis: sample N random keys (lru-samples=5)
  Evict the one with oldest access timestamp
  ~95% accurate vs true LRU with 5 samples
  10 samples: ~98% accurate
```

### LFU (Least Frequently Used)

```
Counter per key:
  Increment on access, decay over time (Morris counter)
  Access counter: 8-bit (0-255), logarithmic increments
  Clock sweep: periodically decays counters

lfu-log-factor=10: probability of counter increment
  Lower = faster incrementing
  Counter incremented by: 1/(counter * lfu_log_factor + 1)

lfu-decay-time=1: minutes between counter halving
  Prevents old high-frequency keys from blocking new hot keys

LFU vs LRU:
  LRU evicts key not recently used (recency)
  LFU evicts key used infrequently (frequency)
  
  LRU issue: recent one-hit-wonder displaces old hot key
  LFU issue: new hot key not yet accumulated frequency
  LFU better for: Zipf-distributed access (most real-world)
```

## Back-of-Envelope Calculations

```
LRU cache effectiveness:
  10M keys, 80/20 rule: 2M hot keys
  Cache 2M keys: 80% hit rate
  Cache 3M keys: ~90% hit rate (diminishing returns)
  
  Memory: 2M keys x 200 bytes avg = 400MB
  Redis 1GB: cache 5M keys, ~90%+ hit rate

LRU vs LFU for repeated scans:
  1M hot keys, scan 100K cold keys once
  LRU: scan displaces 100K hot keys -> hit rate drops
  LFU: scan keys have frequency=1, hot keys have 100+
  LFU: no displacement -> consistent hit rate

eviction rate at capacity:
  100K writes/s, cache at 100% capacity
  evicted_keys/s should ~= write_rate (100K/s)
  If evicted >> write_rate: memory too small

TTL vs eviction:
  Prefer TTL for all cache entries (predictable expiry)
  eviction = last resort (TTL not set or cache too small)
  Best: set TTL + use LRU as safety net
```

## Design Choices

| Policy | Hit Rate | Protects Hot Keys | Complexity |
|---|---|---|---|
| noeviction | N/A (errors) | Yes | Low |
| allkeys-lru | High general | Yes (recent) | Low |
| allkeys-lfu | Highest (skewed) | Yes (frequent) | Medium |
| volatile-lru | Depends | Permanent keys | Low |
| volatile-ttl | Medium | Permanent keys | Low |
| allkeys-random | Low | No | None |

## Python Implementation

```python
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from collections import OrderedDict
import time
import random
import math

@dataclass
class CacheNode:
    key: str
    value: Any
    last_accessed: float = field(default_factory=time.time)
    access_count: int = 0
    expires_at: Optional[float] = None

    def is_expired(self) -> bool:
        return self.expires_at is not None and time.time() > self.expires_at

class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self._cache: OrderedDict[str, Any] = OrderedDict()
        self._hits = 0
        self._misses = 0
        self._evictions = 0

    def get(self, key: str) -> Optional[Any]:
        if key not in self._cache:
            self._misses += 1
            return None
        self._cache.move_to_end(key)  # Mark as recently used
        self._hits += 1
        return self._cache[key]

    def put(self, key: str, value: Any) -> Optional[str]:
        evicted_key = None
        if key in self._cache:
            self._cache.move_to_end(key)
        else:
            if len(self._cache) >= self.capacity:
                evicted_key, _ = self._cache.popitem(last=False)  # Remove LRU (first)
                self._evictions += 1
        self._cache[key] = value
        return evicted_key

    def stats(self) -> dict:
        total = self._hits + self._misses
        return {
            "size": len(self._cache),
            "capacity": self.capacity,
            "hits": self._hits,
            "misses": self._misses,
            "evictions": self._evictions,
            "hit_rate": f"{self._hits/max(1,total)*100:.1f}%",
        }

class LFUCache:
    def __init__(self, capacity: int, decay_interval_s: float = 60.0):
        self.capacity = capacity
        self.decay_interval = decay_interval_s
        self._values: Dict[str, Any] = {}
        self._freqs: Dict[str, int] = {}
        self._last_access: Dict[str, float] = {}
        self._min_freq: int = 0
        self._freq_to_keys: Dict[int, OrderedDict] = {}
        self._last_decay = time.time()
        self._hits = 0
        self._misses = 0
        self._evictions = 0

    def get(self, key: str) -> Optional[Any]:
        if key not in self._values:
            self._misses += 1
            return None
        self._increment_freq(key)
        self._hits += 1
        return self._values[key]

    def _increment_freq(self, key: str):
        old_freq = self._freqs.get(key, 0)
        new_freq = old_freq + 1
        self._freqs[key] = new_freq
        self._last_access[key] = time.time()

        if old_freq in self._freq_to_keys:
            self._freq_to_keys[old_freq].pop(key, None)
            if not self._freq_to_keys[old_freq] and old_freq == self._min_freq:
                self._min_freq = new_freq

        if new_freq not in self._freq_to_keys:
            self._freq_to_keys[new_freq] = OrderedDict()
        self._freq_to_keys[new_freq][key] = True

    def put(self, key: str, value: Any) -> Optional[str]:
        if self.capacity <= 0:
            return None
        self._maybe_decay()
        if key in self._values:
            self._values[key] = value
            self._increment_freq(key)
            return None

        evicted_key = None
        if len(self._values) >= self.capacity:
            # Evict least frequent, then least recent
            evicted_key = self._evict()

        self._values[key] = value
        self._freqs[key] = 1
        self._last_access[key] = time.time()
        self._min_freq = 1
        if 1 not in self._freq_to_keys:
            self._freq_to_keys[1] = OrderedDict()
        self._freq_to_keys[1][key] = True
        return evicted_key

    def _evict(self) -> Optional[str]:
        min_keys = self._freq_to_keys.get(self._min_freq)
        if not min_keys:
            return None
        lru_key = next(iter(min_keys))
        min_keys.pop(lru_key)
        del self._values[lru_key]
        del self._freqs[lru_key]
        self._evictions += 1
        return lru_key

    def _maybe_decay(self):
        now = time.time()
        if now - self._last_decay > self.decay_interval:
            self._freqs = {k: max(1, v // 2) for k, v in self._freqs.items()}
            self._rebuild_freq_index()
            self._last_decay = now

    def _rebuild_freq_index(self):
        self._freq_to_keys = {}
        self._min_freq = min(self._freqs.values()) if self._freqs else 0
        for key, freq in self._freqs.items():
            if freq not in self._freq_to_keys:
                self._freq_to_keys[freq] = OrderedDict()
            self._freq_to_keys[freq][key] = True

    def stats(self) -> dict:
        total = self._hits + self._misses
        return {
            "size": len(self._values), "capacity": self.capacity,
            "hits": self._hits, "misses": self._misses,
            "evictions": self._evictions,
            "hit_rate": f"{self._hits/max(1,total)*100:.1f}%",
        }

class RedisApproxLRU:
    def __init__(self, capacity: int, num_samples: int = 5):
        self.capacity = capacity
        self.samples = num_samples
        self._store: Dict[str, CacheNode] = {}

    def get(self, key: str) -> Optional[Any]:
        node = self._store.get(key)
        if node is None or node.is_expired():
            return None
        node.last_accessed = time.time()
        node.access_count += 1
        return node.value

    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        if len(self._store) >= self.capacity and key not in self._store:
            self._evict_lru()
        self._store[key] = CacheNode(
            key=key, value=value,
            expires_at=time.time() + ttl if ttl else None
        )

    def _evict_lru(self):
        keys = list(self._store.keys())
        candidates = random.sample(keys, min(self.samples, len(keys)))
        oldest = min(candidates, key=lambda k: self._store[k].last_accessed)
        del self._store[oldest]

# Comparison demo
print("=== LRU vs LFU Comparison ===\n")

lru = LRUCache(capacity=5)
lfu = LFUCache(capacity=5)

# Populate both
for i in range(10):
    key = f"key-{i % 7}"  # 7 unique keys, cache size=5
    value = f"value-{i}"
    lru.put(key, value)
    lfu.put(key, value)

# Simulate skewed access: key-0 and key-1 accessed often
print("Simulating Zipf-like access pattern (keys 0-1 are hot):")
for _ in range(20):
    for hot_key in ["key-0", "key-1"]:
        lru.get(hot_key)
        lfu.get(hot_key)
    # Occasional access to other keys
    lru.get(f"key-{random.randint(2, 6)}")
    lfu.get(f"key-{random.randint(2, 6)}")

# Now access cold key (one-hit-wonder scan)
print("\nSimulating scan of cold keys:")
for i in range(100, 110):
    lru.put(f"scan-{i}", "scan-value")  # LRU may evict hot keys
    lfu.put(f"scan-{i}", "scan-value")  # LFU keeps hot keys

# Check if hot keys survived
print("\nHot key survival after cold scan:")
for cache_name, cache in [("LRU", lru), ("LFU", lfu)]:
    survived = sum(1 for k in ["key-0", "key-1"] if cache.get(k) is not None)
    print(f"  {cache_name}: {survived}/2 hot keys survived")

print(f"\nLRU stats: {lru.stats()}")
print(f"LFU stats: {lfu.stats()}")
```

## Java Implementation

```java
import java.util.*;

public class CacheEviction {
    static class LRUCache {
        final int cap; LinkedHashMap<String, String> cache;

        LRUCache(int cap) {
            this.cap = cap;
            this.cache = new LinkedHashMap<>(16, 0.75f, true) { // accessOrder=true
                protected boolean removeEldestEntry(Map.Entry<String,String> e) {
                    return size() > cap;
                }
            };
        }

        String get(String k) { return cache.get(k); }
        void put(String k, String v) { cache.put(k, v); }
        int size() { return cache.size(); }
    }

    public static void main(String[] args) {
        LRUCache cache = new LRUCache(3);
        cache.put("a", "1"); cache.put("b", "2"); cache.put("c", "3");
        cache.get("a");  // Mark 'a' as recently used
        cache.put("d", "4");  // Evicts LRU ('b')
        System.out.println("After eviction (b should be gone): " + cache.cache.keySet());
        System.out.println("a=" + cache.get("a") + " b=" + cache.get("b") + " c=" + cache.get("c") + " d=" + cache.get("d"));
    }
}
```

## Complexity

| Algorithm | Get | Put | Memory | Accuracy |
|---|---|---|---|---|
| True LRU | O(1) | O(1) | O(n) pointers | 100% |
| Redis Approx LRU | O(1) | O(1) | O(1) per key | ~95-98% |
| LFU (min-heap) | O(log n) | O(log n) | O(n) | 100% |
| LFU (frequency map) | O(1) | O(1) | O(n) | 100% |
| FIFO | O(1) | O(1) | O(n) | N/A |

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


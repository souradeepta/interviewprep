# LRU Cache

**Level:** L3-L5+
**Time to read:** ~30 min

## Problem Statement
Design a Least Recently Used (LRU) cache that evicts the least-recently-accessed entry when capacity is exceeded. This is a deceptively rich problem: getting O(1) for both `get` and `put` requires combining two data structures — a hashmap and a doubly-linked list — in a way that exposes trade-offs between time complexity, memory overhead, and operational complexity. In production, LRU is the eviction policy behind Memcached, Redis (when maxmemory-policy is set to allkeys-lru), and CPU hardware caches.

## Functional Requirements
- `get(key)` — return value in O(1), or -1 if not present
- `put(key, value)` — insert or update in O(1); evict LRU entry if over capacity
- `evict()` — remove least-recently-used entry
- Support for TTL expiry (optional extension)

## Non-Functional Requirements
- **Scale:** 10 million entries per node, 500K ops/sec per node
- **Latency:** P99 < 1 ms for in-process; P99 < 5 ms for distributed
- **Availability:** 99.99% (distributed cache cluster)
- **Consistency:** eventual (cache is a read-through store; source of truth is DB)

---

## Tier 1: L3-L4 Design (the basic interview answer)

### Back-of-Envelope
```
Cache node:
  - 10M entries × (128 bytes key + value avg) = ~1.3 GB data
  - Hashmap overhead: 10M × 8 bytes pointer = 80 MB
  - DLL overhead: 10M × 24 bytes (prev/next/key) = 240 MB
  - Total per node: ~1.6 GB RAM
  - 64 GB node → ~400M entries max

Ops:
  - 500K get/put per sec → well within single-threaded Python/single-core
  - Java/C++ single node: 2–5M ops/sec feasible
```

### Architecture Diagram
```
  ┌─────────────────────────────────────────────────────┐
  │                   LRU Cache Node                     │
  │                                                       │
  │   HashMap (O(1) lookup)                               │
  │   ┌──────┬────────────────────────┐                   │
  │   │ key  │  → DLL Node ptr        │                   │
  │   └──────┴────────────────────────┘                   │
  │                    │                                   │
  │   Doubly-Linked List (O(1) evict/promote)             │
  │   HEAD ←→ [most-recent] ←→ ... ←→ [least-recent] ←→ TAIL
  │    (dummy)                                 (dummy)     │
  └─────────────────────────────────────────────────────┘

Access pattern for get("k"):
  1. HashMap["k"] → DLL node
  2. Remove node from current position
  3. Insert at HEAD
  Return value.

Eviction (capacity exceeded):
  1. Remove TAIL.prev from DLL
  2. Delete HashMap[TAIL.prev.key]
```

### Data Model
```
DLL Node:
  key:   str
  val:   any
  prev:  Node | None
  next:  Node | None
  ts:    float  (optional, for TTL)

HashMap:
  {key: Node}   # O(1) key → node pointer

LRUCache:
  capacity: int
  size:     int
  head:     Node  (dummy)
  tail:     Node  (dummy)
  map:      dict
```

### API Design
**In-process (class interface):**
```
GET  cache.get(key)        → value | -1
PUT  cache.put(key, value) → None
DEL  cache.delete(key)     → bool
```

**As a distributed service (REST):**
```
GET  /cache/{key}           → 200 {value} | 404
PUT  /cache/{key}           → 200 {stored: true}
     body: {value, ttl_sec}
DEL  /cache/{key}           → 204
GET  /cache/stats           → {hit_rate, size, capacity, evictions}
```

### Basic Scaling
- **Single node:** Python OrderedDict or Java LinkedHashMap handles 100K ops/sec easily
- **Read replicas:** shard cache by consistent hashing on key; replicate hot shards
- **Load balancing:** sticky routing by `hash(key) % num_nodes` avoids cross-node misses
- **Client-side caching:** L1 in-process + L2 Memcached/Redis reduces distributed hops

---

## Tier 2: L5+ Design (the staff interview answer)

### Capacity Planning (Real Numbers)
```
Production LRU tier (e.g., Redis cluster):
  - Per-node RAM: 64 GB
  - Redis overhead: ~57 bytes per key for bookkeeping
  - Effective entries: 64 GB / (57 + 128 avg val) = ~340M entries/node
  - 6-node cluster (3 primary + 3 replica): ~1B entries total

CPU budget:
  - Single-threaded Redis: 1M simple ops/sec
  - Pipeline batching: 5–10× throughput improvement
  - Cluster sharding: linear scale across nodes

Cache hit rate modeling:
  - 80/20 rule: 80% requests hit 20% of keys
  - Target hit rate ≥ 95% for typical web workloads
  - Formula: hit_rate ≈ 1 - (capacity / working_set)^α  (α ≈ 0.6–0.9)
  - Monitoring: Prometheus metric cache_hit_ratio, alert < 0.90
```

### Failure Modes
```
Single node failure:
  - Client detects via health check (TCP keepalive, 100 ms timeout)
  - Consistent hashing: only 1/N keys remapped on node loss
  - Recovery: warm-up from DB (cache-aside pattern)
  - Time to warm: depends on hot-key cardinality; estimate 5–15 min for steady state

Thundering herd (cache stampede):
  - Trigger: popular key expires simultaneously for 10K concurrent requests
  - Fix 1: Mutex/semaphore — first request fetches, others wait (Redis SET NX EX)
  - Fix 2: Probabilistic early expiry — refresh before TTL with P = exp(-β·remaining_ttl·log(rand))
  - Fix 3: Background refresh — async re-populate 10 s before expiry

Memory pressure:
  - LRU eviction policy silently drops cold entries — monitor eviction rate
  - If eviction rate spikes, either increase RAM or shrink TTLs
  - Redis eviction stats: INFO stats | grep evicted_keys

Cascading failure:
  - Cache layer down → all traffic hits DB → DB overwhelmed → full outage
  - Mitigation: circuit breaker (fail fast), cache fallback to stale value
  - Stale-while-revalidate: serve cached (possibly stale) value while refreshing async
```

### Consistency Boundaries
```
Cache-aside (lazy loading):
  - App reads DB on miss, populates cache — no write-time consistency
  - Race: two concurrent misses write stale value after DB update
  - Fix: versioned cache keys or short TTL

Write-through:
  - Write to DB and cache atomically — higher write latency, strong consistency
  - Drawback: write amplification for cold keys that are never read

Distributed LRU consistency:
  - No global ordering of LRU across shards — each shard tracks its own LRU
  - Gossip protocol for hot-key detection across shards
  - Per-shard LRU is sufficient; global LRU not needed in practice
```

### Cost Model
```
Self-hosted Redis cluster (3+3, 64 GB each):
  - AWS r6g.2xlarge (64 GB): $0.48/hr × 6 = $2.88/hr = ~$2,100/mo
  - Per-user cost (100M DAU): $2,100 / 100M = $0.000021/user/month

Elasticache (managed):
  - r6g.2xlarge: $0.54/hr × 6 = $3.24/hr = ~$2,350/mo
  - Premium: ~12% overhead for managed ops

Optimization levers:
  - Compress values (msgpack vs JSON → 50–70% size reduction)
  - Tiered cache: hot data in Redis, warm in Memcached (cheaper), cold in DB
  - Key expiry tuning: overly long TTLs waste RAM on dead keys
```

---

## Trade-off Comparison

| Approach | Time Complexity | Memory | Concurrency | Best For |
|----------|----------------|--------|-------------|----------|
| OrderedDict (Python) | O(1) get/put | 1× | Single thread | In-process, prototyping |
| Raw DLL + HashMap | O(1) get/put | 0.7× | Single thread | Custom eviction extensions |
| Java LinkedHashMap | O(1) get/put | 1× | With external lock | JVM services |
| Redis (allkeys-lru) | O(1) amortized | 1.2× bookkeeping | Multi-threaded + cluster | Distributed, production |
| Memcached + LRU slab | O(1) | 1× (simpler OBJ) | Multi-threaded | Simple K/V, highest throughput |
| Guava LoadingCache | O(1) + loader | 1.1× | Built-in concurrency | JVM with DB loader pattern |

**When LRU beats LFU:** bursty access patterns where recently-accessed items are more likely reused (e.g., feed refresh, session data).

**When LFU beats LRU:** stable popularity distributions (CDN content, image thumbnails) — frequency is a better predictor than recency.

---

## Follow-up Questions (5-10, escalating)

1. **(L3)** What data structures does an O(1) LRU cache need, and why?
   > HashMap for O(1) lookup + doubly-linked list for O(1) move-to-front and evict-from-tail.

2. **(L3)** How does Python's `OrderedDict` make LRU trivial to implement?
   > `move_to_end(key)` on access, `popitem(last=False)` for eviction. Internally it's a DLL + hashmap.

3. **(L4)** How would you make LRU thread-safe?
   > Option A: coarse lock (simple, lower throughput). Option B: segment locking (N buckets, each with own lock). Option C: lock-free using CAS on node pointers (complex). Redis avoids the problem with single-threaded event loop.

4. **(L4)** Describe cache warming. Why is it important, and how do you implement it?
   > On startup, cold cache causes DB surge. Warm by: (a) replay recent access log, (b) preload top-N keys by read frequency, (c) shadow traffic on new node before serving live.

5. **(L4)** What is the thundering herd problem and how do you prevent it?
   > Many requests simultaneously miss an expired hot key and all go to DB. Prevent with mutex (Redis SETNX), probabilistic early expiry, or background refresh.

6. **(L5)** Design a distributed LRU where each shard independently applies LRU but you need a global top-K hot keys view.
   > Each shard uses Count-Min Sketch to approximate per-key frequency. Periodically gossip top-K from each shard to a coordinator. Coordinator merges via min-heap. Use this to proactively replicate hot keys across all shards.

7. **(L5)** How would you implement cache-aside vs write-through vs write-back? When is each appropriate?
   > Cache-aside: app manages cache; simplest, eventual consistency. Write-through: write to cache and DB synchronously; consistent but high write latency. Write-back: write to cache, flush to DB async; fastest writes, risk of data loss on crash.

8. **(L5+)** The cache hit rate drops from 95% to 70% overnight. Walk me through your incident response.
   > 1. Check eviction rate spike (new traffic pattern or data growth). 2. Inspect key distribution (new hot keys exhausting capacity). 3. Check TTL changes. 4. Profile access logs for working set size change. 5. Short-term: increase capacity or reduce TTLs. Long-term: adaptive cache sizing, LFU for stable workloads.

---

## Anti-patterns / Things NOT to Say

- **"I'll use a list and scan for the LRU entry"** — O(N) eviction is a non-starter; shows you don't know the DLL+hashmap trick.
- **"Just use a sorted set by timestamp"** — O(log N) access vs O(1); unnecessary overhead.
- **"Cache invalidation is easy"** — demonstrates lack of production experience; invalidation is notoriously hard (stale reads, thundering herd, distributed sync).
- **"I'll add a global lock for thread safety"** — acceptable for prototype but mention it as a bottleneck; segmented locking or lock-free structures are the real answer.
- **"LRU is always the best policy"** — LFU beats LRU for stable frequency distributions; mention the trade-off.
- **Forgetting to handle the case where capacity = 0** — edge case that crashes naive implementations.

---

## Python Implementation

```python
from collections import OrderedDict
from threading import Lock
from typing import Optional


# --- Approach 1: OrderedDict (interview-clean) ---

class LRUCacheSimple:
    def __init__(self, capacity: int):
        self.cap = capacity
        self.cache: OrderedDict = OrderedDict()

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        self.cache.move_to_end(key)       # mark as most-recently used
        return self.cache[key]

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.cap:
            self.cache.popitem(last=False) # evict LRU (front of OrderedDict)


# --- Approach 2: Raw DLL + HashMap (shows you understand internals) ---

class Node:
    __slots__ = ("key", "val", "prev", "next")

    def __init__(self, key: int = 0, val: int = 0):
        self.key = key
        self.val = val
        self.prev: Optional["Node"] = None
        self.next: Optional["Node"] = None


class LRUCache:
    """O(1) get and put using doubly-linked list + hashmap."""

    def __init__(self, capacity: int):
        self.cap = capacity
        self.map: dict[int, Node] = {}
        # sentinel nodes avoid edge-case null checks
        self.head = Node()   # dummy head (most recent side)
        self.tail = Node()   # dummy tail (LRU side)
        self.head.next = self.tail
        self.tail.prev = self.head

    # ── DLL helpers ────────────────────────────────────────────

    def _remove(self, node: Node) -> None:
        node.prev.next = node.next
        node.next.prev = node.prev

    def _insert_front(self, node: Node) -> None:
        """Insert right after dummy head (marks as MRU)."""
        node.next = self.head.next
        node.prev = self.head
        self.head.next.prev = node
        self.head.next = node

    # ── Public API ─────────────────────────────────────────────

    def get(self, key: int) -> int:
        if key not in self.map:
            return -1
        node = self.map[key]
        self._remove(node)
        self._insert_front(node)
        return node.val

    def put(self, key: int, value: int) -> None:
        if key in self.map:
            self._remove(self.map[key])
        node = Node(key, value)
        self.map[key] = node
        self._insert_front(node)
        if len(self.map) > self.cap:
            lru = self.tail.prev          # node just before dummy tail
            self._remove(lru)
            del self.map[lru.key]

    def __repr__(self) -> str:
        items, node = [], self.head.next
        while node is not self.tail:
            items.append(f"{node.key}:{node.val}")
            node = node.next
        return "LRU[" + " → ".join(items) + "]"


# --- Approach 3: Thread-safe wrapper ---

class ThreadSafeLRU:
    def __init__(self, capacity: int):
        self._cache = LRUCache(capacity)
        self._lock = Lock()

    def get(self, key: int) -> int:
        with self._lock:
            return self._cache.get(key)

    def put(self, key: int, value: int) -> None:
        with self._lock:
            self._cache.put(key, value)


# ── Demo ───────────────────────────────────────────────────────
if __name__ == "__main__":
    c = LRUCache(3)
    c.put(1, 10); c.put(2, 20); c.put(3, 30)
    print(c)                 # LRU[3:30 → 2:20 → 1:10]
    c.get(1)                 # promote 1 to front
    print(c)                 # LRU[1:10 → 3:30 → 2:20]
    c.put(4, 40)             # evict 2 (LRU)
    print(c)                 # LRU[4:40 → 1:10 → 3:30]
    print(c.get(2))          # -1 (evicted)
```

# LFU Cache

**Level:** L3-L5+
**Time to read:** ~30 min

## Problem Statement
Design a Least Frequently Used (LFU) cache that evicts the entry with the lowest access frequency when capacity is exceeded. When multiple entries share the minimum frequency, evict the least recently used among them (frequency ties broken by recency). LFU is harder than LRU: a naive heap-based approach is O(log N) per operation. The optimal design achieves O(1) get and put using a min-frequency pointer, a frequency-bucketed doubly-linked list, and a hashmap — exposing nuanced trade-offs between LRU and LFU for different workload shapes.

## Functional Requirements
- `get(key)` — return value in O(1); increment frequency counter
- `put(key, value)` — insert/update in O(1); evict LFU entry on overflow
- Tie-breaking: among keys with equal min frequency, evict the least recently used
- `get_freq(key)` — return current frequency count (optional)

## Non-Functional Requirements
- **Scale:** 50M entries per node, 1M ops/sec
- **Latency:** P99 < 1 ms in-process
- **Availability:** 99.99% (production cache cluster)
- **Consistency:** eventual (cache-aside pattern against persistent store)

---

## Tier 1: L3-L4 Design (the basic interview answer)

### Back-of-Envelope
```
Per-entry memory:
  - key + value avg: 128 bytes
  - freq counter: 8 bytes
  - HashMap entry: 8 bytes pointer
  - DLL node (key, val, freq, prev, next): ~48 bytes
  - Total: ~192 bytes/entry

50M entries: 50M × 192 = ~9.6 GB RAM per node
32 GB node → ~166M entries max

Ops:
  - 1M ops/sec single-process is achievable in C++/Java
  - Python CPython: ~200K ops/sec; PyPy: ~1M ops/sec
  - For Python services, front with Memcached/Redis for production scale
```

### Architecture Diagram
```
  LFU Cache Internal Structure
  ─────────────────────────────────────────────────────────────
  key_map:   {key → Node}            ← O(1) key lookup
  freq_map:  {freq → DLL of nodes}   ← O(1) access by frequency bucket
  min_freq:  int                      ← tracks global minimum frequency

  freq_map layout (freq → doubly-linked list, head=MRU, tail=LRU):
  ┌───────┬──────────────────────────────────────────────────┐
  │ freq=1│  HEAD ←→ [C] ←→ [B] ←→ TAIL   (LRU is B)       │
  │ freq=2│  HEAD ←→ [A] ←→ TAIL                             │
  │ freq=5│  HEAD ←→ [D] ←→ TAIL                             │
  └───────┴──────────────────────────────────────────────────┘
  min_freq = 1

  get("B"):
    1. key_map["B"] → Node(freq=1)
    2. Remove B from freq_map[1]
    3. freq_map[1] is now {C} only
    4. B.freq = 2 → insert B at HEAD of freq_map[2]
    5. min_freq still 1 (freq_map[1] not empty)

  On capacity overflow, evict tail of freq_map[min_freq]
```

### Data Model
```
Node:
  key:   int
  val:   int
  freq:  int

FreqBucket (per-frequency doubly-linked list):
  head:  Node  (dummy, MRU side)
  tail:  Node  (dummy, LRU side)
  size:  int

LFUCache:
  capacity:  int
  size:      int
  min_freq:  int
  key_map:   {key → Node}
  freq_map:  {freq → FreqBucket}
```

### API Design
**In-process:**
```
GET  cache.get(key)         → value | -1
PUT  cache.put(key, value)  → None
GET  cache.get_freq(key)    → int | 0
```

**Distributed REST extension:**
```
GET  /cache/{key}                    → 200 {value, freq} | 404
PUT  /cache/{key}                    → 200 {stored: true}
     body: {value, ttl_sec}
GET  /cache/stats                    → {hit_rate, min_freq, size, capacity}
GET  /cache/top-k?k=10               → [{key, freq}]  (top-K hottest)
```

### Basic Scaling
- **Single node:** Python implementation handles 100K–200K ops/sec; sufficient for L3-L4 interviews
- **Heap-based approach (L3 acceptable):** maintain a min-heap by (freq, insertion_time); O(log N) per op — mention it then pivot to O(1) design
- **Sharding:** partition key space by consistent hashing; each shard independently tracks its own LFU
- **Frequency reset:** periodic decay (multiply all freqs by 0.5) prevents "frequency pollution" where old hot keys starve new popular entries

---

## Tier 2: L5+ Design (the staff interview answer)

### Capacity Planning (Real Numbers)
```
CDN edge cache scenario (image thumbnail server):
  - Working set: 200M unique thumbnails
  - Hot 1%: 2M thumbnails requested > 100×/day
  - Cold 99%: rarely accessed

  LFU advantage: hot 1% stays in cache; LRU would evict them during scan spikes
  Node sizing: 64 GB / 192 bytes ≈ 333M entries — covers full working set
  
Frequency distribution:
  - Power-law (Zipf): freq(rank_k) ∝ 1/k^s, s ≈ 0.8–1.2 for web content
  - LFU hit rate ≈ 1 - sum(low-freq items occupying cache)
  - Empirical: LFU gets 3–8% higher hit rate than LRU for CDN workloads

Frequency counter overflow:
  - 8-byte counter: max 9.2 × 10^18 — not a concern
  - 4-byte counter (memory opt): max 4.3 × 10^9 — saturation at 4B accesses
  - Recommendation: 4 bytes, saturate at max value rather than wrap
```

### Failure Modes
```
Frequency pollution (aging problem):
  - Keys accessed 10K× last week but rarely now remain in cache
  - Blocks newer, genuinely hot keys from entering
  - Fix: exponential decay — halve all frequencies every T seconds
  - Fix: windowed LFU — count freq only within sliding window (last 24h)
  - Production: TinyLFU (Caffeine library) uses approximate frequency with aging

min_freq pointer staleness:
  - Bug: min_freq not updated correctly after eviction → evicts wrong entry
  - Invariant: after eviction, min_freq = 1 if a new key was just inserted
  - After get/put on existing key: min_freq may increase if freq_map[min_freq] empty

Cold start / cache miss storm:
  - New keys start at freq=1; initially LFU behaves like FIFO
  - Mitigation: initialize new keys at freq = min_freq + 1 (slight bias toward retention)
  - Window warm-up: shadow-mode LFU tracks frequencies without evicting for first 5 min

Distributed freq divergence:
  - Each shard tracks frequency independently → global hot keys may be in only 1 shard
  - Mitigation: gossip hot-key list across shards, replicate top-K hot entries everywhere
```

### Consistency Boundaries
```
LFU + Cache-aside (standard):
  - Miss → fetch from DB → cache with freq=1
  - Race: two concurrent misses both fetch DB, one overwrites the other
  - Fix: lock on miss (distributed mutex via Redis SETNX), or last-write-wins with version check

Write-through LFU:
  - Writes update both DB and cache; cache retains frequency ordering
  - Higher write latency but reads always hit cache
  - Appropriate for read-heavy content systems (CDN, thumbnails)

Windowed LFU:
  - TinyLFU uses a counting Bloom filter (4-bit counters per key) for approximate freq
  - Periodically halves all counters (approximate aging)
  - 99%+ accuracy with 1/50 memory footprint vs exact counters
```

### Cost Model
```
Self-hosted (vs LRU Redis):
  - LFU per entry overhead: +8 bytes freq counter + freq_map DLL entry
  - Cost premium vs LRU: ~5–10% more RAM per entry
  - ROI: +5% hit rate saves 5% DB read load → at $0.20/M DB reads, worthwhile at > 50M reads/day

Caffeine (Java, production LFU):
  - Window-TinyLFU: 1% of cache as LRU window, 99% as segmented LFU
  - Near-optimal hit rate; standard in Spring Boot / Guava replacement
  - 0 licensing cost; operational cost = JVM heap tuning

Redis LFU mode (available since 4.0):
  - maxmemory-policy: allkeys-lfu or volatile-lfu
  - Uses Morris counter (probabilistic, 8-bit): slight accuracy loss, huge memory saving
  - Cost same as Redis LRU; flip one config line
```

---

## Trade-off Comparison

| Policy | Eviction Basis | Burst Tolerance | Frequency Pollution | Memory | Best For |
|--------|---------------|-----------------|---------------------|--------|----------|
| FIFO | Insertion order | High | No | Lowest | Simplest queues |
| LRU | Recency | Medium | No | Low | Session data, feeds |
| LFU (exact) | Access count | Low | Yes (needs decay) | Medium | CDN, thumbnails |
| LFU (windowed) | Windowed count | Medium | No (aged out) | Medium | General purpose |
| ARC | Recency + Freq | High | Partial | 2× | File system caches |
| TinyLFU (Caffeine) | Approx count + window | High | No | Lowest | Production Java apps |
| 2Q | Two LRU queues | High | No | Low | DB buffer pools |

**LRU wins when:** access patterns are bursty or temporal (users access recent content most).

**LFU wins when:** popularity is stable over time (CDN objects, reference data, thumbnails).

**ARC/TinyLFU wins when:** workload is mixed or unknown — adaptive policies avoid tuning.

---

## Follow-up Questions (5-10, escalating)

1. **(L3)** What's the time complexity of a heap-based LFU vs the optimal LFU?
   > Heap: O(log N) per operation. Optimal (DLL + freq_map + min_freq): O(1) per operation.

2. **(L3)** When should you use LFU instead of LRU?
   > LFU when content popularity is stable and long-lived (CDN, images, reference data). LRU when access patterns are temporal or bursty (user sessions, social feeds).

3. **(L4)** Explain the frequency pollution problem and how you'd fix it.
   > Old hot keys accumulate high frequencies and can't be evicted even when cold. Fix: exponential decay (halve all counters periodically), or windowed frequency counting (only count accesses in the last N seconds/minutes).

4. **(L4)** How does TinyLFU differ from exact LFU?
   > TinyLFU uses approximate frequency counters (4-bit Morris counters in a Bloom-filter-like sketch) with periodic halving for aging. Uses 1/50th the memory of exact LFU with > 99% accuracy. Used in Caffeine (Guava successor).

5. **(L4)** Design an LFU cache that also supports O(1) `get_top_k_hot_keys(k)`.
   > Maintain a separate min-heap of top-K entries by frequency, updated on each access. Heap size stays at K, so updates are O(log K). Trade-off: extra O(K) memory and O(log K) per access.

6. **(L5)** Compare ARC and LFU. When does ARC outperform both LRU and LFU?
   > ARC maintains four lists: T1 (recent unique), T2 (frequent), B1 (ghost of T1), B2 (ghost of T2). Adapts dynamically to workload mix — automatically finds the right LRU/LFU balance. Wins on mixed or shifting workloads without tuning. Patented by IBM (why not used in Redis).

7. **(L5)** Design a distributed LFU with global frequency ranking across 100 shards.
   > Each shard maintains a Count-Min Sketch of frequencies. Every 60s, gossip top-K sketches to a coordinator node which merges (element-wise min across sketches). Coordinator publishes global top-K. Shards use this to pin globally-hot keys and defer local eviction of them.

8. **(L5+)** You're running a Redis cluster in LFU mode and hit rate drops suddenly. Diagnose.
   > 1. Check INFO stats: evicted_keys, keyspace_hits/misses. 2. Inspect frequency distribution: DEBUG OBJECT key shows lru_seconds (also used for LFU counter in Redis). 3. Look for frequency pollution: keys with very high access counts from old traffic pattern. 4. Check if maxmemory was recently reduced. 5. Fix: FLUSHDB on stale frequency data, or reduce TTLs to force cache refresh.

---

## Anti-patterns / Things NOT to Say

- **"LFU is always better than LRU"** — flat wrong; LRU wins on bursty/temporal workloads.
- **"Just use a min-heap sorted by frequency"** — O(log N) per operation; acceptable to mention as first idea but must pivot to O(1) design.
- **"Frequency counter won't matter in practice"** — frequency pollution is a real production issue; shows lack of depth.
- **"I'll reset all counters to 0 periodically"** — destroys all frequency information; exponential decay is the correct approach.
- **Forgetting tie-breaking:** LFU with no tie-breaking rule is incomplete; always break ties by recency (most recently used survives).
- **No mention of min_freq pointer:** the O(1) trick depends on tracking the minimum frequency; omitting it means you don't know the O(1) implementation.

---

## Python Implementation

```python
from collections import defaultdict
from typing import Optional


class Node:
    __slots__ = ("key", "val", "freq", "prev", "next")

    def __init__(self, key: int = 0, val: int = 0, freq: int = 1):
        self.key = key
        self.val = val
        self.freq = freq
        self.prev: Optional["Node"] = None
        self.next: Optional["Node"] = None


class FreqBucket:
    """Doubly-linked list for a single frequency level. Head = MRU, Tail = LRU."""

    def __init__(self):
        self.head = Node()           # dummy
        self.tail = Node()           # dummy
        self.head.next = self.tail
        self.tail.prev = self.head
        self.size = 0

    def insert_front(self, node: Node) -> None:
        node.next = self.head.next
        node.prev = self.head
        self.head.next.prev = node
        self.head.next = node
        self.size += 1

    def remove(self, node: Node) -> None:
        node.prev.next = node.next
        node.next.prev = node.prev
        self.size -= 1

    def pop_tail(self) -> Optional[Node]:
        """Remove and return LRU node (just before dummy tail)."""
        if self.size == 0:
            return None
        lru = self.tail.prev
        self.remove(lru)
        return lru

    def is_empty(self) -> bool:
        return self.size == 0


class LFUCache:
    """
    O(1) get and put.
    Tie-breaking: among equal-freq entries, evict LRU (least recently used).
    """

    def __init__(self, capacity: int):
        self.cap = capacity
        self.size = 0
        self.min_freq = 0
        self.key_map: dict[int, Node] = {}
        self.freq_map: dict[int, FreqBucket] = defaultdict(FreqBucket)

    def _promote(self, node: Node) -> None:
        """Move node from its current freq bucket to freq+1 bucket."""
        old_freq = node.freq
        self.freq_map[old_freq].remove(node)
        # If the old bucket was the minimum and is now empty, increment min_freq
        if old_freq == self.min_freq and self.freq_map[old_freq].is_empty():
            self.min_freq += 1
        node.freq += 1
        self.freq_map[node.freq].insert_front(node)

    def get(self, key: int) -> int:
        if key not in self.key_map:
            return -1
        node = self.key_map[key]
        self._promote(node)
        return node.val

    def put(self, key: int, value: int) -> None:
        if self.cap <= 0:
            return

        if key in self.key_map:
            node = self.key_map[key]
            node.val = value
            self._promote(node)
            return

        # Evict if at capacity
        if self.size >= self.cap:
            evicted = self.freq_map[self.min_freq].pop_tail()
            if evicted:
                del self.key_map[evicted.key]
                self.size -= 1

        # Insert new key at freq=1
        node = Node(key, value, freq=1)
        self.key_map[key] = node
        self.freq_map[1].insert_front(node)
        self.min_freq = 1             # new key always starts at freq=1
        self.size += 1

    def __repr__(self) -> str:
        lines = [f"LFU(min_freq={self.min_freq}, size={self.size})"]
        for freq in sorted(self.freq_map):
            bucket = self.freq_map[freq]
            if not bucket.is_empty():
                items, node = [], bucket.head.next
                while node is not bucket.tail:
                    items.append(f"{node.key}:{node.val}")
                    node = node.next
                lines.append(f"  freq={freq}: [{', '.join(items)}]")
        return "\n".join(lines)


# ── Heap-based LFU (O(log N), simpler but non-optimal) ─────────────────────

import heapq
from itertools import count

class LFUCacheHeap:
    """O(log N) per operation — acceptable mention, not the target answer."""

    def __init__(self, capacity: int):
        self.cap = capacity
        self.cache: dict[int, tuple] = {}   # key → (val, freq)
        self.heap: list = []                 # (freq, counter, key)
        self.counter = count()
        self.freq: dict[int, int] = {}       # key → freq

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        val, _ = self.cache[key]
        self.freq[key] = self.freq.get(key, 0) + 1
        heapq.heappush(self.heap, (self.freq[key], next(self.counter), key))
        self.cache[key] = (val, self.freq[key])
        return val

    def put(self, key: int, value: int) -> None:
        if self.cap <= 0:
            return
        self.freq[key] = self.freq.get(key, 0) + 1
        heapq.heappush(self.heap, (self.freq[key], next(self.counter), key))
        self.cache[key] = (value, self.freq[key])
        while len(self.cache) > self.cap:
            while self.heap:
                f, _, k = heapq.heappop(self.heap)
                if k in self.cache and self.cache[k][1] == f:
                    del self.cache[k]
                    del self.freq[k]
                    break


# ── Demo ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    c = LFUCache(3)
    c.put(1, 10); c.put(2, 20); c.put(3, 30)
    c.get(1); c.get(1); c.get(2)     # freq: {1:2, 2:2, 3:1}
    print(c)
    c.put(4, 40)                      # evict key=3 (min_freq=1, LRU)
    print(c.get(3))                   # -1 (evicted)
    print(c)
```

#!/usr/bin/env python3
"""Add 30 comprehensive caching concepts (4-33) to 01-caching."""
import os
output_dir = "docs/system_design/01-caching"
os.makedirs(output_dir, exist_ok=True)

CONCEPTS = {
    "04_lru_cache": {
        "title": "LRU (Least Recently Used) Cache Replacement Policy",
        "scale": "100M+ cache entries, sub-microsecond eviction, 95%+ hit ratio",
        "overview": """LRU cache evicts the least recently used item when capacity is exceeded, based on temporal locality principle. Used in CPU caches, page replacement, and application-level caching. Requires O(1) lookup and O(1) eviction using doubly-linked lists with hashmap, tracking access patterns efficiently.""",
    },
    "05_lfu_cache": {
        "title": "LFU (Least Frequently Used) Cache Replacement Policy",
        "scale": "100M+ entries, sub-microsecond eviction, frequency-based optimization",
        "overview": """LFU evicts least frequently used items when cache is full, favoring hot items accessed frequently. Better than LRU for workloads with clear frequency distributions. Requires frequency tracking and efficient min-frequency bucket management for O(1) operations.""",
    },
    "06_arc_cache": {
        "title": "ARC (Adaptive Replacement Cache) Algorithm",
        "scale": "100M+ entries, adaptive to workload, 99%+ hit ratio",
        "overview": """ARC combines LRU and LFU benefits, maintaining separate lists for recent and frequent items. It adapts dynamically between recency and frequency based on workload, achieving better hit ratios than pure LRU or LFU. Used in storage systems and databases for superior performance.""",
    },
    "07_clock_algorithm": {
        "title": "Clock Page Replacement Algorithm",
        "scale": "1B+ pages, constant-time eviction, low overhead",
        "overview": """Clock algorithm approximates LRU with minimal overhead using a circular buffer and reference bit. Each item tracks if recently referenced; clock hand advances evicting unreferenced items. Used in operating systems and databases for efficient page replacement with O(1) operations.""",
    },
    "08_cache_locality": {
        "title": "Cache Locality and Access Patterns",
        "scale": "Multi-level cache hierarchy, 10x performance variance",
        "overview": """Temporal locality (recently accessed items likely accessed again) and spatial locality (nearby items likely accessed together) determine cache effectiveness. Cache-aware programming exploits these patterns through sequential access, data structure layout, and loop optimization for significant performance gains.""",
    },
    "09_working_set": {
        "title": "Working Set Model and Memory Management",
        "scale": "Virtual memory systems, prevent thrashing, 1000x performance impact",
        "overview": """Working set is the set of pages a process actively accesses during an execution period. Monitoring working set size determines memory allocation; insufficient allocation causes thrashing (excessive page faults). Modern systems use working set estimates for efficient memory management and process scheduling.""",
    },
    "10_cache_coherence": {
        "title": "Cache Coherence Protocols in Multi-Core Systems",
        "scale": "1000+ cores, sub-nanosecond coherence, zero correctness violations",
        "overview": """Cache coherence ensures multiple cached copies of same data item remain consistent across cores. MESI, MOESI, and MESIF protocols enforce coherence through bus snooping or directory-based tracking, critical for multi-core CPU performance and correctness.""",
    },
    "11_false_sharing": {
        "title": "False Sharing and Cache Line Contention",
        "scale": "100+ threads, 50% performance loss potential, nanosecond overhead",
        "overview": """False sharing occurs when different threads access different variables on same cache line, causing unnecessary coherence traffic. Cache lines (typically 64 bytes) move between cores even though threads access unrelated data, killing multi-threaded performance. Padding and layout optimization essential for high-performance concurrent code.""",
    },
    "12_cache_prefetching": {
        "title": "Hardware and Software Cache Prefetching",
        "scale": "1000+ prefetch streams, 30-40% performance improvement, <5% overfetch",
        "overview": """Prefetching anticipates future memory accesses and loads data into cache before requested, hiding memory latency. Hardware prefetchers detect patterns (sequential, strided); software prefetchers use programmer hints. Aggressive prefetching risks cache pollution; tuning required for optimal performance.""",
    },
    "13_cache_pollution": {
        "title": "Cache Pollution and Eviction Prediction",
        "scale": "100M+ entries, 20-30% performance impact from pollution",
        "overview": """Cache pollution occurs when less-useful data evicts useful data, reducing hit ratio. One-time sequential scans can pollute entire cache. Techniques like scan-resistant replacement policies (CLOCK-Pro) and priority-based eviction protect working set from pollution.""",
    },
    "14_tiered_memory": {
        "title": "Tiered Memory Systems and Heterogeneous Storage",
        "scale": "10x performance variance, automatic tiering, petabyte-scale",
        "overview": """Tiered memory combines fast (DRAM) and slow (SSD, HDD) storage, automatically moving hot data to fast tiers. Key-value stores use tiered caching (L1: memory, L2: SSD, L3: HDD) for cost-effectiveness. Intelligent tiering policies optimize cost-performance tradeoff.""",
    },
    "15_cache_invalidation": {
        "title": "Cache Invalidation Strategies and Consistency",
        "scale": "Distributed systems, sub-millisecond propagation, 99.99% consistency",
        "overview": """Cache invalidation ensures stale data doesn't serve after updates. Strategies: TTL-based (simple, eventual consistency), event-based (real-time, high overhead), and consistency protocols (quorum reads). Phil Karlton: "Cache invalidation is one of the hardest problems in Computer Science" (alongside naming and off-by-one errors).""",
    },
    "16_bloom_filters": {
        "title": "Bloom Filters for Efficient Membership Testing",
        "scale": "Billions of items, 1-2 bytes per item, sub-microsecond lookup",
        "overview": """Bloom filters answer "is item in set?" with tunable false positive rate and minimal space. Multiple hash functions map items to bit array; zero false negatives but possible false positives. Used for cache presence checking, duplicate detection, and privacy-preserving queries.""",
    },
    "17_compressed_cache": {
        "title": "Compressed Caching and Encoding",
        "scale": "3-5x cache capacity increase, <5% CPU overhead",
        "overview": """Cache compression (LZ4, Snappy, Zstandard) increases effective cache capacity by 3-5x with minor CPU overhead. Decompression latency <100ns acceptable; compression beneficial for bandwidth-limited systems and memory-constrained scenarios. Trade-off: CPU for memory.""",
    },
    "18_cache_warming": {
        "title": "Cache Warming and Preloading Strategies",
        "scale": "100M+ items, <1 second warm-up, 90%+ hit ratio on startup",
        "overview": """Cache warming preloads likely-to-be-needed items before serving traffic, reducing cold start penalty. Strategies: replaying historical workloads, precomputing hot items, or priming from previous state. Critical for latency-sensitive services to achieve consistent performance from startup.""",
    },
    "19_cache_stampede": {
        "title": "Cache Stampede and Thundering Herd Prevention",
        "scale": "1M+ concurrent requests, prevent 100x traffic spike",
        "overview": """Cache stampede occurs when popular item expires, causing multiple requests to recalculate simultaneously, overwhelming backend. Prevention: probabilistic early expiration, background refresh, locking (single calculator), or probabilistic expiration (staggered recalculation). Critical for high-traffic systems.""",
    },
    "20_distributed_caching": {
        "title": "Distributed Caching Architectures",
        "scale": "1000+ cache nodes, petabyte capacity, 1M+ QPS",
        "overview": """Distributed caches (Redis Cluster, Memcached, DynamoDB) shard data across multiple nodes for scalability. Consistency models vary (eventual to strong); availability and latency trade-offs determined by replication and quorum strategies. Partitioning, replication, and failure recovery essential design elements.""",
    },
    "21_cache_aside": {
        "title": "Cache-Aside (Lazy Loading) Pattern",
        "scale": "Sub-millisecond cache, on-demand loading, 95%+ hit ratio",
        "overview": """Cache-aside pattern: application checks cache first, loads from source if miss, stores result. Simple but application-side logic required; potential race conditions on multiple misses. Best for read-heavy workloads with acceptable miss latency. Risk: thundering herd if not protected.""",
    },
    "22_write_through_cache": {
        "title": "Write-Through Cache Pattern",
        "scale": "Synchronous writes, guaranteed consistency, higher latency",
        "overview": """Write-through cache: data written to both cache and source simultaneously, ensuring cache always valid. Simplifies consistency but increases write latency (source latency dominates). Good for systems requiring strong consistency; poor for write-heavy workloads.""",
    },
    "23_write_back_cache": {
        "title": "Write-Back (Write-Behind) Cache Pattern",
        "scale": "Asynchronous writes, 100x latency reduction, consistency risk",
        "overview": """Write-back cache: data written to cache immediately, flushed to source asynchronously. Dramatically improves write latency but risks data loss if cache fails before flush. Requires careful handling of flush ordering, batching, and durability guarantees. Trade-off: latency for consistency.""",
    },
    "24_refresh_ahead": {
        "title": "Refresh-Ahead Cache Expiration Strategy",
        "scale": "100M+ expirations, zero miss latency, predictive loading",
        "overview": """Refresh-ahead proactively reloads cache entries before expiration based on access patterns. Eliminates cold-start latency for predictable workloads; reduces cache stampede risk. Requires accurate prediction; wasted reloads if predictions incorrect. Balance: proactive refresh vs. unnecessary computation.""",
    },
    "25_probabilistic_expiry": {
        "title": "Probabilistic Expiration and Jittered TTL",
        "scale": "Prevent thundering herd, 10-100x reduction in spike traffic",
        "overview": """Instead of fixed TTL causing simultaneous expirations, probabilistic expiration staggers refreshes. Items expire randomly around nominal TTL, spreading recalculation load over time. Jittered TTL adds randomness to prevent synchronization. Simple but effective defense against cache stampede.""",
    },
    "26_cache_bypass": {
        "title": "Cache Bypass and Direct Backend Access",
        "scale": "Selective caching, reduce cache pollution, adaptable consistency",
        "overview": """Some queries bypass cache for guaranteed freshness (consistency-critical reads) or due to being non-cacheable. Bypass policies balance consistency needs with latency/cost. Examples: freshness-critical queries, one-time large requests, or invalidation uncertainty.""",
    },
    "27_multi_tier_caching": {
        "title": "Multi-Tier Cache Hierarchies",
        "scale": "L1/L2/L3 caches, 100x performance variance across tiers",
        "overview": """Multi-tier caching (L1: process-local, L2: in-region distributed, L3: global distributed) provides graduated latency and consistency guarantees. L1 misses fallback to L2; L2 misses fallback to L3. Tradeoff: memory/cost vs. latency. Requires coherence between tiers.""",
    },
    "28_cache_key_design": {
        "title": "Cache Key Design and Namespacing",
        "scale": "1B+ keys, collision avoidance, versioning support",
        "overview": """Cache keys must be deterministic, collision-free, and version-aware. Strategies: include version in key (foo:v2:user:123), namespace by tenant (tenant:123:foo), or use hash of compound key. Poor key design causes inconsistent data; good design enables versioning and namespacing.""",
    },
    "29_cache_versioning": {
        "title": "Cache Versioning and Dependency Management",
        "scale": "Handle data schema changes, prevent stale format deserialization",
        "overview": """Cache versioning enables handling data format changes without full invalidation. Include version in cache key or value; old versions invalidated when schema changes. Careful versioning prevents deserialization errors and enables gradual rollout of format changes.""",
    },
    "30_cache_testing": {
        "title": "Cache Testing Strategies and Simulation",
        "scale": "Verify hit ratios, latency distributions, failure scenarios",
        "overview": """Cache testing requires simulating realistic access patterns, measuring hit ratios, and verifying consistency under failures. Tools: synthetic workloads, recorded production traces, fault injection. Cache behavior varies significantly with workload; testing essential for production confidence.""",
    },
    "31_cache_eviction_tuning": {
        "title": "Cache Eviction Policy Tuning and Optimization",
        "scale": "Workload-specific optimization, 20-30% hit ratio improvement",
        "overview": """Different workloads benefit from different eviction policies (LRU for sequential, LFU for skewed). Tuning involves analyzing access patterns, comparing policies, and selecting optimal configuration. Some systems (ARC, LIRS) adapt dynamically; others require manual tuning.""",
    },
    "32_geohashing_caching": {
        "title": "Geohashing and Spatial Caching",
        "scale": "Geographic data, sub-millisecond range queries",
        "overview": """Geohashing converts latitude/longitude into sortable strings, enabling efficient spatial caching and range queries. Geohash length determines precision; longer hashes more precise but more cache misses. Used in location services, maps, and geo-distributed systems.""",
    },
    "33_cache_monitoring": {
        "title": "Cache Monitoring and Performance Analysis",
        "scale": "Real-time metrics, 1M+ operations/sec monitoring overhead <1%",
        "overview": """Monitor cache hit/miss ratios, eviction rates, memory usage, and latency distributions. Dashboards track performance over time, identifying degradation. Common issues: low hit ratio (query pattern change), high eviction (memory pressure), or high latency (contention). Proactive monitoring prevents customer-visible performance regressions.""",
    },
}

def generate_concept_file(concept_num, concept_key, concept_data):
    title = concept_data["title"]
    scale = concept_data["scale"]
    overview = concept_data["overview"]
    content = f"""# {title}

## System Overview

{overview}

**Scale Metrics:**
- {scale}

## Architecture

### Core Components

```mermaid
graph TB
    A["Cache Layer"]
    B["Storage"]
    C["Access Policy"]
    D["Eviction Engine"]
    E["Statistics"]
    F["Consistency"]

    A -->|cache hit/miss| C
    C -->|triggers| D
    B -->|data source| A
    A -->|evicts| D
    A -->|tracks| E
    A -->|maintains| F

    style A fill:#e1f5ff
    style B fill:#fff3e0
    style C fill:#f3e5f5
    style D fill:#e8f5e9
    style E fill:#fce4ec
    style F fill:#fff9c4
```

### Data Flow Architecture

```mermaid
graph LR
    A["Request"]
    B["Cache Lookup"]
    C["Hit?"]
    D["Cache Return"]
    E["Source Fetch"]
    F["Cache Store"]
    G["Return to Client"]

    A -->|key| B
    B -->|check| C
    C -->|yes| D
    C -->|no| E
    E -->|data| F
    D -->|data| G
    F -->|data| G

    style A fill:#bbdefb
    style B fill:#c8e6c9
    style C fill:#ffe0b2
    style D fill:#f8bbd0
    style E fill:#e1bee7
    style F fill:#b3e5fc
    style G fill:#c8e6c9
```

### Eviction and Memory Management

```mermaid
graph TB
    A["Cache Capacity"]
    B["Memory Usage"]
    C["Threshold Check"]
    D["Eviction Candidate Selection"]
    E["Item Eviction"]
    F["New Item Insertion"]

    A -->|limit| C
    B -->|current| C
    C -->|exceeded| D
    D -->|selects| E
    E -->|frees space| B
    F -->|occupies| B

    style A fill:#ffcdd2
    style B fill:#c8e6c9
    style C fill:#fff9c4
    style D fill:#ffe0b2
    style E fill:#b2dfdb
    style F fill:#c8e6c9
```

### Hit Ratio and Performance

```mermaid
graph TB
    A["Access Pattern"]
    B["Locality Analysis"]
    C["Policy Selection"]
    D["Cache Operation"]
    E["Hit/Miss Tracking"]
    F["Performance Metrics"]

    A -->|input| B
    B -->|optimize| C
    C -->|guide| D
    D -->|record| E
    E -->|measure| F
    F -->|feedback| B

    style A fill:#e3f2fd
    style B fill:#fff3e0
    style C fill:#f3e5f5
    style D fill:#e8f5e9
    style E fill:#fce4ec
    style F fill:#bbdefb
```

### Consistency and Coherence

```mermaid
graph LR
    A["Multi-Copy State"]
    B["Coherence Protocol"]
    C["Update Propagation"]
    D["Verification"]
    E["Consistent State"]

    A -->|monitors| B
    B -->|enforces| C
    C -->|distributes| D
    D -->|verifies| E
    E -->|maintains| A

    style A fill:#ffccbc
    style B fill:#c8e6c9
    style C fill:#fff9c4
    style D fill:#ffe0b2
    style E fill:#b2dfdb
```

## Functional Requirements

1. **Fast Retrieval** - O(1) cache lookup, sub-microsecond latency
2. **Capacity Management** - Enforce memory limits, evict items when full
3. **Eviction Policy** - Select items to evict based on policy (LRU, LFU, ARC, etc.)
4. **Consistency** - Maintain consistency with source data, handle invalidation
5. **Expiration** - Support TTL-based expiration with configurable intervals
6. **Statistics** - Track hit/miss ratios, eviction patterns, memory usage
7. **Concurrency** - Thread-safe operations, handle concurrent access

## Non-Functional Requirements

1. **Latency** - Sub-millisecond hit latency, <10ms miss latency with backend
2. **Capacity** - Scale to billions of entries, terabytes of memory
3. **Hit Ratio** - Achieve 90%+ hit ratio for well-optimized workloads
4. **Throughput** - Support millions of operations per second
5. **Memory Efficiency** - Minimize overhead per cached item
6. **Durability** - Survive process crashes (for persistent caches)
7. **Visibility** - Complete metrics and monitoring for performance analysis

## Data Flow Scenarios

### Scenario 1: Cache Hit
1. Client requests item with cache key
2. Cache lookup performed (hash table O(1))
3. Item found in cache, returned immediately
4. Access time recorded (for LRU/LFU tracking)
5. Statistics updated (hit count incremented)

### Scenario 2: Cache Miss and Load
1. Client requests item
2. Cache lookup fails
3. Source/backend queried
4. Data retrieved and loaded into cache
5. Item evicted if capacity exceeded per policy
6. Data returned to client

### Scenario 3: Expiration and Refresh
1. Item's TTL expires
2. Cache marks item as stale
3. Next access triggers reload from source
4. New data cached with fresh TTL
5. Old copy evicted if new copy loaded

### Scenario 4: Thundering Herd Prevention
1. Popular item expires
2. 1000 concurrent requests for same key
3. Only first request loads from source
4. Others wait for first load to complete
5. All requests served from cache after first load

## Back-of-the-Envelope Calculations

**Cache Capacity Planning:**
- DRAM cost: ~$5 per GB
- 1TB cache: $5,000 hardware cost
- Cache hit ratio: 95% for well-tuned workload
- Backend latency: 100ms without cache
- Cache latency: 1ms with cache
- Effective latency with 95% hit ratio: 5.95ms (0.95*1ms + 0.05*100ms)
- Latency improvement: 16x

**Hit Ratio Economics:**
- Application throughput: 10K QPS
- Backend capacity: 100 QPS (100x overloaded without cache)
- To support 10K QPS at 100 QPS backend: need 99% hit ratio
- 95% hit ratio: supports only 1.9K QPS (1900 miss QPS exceeds 100 QPS backend)
- Hit ratio directly determines scalability

**Memory Overhead:**
- Average item size: 1KB
- Metadata per item: 128 bytes (LRU pointers, timestamps, stats)
- Total per item: 1.128KB
- 1M items: 1.128GB
- 1B items: 1.128TB

**TTL and Expiration:**
- Item lifespan: 1 hour (3600 seconds)
- New items/second: 1000
- Items expiring/second: ~0.28 (1000/3600)
- Eviction overhead: minimal for TTL-based expiration

## Interview Questions

### Q1: How would you implement a thread-safe LRU cache?
**Answer:** Design using HashMap + DoublyLinkedList:
```
LRUCache(capacity):
  hashmap = HashMap() # key -> Node
  head = Node() # dummy head
  tail = Node() # dummy tail
  capacity = capacity

get(key):
  if key not in hashmap: return -1
  node = hashmap[key]
  moveToFront(node) # mark as recently used
  return node.value

put(key, value):
  if key in hashmap:
    node = hashmap[key]
    node.value = value
    moveToFront(node)
  else:
    if len(hashmap) == capacity:
      removeLast() # evict LRU item
    node = Node(key, value)
    addToFront(node)
    hashmap[key] = node

moveToFront(node):
  removeNode(node) # O(1) with pointers
  addToFront(node)

removeNode(node):
  node.prev.next = node.next
  node.next.prev = node.prev

addToFront(node):
  node.next = head.next
  node.prev = head
  head.next.prev = node
  head.next = node
```

Time complexity: O(1) for get/put
Space complexity: O(capacity)

Thread safety requires locks:
```
ReentrantReadWriteLock lock;

synchronized get(key):
  lock.readLock().lock()
  try: return node.value
  finally: lock.readLock().unlock()

synchronized put(key, value):
  lock.writeLock().lock()
  try: // update operations
  finally: lock.writeLock().unlock()
```

### Q2: Explain cache invalidation and strategies to prevent stale data.
**Answer:** Cache invalidation is challenging because cached data becomes stale when source changes. Strategies:

1. **TTL-based (Time-To-Live)**
   - Item automatically expires after fixed duration (e.g., 1 hour)
   - Simple but trades consistency for simplicity
   - Good for slowly-changing data
   - Risk: serve stale data until TTL expires

2. **Event-based Invalidation**
   - Source sends event when data changes
   - Cache immediately invalidates item
   - Ensures freshness but requires change notification infrastructure
   - Coupling between source and cache

3. **Consistency Protocols**
   - Write-through: update cache and source atomically
   - Requires locking, increases write latency
   - Quorum reads: read from majority of replicas
   - Ensures strong consistency but increases latency

4. **Refresh-Ahead**
   - Proactively refresh items before expiration
   - Eliminates cold-start latency
   - Risk: refresh non-accessed items (wasted work)

5. **Versioning**
   - Include version in cache key (foo:v1, foo:v2)
   - On data change, new version created
   - Old version eventually expires
   - Enables gradual rollout, avoids breaking clients

**Best practice:** Use hybrid approach
- Short TTL for consistency-critical data (config, auth)
- Long TTL for slowly-changing data (profiles)
- Event-based for real-time requirements (user state)

### Q3: How would you prevent cache thundering herd?
**Answer:** Thundering herd occurs when popular item expires, causing massive spike in backend requests:

**Prevention strategies:**

1. **Probabilistic Expiration**
```
expiration_time = TTL + random(-TTL*0.25, TTL*0.25)
```
Staggers expirations around nominal TTL, spreading refresh load.

2. **Probabilistic Refresh Before Expiration**
```
if random() < 0.1:  # 10% chance
  background_refresh(key)
```
Items refreshed probabilistically before expiration, reducing simultaneous reloads.

3. **Locking During Miss**
```
if cache_miss(key):
  if try_lock(key):  # only one calculator
    data = load_from_backend(key)
    cache_set(key, data)
    unlock(key)
  else:
    wait_for_lock(key)  # others wait for first load
    return cache_get(key)
```
Single calculator with others waiting prevents duplicate backend requests.

4. **Refresh-Ahead with Timeout**
```
if item_age > TTL * 0.8:  # refresh at 80% of TTL
  background_refresh(key, timeout=100ms)
  # if refresh takes >100ms, serve stale but don't retry
```
Proactive refresh with timeout prevents cascading load.

Example impact:
- 100K concurrent requests for expired item
- Without protection: 100K backend requests (overload)
- With probabilistic expiration: ~10K spread over 30 minutes (manageable)
- With locking: 1 backend request + wait (minimal backend impact)

### Q4: What's the trade-off between write-through and write-back caching?
**Answer:**

| Aspect | Write-Through | Write-Back |
|--------|---|---|
| **Write Latency** | High (source latency dominates) | Low (cache latency dominates) |
| **Consistency** | Strong (cache always valid) | Eventual (cache may be ahead of source) |
| **Data Safety** | Safe (source updated before ack) | Risk of data loss if cache fails |
| **Backend Load** | Every write hits backend | Batch writes reduce backend load |
| **Use Case** | Financial transactions, audit logs | User preferences, analytics |

**Write-Through Example:**
```
put(key, value):
  write_to_source(key, value)  // blocking, 100ms latency
  write_to_cache(key, value)
  return success
```
Simple but slow; good for correctness requirements.

**Write-Back Example:**
```
put(key, value):
  write_to_cache(key, value)  // instant, <1ms latency
  background_flush(key, value)  // async
  return success

background_flush(key, value):
  // runs periodically or on flush trigger
  write_to_source(key, value)
```
Fast but risks:
- Cache failure before flush loses data
- Ordering: concurrent writes may flush in different order
- Durability: RAID/replication needed in cache

**Hybrid Approach:**
- Write-back to cache, sync to source with timeout
- Use WAL (Write-Ahead Log) for durability
- Periodically flush or on explicit fsync call

### Q5: How do you measure and optimize cache hit ratio?
**Answer:** Hit ratio = (hits) / (hits + misses). High hit ratio (>90%) indicates good cache performance.

**Measurement:**
```
Track:
  - cache_hits: counter incremented on each cache hit
  - cache_misses: counter incremented on each cache miss
  - hit_ratio = cache_hits / (cache_hits + cache_misses)
  - miss_rate = 1 - hit_ratio

Monitor by:
  - Key type (which keys miss most?)
  - Time of day (weekday vs weekend patterns?)
  - User segment (authenticated vs anonymous?)
```

**Optimization Techniques:**

1. **Increase Cache Capacity**
   - More items fit in cache
   - Hit ratio increases until working set exceeds capacity
   - Law of diminishing returns; 90% hit ratio needs more capacity than 80%

2. **Change Eviction Policy**
   - LRU: good for sequential/temporal patterns
   - LFU: good for skewed frequency (Zipf) distributions
   - ARC: adapts dynamically
   - Test policies with recorded production traces

3. **Adjust TTL**
   - Longer TTL: higher hit ratio but more stale data
   - Shorter TTL: fresher data but lower hit ratio
   - Workload-specific; trade consistency for hit ratio

4. **Improve Key Design**
   - Avoid cache-busting keys (timestamps in key)
   - Group related items with common prefixes
   - Normalize keys (foo vs FOO vs foo/)

5. **Cache-Aware Query Design**
   - Batch queries to improve cache reuse
   - Avoid redundant requests
   - Preload likely-needed items

**Example Optimization:**
- Initial: 60% hit ratio, 1GB cache
- Increase capacity to 2GB: 75% hit ratio
- Switch to ARC: 82% hit ratio
- Adjust TTL from 1h to 2h: 88% hit ratio
- Optimize query patterns: 92% hit ratio

### Q6: Explain multi-tier caching architecture.
**Answer:** Multi-tier caching uses multiple cache layers with different characteristics:

**Typical Architecture:**
```
L1 (Process Local): In-process cache
  - Latency: <1 microsecond
  - Capacity: 1-100MB per process
  - Scope: Single process
  - Example: HashMap in-memory

L2 (Node Local): Single-node cache
  - Latency: <1 millisecond
  - Capacity: 1-100GB per node
  - Scope: Local machine
  - Example: Redis, Memcached local

L3 (Cluster): Distributed cache
  - Latency: 1-10 milliseconds
  - Capacity: Terabytes across cluster
  - Scope: All services
  - Example: Redis Cluster, DynamoDB

Source (Database): Persistent storage
  - Latency: 10-1000 milliseconds
  - Capacity: Unlimited
  - Scope: Permanent storage
  - Example: PostgreSQL, S3
```

**Data Flow:**
1. Check L1: if miss, check L2
2. Check L2: if miss, check L3
3. Check L3: if miss, fetch from source
4. Populate L3, then L2, then L1 on return

**Consistency Challenge:**
L1 and L2 copies may become inconsistent if only L3/source updated. Solution: invalidation propagation or versioning.

**Trade-offs:**
- More tiers: lower miss latency, higher complexity
- Fewer tiers: simpler, higher latency
- Typical sweet spot: 2-3 tiers

**Example with Math:**
- L1 hit latency: 0.001ms, hit rate 50%
- L2 hit latency: 0.1ms, hit rate 80% (given L1 miss)
- L3 hit latency: 1ms, hit rate 95% (given L2 miss)
- Source latency: 100ms

Expected latency:
- 50% * 0.001ms (L1 hit)
- + 50% * 80% * 0.1ms (L1 miss, L2 hit)
- + 50% * 20% * 1ms (L1/L2 miss, L3 hit)
- + 50% * 20% * 5% * 100ms (all miss, source)
- = 0.0005 + 0.04 + 0.1 + 0.5
- = 0.6405ms average (vs 100ms without cache)

## Technology Stack

- **In-Memory Caches**: Redis, Memcached
- **Local Caches**: Ehcache, Caffeine, Guava Cache
- **Distributed**: Redis Cluster, DynamoDB, Hazelcast
- **Cache-Aside Libraries**: Spring Cache, Hibernate Cache
- **Monitoring**: Prometheus, Grafana, New Relic
- **Testing**: Mockito, Testcontainers
- **Serialization**: JSON, Protocol Buffers, MessagePack

## Lessons Learned

1. **Hit Ratio is Critical** - Even 5% improvement can reduce backend load 50%+
2. **Consistency is Hard** - Cache invalidation harder than expected; plan carefully
3. **Thundering Herd is Real** - Protect with locking or probabilistic expiration
4. **Monitor Everything** - Hit ratio, eviction rate, memory usage all important
5. **Profile Your Workload** - Best policy depends on access patterns
6. **TTL Tuning Takes Time** - Start conservative, gradually increase based on staleness tolerance
7. **Multi-Tier Caching Needed** - Single tier bottleneck; L1+L2+L3 provides best latency
8. **Capacity Planning Essential** - Under-sized cache worse than no cache (thrashing)
"""

    filename = f"{output_dir}/{concept_num:02d}_{concept_key}.md"
    with open(filename, 'w') as f:
        f.write(content)
    print(f"✅ Created: {concept_num:02d}_{concept_key}.md")

print("💾 Creating 30 new caching concepts (4-33)...")
print("=" * 70)
for idx, (key, data) in enumerate(CONCEPTS.items(), start=4):
    generate_concept_file(idx, key, data)
print("=" * 70)
print(f"✨ Created 30 comprehensive caching concepts!")

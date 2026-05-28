# Cache Design Patterns: Strategies and Trade-offs

**Level:** L5
**Time to read:** ~20 min

Master caching strategies for building fast, scalable systems.

---

## Cache Fundamentals

**Why Cache?**
- Database latency: 1-100ms
- Cache latency: 1-10μs
- 1000-10000x faster

**Cache Efficiency Metric:**
```
Hit Ratio = Hits / (Hits + Misses)
Typical targets: 80-95% for production systems
```

---

## Cache Invalidation Strategies

### 1. TTL (Time-To-Live)

```python
# Data expires after N seconds
cache.set(key, value, ttl=3600)  # Expire after 1 hour

# Trade-off:
# ✓ Simple, no coordination needed
# ✗ Stale data for up to TTL duration
```

**When to use:** Non-critical data, acceptable staleness (user profiles, articles)

### 2. Write-Through

```python
# Update cache and DB together
def write(key, value):
    db.write(key, value)
    cache.set(key, value)

# Trade-off:
# ✓ Cache always fresh
# ✗ Slower writes (wait for both cache + DB)
```

**When to use:** Critical data requiring consistency (user account, balance)

### 3. Write-Behind (Write-Back)

```python
# Update cache immediately, DB asynchronously
def write(key, value):
    cache.set(key, value)
    queue.enqueue(update_db_job(key, value))

# Trade-off:
# ✓ Fast writes
# ✗ Risk of data loss if cache crashes before DB update
```

**When to use:** Non-critical data, fault tolerance acceptable (views, analytics)

### 4. Cache-Aside (Lazy Loading)

```python
def read(key):
    value = cache.get(key)
    if value is None:
        value = db.get(key)
        cache.set(key, value, ttl=3600)
    return value

# Trade-off:
# ✓ No cache pollution (load only what's accessed)
# ✗ Cache miss → slow read
```

**When to use:** Most common pattern for read-heavy workloads

### 5. Refresh-Ahead

```python
# Preemptively refresh cache before TTL expires
def read_with_refresh(key):
    value = cache.get(key)
    if value is None or is_about_to_expire(key):
        # Background refresh
        queue.enqueue(refresh_cache_job(key))
        # Return stale if available
        return cache.get_stale(key) or db.get(key)
    return value

# Trade-off:
# ✓ Reduced cache miss rate
# ✗ Complex, always fetching
```

**When to use:** High-traffic items (trending topics, popular products)

---

## Cache Eviction Policies

When cache is full, which item to remove?

| Policy | Evict | Use Case |
|--------|-------|----------|
| **LRU** | Least Recently Used | Most common, general purpose |
| **LFU** | Least Frequently Used | Weighted by access frequency |
| **FIFO** | First In First Out | Simple, fair |
| **Random** | Random item | Fast, less accurate |
| **TTL** | Expired items | Time-based |

**LRU Implementation:**
```python
from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity):
        self.cache = OrderedDict()
        self.capacity = capacity
    
    def get(self, key):
        if key in self.cache:
            self.cache.move_to_end(key)  # Mark as recently used
            return self.cache[key]
        return None
    
    def put(self, key, value):
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)  # Remove oldest
```

---

## Cache-Stampede & Solutions

**Problem:** Multiple requests cache miss simultaneously, all hit database.

```
t=0: User A requests data, cache miss
t=1: User B requests data, cache miss (same key)
t=2: User C requests data, cache miss (same key)
     Database hit with 3 requests simultaneously
     Instead of 1 request every hour
```

**Solutions:**

```python
# 1. Lock-based: Only first gets DB, others wait
def read_with_lock(key):
    value = cache.get(key)
    if value is None:
        with lock.acquire(key):
            value = cache.get(key)  # Double-check
            if value is None:
                value = db.get(key)
                cache.set(key, value)
    return value

# 2. Probabilistic: Refresh before expiry with small probability
def read_with_probability_refresh(key):
    value = cache.get(key, with_ttl=True)
    if value is None:
        return db.get(key)
    if is_expiring_soon(ttl):
        if random.random() < 0.1:  # 10% chance to refresh
            queue.enqueue(refresh_job(key))
    return value
```

---

## Cache Consistency Challenges

### Distributed Cache Invalidation

```
Problem: You update user profile in DB
         Need to invalidate cache in 100 cache servers

Solution 1: Publish event → All servers listen and invalidate
Solution 2: Cache server on write → Check version on read
Solution 3: TTL expires cache automatically (simplest)
```

### Read-After-Write Consistency

```python
# Problem: Client writes, immediately reads, gets stale data
# Solution: After write, serve from origin or wait for cache update

def write_and_read(user_id, new_value):
    db.update(user_id, new_value)
    cache.invalidate(user_id)  # Or wait for cache update
    return db.read(user_id)  # Read fresh from DB
```

---

## Cache Warming

**Problem:** Cold start (cache empty, all requests hit database).

```python
# Preload common data on startup
def cache_warmup():
    popular_items = db.query("SELECT * FROM products WHERE views > 10000 LIMIT 1000")
    for item in popular_items:
        cache.set(f"product:{item.id}", item)
```

---

## Cache Monitoring

**Key Metrics:**
- Hit ratio (target > 80%)
- Eviction rate (increase capacity if high)
- Latency p50, p99
- Cache size vs capacity

**Alerts:**
- Hit ratio < 70% → Increase capacity or TTL
- Eviction rate spike → Unusual traffic pattern
- Memory usage > 90% → Scale cache

---

## Real Interview Scenarios

### Scenario 1: User Profile Cache at Uber Scale

```
Requirements:
- 1M active users, each user accessed 100x/day
- Profile: name, rating, history (1KB each)
- Updates: every hour on average
- SLA: <10ms for reads

Cache Strategy:
1. Cache type: Redis (distributed, fast)
2. Invalidation: TTL 1 hour + write-through
   - TTL handles eventual updates
   - Write-through for immediate profile changes
3. Key: "user:{user_id}"
4. Capacity: 1M × 1KB = 1GB (cheap, fits in memory)
5. Eviction: LRU (least active users)
6. Warmup: Pre-load top 100K users on startup

Hit ratio target: 95% (100 requests/day per user)
Expected: ~190 requests hit cache, 10 to DB
```

### Scenario 2: Social Feed with Caching

```
Requirements:
- 10M users, 1M active daily
- Feed: 100 posts per user (cached)
- Writes: New post every 5 minutes (user average)
- SLA: <100ms

Cache Strategy:
1. Cache type: Redis (supporting pub/sub for invalidation)
2. Invalidation: Cache-aside + event-based invalidation
   - Read: Check cache, if miss, query DB
   - Write: Publish "feed_changed" event
   - Subscribers: Invalidate affected user feeds
3. Key: "feed:{user_id}:{page}"
4. TTL: 12 hours (feeds eventually get old)
5. Capacity: 1M users × 100 posts × 100 bytes = 10GB

Problem: Feed changes every 5 minutes (new post from followed users)
Solution: Use "push" model instead of "pull"
- When user posts, push to all followers' feeds
- Cache the pre-computed feed
- TTL as safety net if push fails
```

### Scenario 3: Cache Hotspot (Celebrity on Instagram)

```
Problem:
- Celebrity posts, 1M likes/minute
- Each like increments view counter
- Redis single key becoming bottleneck

Solutions:
1. Local counters (in-process)
   - Each server maintains local count
   - Periodic flush to Redis (e.g., every 10s)
   - Tradeoff: Eventual consistency, ~10s lag
   
2. Counter sharding
   - Split into multiple keys: "likes:{post_id}:{shard}"
   - Each request hits random shard
   - Reduces hotspot from 1M to 100K qps/shard
   
3. Probabilistic counting (HyperLogLog)
   - Approximate count (good enough for display)
   - O(1) space, accurate to 99%
```

---

## Interview Decision Tree for Cache Design

```
Q1: What are you caching?
├─ Static content (images, CSS) → CDN
├─ User data (profile, settings) → Redis with TTL
├─ Frequently computed (recommendations) → Redis with refresh-ahead
└─ Hot data (trending posts) → Local cache + Redis

Q2: How often does data change?
├─ Never (static) → Long TTL (1 day)
├─ Rarely (profile) → Medium TTL (1 hour) + write-through
├─ Often (feed) → Short TTL (1 min) + event-based invalidation
└─ Always (live counter) → Don't cache, or use approximate

Q3: What's the read:write ratio?
├─ 100:1 (read-heavy) → Aggressive caching, simple invalidation
├─ 10:1 (mixed) → Cache-aside, event-based invalidation
└─ 1:1 (write-heavy) → Light caching, cache-aside only

Q4: How much data?
├─ <100MB → Single Redis instance
├─ 100MB-10GB → Redis cluster
├─ >10GB → Distributed cache (sharding) + local cache (CDN)
└─ Unbounded → CDN for static, light cache for hot

Q5: Consistency requirements?
├─ Strong (payment, balance) → Write-through or don't cache
├─ Eventual (profile, feed) → TTL + write-through on explicit updates
└─ Weak (views, recommendations) → Cache-aside, long TTL
```

---

## Cache Design Checklist

**During Interview:**
- ✓ Identified what to cache (hot data, frequent access, slow compute)
- ✓ Calculated cache hit ratio target (80-95% typically)
- ✓ Chose invalidation strategy with clear rationale
- ✓ Set TTL appropriately (not too short, not too long)
- ✓ Handled cache miss path (circuit breaker, fallback to DB)
- ✓ Identified cache-stampede risk and mitigation
- ✓ Planned for capacity (memory budget, growth)
- ✓ Discussed eviction policy (LRU most common)
- ✓ Explained monitoring (hit ratio, latency, memory)
- ✓ Mentioned cache warming for large caches

**Implementation Focus:**
- ✓ Cache key design (namespace, expiring keys cleanup)
- ✓ Error handling (cache failures shouldn't break system)
- ✓ Consistency model (strong vs. eventual)
- ✓ Scalability (single vs. distributed cache)
- ✓ Monitoring metrics (hit ratio target, alerts)


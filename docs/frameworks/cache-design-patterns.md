# Cache Design Patterns: Strategies and Trade-offs

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

## Cache Selection Guide

| Cache Type | Latency | Capacity | Use Case |
|-----------|---------|----------|----------|
| **Local** (in-process) | 1μs | Limited (RAM) | Single server |
| **Redis** | 1ms | Large (distributed) | Shared across servers |
| **Memcached** | 1ms | Large | Simple key-value |
| **CDN** | 10-50ms | Unlimited (distributed) | Static content |

---

## Cache Design Checklist

- ✓ Identified what to cache (frequently accessed, slow to compute)
- ✓ Chose invalidation strategy (TTL, write-through, cache-aside)
- ✓ Set appropriate TTL
- ✓ Designed for cache miss (DB fallback, circuit breaker)
- ✓ Planned for cache-stampede (locks or probability refresh)
- ✓ Monitoring in place (hit ratio, eviction rate, latency)
- ✓ Cache warming strategy if needed
- ✓ Consistency plan for updates (invalidation, refresh)
- ✓ Capacity planning (memory budget, eviction policy)


# Caching & In-Memory Stores — Redis, Memcached, and Beyond

Fast data access with intelligent eviction and persistence strategies.

---

## ⚖️ Storage Layer Comparison

```
Storage Type    | Latency      | Durability | Volatility | Cost/GB | Use Case
────────────────|──────────────|───────────────────|─────────|──────────
In-Memory (RAM) | <1ms         | None       | Volatile  | High    | Cache
SSD Disk        | 1-10ms       | Strong     | Persistent| Medium  | Hot data
HDD Disk        | 100ms        | Strong     | Persistent| Low     | Cold data
Cloud Storage   | 100-1000ms   | Very Strong| Persistent| Very Low| Archive

When In-Memory Cache:
├─ Sub-millisecond latency required
├─ Tolerate data loss (can recompute)
├─ Hot data (frequently accessed)
├─ Session data, leaderboards
└─ Real-time features

When Disk/Database:
├─ Durability critical
├─ Data cannot be lost
├─ Can tolerate 1-100ms latency
├─ Larger datasets (100GB+)
└─ Long-term storage
```

---

## 🔑 Redis Data Structures & Operations

### Strings
```
SET key value [EX seconds]
GET key
INCR counter           (atomic increment)
APPEND key value
GETRANGE key 0 5

Time Complexity: O(1)
Use Case: Sessions, tokens, counters
```

### Hashes (Object storage)
```
HSET user:1 name Alice email alice@example.com
HGET user:1 name         → "Alice"
HGETALL user:1           → {name: "Alice", email: "..."}
HINCRBY user:1 age 1     (atomic increment)

Time Complexity: O(1) per field, O(n) for HGETALL
Use Case: User objects, nested data
Better than: Multiple string keys (fewer network calls)
```

### Lists (Queues)
```
RPUSH queue task1 task2 task3    (append)
LPOP queue                        (pop from front)
LLEN queue                        (get length)
LRANGE queue 0 -1                 (get all)
BRPOP queue 0                     (blocking pop)

Time Complexity: O(1) for RPUSH/LPOP, O(n) for LRANGE
Use Case: Job queues, message buffers
Pattern: Producer → RPUSH, Consumer → LPOP
```

### Sets (Unique values)
```
SADD tags python javascript devops
SMEMBERS tags                           → {"python", "javascript", "devops"}
SISMEMBER tags python                   → 1 (exists)
SINTER tags1 tags2                      (intersection)
SUNION tags1 tags2                      (union)

Time Complexity: O(1) for add/check, O(n) for SMEMBERS
Use Case: Tags, followers, unique visitors
Pattern: Track unique users: SADD daily_users user_1
```

### Sorted Sets (Ranking)
```
ZADD leaderboard 100 player1 95 player2 90 player3
ZRANGE leaderboard 0 -1 WITHSCORES       → [(player3, 90), (player2, 95), (player1, 100)]
ZREVRANGE leaderboard 0 -1               → [(player1, 100), (player2, 95), (player3, 90)]
ZSCORE leaderboard player1               → 100
ZINCRBY leaderboard 5 player2            → 100 (new score)
ZRANK leaderboard player2                → 2

Time Complexity: O(log n) for add/update, O(n log n) for range
Use Case: Leaderboards, priority queues, time-series
Pattern: Real-time ranking (update in O(log n))
```

### Streams (Log/Queue hybrid)
```
XADD events * user_id 123 action "login"
XREAD STREAMS events 0                    (read all)
XRANGE events - +                         (time range)
XLEN events                               (length)

Time Complexity: O(1) add, O(n) read
Use Case: Event logging, message streams, activity feed
Pattern: Kafka-lite for single-node systems
```

---

## 💾 Persistence Strategies

### RDB (Redis Database Snapshot)

```
How it works:
1. Background process forks
2. Saves memory snapshot to disk (rdb file)
3. Fast recovery on restart

Pros:
├─ Compact (compressed)
├─ Fast backup (entire state at point-in-time)
├─ Fast recovery (load snapshot)
└─ Space efficient

Cons:
├─ Data loss between snapshots (seconds to minutes)
├─ Fork can cause pauses (large datasets)
└─ Not durable (async writes)

Configuration:
SAVE 900 1         (save if 1 key changed in 900 sec)
SAVE 300 10        (save if 10 keys changed in 300 sec)
SAVE 60 10000      (save if 10000 keys changed in 60 sec)
```

### AOF (Append-Only File)

```
How it works:
1. Every write command appended to aof file
2. Replay aof on startup to reconstruct state
3. Can rewrite aof to reduce size

Pros:
├─ Very durable (fsync after every command)
├─ Complete write history
├─ Can replay specific point-in-time
└─ Incremental

Cons:
├─ Larger file size (commands not compressed)
├─ Slower writes (fsync overhead)
├─ Rewrite can cause pauses
└─ Recovery slower (replay all commands)

Configuration:
appendfsync always       (fsync after every command, slowest)
appendfsync everysec     (fsync every 1 sec, balanced)
appendfsync no           (OS decides, fastest, less durable)
```

### Hybrid (RDB + AOF)

```
Recommended Strategy:
1. RDB: Periodic snapshots (fast backup)
2. AOF: Continuous command log (durable)
3. Recovery: Load RDB, then replay AOF

Example:
├─ RDB every 1 hour (checkpoint)
├─ AOF with appendfsync=everysec (1 sec risk window)
├─ On failure: Load hour-old RDB + last 1 sec of AOF
├─ Data loss: < 1 second
└─ Recovery time: Fast (RDB + partial AOF)
```

---

## 🔄 Replication & High Availability

### Replication Architecture

```
Master (Primary):
├─ Accepts writes
├─ Replicas pull changes

Replica 1, 2, 3:
├─ Read-only copies
├─ Async replication (eventual consistency)
├─ Can serve reads

Replication lag: < 1 second typical
```

### Sentinel (Automatic Failover)

```
Sentinel Nodes (3+):
├─ Monitor master health
├─ Detect failures
├─ Promote replica if needed

Configuration:
sentinel monitor master_name 127.0.0.1 6379 2
(needs 2 sentinels to agree on failure)

Failover Process:
1. Master crashes
2. Sentinels detect (timeout 30 sec default)
3. Quorum vote (2/3 agree)
4. Promote replica to master
5. Reconfigure other replicas
6. Announce new master to clients
Time: 30-50 seconds
```

### Cluster (Horizontal Sharding)

```
Cluster Setup:
├─ 3+ master nodes (shards)
├─ Each masters 1/N keys
├─ Replicas for each master (HA)

Hash Slot Distribution:
├─ 16384 hash slots (0-16383)
├─ key_slot = CRC16(key) % 16384
├─ Master 1: slots 0-5460
├─ Master 2: slots 5461-10922
├─ Master 3: slots 10923-16383

Cluster Query:
1. Client computes hash slot
2. Sends to correct master
3. Master processes

Scaling:
├─ Add new master node
├─ Migrate 1/N hash slots to new node
├─ Rebalances load

Trade-off:
├─ Horizontal scale (good)
├─ Transaction support limited
├─ Lua scripts must be single slot
└─ Operational complexity
```

---

## 📊 Memory Management

### Eviction Policies

```
Policy           | When to Use          | Behavior
─────────────────|──────────────────────|──────────────
noeviction       | Nothing evicted      | Return error when full
allkeys-lru      | Generic cache        | Evict least recently used
allkeys-lfu      | Variable frequency   | Evict least frequently used
allkeys-random   | Non-critical         | Evict random key
volatile-lru     | With TTL             | Evict expired first, then LRU
volatile-lfu     | With TTL             | Evict expired first, then LFU
volatile-random  | With TTL             | Evict expired first, then random
volatile-ttl     | With TTL             | Evict shortest TTL

Typical Choice: allkeys-lru (good default for cache)
```

### Memory Optimization

```
Memory Usage Calculation:
├─ Object overhead: ~95 bytes per object
├─ String value: actual size + 44 bytes
├─ Hash field: field name + value + overhead

Example:
SET user:1:name "Alice"
├─ Key overhead: 95 bytes
├─ Key size: 11 bytes
├─ Value overhead: 44 bytes
├─ Value size: 5 bytes
├─ Total: ~155 bytes per entry

Optimization:
1. Use shorter key names (important at scale)
   ├─ "user:1:name" → "u:1:n"
   ├─ Saves 8 bytes per key
   └─ Millions of keys → GB saved
2. Use HSET (hash) instead of multiple strings
   ├─ Single hash: overhead once
   ├─ Multiple strings: overhead per field
3. Compression: GZIP compress large values
4. Set TTL: Auto-expire old data
```

---

## 🚀 Caching Patterns

### Cache-Aside (Lazy Loading)

```
Application:
1. Try GET from cache
2. If miss: Query database
3. SET in cache with TTL
4. Return data

Code:
function get_user(user_id):
    cached = REDIS.get(f"user:{user_id}")
    if cached: return deserialize(cached)
    
    user = DB.query(f"SELECT * FROM users WHERE id={user_id}")
    REDIS.setex(f"user:{user_id}", 3600, serialize(user))
    return user

Trade-offs:
✓ Simple to implement
✓ Only cache accessed data
✗ Cache miss on first access
✗ Stale data if not expired

When: Most common pattern
```

### Write-Through

```
Application:
1. Write to both cache AND database
2. Ensure consistency

Code:
function update_user(user_id, data):
    DB.update(f"UPDATE users SET ... WHERE id={user_id}", data)
    REDIS.setex(f"user:{user_id}", 3600, serialize(data))
    return "Updated"

Trade-offs:
✓ Cache always consistent with DB
✓ No stale reads
✗ Slow writes (2 operations)
✗ Cache polluted with writes

When: Critical data, strong consistency needed
```

### Write-Behind (Write-Back)

```
Application:
1. Write to cache
2. Async write to database

Code:
function update_user(user_id, data):
    REDIS.setex(f"user:{user_id}", 3600, serialize(data))
    QUEUE.enqueue({op: "update", user_id, data})
    return "Updated"
    
Background Job:
    while True:
        msg = QUEUE.dequeue()
        DB.update(msg)

Trade-offs:
✓ Fast writes (cache only)
✓ Batch updates to DB
✗ Data loss risk (if Redis crashes)
✗ Complex to implement

When: High-write scenarios, accepts risk
```

---

## ❓ Comprehensive Interview Q&A

**Q: Design caching strategy for user feed (100M users)**

A:
```
Requirements:
├─ 100M users
├─ Each user has 500 followers
├─ Feed = recent posts from followers
├─ 1000 posts/sec write rate

Architecture:

Cache Layer:
├─ Feed cache: {user_id} → [post_id, post_id, ...]
├─ Post cache: {post_id} → {author, content, timestamp}
├─ TTL: 1 hour (feed changes, posts stay longer)

Implementation:

When user posts:
1. INSERT into Database
2. LPUSH feed:{follower_id} post_id (for each follower)
3. SET post:{post_id} post_data (with long TTL)

When user views feed:
1. LRANGE feed:{user_id} 0 99 (first 100 posts)
2. MGET post:{post_id} (get post details)
3. Combine and return

Cache Invalidation:
├─ Feed: TTL-based (1 hour)
├─ Post: Long TTL (24 hours)
├─ User actions: Delete on unfollow

Memory Usage:
├─ Feeds: 100M users × 100 posts × 8 bytes = 80GB
└─ Posts: 1M active posts × 1KB = 1GB
└─ Total: ~100GB Redis cluster (3 nodes × 40GB)

Scaling:
├─ If 100GB too much: Cache top 50 followers only
├─ Fanout-on-read: Query follower DB, aggregate feed
└─ Hybrid: Cache hot users, compute for cold users
```

**Q: Cache warm-up strategy**

A:
```
Scenario: Redis restart loses all cache

Options:

1. Pre-warming (Proactive):
   On startup:
   ├─ Load top 1000 users' feeds
   ├─ Load popular posts
   ├─ Takes 5-10 minutes
   ├─ Users see slow feeds initially, then fast
   
   Code:
   def warmup():
       for user in TOP_1000_USERS:
           feed = DB.get_user_feed(user)
           REDIS.setex(f"feed:{user}", 3600, feed)

2. Lazy Loading (Reactive):
   ├─ Cache misses on first access
   ├─ Instant restart (no warm-up time)
   ├─ First users see slow feeds
   ├─ Automatically warms as users access
   
   Code:
   def get_feed(user_id):
       cached = REDIS.get(f"feed:{user_id}")
       if cached: return cached
       feed = DB.get_user_feed(user_id)  # slow
       REDIS.set(f"feed:{user_id}", feed)
       return feed

3. Hybrid:
   ├─ Pre-warm top 10% of users (hot)
   ├─ Lazy load remaining 90% (cold)
   ├─ Balance: 2-minute warm-up + fast access
   
   Code:
   def startup():
       # Warm hot users
       for user in TOP_10_PERCENT:
           feed = DB.get_user_feed(user)
           REDIS.setex(f"feed:{user}", 3600, feed)

Recommendation: Hybrid approach
```

**Q: Handle cache failures gracefully**

A:
```
Failure Scenarios:

1. Cache Miss (Normal):
   └─ Query DB, cache result
   └─ User sees 100ms latency instead of 10ms

2. Cache Down (No connection):
   ├─ Circuit breaker pattern (detect quickly)
   ├─ Fall back to DB directly
   ├─ Log error, alert ops
   └─ User sees slow response (acceptable)

3. Partial Failure (Some nodes down):
   ├─ In cluster: Some nodes unreachable
   ├─ Replica setup: Use replica
   ├─ Fallback: Query DB
   └─ User sees slow response (acceptable)

Implementation (Python):

def get_user_cached(user_id):
    try:
        # Try cache (fast)
        result = REDIS.get(f"user:{user_id}")
        if result:
            return deserialize(result)
    except RedisException as e:
        LOGGER.error(f"Cache error: {e}")
        # Continue to DB

    # Cache miss or error, query DB
    try:
        result = DB.query(f"SELECT * FROM users WHERE id={user_id}")
        # Try to populate cache, but don't fail if Redis is down
        try:
            REDIS.setex(f"user:{user_id}", 3600, serialize(result))
        except RedisException:
            pass  # Cache error is not critical
        return result
    except DBException as e:
        LOGGER.error(f"Database error: {e}")
        # Return error to user (unavoidable)
        return None

Key Principles:
├─ Cache is optional (not required for correctness)
├─ DB is mandatory (required for correctness)
├─ Fail gracefully: Fast failure → DB fallback
├─ Monitor: Alert if cache frequently unavailable
└─ Don't propagate cache errors to users

Monitoring:
├─ Cache hit rate (target: >80%)
├─ Cache availability (target: >99.9%)
├─ DB load (spike when cache down)
└─ User latency (degrades on cache failure, acceptable)
```

---

## 💡 Interview Tips

**What interviewer is really asking:**
- "Cache strategy" → Do you know cache-aside, write-through patterns?
- "Failures" → Do you understand fallback to DB, circuit breaker?
- "Warm-up" → Do you know pre-loading vs. lazy loading?
- "Memory" → Do you understand eviction policies, TTL?

**How to answer:**
1. **Identify use case:** Session? Feed? Leaderboard?
2. **Choose data structure:** String, Hash, Sorted Set, etc.
3. **Set TTL:** Avoid stale data
4. **Handle failures:** Graceful degradation to DB
5. **Monitor:** Hit rate, availability, latency
6. **Scale:** Replication, clustering, sharding

---

**Last updated:** 2026-05-22

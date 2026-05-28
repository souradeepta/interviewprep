# Caching Strategies — Making Systems Fast

**Level:** L4-L5
**Time to read:** ~10 min

Where, when, and how to cache.

---

## 📍 Cache Levels

### Browser Cache

```
Client stores static assets locally
Headers: Cache-Control, ETag, Last-Modified
Cache-Control: max-age=3600 (1 hour)
```

### CDN Cache

```
Geographically distributed servers
Static content replicated globally
Example: CloudFlare, CloudFront, Akamai
Reduces latency, bandwidth
```

### Application Cache

```
In-memory store (Redis, Memcached)
Fast access (microseconds vs. seconds for DB)
Volatile (data lost on restart)
```

### Database Cache

```
Database caches query results internally
Query result cache, buffer pool
Transparent to application
```

---

## 🔑 Caching Patterns

### Cache-Aside

```
1. Try to get from cache
2. If miss, get from DB
3. Store in cache for future

Code:
value = cache.get(key)
if not value:
    value = db.get(key)
    cache.set(key, value)
return value

Pro: Lazy loading
Con: Cache misses, stale data risk
```

### Write-Through

```
1. Write to cache
2. Write to DB
3. Both succeed or fail

Pro: Cache always up-to-date
Con: Slower writes, extra latency
```

### Write-Behind

```
1. Write to cache immediately
2. Asynchronously write to DB

Pro: Fast writes
Con: Risk of data loss, inconsistency

Use: Non-critical data
```

---

## 🚨 Cache Invalidation

**Cache invalidation is one of the hardest problems in CS**

### Time-Based (TTL)

```
cache.set(key, value, ttl=3600)
Auto-expire after 1 hour
Simple, works for most use cases
Risk: Stale data up to 1 hour
```

### Event-Based

```
When data changes, invalidate cache
cache.delete(key)
Best: Real-time updates
Con: Complex, must remember to invalidate
```

### LRU Eviction

```
Least Recently Used items evicted when full
Automatic, no configuration
Good balance of memory and hit rate
```

---

## 📊 Cache Metrics

```
Hit rate: % of requests from cache
Miss rate: % of requests from origin
Latency: Time from request to response
Cost: Cache storage + computation
```

---

## ❓ Interview Q&A

**Q: Design caching for a social media feed.**
A: Cache-aside: Try Redis, fallback to DB. TTL 5 min (balance freshness). Invalidate on like/comment. Pre-compute trending posts.

**Q: How much should you cache?**
A: Hot data (80/20 rule: 20% of data serves 80% of requests). Working set size. Monitor hit rate, adjust TTL.

**Q: Cache stampede, what is it and how to prevent?**
A: Many concurrent requests on expired key → all hit DB. Prevention: Probabilistic early expiration, lock on miss.

---

**Last updated:** 2026-05-22

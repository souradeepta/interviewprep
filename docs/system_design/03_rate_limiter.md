# Rate Limiter

## Problem Statement

Implement a rate limiter to control request frequency. Support multiple algorithms and per-user limits.

**Operations:**
- `is_allowed(user_id)` — return True if request allowed, False if rate limit exceeded

**Constraints:**
- Support: Token Bucket, Sliding Window Log, Sliding Window Counter
- Per-user rate limits
- Time-based refill

## Design

### Token Bucket Algorithm

```
Tokens refill at rate R tokens/second
Bucket capacity: C

    [T T T T T]  (full bucket)
    
User requests 1: [T T T T]  (1 token consumed)
User requests 3: [T]        (3 tokens consumed)
After 1 sec:     [T T]      (refill at rate R)
```

**Complexity:** O(1) per request

### Sliding Window Log

```
Track timestamps of all requests in current window

Window (last 60s): [t1, t3, t8, t12, ...]
New request: Check if count < limit in window, add timestamp
```

**Complexity:** O(n) where n = requests in window

### Sliding Window Counter

```
Divide time into fixed intervals (1s buckets)
Count requests per bucket

Buckets:  [10 requests] [5 req] [3 req] (last 3 buckets)
New req:  Check if count < limit
```

**Complexity:** O(1)

## Trade-offs

| Algorithm | Pro | Con |
|-----------|-----|-----|
| Token Bucket | Simple, bursty traffic ok | Tuning params (rate, capacity) |
| Sliding Window Log | Accurate | O(n) memory, O(n) per request |
| Sliding Window Counter | Fast, O(1) | Less accurate than log |

## Complexity

| Operation | Token Bucket | Sliding Log | Sliding Counter |
|-----------|--------------|------------|-----------------|
| is_allowed | O(1) | O(n) | O(1) |
| Space | O(users) | O(users × requests) | O(users × buckets) |

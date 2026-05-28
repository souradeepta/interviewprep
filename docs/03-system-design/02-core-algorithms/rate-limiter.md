# Rate Limiter

**Level:** L3-L5+
**Time to read:** ~30 min

## Problem Statement
Design a rate limiter that restricts how many requests a client can make in a given time window. This appears simple but hides hard trade-offs: accuracy vs memory, single-node vs distributed, per-user vs global limits. Rate limiters are foundational to API security (prevent abuse), cost control (limit expensive operations), and reliability (shed load under pressure). Getting this wrong causes either over-blocking legitimate users or under-blocking abusers.

## Functional Requirements
- Enforce request limit per client (e.g., 100 requests/minute per API key)
- Return HTTP 429 (Too Many Requests) with Retry-After header when limit exceeded
- Support multiple granularities: per-user, per-IP, per-endpoint, global
- Allow burst headroom above sustained rate (configurable)
- Admin API to update limits without restart

## Non-Functional Requirements
- **Scale:** 100M DAU, 500K API requests/sec globally
- **Latency:** Rate limit check adds < 2 ms to request path (P99)
- **Availability:** 99.99% — rate limiter failure should fail-open (allow traffic) not fail-closed
- **Consistency:** eventual OK for most cases; strong consistency only for high-value operations (payment APIs)

---

## Tier 1: L3-L4 Design (the basic interview answer)

### Back-of-Envelope
```
Scale:
  - 100M DAU, avg 50 API calls/day = 5B calls/day
  - Peak: 5B / 86,400 × 3× peak factor = ~174K calls/sec
  - Round up: 500K calls/sec across fleet

Memory (token bucket per user):
  - Per-user state: 24 bytes (tokens_remaining float, last_refill_ts int64, lock)
  - 100M users × 24 bytes = 2.4 GB — fits comfortably in Redis

Check latency budget:
  - Redis round-trip: 0.5–1 ms local AZ
  - Redis Lua atomic script: 1 round-trip instead of 2 (GET + SET)
  - Total overhead: 1–2 ms ← within budget
```

### Architecture Diagram
```
Client → Load Balancer → API Gateway
                              │
                              ▼
                     ┌─────────────────┐
                     │  Rate Limiter   │  (in-process OR sidecar)
                     │  Middleware     │
                     └────────┬────────┘
                              │  check(client_id, limit)
                              ▼
                     ┌─────────────────┐
                     │  Redis Cluster  │  (shared state)
                     │  (token state)  │
                     └─────────────────┘
                              │
                    ┌─────────┴──────────┐
                    ▼                    ▼
             Allow request          Return 429
             (proceed to            + Retry-After header
              backend)
```

### Data Model
```
Token Bucket (per client in Redis):
  Key: "rl:{user_id}:{endpoint}"
  Value (hash):
    tokens:        float     # current token count
    last_refill:   int       # unix timestamp ms
    limit:         int       # max tokens (burst ceiling)
    rate:          float     # tokens added per second

Sliding Window Log (per client):
  Key: "rl:log:{user_id}"
  Type: Redis Sorted Set
  Member: request_id
  Score: unix timestamp ms
  (TTL = window size)

Fixed Window Counter:
  Key: "rl:fw:{user_id}:{window_start_ts}"
  Value: int (request count)
  TTL: window size
```

### API Design
```
Internal (middleware function):
  check_rate_limit(client_id, endpoint, limit, window_sec) → (allowed: bool, remaining: int, retry_after_sec: int)

External (admin REST):
  GET  /ratelimit/config/{client_id}          → {limit, window, algorithm}
  PUT  /ratelimit/config/{client_id}          → update limits
  GET  /ratelimit/status/{client_id}          → {tokens_remaining, window_reset_ts}
  POST /ratelimit/reset/{client_id}           → reset counter (admin)

Response headers on each API response:
  X-RateLimit-Limit:     100
  X-RateLimit-Remaining: 42
  X-RateLimit-Reset:     1716825600  (epoch when window resets)
  Retry-After:           30          (only on 429)
```

### Basic Scaling
- **Single node:** in-process token bucket; no network hop; works for single-server APIs
- **Redis cluster:** shared state for distributed rate limiting; partition by `hash(client_id) % num_shards`
- **Local + Redis hybrid:** L1 in-process (approximate, fast) + L2 Redis (authoritative, slower)
- **Fail-open policy:** if Redis is unreachable, allow requests through (don't block due to limiter failure)

---

## Tier 2: L5+ Design (the staff interview answer)

### The 5 Algorithms: Full Comparison

```
Algorithm Comparison
─────────────────────────────────────────────────────────────────────────
                  Fixed    Sliding   Sliding    Token    Leaky
                  Window   Window    Window     Bucket   Bucket
                           Log       Counter
─────────────────────────────────────────────────────────────────────────
Accuracy          Low      High      Med-High   High     High
Memory/user       O(1)     O(N req)  O(windows) O(1)     O(1)
Burst handling    Allows   Blocks    Partial    Allows   Smooths
                  at edge  exactly   burst      burst    burst
Distributed?      Easy     Hard      Medium     Medium   Medium
Implementation    Trivial  Complex   Medium     Medium   Simple
Race conditions   Yes      Need lock Need lock  CAS/Lua  CAS/Lua
─────────────────────────────────────────────────────────────────────────

Fixed Window flaw:
  - 100 req/min limit; window boundary at :00
  - User sends 100 req at :59 and 100 req at :01 → 200 req in 2 seconds
  - "Boundary burst" attack

Sliding Window Log fix:
  - Store every request timestamp; evict entries older than window
  - Check: len(log) >= limit → reject
  - Memory: O(limit) per user — bad at high limits (e.g., 10K req/min)

Sliding Window Counter (compromise):
  - Two fixed windows + interpolation
  - current_count = prev_window_count × (1 - elapsed/window) + cur_window_count
  - O(1) memory, ~5% error vs true sliding window

Token Bucket (recommended for most APIs):
  - Bucket fills at rate R tokens/sec, max capacity = burst_size
  - Request costs 1 token; rejected if bucket empty
  - Natural burst support + simple math

Leaky Bucket (network-style smoothing):
  - Requests enter queue; processed at fixed rate
  - Excess requests dropped or queued
  - No bursting — uniform output rate
  - Good for: downstream rate protection, not user-facing APIs
```

### Capacity Planning (Real Numbers)
```
Redis memory for 100M users (token bucket):
  - Per-user: 2 fields (tokens, last_refill) + key overhead
  - Redis hash: ~85 bytes/key with overhead
  - 100M × 85 bytes = 8.5 GB → single Redis node (64 GB) holds 750M users

Redis ops:
  - 500K API calls/sec × 1 Redis check each = 500K Redis ops/sec
  - Single Redis: ~1M simple ops/sec (sufficient)
  - Redis cluster (3 shards): 3M ops/sec capacity; 3× headroom

Sliding window log (high-limit endpoints):
  - 10K req/min limit = up to 10K timestamps stored per user
  - 10M concurrent users × 10K entries × 8 bytes = 800 GB — not feasible
  - Use token bucket instead for high limits
```

### Failure Modes
```
Redis failure (rate limiter unavailable):
  - Decision: fail-open (allow all) vs fail-closed (block all)
  - Recommended: fail-open with circuit breaker logging
  - Fallback: in-process approximate counter for 60s until Redis recovers

Race condition (distributed check-then-act):
  - Naive: GET tokens → compute new value → SET (2 ops, not atomic)
  - Fix: Redis Lua script (atomic execution on single shard)
  - Fix: Redis INCR + EXPIRE (atomic for fixed window)

Clock skew across nodes:
  - Problem: two API servers have 500ms clock difference → wrong window boundaries
  - Fix: use Redis server time (TIME command) as authoritative clock source
  - Fix: NTP with < 10ms accuracy is sufficient for most use cases

Hot-key problem:
  - Viral API key hammers single Redis shard
  - Fix: local in-process L1 cache (5-second TTL) absorbs burst
  - Fix: key suffixing (add random suffix, aggregate N counters)

Token refill granularity:
  - Continuous refill: accurate but requires float arithmetic
  - Discrete refill (per-second cron): simpler but creates micro-bursts at refill time
  - Recommendation: lazy refill — compute tokens earned since last_refill on each request
```

### Consistency Boundaries
```
Strong consistency (payment/auth APIs):
  - Use Redis single-shard with Lua script (serialized per key)
  - Trade-off: 2–5 ms Redis round-trip on every request
  - Use case: prevent double-charges, login brute-force

Eventual consistency (general APIs):
  - In-process counter with periodic Redis sync (every 500ms)
  - Over-counting allowed by up to 500ms × rate → acceptable for most APIs
  - 10× lower latency overhead (no Redis per request)

Multi-region rate limiting:
  - Problem: user routes to nearest region; global limit requires cross-region coordination
  - Solution A: per-region limit = global_limit / num_regions (simple, slight under-limiting)
  - Solution B: CRDT counter with eventual convergence (accurate, complex)
  - Solution C: sticky routing — always route user to same region
```

### Cost Model
```
Redis for rate limiting (100M users):
  - 8.5 GB storage + 500K ops/sec
  - AWS Elasticache r6g.large (13 GB): $0.15/hr = $108/mo
  - Per-user cost: $108 / 100M = $0.000001/user/month (negligible)

Alternative: DynamoDB for rate limiting:
  - Each rate limit check = 1 DynamoDB eventually consistent read + 1 write
  - 500K ops/sec × $0.25/M writes = $0.125/sec = $324,000/mo (extremely expensive)
  - Redis wins by 3000× for this use case

Local in-process (no Redis):
  - Zero marginal cost; loses cross-instance consistency
  - Acceptable for: single-server APIs, approximate limits OK
```

---

## Trade-off Comparison

| Algorithm | Accuracy | Memory | Burst | Distributed | Use When |
|-----------|----------|--------|-------|-------------|----------|
| Fixed Window | Low (boundary burst) | O(1) | Allows double burst | Easy | Simple counters, non-critical |
| Sliding Window Log | Exact | O(N reqs) | Blocks exactly | Hard | Low request rates, strict limits |
| Sliding Window Counter | ~95% accurate | O(1) | Partial | Medium | General purpose, good balance |
| Token Bucket | High | O(1) | Configurable burst | Medium (Lua) | Most API rate limiting |
| Leaky Bucket | High | O(queue) | None (smoothed) | Medium | Upstream throttling, egress |

---

## Follow-up Questions (5-10, escalating)

1. **(L3)** What's the difference between token bucket and fixed window rate limiting?
   > Fixed window counts requests per time window and resets; allows boundary bursting. Token bucket replenishes tokens continuously; allows burst up to bucket capacity but smoothly limits sustained rate.

2. **(L3)** How would you return a Retry-After header to the client?
   > Calculate time until next token refill: `(tokens_needed - current_tokens) / refill_rate`. Return in seconds as both HTTP header and response body.

3. **(L4)** How do you implement rate limiting in a distributed system without a centralized Redis?
   > Option A: Local counters with gossip (eventual, some over-counting). Option B: Consistent hashing — route all requests for a client_id to the same server (sticky routing). Option C: Two-layer — local L1 for fast approximate check, Redis L2 for authoritative check.

4. **(L4)** What's the race condition in a distributed token bucket and how do you fix it?
   > Two threads simultaneously read tokens=5, both decide to allow, both write tokens=4. Net: 2 requests allowed, tokens decremented once. Fix: Redis Lua script executes GET+compute+SET atomically on the Redis server.

5. **(L4)** Design rate limiting at 3 granularities: per-IP, per-user, per-endpoint. How do you compose them?
   > Hierarchical check: per-endpoint global limit → per-user limit → per-IP limit. Reject if any limit exceeded. Use Redis key namespacing: `rl:global:{endpoint}`, `rl:user:{user_id}:{endpoint}`, `rl:ip:{ip}`. All checks in one Lua pipeline.

6. **(L5)** How would you handle a distributed rate limiter across 5 regions (US, EU, APAC, etc.)?
   > Option A: Per-region limits = global_limit / 5 (simple, slight under-limiting if traffic uneven). Option B: Central Redis in each region + cross-region sync every 1s (complexity, 1s inconsistency window). Option C: CRDT counter — each region maintains local count, sync globally; eventual consistency. For most APIs, Option A is right; Option C for payment APIs.

7. **(L5)** The rate limiter is adding 50 ms latency to P99 requests. How do you debug and fix it?
   > Diagnose: check Redis slow log, network latency between app and Redis (should be < 1 ms same-AZ). Root cause candidates: Redis CPU saturated (too many ops/sec), network hop (cross-AZ), lock contention (Lua scripts queued). Fix: add in-process L1 cache (check Redis only every 100ms for stable clients), move Redis to same AZ, shard by client_id to distribute load.

8. **(L5+)** Design an adaptive rate limiter that increases limits for trusted users and tightens them for suspicious patterns.
   > Trust score = function of: account age, payment history, abuse flags, geographic consistency. Score maps to tier: {bronze: 100/min, silver: 500/min, gold: 2000/min}. Abuse detection: sudden spike (10× normal rate), geographic anomaly, user-agent rotation. On abuse flag: reduce to bronze tier, add to watchlist. Trust score computed async (not on request path) by ML model, cached in Redis with 1-hour TTL.

---

## Anti-patterns / Things NOT to Say

- **"I'll check rate limit in the database"** — DB round-trip for every request will kill your DB and add 10–50ms latency.
- **"Fixed window is fine"** — must mention the boundary burst problem; shows awareness of edge cases.
- **"Just block the IP"** — IP blocking doesn't work for NAT (1000 users behind same IP) or IPv6 rotation; always mention user-level limiting too.
- **"Rate limiter should fail-closed"** — blocking all users when rate limiter is down is worse than allowing some excess traffic; fail-open with logging is almost always correct.
- **"I'll use a sleep/delay to slow down requests"** — leaky bucket queue model, not sleep; sleeping holds threads and exhausts thread pools.
- **Not mentioning the Retry-After header** — this is standard HTTP and critical UX; interviewers expect it.

---

## Python Implementation

```python
import time
import threading
from collections import deque
from typing import Optional


# ── Algorithm 1: Token Bucket (recommended) ───────────────────────────────

class TokenBucket:
    """
    Thread-safe token bucket rate limiter.
    Refill rate: `rate` tokens per second.
    Max burst: `capacity` tokens.
    """

    def __init__(self, capacity: float, rate: float):
        self.capacity = capacity
        self.rate = rate           # tokens added per second
        self._tokens = capacity    # start full
        self._last_refill = time.monotonic()
        self._lock = threading.Lock()

    def _refill(self) -> None:
        now = time.monotonic()
        elapsed = now - self._last_refill
        added = elapsed * self.rate
        self._tokens = min(self.capacity, self._tokens + added)
        self._last_refill = now

    def allow(self, tokens: float = 1.0) -> tuple[bool, float]:
        """
        Returns (allowed, retry_after_seconds).
        retry_after_seconds is 0.0 if allowed.
        """
        with self._lock:
            self._refill()
            if self._tokens >= tokens:
                self._tokens -= tokens
                return True, 0.0
            else:
                wait = (tokens - self._tokens) / self.rate
                return False, round(wait, 2)

    @property
    def remaining(self) -> float:
        with self._lock:
            self._refill()
            return round(self._tokens, 2)


# ── Algorithm 2: Sliding Window Log ───────────────────────────────────────

class SlidingWindowLog:
    """
    Exact sliding window using a deque of request timestamps.
    Memory: O(limit) per client.
    """

    def __init__(self, limit: int, window_sec: float):
        self.limit = limit
        self.window = window_sec
        self._log: deque[float] = deque()
        self._lock = threading.Lock()

    def allow(self) -> tuple[bool, float]:
        with self._lock:
            now = time.monotonic()
            cutoff = now - self.window
            # evict expired entries
            while self._log and self._log[0] <= cutoff:
                self._log.popleft()
            if len(self._log) < self.limit:
                self._log.append(now)
                return True, 0.0
            else:
                retry_after = self._log[0] + self.window - now
                return False, round(retry_after, 2)


# ── Algorithm 3: Sliding Window Counter (memory-efficient approximation) ──

class SlidingWindowCounter:
    """
    Two fixed windows + linear interpolation.
    ~95% accuracy of true sliding window, O(1) memory.
    """

    def __init__(self, limit: int, window_sec: float):
        self.limit = limit
        self.window = window_sec
        self._prev_count = 0
        self._cur_count = 0
        self._window_start = time.monotonic()
        self._lock = threading.Lock()

    def _roll_window_if_needed(self, now: float) -> None:
        elapsed = now - self._window_start
        if elapsed >= 2 * self.window:
            self._prev_count = 0
            self._cur_count = 0
            self._window_start = now
        elif elapsed >= self.window:
            self._prev_count = self._cur_count
            self._cur_count = 0
            self._window_start += self.window

    def allow(self) -> tuple[bool, float]:
        with self._lock:
            now = time.monotonic()
            self._roll_window_if_needed(now)
            elapsed_in_window = now - self._window_start
            # weighted count: prev window contributes proportionally
            weight = 1.0 - (elapsed_in_window / self.window)
            estimated = self._prev_count * weight + self._cur_count
            if estimated < self.limit:
                self._cur_count += 1
                return True, 0.0
            else:
                retry_after = self.window - elapsed_in_window
                return False, round(retry_after, 2)


# ── Multi-tenant rate limiter (per-client) ────────────────────────────────

class RateLimiter:
    """Per-client token bucket registry."""

    def __init__(self, default_capacity: float = 100, default_rate: float = 10):
        self.default_capacity = default_capacity
        self.default_rate = default_rate
        self._buckets: dict[str, TokenBucket] = {}
        self._lock = threading.Lock()

    def _get_bucket(self, client_id: str) -> TokenBucket:
        with self._lock:
            if client_id not in self._buckets:
                self._buckets[client_id] = TokenBucket(
                    self.default_capacity, self.default_rate
                )
            return self._buckets[client_id]

    def check(self, client_id: str) -> tuple[bool, float]:
        return self._get_bucket(client_id).allow()

    def remaining(self, client_id: str) -> float:
        return self._get_bucket(client_id).remaining


# ── Redis Lua script (production distributed token bucket) ─────────────────
# Run with: redis.eval(SCRIPT, 1, key, capacity, rate, now, cost)
REDIS_TOKEN_BUCKET_LUA = """
local key        = KEYS[1]
local capacity   = tonumber(ARGV[1])
local rate       = tonumber(ARGV[2])  -- tokens/sec
local now        = tonumber(ARGV[3])  -- current time ms
local cost       = tonumber(ARGV[4])  -- tokens to consume

local data       = redis.call('HMGET', key, 'tokens', 'last_refill')
local tokens     = tonumber(data[1]) or capacity
local last       = tonumber(data[2]) or now

local elapsed    = (now - last) / 1000.0
tokens           = math.min(capacity, tokens + elapsed * rate)

if tokens >= cost then
    tokens = tokens - cost
    redis.call('HMSET', key, 'tokens', tokens, 'last_refill', now)
    redis.call('EXPIRE', key, math.ceil(capacity / rate) * 2)
    return {1, math.floor(tokens)}   -- allowed, remaining
else
    local wait_ms = math.ceil((cost - tokens) / rate * 1000)
    return {0, wait_ms}              -- blocked, retry_after_ms
end
"""


# ── Demo ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=== Token Bucket ===")
    tb = TokenBucket(capacity=5, rate=2)   # 2 tokens/sec, max 5
    for i in range(8):
        allowed, retry = tb.allow()
        status = "ALLOW" if allowed else f"BLOCK (retry in {retry}s)"
        print(f"  Request {i+1}: {status} | remaining={tb.remaining}")
        if not allowed:
            time.sleep(retry + 0.01)

    print("\n=== Sliding Window Log ===")
    swl = SlidingWindowLog(limit=3, window_sec=1.0)
    for i in range(5):
        allowed, retry = swl.allow()
        print(f"  Request {i+1}: {'ALLOW' if allowed else f'BLOCK ({retry}s)'}")

    print("\n=== Multi-tenant Rate Limiter ===")
    rl = RateLimiter(default_capacity=3, default_rate=1)
    for client in ["alice", "bob", "alice", "alice", "alice"]:
        allowed, retry = rl.check(client)
        print(f"  {client}: {'ALLOW' if allowed else f'BLOCK ({retry}s)'} | remaining={rl.remaining(client)}")
```

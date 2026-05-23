# Rate Limiting & Throttling — Protecting Systems from Overload

Controlling request flow to prevent abuse and overload.

---

## 🚦 Core Concepts

**Rate Limiting:** Restrict requests from single source
**Throttling:** Slow down responses under load
**Quota:** Hard limit over time period (daily, monthly)

---

## 🎯 Rate Limiting Algorithms

### Token Bucket

```
Bucket capacity: N tokens
Refill rate: M tokens per second

Request:
- If token available: take token, allow request
- Else: reject or queue

Burst: Can handle M * N requests instantly

Pro: Allows bursts, fair
Con: Complex implementation
```

### Leaky Bucket

```
Queue requests, process at constant rate
Overflow: Reject excess

Pros: Smooth traffic
Cons: Doesn't allow bursts
```

### Sliding Window

```
Track timestamps of recent requests
If too many in window: reject

Pro: Simple, accurate
Con: Memory overhead for timestamps
```

### Fixed Window

```
Window: 1 minute
Counter: Increments in window
Limit: Max 100 requests/minute

Pro: Simple, fast
Con: Edge cases (requests on boundary)
```

---

## 📍 Rate Limiting Scopes

**Per-User:** 1000 req/hour per user
**Per-IP:** 10000 req/hour per IP
**Per-API-Key:** Different limits per key tier
**Global:** 1M req/second total

---

## 🔄 Distributed Rate Limiting

Single server easy. Multiple servers: challenging.

### Solutions

**Centralized:** Redis stores counters
- Accurate, but central bottleneck

**Distributed:** Each server tracks (approximate)
- Fast, slightly inaccurate

**Decentralized:** Consensus algorithm
- Complex, rare

---

## 📊 Response to Rate Limit

```
HTTP 429 Too Many Requests

Headers:
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 500
X-RateLimit-Reset: 1234567890 (Unix timestamp)

Body:
{
  "error": "Rate limit exceeded",
  "retry_after": 60
}
```

---

## 💡 Common Strategies

**API Tier:** Different limits for free vs. paid users
**Backoff:** Exponential backoff for retries (2s, 4s, 8s)
**Queue:** Queue excess requests instead of rejecting
**Graceful degradation:** Serve cached results under load

---

## ❓ Interview Q&A

**Q: Design rate limiting for API.**
A: Token bucket algorithm. Store in Redis. Per-user limits. Return 429 with retry header.

**Q: How to prevent rate limit abuse?**
A: Client-side: Exponential backoff. Server-side: Strict limits, IP blocking. Monitoring: Alert on abuse.

**Q: Distributed rate limiting across regions?**
A: Centralized Redis (latency issue). Regional Redis with sync. Decentralized with loose consistency.

---

**Last updated:** 2026-05-22

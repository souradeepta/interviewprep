# Rate Limiting & Throttling: Protecting Systems from Overload

Master rate limiting strategies to protect backends from abuse and overload.

---

## Rate Limiting Algorithms

### Token Bucket

```python
class TokenBucket:
    def __init__(self, capacity, refill_rate):
        self.capacity = capacity
        self.refill_rate = refill_rate  # tokens per second
        self.tokens = capacity
        self.last_refill = time.time()
    
    def allow_request(self):
        now = time.time()
        elapsed = now - self.last_refill
        
        # Refill tokens
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now
        
        # Check if we can serve
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False

# Example: 100 requests/sec, burst of 200
bucket = TokenBucket(capacity=200, refill_rate=100)
```

**Characteristics:**
- Allows bursts (bucket capacity)
- Smooth rate limiting (tokens per second)
- Fair (all clients treated equally)

### Leaky Bucket

```python
class LeakyBucket:
    def __init__(self, capacity, leak_rate):
        self.capacity = capacity
        self.leak_rate = leak_rate  # items leaked per second
        self.queue = deque()
        self.last_leak = time.time()
    
    def allow_request(self):
        now = time.time()
        
        # Leak items
        leaked = (now - self.last_leak) * self.leak_rate
        while self.queue and leaked > 0:
            self.queue.popleft()
            leaked -= 1
        self.last_leak = now
        
        # Add to queue
        if len(self.queue) < self.capacity:
            self.queue.append(now)
            return True
        return False
```

**Characteristics:**
- Smooth output (constant leak rate)
- No bursts (queue fills up)
- Used for request smoothing

### Sliding Window Log

```python
class SlidingWindowLog:
    def __init__(self, max_requests, window_seconds):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.log = []  # timestamps of requests
    
    def allow_request(self):
        now = time.time()
        
        # Remove old requests outside window
        cutoff = now - self.window_seconds
        self.log = [ts for ts in self.log if ts > cutoff]
        
        # Check if we can serve
        if len(self.log) < self.max_requests:
            self.log.append(now)
            return True
        return False

# Example: 100 requests per minute
limiter = SlidingWindowLog(max_requests=100, window_seconds=60)
```

**Characteristics:**
- Precise (exact rolling window)
- Memory intensive (stores timestamps)
- Fair enforcement

---

## Distributed Rate Limiting

**Challenge:** Rate limiting across multiple servers.

```python
# Using Redis for distributed rate limiting
import redis

class DistributedRateLimiter:
    def __init__(self, redis_client, key, max_requests, window_seconds):
        self.redis = redis_client
        self.key = key
        self.max_requests = max_requests
        self.window_seconds = window_seconds
    
    def allow_request(self):
        current = self.redis.incr(self.key)
        
        if current == 1:
            self.redis.expire(self.key, self.window_seconds)
        
        return current <= self.max_requests

# For user_id = 123:
# limiter = DistributedRateLimiter(redis, f"rate_limit:user:123", 100, 60)
```

---

## HTTP Status Codes & Headers

### 429 Too Many Requests

```
HTTP/1.1 429 Too Many Requests
Retry-After: 60
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1234567890

{
  "error": "Rate limit exceeded",
  "message": "You have exceeded 100 requests in 60 seconds. Try again in 60 seconds."
}
```

---

## Rate Limiting Strategies by Layer

### 1. API Gateway (First Line)

```
Client → API Gateway (rate limit here first)
       → Backend Services
```

**Advantages:**
- Single point of enforcement
- Protects entire backend
- Easy to scale

### 2. Per-Service (Fine-grained)

```
Client → Service A (rate limit by user)
      → Service B (rate limit by API key)
```

**Advantages:**
- Service-specific policies
- Prevent cascade failures
- Flexible per-service limits

### 3. Database Layer (Last Resort)

```
If rate limiting fails at higher layers, DB connection pooling prevents overload
```

---

## Rate Limiting Policies

### By User

```
Max 100 API calls per minute per user
Prevents single user from overwhelming service
```

### By API Key

```
Premium tier: 10,000 requests/day
Standard tier: 1,000 requests/day
Free tier: 100 requests/day
```

### By IP Address

```
Max 1,000 requests per minute per IP
Prevents DDoS from single origin
```

### By Endpoint

```
GET /api/data: 100 requests/min (read-heavy, allow more)
POST /api/payments: 10 requests/min (write-heavy, restrict)
```

---

## Handling Rate Limit Exceeded

```python
# Option 1: Reject immediately
@app.get("/api/data")
def get_data(user_id: str):
    if not rate_limiter.allow_request(user_id):
        return {"error": "Rate limited"}, 429
    
    return {"data": fetch_data()}

# Option 2: Queue and retry
@app.get("/api/data")
def get_data(user_id: str):
    if not rate_limiter.allow_request(user_id):
        queue.enqueue(request_job(user_id))
        return {"message": "Request queued"}, 202
    
    return {"data": fetch_data()}

# Option 3: Degrade gracefully
@app.get("/api/data")
def get_data(user_id: str, full: bool = True):
    if not rate_limiter.allow_request(user_id):
        if full:
            return cached_data_summary()  # Lighter response
        return {"error": "Rate limited"}, 429
    
    return fetch_full_data()
```

---

## Rate Limiting Checklist

- ✓ Identified rate limiting requirements
- ✓ Chose algorithm (token bucket recommended)
- ✓ Set appropriate limits (requests/sec or per minute)
- ✓ Distributed limiting if multi-server
- ✓ Return proper HTTP 429 status
- ✓ Include Retry-After header
- ✓ Monitored rate limiting violations
- ✓ Tested with load (ensure limits hold)
- ✓ Graceful degradation when limiting triggers
- ✓ Different policies for different tiers/endpoints


# API Gateway

**Level:** L3-L5+
**Time to read:** ~30 min

## Problem Statement

A microservices architecture with 50+ backend services creates chaos for clients if they must
know each service's address, authentication scheme, and protocol. An API gateway is a single
entry point that handles cross-cutting concerns: routing requests to the correct service,
authenticating every request (JWT validation), enforcing rate limits per client, aggregating
multiple service calls into one response, and terminating SSL. It decouples the public API
surface from internal service topology.

At 1M RPS, the gateway must add < 5 ms of overhead, handle circuit breaking when backends
degrade, and support blue-green routing for gradual rollouts — all while being a highly available
component that cannot itself become a single point of failure.

## Functional Requirements

- Route incoming requests to the correct backend service based on path, method, and headers
- Validate JWT/API key authentication on every request
- Enforce per-client rate limits (requests per second, per minute, per day)
- Aggregate multiple service responses into one (API composition)
- Support blue-green / canary routing by percentage

## Non-Functional Requirements

- **Scale:** 1M RPS through gateway; 10K backend service instances behind it
- **Latency:** Gateway overhead P99 < 5 ms (not counting backend service latency)
- **Availability:** 99.999% (5.3 min/year downtime); gateway failure = total platform outage
- **Consistency:** Rate limit counters: eventual (±10% overage acceptable); routing decisions:
  immediately consistent

---

## Tier 1: L3-L4 Design (the basic interview answer)

### Back-of-Envelope

```
RPS:            1M requests/sec
Request size:   avg 2 KB (headers + body)
Response size:  avg 20 KB (API responses)
Inbound:        1M * 2 KB = 2 GB/sec
Outbound:       1M * 20 KB = 20 GB/sec
Network:        25 Gbps NIC per gateway node = 3.125 GB/sec per NIC
                20 GB/sec / 3.125 = 6.4 nodes minimum → deploy 16 nodes (with 2.5× headroom)

JWT validation: RS256 signature verification = ~0.5 ms per request (public key from cache)
                1M * 0.5 ms = 500K CPU-ms/sec = 500 CPU cores for JWT alone
                Optimization: cache validated JWTs by token hash (TTL = token_exp) → 99% hit rate
                With cache: ~1K full validations/sec (new/expiring tokens) = 1 CPU core

Rate limit Redis:
  1M RPS * 10 bytes (counter increment) = 10 MB/sec writes
  Redis: 1M INCR/sec is within single-node capacity (500K-1M ops/sec)
  Use sliding window counter: 2 keys per client (current minute + previous minute window)
```

### Architecture Diagram

```
  Internet / CDN (CloudFront / Fastly)
        |
  +-----v-----------+
  | Load Balancer   |  ← L4 (NLB), routes TCP to gateway nodes
  | (AWS NLB)       |
  +-----+-----------+
        |
  +-----v-----------+  +-----v-----------+  +-----v-----------+
  | Gateway Node 1  |  | Gateway Node 2  |  | Gateway Node N  |
  | (nginx/envoy)   |  | (nginx/envoy)   |  | (nginx/envoy)   |
  +----+----+-------+  +-----------------+  +-----------------+
       |    |
  Auth |    | Rate Limit
       |    |
  +----v-+  +-------v------+
  | JWT  |  | Redis Cluster|  ← rate limit counters
  | Cache|  |              |
  |(Redis)  +--------------+
  +------+
       |
  Route Config (etcd/Consul or config file):
       |  /api/v1/users/*  → user-service:8080
       |  /api/v1/posts/*  → post-service:8080
       |  /api/v1/search   → search-service:8080
       |
  +----v--+  +--------+  +---------+
  |user-  |  |post-   |  |search-  |  ← backend microservices (service mesh)
  |service|  |service |  |service  |
  +-------+  +--------+  +---------+

Circuit Breaker per route (Envoy sidecar):
  If upstream error rate > 5% in 10 sec → open circuit → return 503 immediately
  After 30 sec: probe with 1% traffic → if healthy → close circuit
```

### Data Model

```
# Route configuration (stored in etcd/Consul, hot-reloaded)
routes:
  - path: "/api/v1/users/**"
    methods: [GET, PUT, DELETE]
    upstream: "user-service"
    load_balancer: round_robin
    timeout_ms: 3000
    retry_attempts: 2
    auth_required: true

  - path: "/api/v1/public/**"
    upstream: "public-service"
    auth_required: false
    rate_limit_group: "unauthenticated"

  - path: "/api/v1/search"
    upstream: "search-service"
    canary:
      enabled: true
      target: "search-service-v2"
      percentage: 10   # 10% to new version

# API key store (Postgres, cached in Redis)
CREATE TABLE api_keys (
    key_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    api_key_hash    VARCHAR(64) NOT NULL UNIQUE,  -- SHA256 of actual key
    client_id       VARCHAR(128) NOT NULL,
    rate_limit_rpm  INT NOT NULL DEFAULT 1000,
    rate_limit_rpd  INT NOT NULL DEFAULT 100000,
    scopes          JSON,                          -- ["read:posts", "write:posts"]
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    last_used_at    TIMESTAMP
);

# Rate limit counter (Redis sliding window)
# Key: rl:{client_id}:{minute_bucket}  → INCR + EXPIRE 120
# Key: rl:{client_id}:{day_bucket}    → INCR + EXPIRE 172800
```

### API Design

```
# All external API calls flow through gateway — no separate gateway API

# Gateway adds/validates headers on every request:
Request Headers (inbound to backend):
  X-User-Id:      "42"         (from validated JWT sub claim)
  X-Client-Id:    "mobile_app" (from JWT aud or API key)
  X-Request-Id:   "uuid"       (generated by gateway, for tracing)
  X-Forwarded-For: "1.2.3.4"

# Gateway admin API (internal, management plane)
GET  /admin/routes
PUT  /admin/routes/{route_id}    Body: updated route config
GET  /admin/circuit-breakers     → status of all circuit breakers
POST /admin/circuit-breakers/{service}/reset
GET  /admin/rate-limits/{client_id}  → current usage
POST /admin/api-keys/{key_id}/revoke

# Health check (for load balancer probes)
GET /health
  Response: 200 { status: "ok", version: "1.2.3" }

GET /health/ready   (readiness probe — checks Redis and config store connectivity)
  Response: 200 { ready: true, dependencies: { redis: "ok", etcd: "ok" } }
```

### Basic Scaling

- **Stateless gateway nodes:** All state (rate limits, JWT cache) in Redis; gateway nodes are
  identical and interchangeable; add/remove nodes without config changes
- **JWT caching:** Cache validated JWT by SHA256(token) → {user_id, scopes, exp}; TTL = min(300s,
  token_exp - now); avoids RSA public key verification on every request
- **Rate limit sliding window:** Two Redis keys per client per window (current + previous minute);
  approximate rate = prev_minute_count * (1 - elapsed_fraction) + current_minute_count
- **Circuit breaker:** Implemented in Envoy/nginx as upstream health: track error rate + latency
  P99 per backend; open circuit when threshold exceeded; prevents cascading failures

---

## Tier 2: L5+ Design (the staff interview answer)

### Capacity Planning (Real Numbers)

```
Gateway node sizing (Envoy on c6gn.4xlarge, 16 vCPU + 25 Gbps NIC):
  1M RPS / 16 nodes = 62,500 RPS per node
  Per-request work (Envoy): TLS termination (0.5 ms) + JWT cache lookup (0.3 ms)
                             + Redis rate limit (0.3 ms) + route match (0.1 ms) = ~1.2 ms overhead
  CPU at 62,500 RPS and 1.2 ms: 62,500 * 0.0012 = 75 CPU-sec/sec → 5 vCPUs utilized (31%)
  Network: 62,500 RPS * (2 KB req + 20 KB resp) = 1.375 GB/sec → within 25 Gbps NIC limit

Rate limit Redis cluster:
  1M INCR/sec → single Redis node capacity (500K-1M ops/sec typical)
  Use Redis Cluster with 6 nodes (3 master + 3 replica)
  Hash slots distribute keys: {client_id} → slot → master node
  At 1M INCR/sec / 3 masters: 333K ops/sec per master → comfortable

JWT cache (Redis or in-process):
  New JWTs: 1% of 1M = 10K/sec (tokens rotate every 15 min for 10M users = 11K/sec)
  RSA RS256 verification: ~0.5 ms on modern CPU → 10K * 0.5 ms = 5 CPU cores for JWT
  In-process LRU cache per gateway node: 1M unique tokens * 200 bytes = 200 MB per node
  Use both: in-process L1 cache (miss rate ~20%) → Redis L2 cache (miss rate ~1%) → verify

Distributed tracing:
  1M RPS * 1 span per request = 1M spans/sec
  At 1% sampling rate: 10K spans/sec → Jaeger/Zipkin can handle
  Full sampling for debug: only during incidents (too expensive at 1M spans/sec)
```

### Failure Modes

```
FAILURE: Redis (rate limit store) goes down
  Detection:    Redis health check fails; circuit breaker opens within 5 sec
  Mitigation:   Failopen: continue serving requests without rate limiting (better than 503)
               OR Fallback to in-memory rate limiting (per-node, approximate: 1M / 16 nodes = 62.5K budget/node)
  Risk:         Clients can exceed rate limits during Redis outage (temporary)
  Recovery:     Redis restores → counters reset; brief window of fresh budget after restart

FAILURE: Single gateway node OOM / crash
  Detection:    NLB health check fails within 5 sec; node removed from rotation
  Impact:       1/16 of traffic = 62.5K RPS needs redistribution → 15 remaining nodes handle 66.7K each → +6.7%
  Recovery:     ASG auto-replaces node in 2-3 min
  Mitigation:   Keep 20% headroom (16 nodes for 800K RPS capacity vs 1M peak) for this scenario

FAILURE: Backend service degraded (high latency, not down)
  Detection:    Envoy upstream latency P99 > threshold (e.g., 2× baseline over 30 sec)
  Mitigation:   Outlier detection: remove slow pods from upstream set
               Connection pool: limit open requests to upstream (bulkhead pattern)
               Timeout: gateway-enforced request timeout (3 sec) prevents thread exhaustion
  Cascade prevention: if upstream at capacity, return 429 (rate limit) before queue fills up

FAILURE: Invalid JWT flood (DDoS with expired/forged tokens)
  Detection:    JWT validation error rate > 10% of requests
  Mitigation:   Return 401 quickly (in-process token signature check, sub-1ms)
               Rate limit by IP: max 100 req/sec per IP, regardless of auth status
               WAF (Web Application Firewall) in front of NLB for IP-based blocking
               CDN (CloudFront) absorbs DDoS before traffic reaches gateway
```

### Consistency Boundaries

```
RATE LIMIT ACCURACY:
  Problem:     1M RPS across 16 gateway nodes; each node needs global rate limit state
  Solution A:  Centralized Redis counter (all nodes read/write same counter)
               Accuracy: exact; latency: +0.3 ms per request for Redis INCR
  Solution B:  Local counter per node; sync to Redis every 100 ms
               Accuracy: ±10-15% (overshoot by up to 1 node's local batch)
               Latency: 0 ms (no Redis round trip)
  Solution C:  Approximate sliding window: local counter + periodic Redis sync for correction
               Best trade-off: O(1) per request, < 5% overage on average

ROUTE CONFIG PROPAGATION:
  Route config stored in etcd; gateway polls every 10 sec OR uses etcd Watch (push)
  With Watch: config changes propagate to all 16 nodes in < 1 sec
  Brief window: 0-1 sec where some nodes have old config, some have new
  Mitigation: deploy config changes in phases (canary flag); validate before full rollout

CANARY ROUTING CONSISTENCY:
  Client_id hashed to bucket (0-99) deterministically → same client always in same bucket
  Ensures: a user is always routed to the same version during a canary rollout
  NOT sticky by session: new connection could theoretically get different shard if bucket
  changes, but bucket is deterministic from client_id → won't change mid-rollout
```

### Cost Model

```
Gateway compute (16× c6gn.4xlarge, 16 vCPU + 25 Gbps NIC):
  16 * $0.69/hr * 8760 = $96,595/yr

Rate limit Redis (6-node cluster, r6g.xlarge):
  6 * $0.227/hr * 8760 = $11,939/yr

AWS NLB:
  $0.008/LCU/hr; at 1M RPS: ~100 LCU → $0.80/hr * 8760 = $7,008/yr

Data transfer (inbound free; outbound $0.09/GB):
  1M RPS * 20 KB resp = 20 GB/sec * 86400 * 365 = 631 PB/yr → need CDN to offload
  With CDN (85% cache hit): 20 GB/sec * 0.15 = 3 GB/sec to origin
  CDN outbound (CloudFront): 3 GB/sec * 86400 * 365 * $0.0085/GB = $831K/yr  ← DOMINANT

Total (with CDN): ~$947K/yr
Per million requests: $947K / (1M RPS * 31.5M sec) = $0.030/million requests ($0.00003/request)
Without CDN (all origin): network cost = ~$5.5M/yr → CDN saves $4.5M/yr

Service mesh alternative (Istio):
  Replaces gateway with per-pod sidecar Envoy; better security (mTLS everywhere)
  Cost: ~5% CPU overhead per pod vs. no extra nodes
  Trade-off: no single gateway bottleneck; harder to enforce global rate limits
```

---

## Trade-off Comparison

| Approach | Pros | Cons | Best For |
|----------|------|------|----------|
| Nginx/OpenResty (Lua plugins) | High performance; battle-tested; Lua for custom logic; low overhead | Custom plugins require Lua expertise; less visibility than Envoy | High-throughput APIs, simple routing, well-understood traffic patterns |
| Envoy proxy | Built for service mesh; excellent observability; circuit breaking native; xDS control plane | Complex to configure; heavy memory footprint (~100 MB per instance) | Microservices, service mesh (Istio/Linkerd), Kubernetes-native |
| AWS API Gateway (managed) | Zero ops; scales automatically; WAF integration; usage plans | Limited routing logic; $3.50/million requests (expensive at 1M RPS = $9B/day in cost!); vendor lock-in | Low-medium traffic (<100K RPS); serverless backends; AWS-native |
| Service mesh (Istio/Linkerd) | mTLS everywhere; per-service observability; no centralized bottleneck | Ops complexity; every pod has sidecar overhead; steep learning curve | Large orgs with 50+ services; zero-trust networking requirements |

## Follow-up Questions (escalating difficulty)

1. **(L3)** What is the difference between an API gateway and a load balancer?
   → A load balancer (L4) distributes TCP connections across servers based on IP/port — it knows
   nothing about HTTP semantics. An API gateway (L7) understands HTTP: it reads the URL, headers,
   and body to route to different services, validate JWTs, enforce rate limits, and modify
   requests/responses. A load balancer routes to instances; an API gateway routes to services.

2. **(L3)** Why do you validate JWT at the gateway rather than in each service?
   → Centralizing auth at the gateway ensures every request is authenticated before reaching any
   service — services can trust the X-User-Id header the gateway injects. Without gateway-level
   auth: every service must implement JWT validation (duplication), and a bug in one service's
   auth could expose endpoints. Gateway is a single place to update auth logic.

3. **(L4)** Explain the circuit breaker pattern and when it opens.
   → A circuit breaker wraps calls to an upstream service. It monitors error rate and/or latency.
   When errors exceed a threshold (e.g., 50% in 10 sec): circuit OPENS — all calls immediately
   return 503 without attempting the upstream (fast failure). After a timeout (e.g., 30 sec):
   circuit goes HALF-OPEN — a small % of traffic is allowed through as a probe. If probes succeed:
   circuit CLOSES (normal). Prevents cascading failure: one slow service can't exhaust gateway
   connection pool and bring down the whole platform.

4. **(L4)** How do you implement request aggregation (API composition) at the gateway?
   → For a mobile homepage that needs user profile + feed + notifications: instead of 3 separate
   client requests, the gateway exposes one `/homepage` endpoint that fans out 3 parallel upstream
   calls, waits for all (with timeout), merges the responses, and returns one JSON payload.
   Reduces mobile round-trips from 3 to 1. Use async I/O (Nginx async_call or Envoy Lua filter)
   to parallelize upstream calls without blocking threads.

5. **(L5)** How would you implement blue-green deployment at the gateway level?
   → Define two upstreams: `user-service-blue` (current) and `user-service-green` (new version).
   Start with 100% to blue. Gradually shift traffic: `canary.percentage = 10` → 10% to green.
   Monitor error rate and latency for green. If metrics good: increment to 25%, 50%, 100%.
   If metrics bad: instant rollback to 0%. Client routing is consistent (hash(client_id) →
   same version) so a user doesn't see different behavior on each request during canary.

6. **(L5)** How does mTLS differ from regular TLS at the gateway, and when do you use it?
   → Regular TLS: server proves identity to client (one-way). mTLS (mutual TLS): both server
   AND client prove identity with certificates. At the API gateway, terminate client mTLS
   at the gateway (extract client certificate → service identity). Between gateway and backend:
   gateway presents its own cert to backends (service mesh pattern). Use mTLS in zero-trust
   environments where you don't want to trust internal network traffic — even internal service
   calls require certificate-based authentication.

7. **(L5+)** When would you choose a service mesh (Istio) over a centralized API gateway?
   → Choose service mesh when: (1) You need service-to-service auth (mTLS) throughout, not
   just at the edge; (2) You have 50+ services with complex inter-service communication
   patterns; (3) You need fine-grained observability per service-pair (not just edge); (4)
   You want to avoid a centralized bottleneck for internal traffic. Choose API gateway when:
   (1) Centralizing auth and rate limiting is sufficient; (2) You need request aggregation
   at the edge; (3) Ops team is smaller (service mesh is operationally complex). Many large
   platforms use both: API gateway at the edge for external traffic, service mesh internally.

## Anti-patterns / Things NOT to Say

- **"Use managed API Gateway (AWS API Gateway) at 1M RPS"** — AWS API Gateway charges
  $3.50/million requests. At 1M RPS: 1M * 86400 * 365 * $3.50/million = $110B/year. Use
  self-managed Envoy/nginx for high-throughput — managed is only cost-effective at < 100K RPS.
- **"Put business logic in the API gateway"** — The gateway should handle cross-cutting concerns
  (auth, rate limiting, routing). Business logic belongs in services. Gateway grows into an
  unmaintainable God service if you add product logic (e.g., "if user is premium, route to
  premium-service") — this should be in the service, not the gateway.
- **"Single gateway node for simplicity"** — A single gateway node = single point of failure.
  Gateway failure = entire platform unreachable. Always deploy multiple instances behind a
  load balancer; design for N-1 capacity.
- **"Validate JWT by calling the auth service on every request"** — 1M RPS * 1 auth service
  call = 1M auth RPS — auth service becomes the bottleneck. Cache validated JWTs by token
  hash (public key validation is stateless); only call auth service for token revocation checks
  (rare) or for opaque tokens that require server-side lookup.
- **"Rate limit per IP only"** — IP-based rate limiting breaks for NAT (an office of 1000
  employees shares 1 public IP). Use combination: rate limit by API key/user_id (authenticated
  requests) and by IP (unauthenticated). IP rate limit is last-resort DoS protection, not
  primary rate limiting.

## Python Implementation (sketch)

```python
import time
import hashlib
from collections import defaultdict
from dataclasses import dataclass
from typing import Optional

@dataclass
class Route:
    path_prefix: str
    upstream: str
    auth_required: bool = True
    rate_limit_rpm: int = 1000
    timeout_ms: int = 3000
    canary_upstream: Optional[str] = None
    canary_percentage: int = 0

@dataclass
class GatewayRequest:
    method: str
    path: str
    headers: dict
    client_id: Optional[str] = None

class SlidingWindowRateLimiter:
    """Per-client sliding window rate limiter (in-memory; use Redis in production)."""

    def __init__(self):
        self._windows: dict[str, list[float]] = defaultdict(list)

    def is_allowed(self, client_id: str, limit_rpm: int) -> bool:
        now = time.time()
        window_start = now - 60.0
        key = client_id
        # Remove expired timestamps
        self._windows[key] = [t for t in self._windows[key] if t > window_start]
        if len(self._windows[key]) >= limit_rpm:
            return False
        self._windows[key].append(now)
        return True

class APIGateway:
    def __init__(self):
        self._routes: list[Route] = []
        self._rate_limiter = SlidingWindowRateLimiter()
        self._jwt_cache: dict[str, dict] = {}  # token_hash → claims

    def add_route(self, route: Route) -> None:
        self._routes.append(route)

    def _find_route(self, path: str) -> Optional[Route]:
        for route in self._routes:
            if path.startswith(route.path_prefix):
                return route
        return None

    def _validate_jwt(self, token: str) -> Optional[dict]:
        """Simulate JWT validation with caching."""
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        if token_hash in self._jwt_cache:
            claims = self._jwt_cache[token_hash]
            if claims.get("exp", 0) > time.time():
                return claims
        # In production: verify RSA signature with public key
        # Simulate successful validation
        claims = {"sub": "user_42", "client_id": "mobile_app", "exp": time.time() + 900}
        self._jwt_cache[token_hash] = claims
        return claims

    def _select_upstream(self, route: Route, client_id: str) -> str:
        """Canary routing: deterministic bucket based on client_id."""
        if route.canary_upstream and route.canary_percentage > 0:
            bucket = int(hashlib.md5(client_id.encode()).hexdigest(), 16) % 100
            if bucket < route.canary_percentage:
                return route.canary_upstream
        return route.upstream

    def handle(self, req: GatewayRequest) -> dict:
        route = self._find_route(req.path)
        if not route:
            return {"status": 404, "error": "No route found"}

        # Auth
        if route.auth_required:
            token = req.headers.get("Authorization", "").replace("Bearer ", "")
            claims = self._validate_jwt(token)
            if not claims:
                return {"status": 401, "error": "Invalid token"}
            req.client_id = claims.get("client_id", "unknown")

        # Rate limit
        if req.client_id and not self._rate_limiter.is_allowed(req.client_id, route.rate_limit_rpm):
            return {"status": 429, "error": "Rate limit exceeded"}

        # Route
        upstream = self._select_upstream(route, req.client_id or "anonymous")
        return {
            "status": 200,
            "upstream": upstream,
            "x_user_id": claims.get("sub") if route.auth_required else None,
            "x_request_id": hashlib.md5(f"{time.time()}".encode()).hexdigest()[:16]
        }


# Usage
gw = APIGateway()
gw.add_route(Route("/api/v1/users", upstream="user-service", rate_limit_rpm=1000))
gw.add_route(Route(
    "/api/v1/search", upstream="search-v1", canary_upstream="search-v2", canary_percentage=10
))

req = GatewayRequest(
    method="GET", path="/api/v1/users/42",
    headers={"Authorization": "Bearer eyJhbGciOiJSUzI1NiJ9.fake.token"}
)
print(gw.handle(req))
```

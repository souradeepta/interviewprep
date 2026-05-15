# API Gateway

## Problem Statement
Design an API gateway routing requests to microservices with rate limiting, auth, and transformation.

**Operations:**
- `route(request)` — Route to service
- `authenticate(request)` — Verify credentials
- `rateLimit(user_id)` — Check quota
- `log(request, response)` — Analytics

## Design

### Routing

```
URL path → Service mapping
Load balancing: Round-robin, least-conn
Health checks: Detect failures
Circuit breaker: Prevent cascading failures
```

### Authentication

```
JWT validation
OAuth2 integration
API key verification
Signature validation
```

### Rate Limiting

```
Per-user quotas
Per-endpoint limits
Sliding window counter
Token bucket algorithm
```

### Request/Response Transformation

```
Protocol translation: HTTP → gRPC
Header injection: Auth tokens
Response compression
Caching
```


## Architecture Diagram

```
┌──────────────────────────────────────┐
│   API Gateway (Nginx/Kong)           │
│  ┌──────────────────────────────────┐  │
│  │ Request Routing                  │  │
│  │ - Path → service mapping         │  │
│  │ - Load balancing                 │  │
│  │ Authentication                   │  │
│  │ - JWT validation, OAuth          │  │
│  │ Rate limiting, circuit breaking  │  │
│  │ Request/response transformation  │  │
│  └──────────────────────────────────┘  │
└──────────────────────────────────────────┘
```

## Common Questions & Answers

**Q: Single point of failure?** A: HA gateway cluster (active-active), stateless design, health checks.

**Q: Authentication caching?** A: Cache JWT validation (10min TTL) to reduce auth service load.

**Q: Request timeout tuning?** A: Per-route timeouts. Read timeout > write timeout. Don't timeout indefinitely.

**Q: Versioning (v1, v2)?** A: Header-based or URL path. Deprecate old versions with notice.

## Back-of-Envelope Calculations

1M req/sec, 100ms avg latency budget. Gateway: <5ms overhead ideal. RPS per gateway: 100K-200K. Need 5-10 gateways.

## Design Choice Comparison

| Approach | Pros | Cons |
|----------|------|------|
| Simple proxy | Low overhead | No auth/rate-limit |
| Full gateway | Feature-rich | More complex |
| Service mesh (Istio) | Decentralized | Operational overhead |

## Follow-up Interview Questions

1. Blue-green deployment (zero downtime)? 2. Service discovery integration? 3. Request logging/tracing? 4. Scale beyond 10 gateways? 5. Cost optimization?

## Example Scenario Walkthrough

[Describe a concrete example with step-by-step execution]

## Complexity

| Operation | Time |
|-----------|------|
| Route | O(log n) |
| Authenticate | O(1) |
| Rate limit | O(1) |
| Transform | O(k) where k=payload |

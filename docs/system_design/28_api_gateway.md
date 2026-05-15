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

## Complexity

| Operation | Time |
|-----------|------|
| Route | O(log n) |
| Authenticate | O(1) |
| Rate limit | O(1) |
| Transform | O(k) where k=payload |

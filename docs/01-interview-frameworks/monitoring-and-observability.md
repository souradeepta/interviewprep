# Monitoring & Observability: Metrics, Logging, and Tracing

**Level:** L4-L5
**Time to read:** ~10 min

Build visibility into systems with comprehensive monitoring and observability.

---

## Three Pillars of Observability

### 1. Metrics

**Definition:** Quantitative measurements (counters, gauges, histograms).

```
Requests per second: 1000 QPS
Latency p99: 150ms
Error rate: 0.5%
CPU usage: 45%
Memory: 8GB / 16GB
```

**Key Metrics by Layer:**

| Layer | Metrics |
|-------|---------|
| **Application** | QPS, latency (p50, p95, p99), error rate, business metrics |
| **Database** | Query latency, queries/sec, connection pool, slow queries |
| **Infrastructure** | CPU, memory, disk I/O, network bandwidth |
| **Cache** | Hit ratio, eviction rate, latency |

### 2. Logging

**Definition:** Text records of events for debugging.

```
2024-01-15 10:30:45.123 INFO  [OrderService] User 123 created order
2024-01-15 10:30:46.456 ERROR [PaymentService] Payment failed: timeout after 5s
2024-01-15 10:30:47.789 DEBUG [OrderService] Order 456 moved to shipped state
```

**Best Practices:**
- Include timestamp, level, component, message
- Use structured logging (JSON) for parsing
- Log at right level (DEBUG, INFO, WARN, ERROR)
- Include context (user_id, request_id, order_id)
- Don't log sensitive data (passwords, API keys)

### 3. Tracing

**Definition:** End-to-end request flow across services.

```
Request: GET /api/orders/123
├─ API Server (10ms)
│  ├─ Auth service (5ms)
│  ├─ Order service (15ms)
│  │  ├─ Database query (10ms)
│  │  └─ Cache lookup (1ms, miss)
│  └─ Recommendation service (20ms)
└─ Response (50ms total)
```

**Tools:** Jaeger, Zipkin, AWS X-Ray

---

## Alerting Strategy

### Alert Thresholds

```
Critical alerts (page immediately):
- Error rate > 5%
- P99 latency > 1000ms
- Service down
- Database connection pool depleted

Warning alerts (ticket + monitor):
- Error rate > 1%
- P99 latency > 500ms
- CPU > 80% sustained
- Memory > 85%

Info alerts (dashboard only):
- Service deployed
- Configuration changed
- Maintenance window
```

### Alert Fatigue Prevention

```
❌ Alert on every small anomaly (boy who cried wolf)
✓ Alert only on actionable issues
✓ Use thresholds (not strict equality)
✓ Set reasonable runbooks for each alert
✓ Tune over time (reduce false positives)
```

---

## Monitoring Dashboard

**Real-time displays should include:**

```
Status:
- Service availability: 99.95%
- Active incidents: 0

Performance:
- QPS: 50,000 (trend line: steady)
- P50 latency: 45ms, P95: 120ms, P99: 500ms
- Error rate: 0.1%

Infrastructure:
- CPU: 65% (yellow if > 80%)
- Memory: 12GB / 16GB
- Disk: 80% full
- Network: 500Mbps in, 300Mbps out

Database:
- Active connections: 245 / 500
- Replication lag: 2.3s
- Slow queries: 3 in last hour
```

---

## Observability Best Practices

### Request Tracing

```python
# Add unique ID to each request for tracking
import uuid

request_id = str(uuid.uuid4())
# Include in logs: print(f"[{request_id}] Processing order...")
# Include in responses: response.headers['X-Request-ID'] = request_id
# Client can correlate logs, spans, metrics
```

### Health Checks

```python
# Health endpoint returns status of dependencies
@app.get("/health")
def health():
    db_ok = check_db()
    cache_ok = check_cache()
    queue_ok = check_queue()
    
    if db_ok and cache_ok and queue_ok:
        return {"status": "healthy"}, 200
    else:
        return {"status": "degraded", "db": db_ok, ...}, 503
```

### SLOs & SLIs

```
SLO (Service Level Objective): Target (99.9% uptime)
SLI (Service Level Indicator): Measured (99.92% uptime)
SLA (Service Level Agreement): Contract (99.95% or refund)

Monitor: Are we meeting SLOs?
Track: SLO budget (how much downtime allowed?)
```

---

## Observability Checklist

- ✓ Metrics collected for all critical paths
- ✓ Logging at appropriate levels (DEBUG, INFO, WARN, ERROR)
- ✓ Request tracing with unique IDs
- ✓ Alerting configured for critical issues
- ✓ Dashboard shows key metrics
- ✓ Health check endpoint
- ✓ On-call runbooks for major alerts
- ✓ Structured logging (JSON, not plain text)
- ✓ No sensitive data logged
- ✓ Monitoring for data quality (not just availability)


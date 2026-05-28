# Logging & Monitoring — Observability in Production

**Level:** L4-L5
**Time to read:** ~10 min

Seeing what's happening in your systems.

---

## 📝 Logging Levels

```
DEBUG: Detailed for debugging (low priority)
INFO: General information (requests, milestones)
WARN: Warning (deprecated APIs, slow requests)
ERROR: Error occurred (request failed, recoverable)
FATAL: System critical (unrecoverable)

Production: Usually INFO or WARN (reduce noise)
```

### Structured Logging

```json
{"timestamp": "2024-05-22T10:30:00Z",
 "level": "ERROR",
 "service": "payment",
 "user_id": 123,
 "error": "Payment failed",
 "status_code": 502}
```

Better than: "Payment failed for user 123"

---

## 📊 Metrics

**Latency:** p50, p99 response times
**Throughput:** Requests per second
**Error rate:** % of requests failing
**Resource utilization:** CPU, memory, disk

---

## 🚨 Monitoring

**Black box:** Monitor from outside (HTTP requests)
**White box:** Monitor internals (logs, metrics)
**Hybrid:** Both for complete picture

### Alerting

```
Rule: If error_rate > 5% for 5 minutes
Action: Page oncall engineer

Too sensitive: False alarms → alert fatigue
Too lax: Miss real issues
```

---

## 📈 Observability Stack

**Logs:** ELK (Elasticsearch, Logstash, Kibana)
**Metrics:** Prometheus, Grafana
**Traces:** Jaeger, Zipkin, DataDog
**Correlation:** Trace ID across services

---

## 🔍 Common Patterns

**Tail sampling:** Sample only errors/slow requests
**Log aggregation:** Centralize logs from all services
**Distributed tracing:** Follow request across services
**Error tracking:** Sentry, Rollbar for exceptions

---

## ❓ Interview Q&A

**Q: How would you detect a database query performance issue?**
A: Monitor slow query logs. Track p99 latency. Alert if >threshold. Enable query profiling, analyze execution plan.

**Q: How to debug latency spike?**
A: Check logs (errors), metrics (CPU/memory), traces (which service), database query logs (slow queries).

**Q: Design monitoring for payment system.**
A: Track: transaction count, success rate, latency. Alert: >1% failure, p99 latency >2s. Trace: full transaction path.

---

**Last updated:** 2026-05-22

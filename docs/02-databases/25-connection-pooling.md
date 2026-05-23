# Connection Pooling

Manage database connections efficiently to reduce overhead and prevent connection exhaustion.

---

## ⚖️ Connection Pool Trade-offs

| Parameter | Small Pool | Large Pool |
|-----------|-----------|-----------|
| **Connections** | 10 | 100 |
| **Memory** | Low | High |
| **Latency** | High (wait) | Low (available) |
| **DB Overhead** | Low | High |
| **Scalability** | Limited | Good |

---

## 🏗️ Pool Sizing

```
Formula: pool_size = (core_count * 2) + effective_spindle_count

Example: 8 core CPU
  pool_size = (8 * 2) + 0 = 16 connections

For 100 concurrent users:
  10 pool size → queue, latency increases
  50 pool size → good
  100 pool size → overkill, waste memory
```

---

## ❓ Interview Q&A

**Q1: Connection pool exhausted - 1000 requests waiting**

A:
- Causes:
  1. Pool too small relative to traffic
  2. Connection not released (leak)
  3. Long-running queries holding connections
  
- Solutions:
  1. Increase pool size
  2. Set connection timeout (force close)
  3. Optimize queries (reduce duration)
  4. Implement circuit breaker (stop new requests if queue > threshold)

---

**Last updated:** 2026-05-22

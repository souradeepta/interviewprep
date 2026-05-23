# Database Monitoring & Alerting

Monitor key database metrics and set up alerts to detect issues before they impact users.

---

## ⚖️ Monitoring Strategy

### Key Metrics to Track

| Metric | Warning | Critical | Action |
|--------|---------|----------|--------|
| **CPU** | > 70% | > 90% | Scale up or optimize queries |
| **Memory** | > 80% | > 95% | Add memory or reduce cache |
| **Disk** | > 70% | > 90% | Archive old data or expand |
| **Query Latency** | > 100ms | > 1s | Add index or rewrite |
| **Connections** | > 80% pool | > 95% | Increase pool or close leaks |
| **Replication Lag** | > 1s | > 5s | Check replica, restart |

---

## 🏗️ Monitoring Patterns

### Alert Types

```
Type 1: Threshold
  if cpu > 90% for 5 min → alert

Type 2: Trend
  if cpu increased 20% in 1 hour → alert

Type 3: Anomaly
  if query latency 10x normal → alert

Type 4: Composite
  if (cpu > 80% AND connections > 80%) → alert
```

---

## ❓ Interview Q&A

**Q1: Database CPU spike at 2AM - how to prevent?**

A:
- Solutions:
  1. Set alert at 70% CPU
  2. Implement autoscaling
  3. Schedule heavy workloads off-peak
  4. Cache popular queries

**Q2: Disk full prevented write - solution?**

A:
- Monitoring: Alert at 70% used
- Prevention: Implement retention (delete old data)
- Quick fix: Archive to S3

---

**Last updated:** 2026-05-22

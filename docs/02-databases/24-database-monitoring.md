# Database Monitoring & Alerting

**Level:** L4-L5+
**Time to read:** ~30 min

Detect problems before users do by tracking the right metrics, setting meaningful thresholds, and building runbooks for every alert.

---

## ⚖️ Monitoring Strategy Trade-offs

| Approach | Coverage | Cost | Noise | Lag | Best For |
|----------|----------|------|-------|-----|---------|
| **Threshold alerts** | Specific metrics | Low | Medium | Low | Known failure modes |
| **Anomaly detection** | Any metric | High | High | Medium | Unknown issues |
| **SLO-based** | User-visible | Medium | Low | Medium | Production SLAs |
| **Log-based** | Full detail | High | High | Low | Debugging |
| **Synthetic probes** | End-to-end | Low | Low | Low | External validation |

---

## 🏗️ Metric Taxonomy

### The Four Golden Signals (applied to databases)

```
1. LATENCY
   ├─ Query latency p50 / p95 / p99 / p999
   ├─ Transaction duration
   └─ Replication lag

2. TRAFFIC
   ├─ Queries per second (QPS) by type (SELECT/INSERT/UPDATE/DELETE)
   ├─ Connection rate
   └─ Bytes in / bytes out

3. ERRORS
   ├─ Query error rate (%)
   ├─ Deadlock rate
   └─ Connection refused count

4. SATURATION
   ├─ CPU utilization
   ├─ Memory (buffer pool hit rate)
   ├─ Disk I/O utilization
   └─ Connection pool usage (%)
```

### Alert Thresholds (PostgreSQL / MySQL)

| Metric | Warning | Critical | Action |
|--------|---------|----------|--------|
| **Query latency p99** | > 200ms | > 1000ms | Check slow query log, add index |
| **CPU utilization** | > 70% for 5m | > 90% for 2m | Scale instance / kill long queries |
| **Memory (shared_buffers hit rate)** | < 95% | < 90% | Increase memory / reduce dataset |
| **Disk I/O wait** | > 20% | > 50% | Add IOPS / move to SSD |
| **Active connections** | > 70% of max | > 90% of max | Tune pool / scale replicas |
| **Replication lag** | > 1s | > 5s | Check replica health / add capacity |
| **Deadlock rate** | > 1/min | > 10/min | Analyze lock ordering |
| **Disk usage** | > 70% | > 85% | Archive / autovacuum / expand |
| **Long-running queries** | > 30s | > 300s | Kill / optimize |

---

## 📊 Monitoring Stack Architecture

```
Applications / DB Instances
       │
   [Exporters]
   ├─ postgres_exporter  (PostgreSQL metrics)
   ├─ mysqld_exporter    (MySQL metrics)
   └─ custom SQL probes  (business metrics)
       │
       ↓
[Prometheus]  ← scrapes every 15s, retains 15 days
       │
   ┌───┴───┐
[Grafana]  [AlertManager]
(dashboards) (routes alerts → PagerDuty / Slack)
```

### Key Prometheus Queries

```promql
# Query latency p99 (milliseconds)
histogram_quantile(0.99,
  rate(pg_stat_statements_total_time_seconds_bucket[5m])
) * 1000

# Connection pool utilization %
pg_stat_activity_count{state="active"} /
pg_settings_max_connections * 100

# Replication lag in seconds
pg_replication_lag

# Cache hit rate
pg_stat_bgwriter_buffers_hit /
(pg_stat_bgwriter_buffers_hit + pg_stat_bgwriter_buffers_read) * 100

# Deadlocks per minute
rate(pg_stat_database_deadlocks[1m]) * 60
```

---

## 🔍 Implementation

### Metrics Collector

```python
import time, statistics, threading
from collections import defaultdict, deque
from typing import Dict, List, Optional

class DBMetricsCollector:
    """Lightweight in-process metrics collector for a database connection pool."""

    def __init__(self, window_secs: int = 60):
        self.window = window_secs
        self._latencies: deque = deque()  # (timestamp, latency_ms)
        self._errors: deque = deque()
        self._lock = threading.Lock()
        self.counters: Dict[str, int] = defaultdict(int)

    def record_query(self, latency_ms: float, error: bool = False,
                     query_type: str = "SELECT"):
        now = time.time()
        with self._lock:
            self._latencies.append((now, latency_ms))
            self._trim(self._latencies)
            if error:
                self._errors.append(now)
                self._trim(self._errors)
            self.counters[f"query_{query_type.lower()}"] += 1

    def _trim(self, dq: deque):
        cutoff = time.time() - self.window
        while dq and dq[0][0] < cutoff:
            dq.popleft()

    def percentile(self, p: float) -> Optional[float]:
        with self._lock:
            lats = [v for _, v in self._latencies]
        if not lats:
            return None
        lats.sort()
        idx = int(len(lats) * p / 100)
        return lats[min(idx, len(lats) - 1)]

    def error_rate(self) -> float:
        total = sum(1 for _ in self._latencies)
        errors = len(self._errors)
        return errors / total if total else 0.0

    def snapshot(self) -> dict:
        return {
            "p50_ms":      self.percentile(50),
            "p95_ms":      self.percentile(95),
            "p99_ms":      self.percentile(99),
            "error_rate":  self.error_rate(),
            "total_queries": sum(self.counters.values()),
        }

# Demo
import random
collector = DBMetricsCollector(window_secs=60)

for _ in range(1000):
    lat = random.lognormvariate(3, 1)  # realistic skewed latency
    err = random.random() < 0.01
    collector.record_query(lat, error=err)

snap = collector.snapshot()
for k, v in snap.items():
    print(f"  {k:<20} {v:.2f}" if v is not None else f"  {k:<20} None")
```

### Alert Manager

```python
from enum import Enum
from typing import Callable
import time

class Severity(Enum):
    WARNING  = "warning"
    CRITICAL = "critical"

class Alert:
    def __init__(self, name: str, severity: Severity, message: str):
        self.name = name
        self.severity = severity
        self.message = message
        self.fired_at = time.time()

class AlertManager:
    def __init__(self):
        self.rules: List[dict] = []
        self.active_alerts: Dict[str, Alert] = {}
        self.handlers: List[Callable] = []

    def add_rule(self, name: str, fn: Callable, warning, critical, unit=""):
        self.rules.append({
            "name": name, "fn": fn,
            "warning": warning, "critical": critical, "unit": unit,
        })

    def add_handler(self, fn: Callable):
        self.handlers.append(fn)

    def evaluate(self, metrics: dict):
        for rule in self.rules:
            value = rule["fn"](metrics)
            if value is None:
                continue
            if value >= rule["critical"]:
                self._fire(rule["name"], Severity.CRITICAL,
                           f"{rule['name']} = {value:.1f}{rule['unit']} (critical: {rule['critical']})")
            elif value >= rule["warning"]:
                self._fire(rule["name"], Severity.WARNING,
                           f"{rule['name']} = {value:.1f}{rule['unit']} (warning: {rule['warning']})")
            else:
                self._resolve(rule["name"])

    def _fire(self, name: str, severity: Severity, message: str):
        if name not in self.active_alerts:
            alert = Alert(name, severity, message)
            self.active_alerts[name] = alert
            for h in self.handlers:
                h(alert)

    def _resolve(self, name: str):
        if name in self.active_alerts:
            print(f"  ✅ RESOLVED: {name}")
            del self.active_alerts[name]

# Demo
def log_alert(alert: Alert):
    icon = "🔴" if alert.severity == Severity.CRITICAL else "🟡"
    print(f"  {icon} {alert.severity.value.upper()}: {alert.message}")

mgr = AlertManager()
mgr.add_handler(log_alert)
mgr.add_rule("query_latency_p99_ms", lambda m: m.get("p99_ms"), warning=200, critical=1000, unit="ms")
mgr.add_rule("error_rate_pct",        lambda m: m.get("error_rate", 0) * 100, warning=1, critical=5, unit="%")

print("Normal metrics:")
mgr.evaluate({"p99_ms": 80, "error_rate": 0.001})

print("\nDegraded metrics:")
mgr.evaluate({"p99_ms": 1200, "error_rate": 0.08})
```

---

## ❓ Interview Q&A

**Q1: Design monitoring for a 10-node PostgreSQL cluster.**

A:
- **Exporters**: postgres_exporter on each node → Prometheus
- **Metrics**: 4 golden signals per node + cluster-level (replication lag, leader status)
- **Dashboards** (Grafana):
  - Cluster overview: QPS, error rate, p99 latency per node
  - Replication panel: lag per replica, WAL position delta
  - Slow query heatmap
- **Alerts**:
  - p99 > 500ms for 5 min → PagerDuty
  - Replication lag > 5s → Slack
  - Any node CPU > 90% for 2 min → Slack
- **Runbooks**: each alert links to runbook with decision tree

**Q2: Database CPU spiked to 100% at 2 AM and auto-resolved. How do you prevent recurrence?**

A:
1. Pull slow query log from that window: `pg_stat_statements` or `slow_query_log`
2. Identify top 3 queries by total time
3. Check if it was a scheduled job (batch report, vacuum, backup)
4. Fix: add index, rewrite query, or reschedule job to 4 AM with `SET statement_timeout`
5. Add alert: if CPU > 80% for > 3 min → page on-call. Set `log_min_duration_statement = 100` to capture queries going forward.

**Q3: How do you alert on anomalies rather than fixed thresholds?**

A: Use rate-of-change alerting:
```promql
# Alert if p99 latency increases > 50% vs previous hour
(query_p99 - query_p99 offset 1h) / (query_p99 offset 1h) > 0.5
```
Or use Prometheus `predict_linear` to catch trends:
```promql
predict_linear(pg_database_size_bytes[6h], 3600) > 500e9
# → Alert if DB will exceed 500GB in 1 hour
```

**Q4: Disk fills up and prevents writes. How do you prevent this?**

A:
1. **Alert at 70%**: enough runway to act
2. **Auto-archiving**: move data older than 90 days to S3 on schedule
3. **Retention policies**: `DELETE FROM events WHERE created_at < now() - interval '1 year'`
4. **Autovacuum tuning**: reclaim dead row space frequently
5. **Monitoring**: `predict_linear` to estimate days until full

**Q5: How do you build an on-call rotation for database alerts?**

A:
- **Alert routing**: PagerDuty / OpsGenie with escalation policies
- **Runbooks linked to every alert** — on-call engineer should never have to improvise
- **Alert fatigue prevention**: consolidate related alerts, require >5min persistence before paging
- **Post-mortems**: every P1 → blameless post-mortem → action items → alert refinement
- **SLO tracking**: burn rate alerts catch SLO budget consumption before it's critical

---

## 🧪 Practical Exercises

### Exercise 1: Slow Query Detector (Easy)

**Problem:** Log queries taking > 100ms and emit a metric for alerting.

```python
import time, functools, logging

logger = logging.getLogger("slow_queries")

def track_query(threshold_ms: float = 100):
    """Decorator that logs and tracks slow queries."""
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            try:
                result = fn(*args, **kwargs)
                return result
            finally:
                elapsed = (time.perf_counter() - start) * 1000
                if elapsed > threshold_ms:
                    logger.warning(
                        "SLOW_QUERY fn=%s duration_ms=%.1f args=%s",
                        fn.__name__, elapsed, args[:2]
                    )
        return wrapper
    return decorator

@track_query(threshold_ms=50)
def get_user(user_id: int):
    time.sleep(0.08)  # simulate 80ms query
    return {"id": user_id, "name": "Alice"}

logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(message)s")
get_user(42)
```

---

### Exercise 2: Connection Pool Monitor (Medium)

**Problem:** Pool of 20 connections. Alert when utilization > 80% and log when queues form.

```python
import threading, time, queue, random
from dataclasses import dataclass, field

@dataclass
class PoolStats:
    total: int = 20
    active: int = 0
    waiting: int = 0
    peak_active: int = 0
    wait_events: int = 0

class MonitoredPool:
    def __init__(self, size: int = 20, alert_threshold: float = 0.8):
        self.size = size
        self.alert_threshold = alert_threshold
        self._semaphore = threading.Semaphore(size)
        self.stats = PoolStats(total=size)
        self._lock = threading.Lock()

    def acquire(self, timeout: float = 5.0) -> bool:
        with self._lock:
            self.stats.waiting += 1
        acquired = self._semaphore.acquire(timeout=timeout)
        with self._lock:
            self.stats.waiting -= 1
            if acquired:
                self.stats.active += 1
                self.stats.peak_active = max(self.stats.peak_active, self.stats.active)
                util = self.stats.active / self.size
                if util >= self.alert_threshold:
                    print(f"  ⚠️  Pool utilization {util:.0%} — {self.stats.active}/{self.size} connections")
            else:
                self.stats.wait_events += 1
                print(f"  🔴 Connection wait timeout! waiting={self.stats.waiting}")
        return acquired

    def release(self):
        with self._lock:
            self.stats.active -= 1
        self._semaphore.release()

    def snapshot(self) -> dict:
        with self._lock:
            return {
                "active": self.stats.active,
                "waiting": self.stats.waiting,
                "utilization_pct": self.stats.active / self.size * 100,
                "peak_active": self.stats.peak_active,
                "wait_events": self.stats.wait_events,
            }

pool = MonitoredPool(size=10, alert_threshold=0.7)

def simulate_request(pool, duration):
    if pool.acquire(timeout=2):
        time.sleep(duration)
        pool.release()

threads = [threading.Thread(target=simulate_request, args=(pool, random.uniform(0.1, 0.5)))
           for _ in range(15)]
for t in threads: t.start()
for t in threads: t.join()
snap = pool.snapshot()
print(f"\nFinal stats: {snap}")
```

---

### Exercise 3: SLO Dashboard Design (Hard)

**Problem:** Design an SLO where 99.9% of queries complete in < 200ms. Compute burn rate and time to exhaustion.

```python
from collections import deque
import time, random

class SLOTracker:
    """Track an error-budget SLO: target=99.9%, threshold_ms=200."""

    def __init__(self, target: float = 0.999, threshold_ms: float = 200,
                 window_hours: int = 720):  # 30 days
        self.target = target
        self.threshold_ms = threshold_ms
        self.window_secs = window_hours * 3600
        self._events: deque = deque()  # (ts, is_good)

    def record(self, latency_ms: float):
        self._events.append((time.time(), latency_ms <= self.threshold_ms))
        self._trim()

    def _trim(self):
        cutoff = time.time() - self.window_secs
        while self._events and self._events[0][0] < cutoff:
            self._events.popleft()

    def slo_status(self) -> dict:
        if not self._events:
            return {}
        total = len(self._events)
        good  = sum(1 for _, ok in self._events if ok)
        bad   = total - good
        reliability = good / total
        budget_total    = (1 - self.target) * total
        budget_remaining = max(0, budget_total - bad)
        burn_rate = bad / max(budget_total, 1)

        hours_remaining = None
        if burn_rate > 0:
            # How long until budget exhausted at current burn rate?
            rate_per_sec = bad / max((self._events[-1][0] - self._events[0][0]), 1)
            budget_secs_remaining = budget_remaining / max(rate_per_sec, 1e-9)
            hours_remaining = budget_secs_remaining / 3600

        return {
            "reliability_pct":      reliability * 100,
            "slo_met":              reliability >= self.target,
            "error_budget_pct":     budget_remaining / budget_total * 100 if budget_total else 100,
            "burn_rate":            burn_rate,
            "hours_to_exhaustion":  hours_remaining,
        }

# Simulate 10,000 queries with 0.5% above threshold
slo = SLOTracker(target=0.999, threshold_ms=200)
for _ in range(10000):
    lat = random.lognormvariate(4.5, 0.8)  # mostly fast, some slow
    slo.record(lat)

status = slo.slo_status()
print("SLO Status:")
for k, v in status.items():
    print(f"  {k:<30} {v:.2f}" if isinstance(v, float) else f"  {k:<30} {v}")
```

---

## 💡 Observability Stack Recommendations

| Stack Size | Recommended Tools |
|---|---|
| **Startup (< 5 DBs)** | Datadog / New Relic (managed, fast setup) |
| **Mid-size (5–20 DBs)** | Prometheus + Grafana + AlertManager |
| **Large (20+ DBs)** | Prometheus + Thanos (long retention) + Grafana + PagerDuty |
| **AWS shops** | CloudWatch + RDS Enhanced Monitoring + SNS |
| **GCP shops** | Cloud Monitoring + Cloud Spanner insights |

---

**Last updated:** 2026-05-22

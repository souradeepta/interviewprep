# Time-Series Optimization Deep Dive

Optimize databases for fast ingestion and querying of massive time-series datasets: metrics, events, sensor data, financial ticks, and IoT streams.

---

## ⚖️ Time-Series Strategy Trade-offs

| Strategy | Write Throughput | Query Speed | Storage Cost | Complexity |
|----------|-----------------|-------------|--------------|-----------|
| **Raw storage** | Very High | Slow (full scan) | Very High | Low |
| **Downsampling** | High | Fast (fewer rows) | Low | Medium |
| **Pre-aggregation** | Medium | Instant | Very Low | High |
| **Gorilla compression** | Medium | Medium | 12× cheaper | High |
| **Columnar (Parquet)** | Low | Very fast | Low | Medium |
| **TimescaleDB hypertable** | Very High | Fast (chunk pruning) | Low | Low |

### Storage Comparison (1B samples/day)

```
Format                  Size/sample   Daily total   Annual total
──────────────────────────────────────────────────────────────────
Raw (int64 + int64)     16 bytes      15.3 GB        5.6 TB
Float64 + timestamp     16 bytes      15.3 GB        5.6 TB
Gorilla compressed      1.37 bytes    1.3 GB         482 GB
Downsampled 1-min avg   16 bytes/min  22 MB          8 GB
Downsampled 1-hr avg    16 bytes/hr   384 KB         136 MB
Columnar (Parquet)      ~2 bytes      1.9 GB         684 GB
```

### TSDB Comparison

| Feature | InfluxDB | TimescaleDB | Prometheus | VictoriaMetrics |
|---------|----------|-------------|------------|-----------------|
| Query lang | InfluxQL/Flux | SQL | PromQL | MetricsQL |
| Write/s | 500K | 300K | 1M | 1M+ |
| Compression | 8–12× | 2–5× | 1–3× | 10–20× |
| Long-term storage | 3rd party | Postgres | Thanos/Cortex | Built-in |
| SQL joins | No | Yes | No | No |
| Best for | IoT, metrics | Analytics | Monitoring | Metrics at scale |

---

## 🏗️ Architecture Patterns

### Pattern 1: Tiered Storage (Hot / Warm / Cold)

```
Data Age        Storage          Access Time     Cost/GB/mo
──────────────────────────────────────────────────────────────
0–24 hours      Memory/SSD       <1ms             $50
1–7 days        SSD (local)      <10ms            $0.20
7–30 days       SSD (EBS gp3)    <50ms            $0.08
30d–1 year      HDD/S3 IA        <500ms           $0.023
> 1 year        S3 Glacier       minutes          $0.004

Automatic tier transitions:
  TimescaleDB compression policy:
    CALL add_compression_policy('metrics', INTERVAL '7 days');
  Data retention:
    CALL add_retention_policy('metrics', INTERVAL '1 year');
  External archival:
    Export to Parquet on S3 via Spark job (weekly batch)
```

### Pattern 2: Chunk Pruning (TimescaleDB)

```
Standard PostgreSQL:
  SELECT avg(value) FROM metrics WHERE time > now() - interval '1 hour'
  → Full table scan: reads ALL 365B rows, returns last 3.6M

TimescaleDB hypertable (chunk_time_interval = '1 day'):
  → Chunk pruning: skips 364 daily chunks, reads ONLY today's chunk
  → 1M rows scanned instead of 365B rows → 365,000× faster

 Table: metrics (hypertable)
 ├── chunk_2026_01_01 (1 day)
 ├── chunk_2026_01_02 (1 day)
 │   ...
 └── chunk_2026_05_22 (today) ← only chunk read
```

### Pattern 3: Gorilla Compression (Delta-of-Delta)

```
Timestamps (seconds since epoch):
  Raw:      [1700000000, 1700000060, 1700000120, 1700000181]
  Delta:    [       60,          60,          61]
  DoD:      [           0,          1]  ← nearly always 0
  Encoded:  "00" (same delta) or "10" + 7-bit correction

Values (float64):
  XOR with previous value; leading/trailing zero compression
  Same value:   "0" (1 bit)
  Near value:   variable-length XOR encoding
  
Result: 1.37 bytes/point average (vs. 16 bytes raw = 12× compression)
```

---

## 📊 Implementation Examples

```python
import time
import struct
import math
from collections import deque
from typing import List, Tuple, Optional

# ── Downsampler ───────────────────────────────────────────────────────────────

class TimeSeriesDownsampler:
    """
    Streaming downsampler: aggregates incoming samples into configurable windows.
    Supports: mean, min, max, sum, count, p99.
    """

    def __init__(self, window_seconds: int = 60):
        self.window_seconds = window_seconds
        self._buffer: deque = deque()
        self._window_start: Optional[float] = None
        self._completed: list = []

    def add(self, timestamp: float, value: float):
        """Add a raw sample. Flushes completed windows automatically."""
        if self._window_start is None:
            self._window_start = timestamp - (timestamp % self.window_seconds)

        window_end = self._window_start + self.window_seconds
        if timestamp >= window_end:
            self._flush()
            self._window_start = timestamp - (timestamp % self.window_seconds)

        self._buffer.append((timestamp, value))

    def _flush(self):
        if not self._buffer:
            return
        values = [v for _, v in self._buffer]
        agg = {
            "window_start": self._window_start,
            "count": len(values),
            "sum": sum(values),
            "mean": sum(values) / len(values),
            "min": min(values),
            "max": max(values),
            "p99": sorted(values)[int(len(values) * 0.99)],
        }
        self._completed.append(agg)
        self._buffer.clear()

    def get_aggregates(self) -> list:
        return list(self._completed)


# ── Retention Manager ─────────────────────────────────────────────────────────

class RetentionManager:
    """
    Policy-based retention: different resolutions for different ages.
    Simulates a continuous rollup job.
    """

    POLICIES = [
        {"max_age_days": 1,   "resolution_sec": 1,     "label": "raw"},
        {"max_age_days": 7,   "resolution_sec": 60,    "label": "1-min"},
        {"max_age_days": 30,  "resolution_sec": 3600,  "label": "1-hour"},
        {"max_age_days": 365, "resolution_sec": 86400, "label": "1-day"},
    ]

    def __init__(self):
        self._tiers: dict = {p["label"]: [] for p in self.POLICIES}

    def ingest(self, timestamp: float, value: float):
        self._tiers["raw"].append((timestamp, value))

    def apply_retention(self, now: Optional[float] = None):
        """Move data between tiers and expire old data."""
        now = now or time.time()
        for policy in self.POLICIES:
            tier = policy["label"]
            cutoff = now - policy["max_age_days"] * 86400
            before = len(self._tiers[tier])
            self._tiers[tier] = [
                (ts, v) for ts, v in self._tiers[tier] if ts >= cutoff
            ]
            expired = before - len(self._tiers[tier])
            if expired:
                print(f"Expired {expired} samples from {tier}")

    def stats(self) -> dict:
        return {label: len(data) for label, data in self._tiers.items()}


# ── Gorilla-style compressor (simplified) ────────────────────────────────────

class GorillaCompressor:
    """
    Simplified Gorilla timestamp compression (delta-of-delta).
    Demonstrates the space efficiency without bit-packing complexity.
    """

    def compress(self, timestamps: List[float]) -> List[int]:
        """Returns list of delta-of-deltas (integers)."""
        if len(timestamps) < 2:
            return list(timestamps)
        deltas = [int(timestamps[i+1] - timestamps[i]) for i in range(len(timestamps)-1)]
        dod = [deltas[0]] + [deltas[i+1] - deltas[i] for i in range(len(deltas)-1)]
        return dod

    def decompress(self, first_ts: float, dods: List[int]) -> List[float]:
        """Reconstruct timestamps from delta-of-deltas."""
        if not dods:
            return [first_ts]
        deltas = [dods[0]]
        for d in dods[1:]:
            deltas.append(deltas[-1] + d)
        timestamps = [first_ts]
        for delta in deltas:
            timestamps.append(timestamps[-1] + delta)
        return timestamps

    def compression_ratio(self, timestamps: List[float]) -> float:
        """Estimate compression ratio (assuming 4 bits avg per DoD vs 64 bits raw)."""
        dods = self.compress(timestamps)
        zeros = sum(1 for d in dods if d == 0)
        pct_zeros = zeros / max(len(dods), 1)
        avg_bits = 2 * pct_zeros + 10 * (1 - pct_zeros)  # simplified
        raw_bits = 64
        return raw_bits / avg_bits


# Demo
print("=== Downsampler ===")
ds = TimeSeriesDownsampler(window_seconds=60)
now = time.time()
for i in range(120):
    ds.add(now + i, 100 + (i % 10) - 5)  # Simulated metric: 100 ± 5

aggs = ds.get_aggregates()
print(f"120 raw samples → {len(aggs)} 1-minute aggregates")
if aggs:
    print(f"  Window: mean={aggs[0]['mean']:.2f}, p99={aggs[0]['p99']:.2f}, count={aggs[0]['count']}")

print("\n=== Gorilla compression ===")
gc = GorillaCompressor()
timestamps = [now + i * 60 for i in range(1440)]  # 1 day at 1-min resolution
dods = gc.compress(timestamps)
zeros_pct = sum(1 for d in dods if d == 0) / len(dods) * 100
print(f"1,440 timestamps → {len(dods)} DoDs, {zeros_pct:.1f}% zeros")
print(f"Estimated compression ratio: {gc.compression_ratio(timestamps):.1f}×")

print("\n=== Retention Manager ===")
rm = RetentionManager()
for i in range(100):
    rm.ingest(now - i * 3600, i * 1.5)  # 100 hours of data
print("Before:", rm.stats())
rm.apply_retention(now)
print("After:", rm.stats())
```

---

## 🔧 TimescaleDB Configuration

```sql
-- 1. Create hypertable (partitions by time automatically)
CREATE TABLE metrics (
    time        TIMESTAMPTZ NOT NULL,
    metric_name TEXT NOT NULL,
    host        TEXT NOT NULL,
    value       DOUBLE PRECISION,
    tags        JSONB
);

SELECT create_hypertable('metrics', 'time', chunk_time_interval => INTERVAL '1 day');

-- 2. Composite index for common query patterns
CREATE INDEX ON metrics (metric_name, host, time DESC);

-- 3. Native compression (enable after 7 days)
ALTER TABLE metrics SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'metric_name, host',
    timescaledb.compress_orderby = 'time DESC'
);

SELECT add_compression_policy('metrics', compress_after => INTERVAL '7 days');

-- 4. Continuous aggregates (pre-computed rollups)
CREATE MATERIALIZED VIEW metrics_hourly
WITH (timescaledb.continuous) AS
    SELECT
        time_bucket('1 hour', time) AS bucket,
        metric_name,
        host,
        avg(value)    AS avg_value,
        min(value)    AS min_value,
        max(value)    AS max_value,
        count(*)      AS sample_count
    FROM metrics
    GROUP BY bucket, metric_name, host
WITH NO DATA;

SELECT add_continuous_aggregate_policy('metrics_hourly',
    start_offset => INTERVAL '3 hours',
    end_offset   => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour'
);

-- 5. Query: last hour per host (chunk-pruned, index-only)
SELECT host, avg(value) AS avg_cpu
FROM metrics
WHERE metric_name = 'cpu_usage'
  AND time > now() - INTERVAL '1 hour'
GROUP BY host
ORDER BY avg_cpu DESC;

-- Uses: chunk pruning (1 chunk) + index on (metric_name, host, time DESC)
-- Estimated: 5–20ms for 1M samples/hour

-- 6. Retention policy
SELECT add_retention_policy('metrics', drop_after => INTERVAL '90 days');
```

---

## ❓ Interview Q&A

**Q1: Store 1 billion metrics per day for 1 year. How do you size the system?**

A: Storage calculation:
- Raw: 1B × 16 bytes = 16 GB/day × 365 = 5.8 TB/year — feasible but expensive
- Gorilla compressed: 1B × 1.37 bytes = 1.3 GB/day × 365 = **482 GB/year** — practical
- With downsampling after 7 days: keep raw 7 days (91 GB), then 1-min rollup: 10 MB/day × 358 = **3.6 GB/year**
- Total: ~100 GB — fits on a single SSD

Architecture: VictoriaMetrics (1M+ writes/sec single node), 30× compression, built-in downsampling, S3 remote storage for cold tier.

**Q2: Query "sum of errors last 6 months" is taking 30 seconds. How do you fix it?**

A: Three approaches in increasing complexity:
1. **Continuous aggregate** (instant, best): Pre-compute daily error sums; query 180 rows instead of 15B samples
2. **Materialized view** with scheduled refresh: `CREATE MATERIALIZED VIEW daily_errors AS SELECT date, SUM(value) FROM metrics WHERE metric_name='errors' GROUP BY date`; refresh nightly
3. **Index + chunk pruning**: Ensure index on `(metric_name, time)` and the query uses `WHERE metric_name='errors'` first — reduces scan from all metrics to error-only chunks

**Q3: Cardinality explosion is killing your TSDB. What's happening and how do you fix it?**

A: High cardinality = too many unique label combinations. Example: `request_id` as a label = 1M unique time series (one per request) instead of 1 (one per endpoint).

Detection: InfluxDB Cardinality metrics; Prometheus `tsdb_head_series > 1M` alert.

Fix:
1. Remove high-cardinality labels from metrics (request_id, user_id, session_id)
2. Record events in a log/trace system instead (not metrics)
3. Aggregate before ingestion: count requests per endpoint, not per request
4. Set `max_series_per_metric = 10,000` limit in VictoriaMetrics

**Q4: How does delta-of-delta compression work in practice?**

A: Prometheus/InfluxDB timestamps at 15s intervals:
```
Raw:    [0, 15, 30, 45, 60, 75]
Delta:  [15, 15, 15, 15, 15]          # all 15
DoD:    [0, 0, 0, 0]                  # all zeros → 2-bit "00" encoding
Result: first timestamp (64 bits) + 1 delta (32 bits) + N zeros (2 bits each)
```
For regular scrape intervals (99% of monitoring): 2-bit/sample vs. 64-bit/sample = **32× compression** on timestamps. Values use XOR compression: if `val[i] XOR val[i-1] == 0` (same value), store single "0" bit.

**Q5: How do you handle out-of-order writes in a time-series database?**

A: Out-of-order writes happen with network delays or late-arriving sensors. Two approaches:
1. **Accept out-of-order within a window** (InfluxDB/Prometheus): allow writes up to `out_of_order_time_window` (e.g., 1 hour) into already-compressed chunks. Penalty: re-open and re-compress affected chunk
2. **Reject late arrivals** (strict, Prometheus default): reject any sample with timestamp older than 1h; agent must handle retransmission
3. **Dedicated late-data lane**: ingest late samples into a separate "backfill" table, merge with main data during nightly compaction; ensures main query path is always optimized

---

## 🧪 Practical Exercises

### Exercise 1: Time-Series Aggregation Engine (Easy)

**Problem:** Implement a multi-resolution rollup: raw → 1-min → 1-hour → 1-day.

```python
from collections import defaultdict
import math

class MultiResolutionStore:
    RESOLUTIONS = [
        ("raw",    1),
        ("1min",   60),
        ("1hour",  3600),
        ("1day",   86400),
    ]

    def __init__(self):
        self.tiers: dict = {name: defaultdict(list) for name, _ in self.RESOLUTIONS}

    def insert(self, metric: str, timestamp: float, value: float):
        """Insert into raw tier; rollup happens on query."""
        bucket = int(timestamp)  # 1s bucket
        self.tiers["raw"][(metric, bucket)].append(value)

    def rollup(self, metric: str, source_tier: str, target_tier: str, resolution: int):
        """Aggregate source_tier into target_tier at given resolution."""
        for (m, bucket), values in list(self.tiers[source_tier].items()):
            if m != metric:
                continue
            aligned = (bucket // resolution) * resolution
            self.tiers[target_tier][(m, aligned)].extend(values)

    def query(self, metric: str, tier: str) -> list:
        result = []
        for (m, bucket), values in sorted(self.tiers[tier].items()):
            if m == metric:
                result.append({
                    "bucket": bucket,
                    "mean": sum(values) / len(values),
                    "count": len(values),
                })
        return result


import time
store = MultiResolutionStore()
now = int(time.time())

# Simulate 5 minutes of 1-second samples
for i in range(300):
    store.insert("cpu", now + i, 40 + (i % 20) - 10)

store.rollup("cpu", "raw", "1min", 60)
store.rollup("cpu", "1min", "1hour", 3600)

print(f"Raw: {len(store.query('cpu', 'raw'))} buckets")
print(f"1-min: {len(store.query('cpu', '1min'))} buckets")
if store.query("cpu", "1min"):
    print(f"  Sample: {store.query('cpu', '1min')[0]}")
```

---

### Exercise 2: Anomaly Detection on Time-Series (Medium)

**Problem:** Detect anomalies using rolling z-score on a metric stream.

```python
import math
from collections import deque

class ZScoreAnomalyDetector:
    """
    Flags samples more than `threshold` standard deviations from the rolling mean.
    Window size: last N samples.
    """

    def __init__(self, window: int = 60, threshold: float = 3.0):
        self.window = window
        self.threshold = threshold
        self._values = deque(maxlen=window)
        self._anomalies = []

    def add(self, timestamp: float, value: float) -> bool:
        is_anomaly = False
        if len(self._values) >= 10:  # Need enough history
            mean = sum(self._values) / len(self._values)
            variance = sum((v - mean) ** 2 for v in self._values) / len(self._values)
            std = math.sqrt(variance) or 1e-9
            z_score = abs(value - mean) / std

            if z_score > self.threshold:
                is_anomaly = True
                self._anomalies.append({
                    "timestamp": timestamp,
                    "value": value,
                    "z_score": round(z_score, 2),
                    "mean": round(mean, 2),
                    "std": round(std, 2),
                })

        self._values.append(value)
        return is_anomaly

    def get_anomalies(self) -> list:
        return list(self._anomalies)


detector = ZScoreAnomalyDetector(window=30, threshold=3.0)
now = time.time()

# Normal traffic
for i in range(60):
    detector.add(now + i, 100 + (i % 10) - 5)

# Spike
detector.add(now + 60, 500)   # Anomaly
detector.add(now + 61, 520)   # Anomaly

# Return to normal
for i in range(10):
    detector.add(now + 62 + i, 100 + i % 5)

print(f"Anomalies detected: {len(detector.get_anomalies())}")
for a in detector.get_anomalies():
    print(f"  value={a['value']}, z={a['z_score']}, mean±std={a['mean']}±{a['std']}")
```

---

### Exercise 3: Adaptive Downsampling Policy (Hard)

**Problem:** Implement adaptive downsampling that increases resolution during anomalies.

```python
from enum import Enum

class Resolution(Enum):
    SECOND  = 1
    MINUTE  = 60
    HOUR    = 3600

class AdaptiveDownsampler:
    """
    Normal: 1-min resolution
    Anomaly detected: switch to 1-sec resolution for anomaly window
    After 5 min calm: revert to 1-min
    """

    def __init__(self, anomaly_detector: ZScoreAnomalyDetector):
        self.detector = anomaly_detector
        self._resolution = Resolution.MINUTE
        self._anomaly_last_seen: Optional[float] = None
        self._calm_threshold = 300  # 5 minutes before reverting
        self._store: list = []

    def ingest(self, timestamp: float, value: float):
        is_anomaly = self.detector.add(timestamp, value)

        if is_anomaly:
            self._anomaly_last_seen = timestamp
            self._resolution = Resolution.SECOND
            print(f"  [t={timestamp:.0f}] Anomaly! Switching to 1s resolution")
        elif (self._resolution != Resolution.MINUTE
              and self._anomaly_last_seen
              and timestamp - self._anomaly_last_seen > self._calm_threshold):
            self._resolution = Resolution.MINUTE
            print(f"  [t={timestamp:.0f}] Calm. Reverting to 1-min resolution")

        # Only store at current resolution
        res = self._resolution.value
        bucket = (int(timestamp) // res) * res
        if not self._store or self._store[-1]["bucket"] != bucket:
            self._store.append({"bucket": bucket, "values": [], "resolution": res})
        self._store[-1]["values"].append(value)

    def get_store(self) -> list:
        return [
            {**s, "mean": sum(s["values"]) / len(s["values"]), "count": len(s["values"])}
            for s in self._store
        ]


# Demo
base_detector = ZScoreAnomalyDetector(window=30, threshold=3.0)
adaptive = AdaptiveDownsampler(base_detector)
now = time.time()

for i in range(200):
    value = 100 + (i % 10) - 5
    if 80 <= i <= 90:
        value = 800  # Anomaly spike
    adaptive.ingest(now + i, value)

store = adaptive.get_store()
print(f"\nTotal buckets: {len(store)}")
resolutions = set(s["resolution"] for s in store)
print(f"Resolutions used: {sorted(resolutions)}")

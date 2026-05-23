# Time-Series Databases — Metrics and Monitoring at Scale

Optimized for time-indexed data.

---

## 📈 Time-Series Fundamentals

```
Metric: cpu_usage
Timestamp: 2024-05-22 10:00:00
Value: 75

Dimensions/Tags:
  host: server-1
  region: us-west
  environment: production
```

---

## 🗂️ Storage Optimization

### Bucketing (Sharding by Time)

```
Bucket 1: 2024-05-22 (1 day)
Bucket 2: 2024-05-23
...

New bucket daily (or hourly for high volume)
Old buckets become read-only (compress)
```

### Compression

```
Timestamps: Often regular intervals → store deltas
Values: Often similar → delta-of-delta encoding
Result: 1000x compression vs. raw storage
```

---

## 📊 Common Queries

```
-- Recent metrics
SELECT * FROM cpu_usage
WHERE time > now() - interval '1 hour';

-- Aggregation by time window
SELECT 
  time_bucket('1 minute', time) as minute,
  host,
  AVG(value) as avg_cpu
FROM cpu_usage
WHERE time > now() - interval '1 day'
GROUP BY minute, host;
```

---

## 🗑️ Data Retention

```
Retention policy:
- 7 days: Raw data (1-minute intervals)
- 1 year: Aggregated (1-hour intervals)
- Forever: Archived (1-day aggregates)

Downsampling: Compress old data
```

---

## 🏆 Popular Systems

**Prometheus:** Metrics, time-based
**InfluxDB:** Time-series specialized
**TimescaleDB:** PostgreSQL extension
**VictoriaMetrics:** Prometheus-compatible, efficient

---

## ❓ Interview Q&A

**Q: Design monitoring for 1000 servers**
A: Time-series DB (Prometheus). Scrape metrics every 15s. Store raw for 7 days. Aggregate hourly for long-term.

**Q: How to handle 1M metrics per second?**
A: Sharding by metric name/host. Distributed time-series DB. Downsampling for retention.

---

**Last updated:** 2026-05-22

# Time-Series Optimization Deep Dive

Optimize databases for fast ingestion and querying of massive time-series datasets.

---

## ⚖️ Time-Series Optimization Trade-offs

| Strategy | Ingestion | Query | Storage | Complexity |
|----------|-----------|-------|---------|-----------|
| **Raw** | Fast | Slow | High | Low |
| **Downsampling** | Fast | Fast | Low | Medium |
| **Aggregation** | Slow | Fast | Low | High |
| **Compression** | Medium | Medium | Very Low | High |

---

## 🏗️ Optimization Patterns

### Pattern 1: Tiered Storage

```
Hot (recent):     Last 7 days → SSD, in memory
Warm (1-30 days): → Disk
Cold (> 30 days): → Archive (S3, Glacier)

Benefits:
  - Recent queries fast (in-memory)
  - Old data accessible but slow
  - Cost optimized
```

### Pattern 2: Downsampling

```
Raw data: 1 point per second
  1M points/day × 365 = 365M points/year

Downsampled:
  1 minute:  1440 points/day = 525K/year (1000x less)
  1 hour:    24 points/day = 8.7K/year
  1 day:     1 point/day = 365/year

Keep all raw for 7 days, then downsample
```

### Pattern 3: Compression

```
Gorilla compression (Facebook):
  - Delta-of-delta compression
  - Time: 1.37 bytes/sample (vs. 8 raw)
  - Space: 94% reduction
  
Delta-of-delta:
  Raw:      [1000, 1010, 1020, 1015]
  Delta:    [10, 10, -5]
  DoD:      [0, -15]
  Encoded:  (bits vary by value)
```

---

## ❓ Interview Q&A

**Q1: Store 1B metrics/day, 365 days = 365B points**

A:
- Storage calculation:
  - Raw: 8 bytes × 365B = 2.9 PB (impossible)
  - Compressed: 1.37 bytes × 365B = 500 TB (feasible)
  - Downsampled + compressed: < 50 TB (practical)

**Q2: Query "sum of errors last 6 months" - too slow?**

A:
- Problem: Scan 180 days × 86400 samples = 15B samples
- Solution: Pre-aggregated tables
  - Daily aggregate: 180 days × 1 = 180 rows (instant)
  - Or: Materialized views

---

**Last updated:** 2026-05-22

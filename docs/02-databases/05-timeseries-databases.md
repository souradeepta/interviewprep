# Time-Series Databases — Metrics and Monitoring at Scale

**Level:** L4-L5
**Time to read:** ~20 min

Optimized for time-indexed data with fast aggregations and retention policies.

---

## 📈 Time-Series Fundamentals

```
Metric: cpu_usage
Timestamp: 2024-05-22 10:00:00
Value: 75

Dimensions/Tags (labels):
  host: server-1
  region: us-west
  environment: production

Cardinality: Unique combinations of tags
  Example: 1000 hosts × 5 regions = 5000 cardinality
```

---

## ⚖️ Time-Series vs. Traditional Database

```
Feature              | Time-Series     | PostgreSQL
─────────────────────|─────────────────|──────────────
Ingestion speed      | 1M metrics/sec  | 100K rows/sec
Compression          | 1000x           | 10x
Aggregation (avg)    | Fast (by time)  | O(n log n)
Point query          | Fast            | O(log n)
Time range query     | O(log n)        | O(log n)
Update              | Append-only     | Read-Modify-Write
Storage efficiency   | 1GB/day (1M/sec)| 100GB/day
Retention           | Days to months  | Permanent
Transaction         | Single metric   | Multi-row

When Time-Series DB:
├─ High cardinality (millions of unique metrics)
├─ Append-only data (metrics never update)
├─ Massive ingestion rates
├─ Time-based aggregations
├─ Retention policies (old data pruned)
└─ Real-time dashboards

When PostgreSQL:
├─ Transactional updates
├─ Complex relationships
├─ Small cardinality
├─ Rich queries (JOINs, complex WHERE)
└─ Long-term data retention
```

---

## 🏗️ Storage Optimization Techniques

### Bucketing (Time-Based Sharding)

```
Time Buckets (Tables/Partitions):
├─ 2024-05-22 (1 day) → active bucket (new inserts)
├─ 2024-05-21 → sealed (read-only)
├─ 2024-05-20 → sealed (can compress)
└─ 2024-05-01 → archived (low query frequency)

Benefits:
├─ New inserts only to active bucket
├─ Old buckets optimized for compression
├─ Easy TTL (drop old buckets)
├─ Parallelism (query multiple buckets)

Query: SELECT * WHERE time > '2024-05-20'
└─ Scans: 3 buckets (2024-05-22, 2024-05-21, 2024-05-20)
```

### Compression Techniques

```
Timestamp Compression (Delta):
Original:  [1000, 1001, 1002, 1003, 1004]
Delta:     [1000, 1, 1, 1, 1]  ← 80% reduction!

Value Compression (Delta-of-Delta):
Values:    [98.5, 98.6, 98.7, 98.8]
Deltas:    [0.1, 0.1, 0.1]
Deltas²:   [0, 0]  ← Highly compressible!

Tag Compression (Dictionary):
Tags:      ["us-west", "us-east", "us-west", "us-west"]
Dict:      {0: "us-west", 1: "us-east"}
Encoded:   [0, 1, 0, 0]  ← 4 bytes vs. 25 bytes

Total: 1000x compression possible
```

### Time Bucketing Strategy

```
High Cardinality Scenario (1M metrics/sec):

Bucket Duration: 1 hour (optimal balance)
├─ Too short: Many buckets, overhead
├─ Too long: Bucket fills up, slow queries
├─ 1 hour: ~3.6B points per bucket (manageable)

Sharding by Tag:
├─ Shard 0: region="us-west"
├─ Shard 1: region="us-east"
├─ Shard 2: region="eu"
├─ Each shard handles 333K metrics/sec
```

---

## 📊 Common Query Patterns

```sql
-- Recent metrics (hot data)
SELECT * FROM cpu_usage
WHERE time > now() - interval '1 hour'
AND host = 'server-1';
Time: 10ms (recent bucket in cache)

-- Aggregation by time window
SELECT 
  time_bucket('1 minute', time) as minute,
  host,
  AVG(value) as avg_cpu,
  MAX(value) as peak_cpu,
  MIN(value) as min_cpu
FROM cpu_usage
WHERE time > now() - interval '1 day'
AND host LIKE 'server-%'
GROUP BY minute, host
ORDER BY minute DESC;
Time: 100ms (pre-aggregated if available)

-- Year-over-year comparison
SELECT 
  time_bucket('1 day', time) as day,
  AVG(value) as avg_cpu
FROM cpu_usage
WHERE time >= '2023-05-22' AND time < '2023-05-23'
UNION ALL
SELECT 
  time_bucket('1 day', time) + interval '1 year',
  AVG(value)
FROM cpu_usage
WHERE time >= '2024-05-22' AND time < '2024-05-23';
```

---

## 🗑️ Data Retention & Downsampling

### Retention Strategy

```
Tiered Storage:

Raw Data (Last 7 days):
├─ Resolution: 1-second intervals
├─ Storage: 100GB
├─ Retention: Automatic delete after 7 days
├─ Query latency: <10ms
└─ Cost: High (SSD)

Hourly Aggregate (Last 1 year):
├─ Resolution: 1-hour aggregates
├─ Storage: 1GB (100x compression)
├─ Retention: Auto-computed from raw
├─ Query latency: <100ms
└─ Cost: Medium (SSD)

Daily Archive (Forever):
├─ Resolution: 1-day aggregates
├─ Storage: 100MB
├─ Retention: Permanent
├─ Query latency: 1-5s
└─ Cost: Low (cold storage)
```

### Downsampling Pattern

```
Raw metrics → Hourly aggregates → Daily archives

Downsampling Job (runs hourly):
├─ Input: Last hour of raw data
├─ Compute: AVG, MAX, MIN, COUNT
├─ Store: Hourly aggregates table
├─ Delete: Raw data older than 7 days
└─ Repeat: Every hour

Cost benefit:
├─ Raw storage: 100GB / day
├─ Hourly storage: 1GB / day (saved: 99%)
├─ Total 1-year cost: 1GB * 365 = 365GB vs. 36TB!
```

---

## 🔄 Cardinality Management

```
High Cardinality Problem:

Metric: request_latency
Tags: {user_id, endpoint, status_code}

Example:
├─ user_id: 10M users
├─ endpoint: 100 endpoints
├─ status_code: 5 values
├─ Cardinality: 10M × 100 × 5 = 5 billion!

Issues:
├─ Memory explosion (index can't fit)
├─ Performance degradation
├─ Slow queries on high cardinality

Solutions:
1. Don't tag on user_id (aggregate, lose detail)
2. Use sampling (1% of requests)
3. Bounded tags (only top 1000 users)
4. Separate systems (user metrics vs. system metrics)
5. Reduce tag combinations (don't combine all tags)

Best Practice:
├─ Keep cardinality < 10K per metric
├─ Monitor cardinality explosion
├─ Drop low-value tags
├─ Use sampling for high-cardinality dimensions
```

---

## 💡 Architecture Comparison

### Prometheus (Pull-based)
```
Targets (apps, exporters) → Prometheus ← Scraper
                           (stores locally)
                                ↓
                            Dashboard

Pros:
├─ Simple push: Apps just expose /metrics
├─ Built-in scraper
├─ No agent required
└─ Good for infrastructure

Cons:
├─ Pull mechanism (not real-time)
├─ Single-node (clustering complex)
├─ 15GB/year of storage (1M series)
```

### InfluxDB (Write-optimized)
```
Apps → InfluxDB (optimized for writes)
         ↓
      Distributed
         ↓
      Dashboard

Pros:
├─ Write-optimized (1M writes/sec)
├─ Distributed
├─ InfluxQL (familiar)
└─ Cloud version available

Cons:
├─ Proprietary (InfluxQL)
├─ Higher cost
└─ Query performance varies
```

### VictoriaMetrics (Prometheus-compatible)
```
Apps → VictoriaMetrics (Prometheus API)
         ↓
      Cluster
         ↓
      Dashboard

Pros:
├─ Prometheus-compatible
├─ 10x more efficient
├─ Distributed
├─ Open-source

Cons:
├─ Younger project
├─ Smaller ecosystem
```

---

## ❓ Comprehensive Interview Q&A

**Q: Design monitoring system for 1000 servers**

A:
```
Requirements:
- Monitor 1000 servers
- 10 metrics per server
- 15-second scrape interval
- Ingestion: (1000 × 10) / 15 = 667 metrics/sec
- 1-year retention

Architecture:

1. Agent Layer:
   ├─ Node Exporter on each server
   ├─ Collects: CPU, memory, disk, network
   └─ Exposes on :9100/metrics

2. Prometheus:
   ├─ Scrapes all targets every 15 seconds
   ├─ Stores locally in TSDB
   ├─ Retention: 15 days raw data
   └─ Local storage: ~50GB

3. Long-term Storage:
   ├─ Remote storage (S3/GCS)
   ├─ Downsampled: 1-hour aggregates
   ├─ Retention: 1 year
   └─ Storage: ~1GB

4. Analytics:
   ├─ Grafana for dashboards
   ├─ AlertManager for alerts
   └─ Query: Prometheus + remote storage

Configuration:
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'nodes'
    static_configs:
      - targets: ['server-1:9100', 'server-2:9100', ...]
```

Query Examples:
```promql
# CPU usage over 5 minutes
rate(cpu_seconds_total[5m])

# Memory available
(node_memory_MemTotal - node_memory_MemAvailable) / node_memory_MemTotal

# Disk usage by device
1 - (node_filesystem_avail / node_filesystem_size)
```
```

**Q: Handle 1M metrics per second, design retention**

A:
```
Scale: 1M metrics/sec = 86.4B metrics/day

Requirements:
├─ Raw retention: 7 days
├─ Aggregated: 1 year
├─ High availability (multi-region)

Architecture:

Ingestion:
├─ Load balancer → 3x InfluxDB nodes
├─ Each handles ~333K metrics/sec
├─ Sharding by tag (region, service)

Sharding Strategy:
Shard 0: hash(tags) % 3 = 0
Shard 1: hash(tags) % 3 = 1
Shard 2: hash(tags) % 3 = 2

Write Path:
App → Load Balancer → Hash(tags) → Shard 0/1/2

Retention:
├─ Raw (7 days): 604.8B points = 600GB
├─ 1-hour agg: 24.4B points = 24GB (99% reduction!)
├─ Downsampling job: Runs every hour
├─ Auto-delete: Raw data > 7 days

Storage Calculation:
├─ 3 nodes, 250GB each = 750GB total
├─ 1 week raw + 1 year hourly = manageable
├─ Replication: 3x (HA) = 2.25TB total

Queries:
```promql
# Average latency by service (recent)
avg by (service) (latency_bucket)

# Daily trend (hourly aggregates)
avg by (service) (rate(requests_total[1h]))
```

Query Performance:
├─ Hot data (last hour): <10ms
├─ Warm data (7 days): <100ms
├─ Cold data (1 year): <1s
```

**Q: Handle cardinality explosion (millions of unique metrics)**

A:
```
Problem: Cardinality explosion
├─ Metric: request_latency
├─ Tags: endpoint, user_id, region, status
├─ Users: 10M → Explosion!

Solutions:

1. Sampling (Best for this scenario):
   ├─ Sample 1% of requests
   ├─ Store with sample_rate=0.01
   ├─ Multiply results by 100 for totals
   ├─ Cardinality: 10K (manageable)
   └─ Storage: 1% of original

2. Pre-aggregation:
   ├─ Aggregate by endpoint (drop user_id)
   ├─ Aggregate by region (drop user_id)
   ├─ Keep separate "top users" metric
   └─ Cardinality: manageable

3. Bounded cardinality:
   ├─ Only track top 1000 users
   ├─ Drop tail into "other"
   ├─ Cardinality: Bounded
   └─ Storage: Known limit

4. Separate systems:
   ├─ System metrics → TSDB
   ├─ User events → Analytics DB
   ├─ Query: Join results in application
   └─ Storage: Optimized per use case

Recommended Approach:
├─ Use sampling (1% of requests)
├─ Pre-aggregate by endpoint
├─ Monitor cardinality continuously
├─ Alert if > 10K combinations
```

---

## 💡 Interview Tips

**What interviewer is really asking:**
- "Design monitoring for X servers" → Do you know scrape intervals, retention, downsampling?
- "Handle high cardinality" → Do you understand tag explosion, sampling solutions?
- "1M metrics/sec" → Do you know sharding, clustering, load distribution?
- "Retention strategy" → Do you know tiered storage, downsampling, TTL?

**How to answer:**
1. **Clarify:** Metrics/sec, metric types, retention needs
2. **Ingestion:** Scrape interval, push vs. pull, agents
3. **Storage:** Raw + aggregated, compression, sharding
4. **Retention:** Time-based TTL, downsampling levels
5. **Query:** Recent (fast), historical (aggregated)
6. **Optimize:** Cardinality management, sampling

---

**Last updated:** 2026-05-22

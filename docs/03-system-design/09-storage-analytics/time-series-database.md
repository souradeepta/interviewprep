# Time-Series Database

**Level:** L3-L5+
**Time to read:** ~30 min

## Problem Statement

Monitoring, IoT, financial markets, and infrastructure observability generate data that is fundamentally different from transactional records: it is append-only, arrives in time order, is almost always queried by time range, and accumulates at rates that would overwhelm a general-purpose relational database within days.

A time-series database (TSDB) is optimized for this pattern: fast writes at 1M+ samples/sec, efficient storage using temporal compression, and fast range queries with aggregations over millions of data points. The core challenge is balancing write throughput, query performance, storage cost, and data retention across hot (recent, frequently queried) and cold (historical, rarely queried) tiers.

## Functional Requirements

- Ingest time-series data as (metric_name, tags, timestamp, value) tuples
- Support high-cardinality tag dimensions (e.g., host, region, service, endpoint)
- Query by metric name + tag filters over a time range with aggregations (sum, avg, max, percentile)
- Apply retention policies: delete or downsample data older than N days
- Support out-of-order writes (late-arriving data, backfill scenarios)
- Dashboard queries: return results within 2 seconds for 30-day range over 1K metrics

## Non-Functional Requirements

- **Scale:** 1M samples/sec ingest; 10K concurrent query requests/sec
- **Latency:** P99 write < 10ms; P99 query (30-day range) < 2s
- **Availability:** 99.9% (monitoring systems are critical but tolerate brief lag)
- **Consistency:** Eventual — slight ingest delay acceptable; queries may miss last 5-10s of data

---

## Tier 1: L3-L4 Design (the basic interview answer)

### Back-of-Envelope

```
Ingest: 1M samples/sec
  - Sample size: metric_name (50B) + tags (100B) + timestamp (8B) + value (8B) = ~166B raw
  - Before compression: 1M * 166B = 166 MB/sec
  - After Gorilla compression (typical 12:1 ratio): ~14 MB/sec on disk
  - Daily storage (compressed): 14MB/s * 86400s = ~1.2 TB/day
  - Annual storage: 438 TB/year (hot tier: 30 days = 36 TB; cold: rest on cheaper storage)

Queries: 10K QPS
  - Avg query scans 1 metric * 30 days * 1-min resolution = 43,200 data points
  - At 8 bytes/point: 43,200 * 8 = 346KB per query scan (in-memory after caching)
  - With 10K QPS and 50ms avg scan time: 10K * 50ms = 500 concurrent queries
  - RAM for hot data (30 days): 36 TB (too large for pure in-memory; use columnar + file cache)

Cardinality:
  - 1M metrics, each with avg 10 tag combinations = 10M unique time series
  - Index memory: 10M series * 100B per index entry = 1 GB (fits in RAM on each query node)
```

### Architecture Diagram

```
Producers (agents, apps, IoT)
  |
  | Push metrics (Prometheus remote_write, StatsD, OpenTelemetry)
  v
+------------------+
| Ingest Gateway   |  <-- Validates, batches, routes by metric shard
| (stateless)      |
+------------------+
  |
  | (Kafka: 100 partitions, sharded by metric_name hash)
  v
+------------------+
| Write Nodes      |  <-- Append to WAL, write to in-memory buffer
| (10 nodes)       |      Flush to columnar files every 2 hours
+------------------+
  |         |
  | files   | compact
  v         v
+------------------+   +------------------+
| Hot Tier         |   | Cold Tier        |
| (SSD, 30 days)   |   | (S3/GCS, 1 year) |
| Parquet or       |   | Parquet files    |
| InfluxDB TSM     |   | by day/metric    |
+------------------+   +------------------+

Query Path:
Client
  |
  v
+------------------+
| Query Router     |  <-- Parses query, identifies shards, fans out
+------------------+
  |          |
  v          v
Write Node  Hot Tier   [merge results in query router]
(last 2hr)  (30d)
```

### Data Model

```
Time-series data model: (metric, tags, timestamp, value)

Example data points:
  cpu.usage | {host=web-01, region=us-east, env=prod} | 1716912345 | 73.5
  http.rps  | {service=api, endpoint=/checkout}        | 1716912346 | 12000
  mem.used  | {host=db-01, region=eu-west}             | 1716912345 | 85.2

Internal representation (columnar, per time series):
  Series key: hash(metric_name + sorted(tags)) → uint64
  Data file structure:
    - Timestamps column: delta-encoded int64[] (Gorilla TSC)
    - Values column:     XOR-compressed float64[] (Gorilla/Delta-of-Delta)
    - Block size: 2-hour chunks (efficient for both writes and range queries)

SQL schema (for TimescaleDB approach):
CREATE TABLE metrics (
    time        TIMESTAMPTZ NOT NULL,
    metric_name VARCHAR(200) NOT NULL,
    host        VARCHAR(100),
    region      VARCHAR(50),
    service     VARCHAR(100),
    value       DOUBLE PRECISION NOT NULL
);
SELECT create_hypertable('metrics', 'time', chunk_time_interval => INTERVAL '1 day');
CREATE INDEX ON metrics (metric_name, time DESC);
```

### API Design

```
# Write API (OpenTelemetry / Prometheus compatible)

POST /api/v1/write
  Content-Type: application/x-protobuf
  Body: TimeSeries[] (Prometheus remote_write format)
  Response: 204 No Content

POST /api/v1/write/json
  Body: [{ metric: "cpu.usage", tags: { host: "web-01" }, timestamp: 1716912345, value: 73.5 }]
  Response: { ingested: 1000, failed: 0 }

# Query API (PromQL or SQL)

GET /api/v1/query_range
  Params: query=cpu_usage{host="web-01"}, start, end, step
  Response: { status: "success", data: { result: [...] } }

POST /api/v1/sql
  Body: { sql: "SELECT time_bucket('5m', time) AS t, avg(value) FROM metrics WHERE ... GROUP BY t" }
  Response: { columns: [...], rows: [...], query_ms: 245 }

GET /api/v1/series?match=cpu.usage{region="us-east"}&start=...&end=...
  Response: [{ metric: "cpu.usage", tags: { host: "web-01", region: "us-east" } }, ...]

DELETE /api/v1/series
  Params: match=old_metric{host="decommissioned-server"}
  Response: { deleted_series: 12 }
```

### Basic Scaling

- Shard write nodes by consistent hashing on metric_name — same metric always goes to the same write node, enabling in-memory aggregation before flush
- Use WAL (Write-Ahead Log) on each write node: survive crashes without losing recent data
- Keep last 2 hours in-memory for sub-millisecond query latency on recent data; flush to SSD-backed columnar files
- Apply retention policy by deleting entire time-partitioned files (no row-level deletes needed)

---

## Tier 2: L5+ Design (the staff interview answer)

### Capacity Planning (Real Numbers)

```
Write nodes: 10 x i3.2xlarge (NVMe SSD, 1.9 TB, 8 vCPU, 61 GB RAM)
  - Each node handles: 1M / 10 = 100K samples/sec
  - In-memory WAL: 100K * 166B * 2hr = ~120 MB (fits easily in RAM)
  - Flush to SSD: every 2 hours, write 120MB * 12 shards = 1.44 GB per node per 2hr
  - SSD writes: 0.2 MB/sec per node (trivial; NVMe can do 2GB/sec)
  - Hot tier (30 days) per node: 1.2 TB / 10 nodes = 120 GB compressed (well within 1.9 TB NVMe)

Query nodes: 5 x r5.4xlarge (16 vCPU, 128 GB RAM)
  - RAM cache: 128 GB per node; LRU cache for hot time series blocks
  - 10K QPS / 5 nodes = 2K QPS per node; at 50ms avg query = 100 concurrent queries per node
  - CPU: 2K * 50ms * 16 cores = 1600 core-ms = 1.6 CPU-seconds/sec → 10% CPU utilization

Cold tier (S3, data older than 30 days):
  - Storage: 1.2 TB/day * 335 days (beyond 30-day hot) = 402 TB
  - S3 cost: $0.023/GB → 402 TB * $0.023 * 1000 = $9,246/month
  - Query speed (S3 Select on Parquet): scan 30GB of one metric's annual data in 5-10s
    Use columnar predicate pushdown: only read relevant columns and row groups

Kafka ingest buffer:
  - 1M samples/sec * 166B = 166MB/sec write rate
  - 100 Kafka partitions → 1.66MB/sec per partition (trivial)
  - Retention: 6 hours (for recovery from write node failures)
  - Storage: 166MB/sec * 21600s = 3.6 TB for 6-hour retention (MSK m5.xlarge, 3 brokers: $270/month)
```

### Failure Modes

```
Failure: Write node crashes before flushing in-memory buffer
  Impact: Loss of last 2 hours of data on that shard
  Mitigation:
    - WAL on local NVMe: every sample written to WAL before ACK to producer
    - WAL replay on restart: recover up to crash point with <1s overhead
    - Replication: replicate WAL to a standby write node (RF=2)
      Standby takes over within 10s of primary failure

Failure: Cardinality explosion (new tag added with high-cardinality value like trace_id)
  Impact: Index grows from 10M series to 10B series → OOM on write/query nodes
  Mitigation:
    - Hard limit: reject metrics with series count > 10M per metric name
    - Rate limit new series creation: max 1000 new series/sec globally
    - Alert on cardinality growth: page when a metric gains >10K new series/hour
    - Cardinality quarantine: new metrics held in a sandboxed shard; promoted after cardinality validation
    - Common mistake: using request_id, trace_id, or user_id as tag values

Failure: Out-of-order writes (late data from a crashed agent)
  Impact: Data arrives 10 minutes late; already-flushed file doesn't contain it
  Mitigation:
    - Accept out-of-order data up to configured tolerance window (e.g., 1 hour)
    - Write late data to a separate "late arrival" buffer; merge with existing block at next compaction
    - For data older than tolerance: reject with 422 and log for manual backfill
    - Compaction runs every 6 hours: merges blocks, sorts by timestamp, re-compresses

Failure: Hot tier SSD fails
  Impact: 30 days of data for 1/10 shards inaccessible
  Mitigation:
    - RAID-1 on NVMe (mirroring) or replicate write node data to second node
    - Cold tier S3 backup: copy hot tier files to S3 every 6 hours (last-resort recovery)
    - Recovery from replica: new write node joins shard group and syncs from replica — ETA 2-4 hours for 120 GB over 10 Gbps network
```

### Consistency Boundaries

```
Ingest lag: writes ACK after WAL commit; data queryable after flush (up to 2 hours for very recent data)
  - Option: make in-memory WAL queryable (Prometheus does this) → recent data queryable in <1s
    Cost: query nodes must also query write nodes (scatter-gather across 10 write nodes)

Gorilla compression (floating-point time series):
  - XOR encoding: stores XOR of consecutive float64 values; same value sequence → 1 bit
  - Delta-of-delta for timestamps: only encodes change in inter-sample interval
  - Effective compression: 12:1 for typical infrastructure metrics (many repeated values)
  - Decompression is lossless — no data is lost

Downsampling (lossy, for cold tier):
  - Raw data (1s resolution): keep for 30 days
  - 1-minute rollups: keep for 1 year (avg, min, max, p99)
  - 1-hour rollups: keep forever (for trend graphs)
  - Storage reduction: 1M samples/sec → 1M / 60 = 16.7K 1-min aggregates/sec → 1/60 storage
  - Trade-off: cannot reconstruct exact spike timing from 1-minute rollup;
    choose rollup resolution based on alerting requirements

Strong consistency for writes:
  - WAL guarantees: if producer receives ACK, data is durable to disk
  - If producer does NOT receive ACK (network timeout): safe to retry with same data
    (write nodes detect duplicate timestamps per series and deduplicate)
```

### Cost Model

```
Write nodes (10 x i3.2xlarge): 10 * $0.624/hr = $6.24/hr = $4,493/month
Query nodes (5 x r5.4xlarge): 5 * $1.008/hr = $5.04/hr = $3,629/month
Kafka (MSK 3-broker m5.xlarge): ~$270/month
Hot tier NVMe storage (included in i3.2xlarge instance cost)
Cold tier S3 (402 TB at $0.023/GB): $9,246/month
Networking (ingest ingress: free; query egress 10K QPS * 346KB = 3.46 GB/sec → $270/month)

Total: ~$18,000/month

Per metric per month (10M unique series):
  $18,000 / 10M = $0.0018/series/month = $0.18/100 series/month
  (Lower than commercial TSDBs: InfluxDB Cloud charges $0.002/series/month → competitive)
```

---

## Trade-off Comparison

| System         | Write Throughput    | Query Performance       | Cardinality Limit       | Cost (at 1M series)   | Best For                        |
|----------------|---------------------|-------------------------|-------------------------|-----------------------|---------------------------------|
| InfluxDB OSS   | 300K samples/sec    | Fast for simple queries | Medium (~10M series)    | Free (self-hosted)    | Small/medium monitoring stacks  |
| TimescaleDB    | 200K samples/sec    | Excellent (full SQL)    | High (Postgres scales)  | Low (Postgres cost)   | Teams already on PostgreSQL     |
| Prometheus     | 500K samples/sec    | Fast (PromQL)           | Low (local storage)     | Very low              | Single-cluster K8s monitoring   |
| ClickHouse     | 1M+ samples/sec     | Very fast (columnar)    | Very high (billions)    | Low-medium            | Analytics, logs, high-card TSDB |
| M3DB (Uber)    | 1M+ samples/sec     | Fast                    | Very high               | High (complex ops)    | Uber/large-scale infra TSDB     |
| VictoriaMetrics| 1M+ samples/sec     | Fast (MetricsQL)        | High                    | Low (efficient)       | Prometheus replacement at scale |

## Follow-up Questions (escalating difficulty, 7 minimum)

1. **(L3)** What is Gorilla compression and why does it achieve 12:1 compression on time-series data?
   → Gorilla stores only the delta between consecutive values. For timestamps: it stores delta-of-delta (change in the time gap between samples); for most regular metrics, this is 0 — compresses to 1 bit. For float values: it stores the XOR of consecutive values; if CPU usage changes from 73.5 to 73.6, the XOR has few significant bits and compresses to 5-6 bits. Most infrastructure metrics change slowly, so consecutive values XOR to small numbers — achieving 12:1 compression vs. raw float64.

2. **(L3)** What is a hypertable in TimescaleDB?
   → A hypertable is a PostgreSQL table that TimescaleDB automatically partitions by time. Each partition is called a "chunk" and covers a configurable time interval (e.g., 1 day). Queries with a time range predicate only scan relevant chunks, not the entire table. Chunk files can be compressed independently and moved to cheaper storage tiers. The user interacts with one logical table while TimescaleDB handles the physical partitioning transparently.

3. **(L4)** What is the cardinality explosion problem and how do you prevent it?
   → Cardinality is the number of unique time series, determined by the number of distinct tag value combinations. If you add a tag `user_id` to a metric with 10M users, that metric now has 10M unique series × existing tag combinations = potentially billions of series. Each unique series requires an index entry and in-memory state. Billions of series exhaust RAM on write and query nodes. Prevention: never use high-cardinality values (user_id, request_id, trace_id, IP address) as metric tags. These belong in logs or traces, not metrics. Set a hard cardinality limit per metric and reject metrics that exceed it.

4. **(L4)** How do you handle out-of-order writes in a time-series database?
   → Time-series databases expect data to arrive in time order. Out-of-order data (from clock drift, network delays, or crashed agents that replay) disrupts sorted block structure. Accept out-of-order data within a tolerance window (e.g., 1 hour): maintain a "late arrival" buffer per shard alongside the main write buffer. At compaction time (every 6 hours), merge late arrival data into the correct time blocks, re-sort, and re-compress. Reject data older than the tolerance window (e.g., 1 hour) to avoid unbounded memory usage. For backfill scenarios (loading historical data), use a dedicated backfill API that bypasses real-time write paths.

5. **(L5)** How would you design a downsampling pipeline for 1-year retention at 1M samples/sec?
   → Raw data (1-second resolution) kept for 30 days: ~36 TB compressed. After 30 days, a downsampling job runs: reads raw data, computes per-minute aggregates (min, max, avg, sum, count, p99 via T-Digest), writes aggregated series to cold tier. 1-minute aggregates kept for 1 year: 36 TB / 60 = 600 GB compressed. After 1 year: downsample to 1-hour aggregates, keep forever (10 GB for 10 years of hourly data). The downsampling job uses Spark or a dedicated rollup service that reads from hot-tier S3-backed files. Key: always store both raw and rollup for the same time period during the overlap window — queries prefer raw when available, fall back to rollup for older time ranges.

6. **(L5)** What is the Prometheus scrape model and when is it insufficient?
   → Prometheus uses a pull model: it scrapes targets (HTTP endpoints exposing metrics) every 15 seconds. This works well for homogeneous infrastructure (same K8s cluster) but fails when: (1) targets are behind NAT or firewalls (Prometheus can't reach them), (2) targets are ephemeral (Lambda, batch jobs that may not exist when scrape fires), (3) you need sub-15-second resolution for SLA alerting. For these cases, use push-based ingestion: agents push to a gateway (Prometheus Pushgateway, Victoria Metrics remote_write, OpenTelemetry Collector) which Prometheus then scrapes. At 1M samples/sec, replace Prometheus with VictoriaMetrics or Thanos for horizontal scaling.

7. **(L5+)** Design a multi-tenant time-series database where tenants cannot see each other's data, queries are isolated, and a noisy tenant cannot degrade others.
   → Tenant isolation at three layers: (1) Data isolation: shard by tenant_id as the outermost key in the series hash; each tenant's data lives on dedicated write node partitions. Cross-tenant queries are physically impossible — the data is on different nodes. (2) Query isolation: query router enforces tenant context from authenticated JWT; rejects queries without valid tenant_id. Rate limit each tenant to a configurable query budget (e.g., 100 QPS, 1000 concurrent series per query). Use separate query node pools for premium vs. standard tenants. (3) Ingest isolation: each tenant has a dedicated Kafka consumer group and write node shard. Noisy tenant's ingest backlog does not affect other tenants' write latency — Kafka partitions are independent. Billing: charge per series per month + per GB ingested + per GB scanned in queries.

## Anti-patterns / Things NOT to Say

- **"Use a relational database for time-series data"** — A MySQL table with (metric_name, timestamp, value) at 1M samples/sec would require 86.4B rows/day. Index maintenance on a B-tree of this scale causes write amplification exceeding 10x. Query performance without time-based partitioning degrades to full table scans. Use a TSDB purpose-built for time-ordered append workloads.
- **"Use user_id or request_id as a metric tag"** — High-cardinality tags create billions of unique time series, each requiring its own in-memory index entry. This is the cardinality explosion problem. user_id belongs in logs or distributed traces (Jaeger, Zipkin), not in metrics. Metrics should use fixed-cardinality tags (host, region, service, endpoint — things with <10K distinct values).
- **"Store all data at raw resolution forever"** — Raw 1-second data at 1M samples/sec accumulates 438 TB/year. Querying a 1-year range at 1-second resolution would scan 31.5 billion data points per metric — no query system returns this in 2 seconds. Use downsampling: keep raw for 30 days, 1-minute rollups for 1 year, 1-hour rollups forever. Design your alerting SLAs to match the available resolution.
- **"Prometheus scales to any size with just more replicas"** — Prometheus uses local storage with no native clustering. Each replica scrapes all targets independently (wasted work) and stores data locally (no sharing). For scale, use Thanos (object store for global view + deduplication) or VictoriaMetrics (horizontal write clustering). Running 50 Prometheus replicas means 50x scrape load on targets and 50 disconnected data silos.

## Python Implementation (sketch)

```python
import struct
import time
from collections import defaultdict
from typing import Dict, List, Tuple, Optional

# Gorilla-inspired timestamp and value compression (simplified)

class GorillaBlock:
    """Compress a 2-hour block of (timestamp, value) pairs using XOR encoding."""

    def __init__(self):
        self._timestamps: List[int] = []
        self._values: List[float] = []
        self._count = 0

    def append(self, ts: int, value: float):
        self._timestamps.append(ts)
        self._values.append(value)
        self._count += 1

    def compress(self) -> bytes:
        if not self._timestamps:
            return b""
        ts_deltas = self._delta_encode(self._timestamps)
        val_xors  = self._xor_encode_floats(self._values)
        # Simplified: just pack them (real Gorilla uses bit-level encoding)
        header = struct.pack(">IQ", self._count, self._timestamps[0])
        ts_bytes  = struct.pack(f">{len(ts_deltas)}i", *ts_deltas)
        val_bytes = struct.pack(f">{len(val_xors)}Q", *val_xors)
        return header + ts_bytes + val_bytes

    def _delta_encode(self, ts: List[int]) -> List[int]:
        if len(ts) < 2:
            return []
        deltas = [ts[i] - ts[i-1] for i in range(1, len(ts))]
        # Delta-of-delta: most are 0 for regular metrics
        dod = [deltas[0]] + [deltas[i] - deltas[i-1] for i in range(1, len(deltas))]
        return dod

    def _xor_encode_floats(self, vals: List[float]) -> List[int]:
        result = []
        prev_bits = 0
        for v in vals:
            bits = struct.unpack(">Q", struct.pack(">d", v))[0]
            result.append(bits ^ prev_bits)
            prev_bits = bits
        return result

class InMemoryWriteBuffer:
    """Accumulate samples in-memory before flushing to columnar storage."""

    def __init__(self, flush_interval_sec: int = 7200):
        # series_key -> GorillaBlock
        self._buffers: Dict[str, GorillaBlock] = defaultdict(GorillaBlock)
        self._started_at = time.monotonic()
        self._flush_interval = flush_interval_sec

    def write(self, metric: str, tags: Dict[str, str], ts: int, value: float):
        series_key = self._series_key(metric, tags)
        self._buffers[series_key].append(ts, value)

    def should_flush(self) -> bool:
        return (time.monotonic() - self._started_at) >= self._flush_interval

    def flush(self) -> Dict[str, bytes]:
        """Return compressed blocks per series key, then reset buffer."""
        compressed = {key: block.compress() for key, block in self._buffers.items()}
        self._buffers.clear()
        self._started_at = time.monotonic()
        return compressed

    def query_recent(self, metric: str, tags: Dict[str, str]) -> List[Tuple[int, float]]:
        """Return raw (timestamp, value) pairs from in-memory buffer (for recent data queries)."""
        series_key = self._series_key(metric, tags)
        block = self._buffers.get(series_key)
        if not block:
            return []
        return list(zip(block._timestamps, block._values))

    @staticmethod
    def _series_key(metric: str, tags: Dict[str, str]) -> str:
        sorted_tags = ",".join(f"{k}={v}" for k, v in sorted(tags.items()))
        return f"{metric}{{{sorted_tags}}}"
```

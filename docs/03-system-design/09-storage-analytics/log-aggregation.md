# Log Aggregation System

**Level:** L3-L5+
**Time to read:** ~30 min

## Problem Statement

A large microservices platform generates 100TB of logs per day across thousands of service instances. Engineers need to search logs for debugging (find all errors for a specific user in the last hour), operations teams need dashboards (error rate over time by service), and security teams need audit log retention (immutable 7-year archive for compliance).

The challenge is building a pipeline that ingests logs reliably at high throughput, makes them searchable with low latency, enforces cost-effective retention policies, and prevents any single noisy service from degrading the entire system.

## Functional Requirements

- Collect structured log lines from application agents (Fluentd, Filebeat, Vector)
- Transport logs through a durable buffer (Kafka) before storage
- Store logs in a queryable store (Elasticsearch or ClickHouse) for hot search
- Support full-text search, field filters, and time-range queries
- Apply retention policies: hot (7 days), warm (30 days), cold (1 year), archive (7 years)
- Emit real-time alerts when error rate exceeds threshold

## Non-Functional Requirements

- **Scale:** 100TB logs/day = 1.16 GB/sec ingest; 1B log lines/day
- **Latency:** Logs searchable within 30 seconds of emission; query P99 < 5s
- **Availability:** 99.9% for query; ingestion can tolerate brief loss (at-least-once delivery)
- **Consistency:** Eventual — slight delay between emission and searchability acceptable

---

## Tier 1: L3-L4 Design (the basic interview answer)

### Back-of-Envelope

```
Volume: 100 TB/day raw = 1.16 GB/sec
Compression ratio (text logs, gzip): ~10:1
Compressed: ~10 TB/day = 116 MB/sec

Log line size: avg 1KB uncompressed (structured JSON)
Lines/day: 100 TB / 1 KB = 100B log lines/day = ~1.16M lines/sec

Kafka:
  - 1.16 GB/sec * RF=3 = 3.5 GB/sec total writes across brokers
  - 100 partitions → 11.6 MB/sec per partition
  - Retention 24h: 100 TB raw = 10 TB compressed stored in Kafka

Elasticsearch:
  - Index storage: 10 TB/day compressed → 7-day hot tier = 70 TB
  - Per shard: 50 GB max → 70,000 GB / 50 GB = 1,400 shards for 7 days
  - Indexing throughput: 1.16M lines/sec across 50 data nodes = 23K lines/sec per node
  - RAM per node: Elasticsearch recommends 50% heap: r5.4xlarge (128GB RAM, 64GB heap)

Storage tiers:
  - Hot (SSD, 7 days): 70 TB
  - Warm (HDD, 30 days): 300 TB (10 TB/day * 30 = 300 TB)
  - Cold (S3, 1 year): 3.6 PB
  - Archive (S3 Glacier, 7 years): 25.2 PB
```

### Architecture Diagram

```
Application Instances (1000s of pods)
  |
  | stdout / file
  v
+-----------+
| Log Agent |  <-- Fluentd or Filebeat: tails log files, parses JSON, adds metadata
| (per pod) |      fields: service, host, pod, environment, log_level, trace_id
+-----------+
  |
  | Forward (compressed batches)
  v
+------------------+
| Kafka            |  <-- 100 partitions; log_level-based routing
| log.error        |      log.error: 10 partitions (critical, no sampling)
| log.info         |      log.info:  90 partitions (100M lines/hr → sampled at 1%)
| log.debug        |      log.debug: separate topic, 24h retention only
+------------------+
  |              |
  v              v
+----------+  +----------+
| Hot Path |  | Cold Path|
| Indexer  |  | Archiver |
| (ES/     |  | (S3)     |
|  CH)     |  |          |
+----------+  +----------+
  |              |
  v              v
+----------+  +----------+
| Elastic- |  | S3 Parquet|
| search   |  | (cold/   |
| (7 days) |  |  archive)|
+----------+  +----------+
  |
  v
+----------+
| Kibana / |  <-- Search UI, dashboards, alert rules
| Grafana  |
+----------+
```

### Data Model

```json
// Structured log line (JSON, required fields):
{
  "@timestamp": "2026-05-28T10:23:45.123Z",
  "log_level":  "ERROR",
  "service":    "checkout-api",
  "host":       "web-pod-0042",
  "trace_id":   "abc123def456",
  "span_id":    "789xyz",
  "message":    "Payment processor timeout after 5000ms",
  "user_id":    12345678,
  "request_id": "req-uuid-here",
  "duration_ms": 5001,
  "http_status": 503,
  "error_class": "TimeoutException",
  "stack_trace": "...",
  "env":         "production",
  "region":      "us-east-1"
}
```

```
Elasticsearch index template:
  Index pattern: logs-YYYY.MM.DD (one index per day)
  Primary shards: 10 per index
  Replica shards: 1 (RF=2 for hot tier)
  ILM policy:
    Phase hot  (0-7d):   SSD nodes, 1 replica,  max shard 50GB
    Phase warm (7-30d):  HDD nodes, 1 replica,  force-merge to 1 segment/shard
    Phase cold (30d-1y): frozen tier / S3-backed, 0 replicas (read-only, slower query)
    Phase delete (1y+):  delete from ES; rely on S3 Parquet for archive queries
```

### API Design

```
# Kibana / Elasticsearch Query API

GET /logs/_search
  Body: {
    "query": {
      "bool": {
        "filter": [
          { "term": { "log_level": "ERROR" } },
          { "term": { "service": "checkout-api" } },
          { "range": { "@timestamp": { "gte": "now-1h" } } }
        ]
      }
    },
    "sort": [{ "@timestamp": { "order": "desc" } }],
    "size": 100
  }

GET /logs/_search  (search by trace_id — join-by-field pattern)
  Body: { "query": { "term": { "trace_id": "abc123def456" } } }

POST /api/v1/logs/stream  (real-time tail via SSE)
  Body: { filter: { service: "checkout-api", log_level: "ERROR" } }
  Response: text/event-stream

GET /api/v1/logs/aggregate
  Params: metric=count, field=log_level, service=checkout-api, window=5m
  Response: { buckets: [{ time: "...", ERROR: 42, WARN: 120, INFO: 5000 }] }
```

### Basic Scaling

- Route by log_level at Kafka topic level: high-priority ERROR logs get dedicated partitions and dedicated consumers, preventing INFO flood from delaying error visibility
- Use ILM (Index Lifecycle Management) to automatically move indices through hot → warm → cold → delete phases
- Force-merge warm indices to 1 segment per shard: reduces Lucene file handles and improves query performance for historical queries
- Apply 1% sampling on INFO logs and 0.1% on DEBUG before Kafka (in the agent): reduces volume 50x while preserving full ERROR fidelity

---

## Tier 2: L5+ Design (the staff interview answer)

### Capacity Planning (Real Numbers)

```
Kafka cluster:
  - 10 x kafka.m5.2xlarge (MSK): 8 vCPU, 32 GB RAM, 2 TB EBS gp3 each
  - Total storage: 20 TB (covers 2-day retention at 10 TB compressed/day)
  - Network: 1.16 GB/sec * 3 (replication) = 3.5 GB/sec → 28 Gbps across 10 brokers → 2.8 Gbps each (within 10 Gbps NIC)
  - Cost: 10 * $0.384/hr = $3.84/hr = $2,765/month

Elasticsearch hot tier: 50 x r5.2xlarge (8 vCPU, 64 GB RAM, 2 TB NVMe)
  - Heap: 32 GB per node
  - Shard capacity: 2 TB * 0.5 (don't fill disk) = 1 TB NVMe → 20 shards of 50GB
  - Total capacity: 50 * 1TB = 50 TB → 7-day hot tier (70 TB needed → 70 nodes, 50 TB shown is estimate)
  - Actually: 70 TB / 50 GB per shard = 1400 shards / 20 shards per node = 70 data nodes
  - Cost: 70 * r5.2xlarge $0.504/hr = $35.28/hr = $25,400/month for hot tier

Elasticsearch warm tier: 30 x i3.8xlarge (32 vCPU, 244 GB RAM, 25 TB HDD)
  - Warm tier: 30 days * 10 TB/day = 300 TB; 30 nodes * 25 TB = 750 TB capacity (plenty of headroom)
  - Cost: 30 * $2.498/hr = $74.94/hr = $53,960/month

S3 cold tier (1 year, Parquet):
  - 3.6 PB * $0.023/GB = $82,800/month

S3 Glacier archive (7 years):
  - 25.2 PB * $0.004/GB = $100,800/month

Log agent fleet:
  - Fluentd on every pod: 5MB RAM + 1% CPU per node (negligible)
  - Filebeat: 10 MB RAM, 5% CPU; preferred for high-throughput nodes

Total infrastructure: ~$280K/month at 100 TB/day scale
  Per GB ingested: $280K / (100 * 1024 GB/day * 30 days) ≈ $0.091/GB/month
```

### Failure Modes

```
Failure: Log agent cannot reach Kafka (network partition, Kafka broker restart)
  Impact: Log lines accumulate in agent buffer; if buffer fills, logs are dropped
  Mitigation:
    - Increase agent disk buffer: 1 GB on-disk buffer in Fluentd/Filebeat
    - At 1.16 MB/sec per agent, 1 GB = 14 minutes of buffering before loss
    - Enable Kafka producer retries with exponential backoff (max 30 minutes)
    - Alert when agent buffer > 50% full

Failure: Elasticsearch indexing lag spikes (GC pause, shard rebalancing)
  Impact: Recent logs not searchable; alerts fire with stale data
  Mitigation:
    - Kafka provides buffer: Elasticsearch consumer can lag and catch up
    - Consumer group offset monitoring: alert if lag > 5 minutes
    - Index consumers scale independently of Kafka: add indexing workers to clear lag
    - Two separate consumer groups: real-time alerting (consumes log.error topic first)
      and bulk indexing (all topics, higher lag tolerance)

Failure: Hot Elasticsearch node disk fills up (unexpected log volume spike)
  Impact: Index writes rejected; 429 Too Many Requests from ES
  Mitigation:
    - ILM watermark: trigger rollover at 40 GB (not 50 GB) to avoid disk-full
    - Auto-scale hot tier: if disk > 70%, add nodes and rebalance shards
    - Emergency sampling: circuit breaker in log router samples INFO logs at 0.1% if
      Elasticsearch write rejection rate > 1%

Failure: A single service logs at 100x normal rate (log storm)
  Impact: Drowns other services' logs in Elasticsearch; fills hot tier prematurely
  Mitigation:
    - Per-service rate limiting at the Kafka producer level (Fluentd plugin)
      Default: 10 MB/sec per service; burst: 50 MB/sec for 60 seconds
    - Per-service quota enforcement in log router: excess lines sampled at 1%
    - Alert: "service X logging at 100x baseline" → investigate runaway logging

Failure: Log agent drops logs (at-least-once vs. exactly-once)
  Impact: Missing error logs → missed alerts; compliance gaps
  Mitigation:
    - At-least-once: prefer duplicate log lines over missing lines (deduplicate by request_id in ES)
    - Use Kafka's acks=all for log.error topic (ERROR logs must not be lost)
    - Accept loss for DEBUG/INFO at high load: sample these down rather than guarantee delivery
    - Compliance logs (audit trail): separate pipeline with exactly-once Kafka semantics and S3 archival
```

### Consistency Boundaries

```
Ingest → searchability lag: target P95 < 30 seconds
  - Agent batch interval: 5 seconds
  - Kafka transit: <1 second
  - ES indexing: up to 30 seconds per flush interval
  - Acceptable: logs appear in search within 30s of emission

Sampling strategy by severity:
  - ERROR/CRITICAL: 100% (no sampling ever)
  - WARN:           100% (no sampling — WARN often precedes ERROR)
  - INFO:           1% (vast majority are routine health checks and request logs)
  - DEBUG:          0.1% (almost never needed in production search)
  - Result: INFO sampling reduces log volume from 100 TB/day to ~2 TB/day
    without losing any error-level signal

Log retention by severity:
  - ERROR: hot 30 days → warm 1 year → archive 7 years
  - WARN:  hot 7 days → warm 90 days → delete
  - INFO:  hot 7 days → warm 30 days → delete (unsampled INFO is valuable only for recent debugging)
  - DEBUG: hot 24 hours → delete (no long-term value; too high volume)

Immutability for compliance (audit logs):
  - Audit logs (authentication, data access, admin actions) written to append-only S3 bucket
  - S3 Object Lock (WORM - Write Once Read Many): prevents deletion for 7 years
  - Separate from application logs: different Kafka topic, different ES index, different S3 bucket
  - Hash each batch of audit logs and store hash in a separate tamper-evidence log
```

### Cost Model

```
Cost breakdown by tier (monthly at 100 TB/day):
  - Kafka ingest buffer:           $2,765/month
  - Elasticsearch hot tier:        $25,400/month
  - Elasticsearch warm tier:       $53,960/month
  - S3 cold tier (1 year):         $82,800/month
  - S3 Glacier archive (7 years):  $100,800/month
  - Fluentd/Filebeat agents:       ~$0 (runs on existing compute)
  - Kibana/Grafana compute:        ~$1,000/month

Total: ~$267K/month

With INFO sampling at 1%:
  - Reduce total log volume from 100 TB/day to ~20 TB/day
  - Savings: ~$200K/month
  - Reduced total: ~$67K/month
  - Per GB ingested (after sampling): $0.11/GB/month

Cost per engineering team (100 teams, 3 services each = 300 services):
  $67K / 300 = ~$223/service/month for full log infrastructure
```

---

## Trade-off Comparison

| Storage Backend         | Search Latency       | Ingest Throughput    | Cost Efficiency      | Best For                         |
|-------------------------|----------------------|----------------------|----------------------|----------------------------------|
| Elasticsearch           | <1s (full-text)      | High (with tuning)   | Medium               | Full-text search, ad-hoc queries |
| ClickHouse              | <1s (columnar)       | Very high (1M+/sec)  | High                 | Aggregations, analytics queries  |
| Loki (Grafana)          | Medium (label-based) | High (chunk-based)   | Very high (no index) | Cost-sensitive; label-only query |
| OpenSearch              | <1s                  | High                 | Medium               | Elasticsearch alternative (open) |
| BigQuery/Athena         | 5-30s (serverless)   | High (batch)         | Low (query cost)     | Infrequent ad-hoc over cold data |
| Splunk                  | <1s (proprietary)    | Very high            | Very low (expensive) | Enterprise security, SIEM        |

## Follow-up Questions (escalating difficulty, 7 minimum)

1. **(L3)** What is the role of Kafka in a log aggregation pipeline?
   → Kafka acts as a durable buffer between log producers (agents) and consumers (Elasticsearch indexers, alerters). Without it, if Elasticsearch goes down or slows down, the agents have nowhere to write and start dropping logs. Kafka absorbs bursts, decouples producer throughput from consumer throughput, and allows multiple consumers (indexer + alerter + archiver) to read the same log stream independently at their own pace.

2. **(L3)** What is the difference between Fluentd and Filebeat?
   → Both are log shipping agents. Filebeat (Elastic) is lightweight (10 MB RAM) and optimized for tailing log files and shipping to Elasticsearch or Kafka. Fluentd (CNCF) is more flexible, supports 500+ plugins, and can parse/filter/route logs to multiple destinations. Use Filebeat when the stack is all-Elastic; use Fluentd or Vector for complex routing (e.g., route ERROR logs to PagerDuty, INFO to S3, DEBUG to /dev/null).

3. **(L4)** What is Elasticsearch Index Lifecycle Management (ILM) and why is it critical at 100 TB/day?
   → ILM automatically moves indices through phases: hot (recent, SSD, high-replica) → warm (older, HDD, lower-replica) → cold (frozen, S3-backed) → delete. Without ILM, all data stays on expensive hot-tier SSDs indefinitely. At 100 TB/day, ILM reduces active SSD storage from petabytes to 70 TB (7-day hot) and pushes the rest to progressively cheaper tiers. Critical configurations: rollover triggers (shard size at 50 GB, index age at 1 day), force-merge before warm (reduces segment file handles from 50 to 1 per shard).

4. **(L4)** How would you implement per-service log rate limiting to prevent log storms?
   → Add a Fluentd limiter plugin or a Kafka quota at the broker. In Kafka: set per-client-id quota (--describe --entity-type clients --entity-name checkout-api). In Fluentd: use the throttle filter plugin (max_lines_per_second: 10000). When limit is hit, sample excess lines: keep 1 in 100. Additionally: add a rate monitor consumer that reads from Kafka, tracks per-service volume over 1-minute windows, and fires a PagerDuty alert if any service exceeds 2x baseline. Auto-sampling kicks in at 10x baseline to protect cluster stability.

5. **(L5)** How do you handle a compliance requirement that ERROR and audit logs must be retained for 7 years with tamper-evidence?
   → Use a separate Kafka topic (log.audit) for compliance logs. A dedicated consumer writes audit log batches to S3 with Object Lock (WORM mode, legal-hold retention for 7 years). To add tamper evidence: compute SHA-256 hash of each daily batch file, store the hash in an immutable append-only ledger (separate S3 bucket, or a blockchain-anchored system for high-assurance). When auditors need to verify integrity: re-download the file, recompute the hash, compare to the stored hash — any modification is detectable. Keep audit logs in a separate Elasticsearch index with no delete permissions for regular operators.

6. **(L5)** Design the sampling strategy for INFO logs to reduce storage cost without missing critical signals.
   → Sample INFO logs probabilistically at 1% using consistent hashing on request_id: `hash(request_id) % 100 < 1`. This means: for a given request, all logs (across services) either all-sampled or all-dropped — preserving trace coherence. If an ERROR occurs for a request, immediately promote all that request's logs to 100% (no sampling): retroactively "unsample" them by writing them to the ERROR topic. This ensures every error trace is fully reconstructable. Use reservoir sampling for aggregate metrics: even at 1% sample rate, aggregate error rates and P99 latency are statistically accurate. The 1% INFO sample reduces daily volume from 100 TB to ~20 TB, saving $200K/month.

7. **(L5+)** How would you design a log aggregation system that handles both real-time search (sub-second) and batch analytics (SQL over months of data) cost-effectively?
   → Use a lambda architecture with two paths from Kafka: (1) Speed layer: Elasticsearch or Loki for last-7-days real-time search — engineers type queries, get results in 1 second. Store on SSD, full indexing. (2) Batch layer: ClickHouse or Athena over Parquet files on S3 for analytics over months of data. Partition Parquet files by day + service + log_level for partition pruning. ClickHouse: sub-second aggregations over months via columnar scan. Athena: serverless, pay-per-query (no idle cost) for infrequent historical queries. Serving layer: router inspects query time range — if within 7 days, route to Elasticsearch; if older, route to ClickHouse/Athena. This cuts infrastructure cost by 60% vs. keeping all data in Elasticsearch, while maintaining fast real-time search for operational use.

## Anti-patterns / Things NOT to Say

- **"Log everything at DEBUG level in production"** — DEBUG logs can increase volume 10-100x over INFO. At 100 TB/day INFO volume, enabling DEBUG would generate 1-10 PB/day — blowing Kafka capacity, exhausting Elasticsearch disk within hours, and costing millions per month. Always use DEBUG only in development or with targeted, short-duration sampling (e.g., 10 minutes for a specific service to diagnose an incident).
- **"Use a single Kafka topic for all log levels"** — Mixed severity in one topic means a single slow consumer (e.g., batch archiver) delays real-time processing of ERROR logs. Always separate by severity: ERROR/CRITICAL logs in high-priority topics with dedicated consumers that feed real-time alerting. INFO/DEBUG in lower-priority topics that can tolerate higher consumer lag.
- **"Store all logs in Elasticsearch forever"** — Elasticsearch is expensive for long-term storage ($0.50-$1.00/GB/month vs. S3 at $0.023/GB). At 100 TB/day, keeping 1 year of data in Elasticsearch would cost over $1.8M/month in storage alone. Use Elasticsearch only for hot data (7-30 days); move cold data to S3-backed Parquet or frozen Elasticsearch tiers.
- **"Logs are append-only so you don't need to worry about ordering"** — While logs are append-only within a single process, distributed systems produce logs out of order. A user's request spans 5 services; the gateway log may arrive 2 seconds after the DB log due to different agent flush intervals. Never assume log timestamps are totally ordered across services. Use correlation IDs (trace_id, request_id) to join logs from different services, not timestamp ordering.
- **"Parse logs at query time using regex"** — Parsing unstructured text at query time is 100x slower than querying pre-parsed, indexed structured fields. A regex scan over 7 days of raw text at 100 TB can take minutes. Parse logs at collection time (in the agent or a stream processor), emit structured JSON with explicit fields, and index those fields. Structured logging is the foundation of fast log search.

## Python Implementation (sketch)

```python
import json
import time
import hashlib
import logging
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any
from kafka import KafkaProducer

@dataclass
class StructuredLog:
    timestamp: str
    log_level: str
    service: str
    message: str
    trace_id: Optional[str] = None
    request_id: Optional[str] = None
    user_id: Optional[int] = None
    duration_ms: Optional[float] = None
    http_status: Optional[int] = None
    error_class: Optional[str] = None
    env: str = "production"
    region: str = "us-east-1"

class StructuredLogger:
    """Structured logger that ships to Kafka with log-level-based routing and sampling."""

    TOPIC_MAP = {
        "ERROR":    "logs.error",
        "CRITICAL": "logs.error",
        "WARN":     "logs.warn",
        "INFO":     "logs.info",
        "DEBUG":    "logs.debug",
    }
    SAMPLE_RATES = {"ERROR": 1.0, "CRITICAL": 1.0, "WARN": 1.0, "INFO": 0.01, "DEBUG": 0.001}

    def __init__(self, service: str, kafka_producer: KafkaProducer):
        self.service = service
        self.producer = kafka_producer

    def log(self, level: str, message: str, **kwargs):
        if not self._should_sample(level, kwargs.get("request_id")):
            return

        entry = StructuredLog(
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%S.") + f"{int(time.time() * 1000) % 1000:03d}Z",
            log_level=level,
            service=self.service,
            message=message,
            **{k: v for k, v in kwargs.items() if hasattr(StructuredLog, k)}
        )
        topic = self.TOPIC_MAP.get(level, "logs.info")
        self.producer.send(topic, value=json.dumps(asdict(entry)).encode())

    def _should_sample(self, level: str, request_id: Optional[str]) -> bool:
        rate = self.SAMPLE_RATES.get(level, 0.01)
        if rate >= 1.0:
            return True
        # Consistent hash on request_id: same request either always or never sampled
        seed = request_id or str(time.time())
        hash_val = int(hashlib.md5(seed.encode()).hexdigest(), 16) % 10000
        return hash_val < int(rate * 10000)

    def error(self, msg: str, **kw): self.log("ERROR", msg, **kw)
    def warn(self,  msg: str, **kw): self.log("WARN",  msg, **kw)
    def info(self,  msg: str, **kw): self.log("INFO",  msg, **kw)
    def debug(self, msg: str, **kw): self.log("DEBUG", msg, **kw)


def compute_audit_batch_hash(log_lines: list) -> str:
    """Compute SHA-256 of a batch of audit log lines for tamper detection."""
    content = "\n".join(json.dumps(line, sort_keys=True) for line in log_lines)
    return hashlib.sha256(content.encode()).hexdigest()


# Usage example
if __name__ == "__main__":
    producer = KafkaProducer(bootstrap_servers=["kafka:9092"])
    logger = StructuredLogger(service="checkout-api", kafka_producer=producer)

    logger.error("Payment processor timeout",
                 trace_id="abc123", request_id="req-456",
                 user_id=12345, duration_ms=5001, http_status=503,
                 error_class="TimeoutException")

    logger.info("Order created successfully",
                trace_id="def789", request_id="req-789",
                user_id=12345, duration_ms=42)
```

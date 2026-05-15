# Log Aggregation System

## Problem Statement
Design a system collecting, storing, and searching logs from distributed services.

**Pipeline:**
- Collection: Agents on servers
- Processing: Parse and enrich
- Storage: Searchable index
- Querying: Full-text search

## Design

### Collection

```
Agent on each server: Reads logs
Buffering: Batch before send
Retry: Exponential backoff
Compression: Reduce bandwidth
```

### Processing

```
Parse: Extract fields
Enrich: Add context (timestamp, host)
Filter: Drop unneeded logs
Deduplicate: Combine same errors
```

### Storage

```
Time-series indexed
Searchable (Elasticsearch)
Partitioned by time
TTL: Auto-delete old logs
```

### Querying

```
Full-text search
Field filtering
Time range
Aggregation: Error counts, rates
```


## Architecture Diagram

```
┌───────────────────────────────┐
│   Log Collection Pipeline    │
│  Shipping (Filebeat)          │
│  - Tail files, ship           │
│  - Retry on failure           │
│  Broker (Kafka)               │
│  - Durable, replay-capable    │
│  - Retention: 7 days          │
│  Storage                      │
│  - Index (Elasticsearch)      │
│  - Archive (S3, Glacier)      │
└───────────────────────────────┘
```

## Common Questions & Answers

**Q: Log loss prevention?** A: Broker acks=all. Persistence. Replay if process fails.

**Q: Parsing logs?** A: Grok patterns for common. Best: enforce JSON output.

**Q: Search latency?** A: ES shard by time. Old logs in cold storage (Glacier).

**Q: Retention?** A: 30 days hot (ES). 1 year warm (S3). Archive Glacier.

## Back-of-Envelope Calculations

100K servers, 1K log/sec each = 100M logs/sec. Raw: 100TB/sec, compressed: 10TB/sec. ES: 100TB daily. Kafka: 700TB/7days.
## Design Choice Comparison

| Approach | Pros | Cons |
|----------|------|------|
| Centralized | Searchable, correlated | Network overhead |
| Local | Simple | Hard debug |
| Sampling | Scalable | Rare issues lost |

## Follow-up Interview Questions

1. Correlate logs (trace IDs)? 2. Real-time alerting? 3. Tamper-proof audit? 4. ES throughput bottleneck? 5. Multi-service debugging?

## Example Scenario Walkthrough

[Describe a concrete example with step-by-step execution]

## Complexity

| Operation | Time |
|-----------|------|
| Collect | O(1) |
| Index | O(log n) |
| Search | O(log n + k) |

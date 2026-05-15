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

## Complexity

| Operation | Time |
|-----------|------|
| Collect | O(1) |
| Index | O(log n) |
| Search | O(log n + k) |

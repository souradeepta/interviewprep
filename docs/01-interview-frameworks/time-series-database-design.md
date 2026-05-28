# Time Series Database Design: Storing and Querying Temporal Data

**Level:** L4-L5
**Time to read:** ~10 min

Master time series database patterns for metrics, logs, and events.

---

## Time Series Data Characteristics

```
Traditional DB                Time Series DB
─────────────────            ──────────────
Few updates/deletes           Many appends, rare updates
Random access                 Sequential append
Complex queries               Range queries (time windows)
ACID transactions             Write throughput critical

Example metrics:
Temperature: [timestamp, value, location]
CPU usage: [timestamp, percentage, host]
Stock prices: [timestamp, price, ticker]
User events: [timestamp, event_type, user_id]
```

---

## Time Series Compression

### Problem
```
10K metrics × 1 sample/minute × 365 days = 5.2B data points
Each point: 16 bytes (timestamp + value) = 83GB/year
Without compression: Expensive storage and slow queries
```

### Compression Techniques

#### Delta-of-Delta Encoding

```
Timestamps:
1000, 1060, 1120, 1180, 1240
                    (regular 60-second intervals)

Delta:   60, 60, 60, 60       (differences)
Delta-of-delta: 0, 0, 0       (differences of differences)

Encode only the delta-of-delta (mostly 0s = highly compressible)
```

#### Gorilla Algorithm (Facebook)

```
Compresses time series 10-100x:
1. Delta-of-delta for timestamps
2. XOR encoding for floating-point values
3. Run-length encoding

Result: 1.37 bytes per data point (vs 16 raw)
```

---

## Time Series Database Operations

### Write (Append-Only)

```python
# Very fast, sequential writes
def write_metric(metric_name, timestamp, value, tags):
    # Append to time series
    # Index: metric_name, tags → timeseries_id
    # Data: timeseries_id, timestamp, value
    
    # Update index
    index.add(metric_name, tags, timestamp)
    
    # Append to time series file
    timeseries_file.append(encode(timestamp, value))
```

### Read (Range Query)

```python
def query_range(metric_name, tags, start_time, end_time):
    # Find time series ID
    timeseries_ids = index.query(metric_name, tags)
    
    # For each time series, read range
    results = []
    for tsid in timeseries_ids:
        # Binary search on timestamp
        start_block = find_block(tsid, start_time)
        end_block = find_block(tsid, end_time)
        
        # Read blocks between start and end
        for block_id in range(start_block, end_block + 1):
            data = read_block(tsid, block_id)
            results.extend(decompress(data))
    
    return results
```

### Aggregation (Common Query)

```
SELECT average(cpu_usage) 
WHERE timestamp >= now() - 1hour 
GROUP BY 5min

Result:
12:00-12:05: 45%
12:05-12:10: 47%
12:10-12:15: 42%
...

Optimization: Pre-compute aggregates at multiple granularities
```

---

## Time Series Databases

### InfluxDB

```
Optimized for metrics and events
- Automatic retention policies (keep 30 days)
- Time series compression
- Downsampling (5min resolution from 1sec)

Query:
SELECT mean(cpu_usage) FROM system WHERE time > now() - 1h GROUP BY 5m
```

### Prometheus

```
Pull-based (servers scrape metrics)
- Time series: metric_name{label1=value1, label2=value2}
- 15-second default scrape interval
- Local storage (good for smaller scale)

Query (PromQL):
rate(http_requests_total[5m])  // 5-minute request rate
```

### TimescaleDB

```
PostgreSQL extension for time series
- Hypertables (automatically partitioned by time)
- Compression (2-4x better than raw PostgreSQL)
- Native time series functions

Query:
SELECT time_bucket('5 minutes', time) AS bucket,
       avg(value)
FROM metrics
WHERE time > now() - interval '1 day'
GROUP BY bucket;
```

---

## Time Series Challenges

| Challenge | Solution |
|-----------|----------|
| **Storage growth** | Downsampling (keep 1sec for 1 day, 1min for 30 days) |
| **High cardinality** | Limit label combinations, use tags carefully |
| **Missing data** | Forward fill or leave gaps |
| **Outliers** | Alerting rules, statistical detection |
| **Time zone issues** | Store all in UTC |

---

## Time Series Checklist

- ✓ Chose appropriate time series database
- ✓ Retention policy defined (how long to keep data)
- ✓ Downsampling strategy (aggregate old data)
- ✓ Compression enabled (10-100x better)
- ✓ Indexing on common queries (metric name, tags)
- ✓ Cardinality limits (avoid explosion)
- ✓ Aggregation queries pre-computed
- ✓ Backup and disaster recovery
- ✓ Query optimization (time range predicates)
- ✓ Monitoring: storage growth, query latency


# Columnar Databases — Analytics at Scale

Optimized for OLAP queries and data warehousing.

---

## 📊 Column Store vs. Row Store

### Row Store
```
Row 1: [user_id, name, email, created_at]
Row 2: [user_id, name, email, created_at]
Row 3: [user_id, name, email, created_at]

Good for: Updates, single row access
Bad for: Aggregations (read all data even if only need 1 column)
```

### Column Store
```
Column 1 (user_id): [1, 2, 3, 4, 5, ...]
Column 2 (name): ["Alice", "Bob", "Charlie", ...]
Column 3 (email): ["alice@...", "bob@...", ...]

Good for: Aggregations (read only needed columns)
Bad for: Single row updates (update multiple columns)
```

---

## 🎯 Columnar Databases

**ClickHouse:** High-speed OLAP
**Snowflake:** Cloud data warehouse
**BigQuery:** Google's data warehouse
**Redshift:** AWS data warehouse

---

## ⚡ Compression

Columns of same type compress well:

```
Integers: [1, 2, 3, 4, 5, ...]
Compression: Delta encoding (store differences)

Strings: ["John", "Jane", "John", "John", ...]
Compression: Dictionary encoding (store index)
```

**Result:** 10-100x compression vs. row store

---

## 📈 Partitioning

```
Table: events (1B rows)

Partition by date:
- 2024-01-01: 1M rows
- 2024-01-02: 1M rows
...

Query by date range: Only read relevant partitions
```

---

## 📊 Aggregation Performance

```sql
-- Row store: Scan all rows, compute sum
SELECT SUM(amount) FROM orders;  -- 10 seconds

-- Column store: Scan amount column, compute sum
SELECT SUM(amount) FROM orders;  -- 100ms (100x faster!)
```

---

## 🔄 ETL Pipeline

```
Source DB → Extract → Transform → Load → Columnar Store

Batch or streaming:
- Batch: Daily snapshots (simple)
- Streaming: Real-time updates (complex)
```

---

## 💰 Cost Optimization

**Query:** Only read needed columns (cheaper)
**Partitioning:** Prune partitions (faster)
**Compression:** Smaller storage (cheaper)

---

## ⚖️ Columnar vs. Row-Based Trade-offs

```
Feature           | Columnar       | Row-Based (PostgreSQL)
─────────────────|────────────────|──────────────────────
Aggregations     | 100-1000x fast | Standard
Compression      | 10-100x better | Normal
Read columns     | Only needed    | All columns
Write speed      | Slower         | Fast
Update single row| Slow (rewrite) | Fast
ACID transactions| Limited        | Full
Disk I/O         | Minimal        | Higher
Memory usage     | Lower per col  | Higher
Schema changes   | Slower         | Faster
Real-time feeds | No             | Yes

When Columnar (OLAP):
├─ Analytics (SUM, AVG, COUNT)
├─ 1B+ row datasets
├─ Read-heavy (analytics)
├─ Denormalized schema
├─ Time-series aggregation
└─ Business intelligence

When Row-Based (OLTP):
├─ Frequent updates
├─ ACID transactions
├─ Small-medium datasets
├─ Real-time operations
├─ Complex queries (joins)
└─ Normalized schema
```

---

## 🏗️ Compression Techniques

### Delta Encoding
```
Original: [1000, 1001, 1002, 1003, 1004]
Delta:    [1000, 1, 1, 1, 1]        ← Much smaller!

Compression ratio: 5x
Use case: Time-series (monotonically increasing)
```

### Dictionary Encoding
```
Original: ["John", "Jane", "John", "John", "Jane", ...]
Dict:     {0: "John", 1: "Jane"}
Encoded:  [0, 1, 0, 0, 1, ...]      ← Stored as integers

Compression ratio: 10x (if few unique values)
Use case: Categorical data (user_id, product_id)
```

### Run-Length Encoding (RLE)
```
Original: ["USA", "USA", "USA", "USA", "UK", "UK", "UK", ...]
Encoded:  [("USA", 4), ("UK", 3), ...]

Compression ratio: 100x (for repetitive data)
Use case: Regions, categories with clustering
```

### Bit-Packing
```
Original: [0, 1, 0, 0, 1, 1, 0, 1]  (8 bytes = 8 bools)
Packed:   [01001101]                 (1 byte = 8 bools)

Compression ratio: 8x (for boolean columns)
Use case: Feature flags, boolean attributes
```

---

## 📊 Architecture Patterns

### Data Warehouse Medallion Architecture
```
Bronze Layer (Raw Data):
├─ Unprocessed data directly from source
├─ Partitioned by date/source
├─ Full history retained
├─ Example: daily_events_raw

Silver Layer (Cleaned Data):
├─ Deduplicated, validated, enriched
├─ Business logic applied
├─ Schema stabilized
├─ Example: events_clean

Gold Layer (Analytics):
├─ Aggregated, denormalized
├─ Optimized for specific use cases
├─ Pre-computed metrics
├─ Example: user_daily_metrics, product_performance
```

### Separation of Compute and Storage
```
Snowflake/BigQuery architecture:

           ┌─────────────────┐
           │  Query Engine   │
           │  (Scalable)     │
           └────────┬────────┘
                    │
                    │ Pulls only needed columns
                    ↓
           ┌─────────────────┐
           │  Cloud Storage  │
           │  (S3/GCS)       │
           │  (Cheap)        │
           └─────────────────┘

Benefit: Pay for compute and storage independently
- Compute down when not querying
- Storage cheap and unlimited
```

---

## ⚡ Performance Optimization Techniques

### Query Optimization
```sql
-- Bad: Reads all columns, including large ones
SELECT * FROM events WHERE event_type = 'click';

-- Good: Select only needed columns
SELECT user_id, event_timestamp, event_type 
FROM events 
WHERE event_type = 'click';

Performance: 10x faster (less data to scan)
```

### Partitioning Strategy
```
Partition by date (most common):
├─ 2024-01-01: 100M rows (partitions pruned in WHERE clause)
├─ 2024-01-02: 100M rows
└─ 2024-01-03: 100M rows

Query: WHERE date = '2024-01-02'
Scans: Only 100M rows (not 300M)

Alternative partitioning:
├─ By region: North, South, East, West
├─ By source: web, mobile, api
├─ By customer: customer_segment
└─ Composite: date + region
```

### Clustering Keys
```sql
-- Define sort order (helps compression)
CREATE TABLE events CLUSTER BY (user_id, event_timestamp);

Query benefits:
├─ Related rows stored together
├─ Better compression
├─ Faster range queries
└─ Skipping still works

Snowflake syntax:
CREATE TABLE events (...) CLUSTER BY (user_id, event_timestamp);
Query: SELECT * FROM events WHERE user_id = 123
→ Scans smaller range (auto-pruned)
```

---

## 📈 Real-World Performance Comparison

### Query: SUM of amount by region (1B rows)
```
PostgreSQL (Row-based):
├─ Scan: 1B rows × 100 bytes = 100GB
├─ Filter: amount column (80 bytes per row)
├─ Memory: 100GB required
├─ Time: 100 seconds

Snowflake (Columnar):
├─ Scan: amount column × 1B rows = 8GB (dictionary encoded)
├─ Filter: region column = 4GB (integer encoded)
├─ Memory: 12GB required
├─ Time: 1 second (100x faster!)
```

---

## 🔄 ETL vs. ELT Comparison

```
ETL (Extract, Transform, Load):
1. Extract data from source
2. Transform in staging area
3. Load into data warehouse

Traditional approach:
├─ Data cleaned before loading
├─ Smaller warehouse (only processed data)
├─ More control over quality
└─ Slower (multiple stages)

ELT (Extract, Load, Transform):
1. Extract data from source
2. Load raw into data warehouse
3. Transform using SQL queries

Modern approach (Cloud):
├─ Faster loading (raw data)
├─ Warehouse is transformation engine
├─ Flexibility (reprocess as needed)
├─ Better for rapidly changing schemas
```

---

## ❓ Comprehensive Interview Q&A

**Q: When to use columnar DB vs. PostgreSQL?**

A:
```
PostgreSQL when:
✓ Real-time transactional data
✓ ACID transactions mandatory
✓ Frequent updates/deletes
✓ Complex multi-table queries
✓ < 100 million rows

Columnar (Snowflake/BigQuery) when:
✓ Analytics and aggregations
✓ 1 billion+ rows
✓ Read-heavy workload
✓ Cloud infrastructure
✓ Cost-sensitive (storage cheap)
✓ Batch processing (daily/hourly)

Example decision:
→ Order management: PostgreSQL (real-time, ACID)
→ Analytics dashboard: Snowflake (bulk analytics)
→ Hybrid: Both (PostgreSQL for OLTP, Snowflake for OLAP)
```

**Q: Design data warehouse for 10B daily events**

A:
```
Architecture:

Source → Kafka → Data Lake (Raw) → Snowflake (Processed)
                      ↓
                   S3/GCS

Schema Design:

Bronze (Raw events):
CREATE TABLE bronze.events_raw (
  received_timestamp TIMESTAMP,
  source_system STRING,
  raw_data JSON,
  load_date DATE
)
PARTITION BY load_date
CLUSTER BY source_system;

Silver (Cleaned events):
CREATE TABLE silver.events (
  event_id STRING,
  user_id STRING,
  event_type STRING,
  event_timestamp TIMESTAMP,
  properties MAP,
  event_date DATE
)
PARTITION BY event_date
CLUSTER BY (user_id, event_timestamp);

Gold (Aggregated metrics):
CREATE TABLE gold.user_daily_metrics (
  user_id STRING,
  event_date DATE,
  event_count INT,
  click_count INT,
  purchase_count INT,
  total_spent DECIMAL,
  session_count INT
)
CLUSTER BY (user_id, event_date);

Data Pipeline:
1. Kafka streams raw events
2. Lambda/Airflow: Parse, deduplicate → Silver
3. dbt: Transform → Gold (hourly)
4. Snowflake: Store compressed (10GB per day)

Query Examples:
-- Find trend (Gold layer, super fast)
SELECT event_date, SUM(click_count) as total_clicks
FROM gold.user_daily_metrics
WHERE event_date >= '2024-01-01'
GROUP BY event_date
ORDER BY event_date DESC;

Performance: 100ms (aggregated)

Scaling:
├─ Partitioning: Prunes unnecessary data
├─ Clustering: Groups similar rows
├─ Compression: 10-100x smaller
├─ Cost: ~$1-2 per TB stored
├─ Query cost: ~$0.10 per TB scanned
```

**Q: How to handle late-arriving data in data warehouse?**

A:
```
Scenario: Event from yesterday arrives today

Option 1: Reprocessing (Simple, batch-based)
├─ Store events in Silver by event_date (not arrival_date)
├─ Reprocess entire day (refresh Gold metrics)
├─ SQL: DELETE FROM gold WHERE event_date = '2024-01-15'
├─ Then: Recompute Gold layer
├─ Trade-off: Simple, but resource-intensive

Option 2: Incremental updates (Complex, streaming-based)
├─ Track updates using event_date + version
├─ Upsert into Gold (CDC pattern)
├─ SQL: MERGE INTO gold USING silver WHERE event_date = TODAY()
├─ Trade-off: Efficient, but complex logic

Option 3: Late-arriving data partition
├─ Separate partition: late_arriving_events
├─ Metadata: event_received_status (on_time, late, very_late)
├─ SLA: Accept max 24-hour latency
├─ Reprocess: Only late events

Best Practice:
├─ Define SLA for late data (24 hours = acceptable)
├─ Partition by event_date (not arrival_date)
├─ Reprocess daily (automatic)
├─ Monitor: % of late data
```

**Q: Columnar DB compression trade-offs?**

A:
```
Compression Ratio vs. Query Latency:

Dictionary Encoding:
├─ Ratio: 10-100x (if low cardinality)
├─ Decompression: Fast (integer lookup)
├─ Query latency: Minimal impact
├─ Best for: Categorical columns (country, product_id)

Delta Encoding:
├─ Ratio: 5-10x (monotonic data)
├─ Decompression: Fast (sequential decode)
├─ Query latency: Minimal impact
├─ Best for: Timestamps, sequential IDs

LZ4/ZSTD (Generic):
├─ Ratio: 3-5x (varies)
├─ Decompression: Moderate CPU cost
├─ Query latency: 5-10% overhead
├─ Best for: Mixed data types

Optimization Strategy:
1. Use automatic compression (Snowflake does this)
2. Monitor: Compression ratio by column
3. Profile: Query latency before/after
4. Trade-off: Storage vs. Query speed
5. Usually: Storage wins (cloud cheap, query fast enough)
```

---

## 💡 Interview Tips

**What interviewer is really asking:**
- "Design data warehouse" → Do you know medallion architecture, partitioning?
- "Optimize slow query" → Do you understand compression, clustering, partition pruning?
- "ETL vs ELT" → Do you know modern cloud approaches?
- "Handle 10B rows" → Do you know scaling strategies (partitioning, compression)?

**How to answer:**
1. **Clarify:** Scale (rows/day), latency SLA, query patterns
2. **Architecture:** Bronze/Silver/Gold layers
3. **Partitioning:** By date (most common), consider region/source
4. **Compression:** Automatic (let cloud provider handle)
5. **Optimization:** Clustering keys, select only needed columns
6. **Cost:** Consider compute vs. storage trade-off

---

**Last updated:** 2026-05-22

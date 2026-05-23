# Data Warehousing & Lakehouses — Analytics Infrastructure

Building scalable, cost-effective analytics systems with governance and performance.

---

## ⚖️ OLTP vs. OLAP Comparison

```
Dimension         | OLTP (Operational) | OLAP (Analytical)
─────────────────:|───────────────────:|──────────────────
Source            | Production DB      | Warehouse/Lake
Schema            | Normalized (3NF)   | Denormalized (Star)
Workload          | CRUD, transactions | Aggregations, joins
Query type        | Simple, single-row | Complex, multi-table
Read/Write ratio  | 50/50              | 95/5 (mostly reads)
Latency target    | <100ms             | <5 seconds
Data freshness    | Real-time          | Hours to daily
Row format        | Row-oriented       | Columnar
Cardinality       | High (millions)    | Low (aggregated)

OLTP Example:
├─ Insert order: INSERT INTO orders (...) → 1ms
├─ Update user: UPDATE users SET ... → 1ms
└─ Query single: SELECT * FROM orders WHERE id=123 → 5ms

OLAP Example:
├─ Monthly revenue: SELECT SUM(amount) GROUP BY month → 1s
├─ Cohort analysis: JOIN users, orders, events → 5s
└─ Trend detection: Complex aggregations → 10s
```

---

## 🏗️ Modern Analytics Architecture

### Traditional Data Warehouse

```
ETL Pipeline (Data Transformation):
Source DB → Extract → Transform → Load → Warehouse
            (SQL)                        (Snowflake/BigQuery)
            
Data Quality:
- Clean, validated data before load
- Single source of truth
- Schema enforced

Cons:
- ETL complexity (data transformation logic)
- Slow iteration (change = rebuild pipeline)
- Expensive (pre-processing costs)
```

### Data Lake

```
Flexible Storage:
Source DB → Raw Data → S3/ADLS/GCS
            (Parquet)
            
Schema-on-read:
- Raw data as-is
- Transform on query
- Fast ingestion

Cons:
- Data quality issues (no validation)
- No governance (chaos)
- Hard to find data (no catalog)
```

### Lakehouse (Modern Best Practice)

```
Hybrid Approach:
Source DB → Bronze (Raw)
         → Silver (Cleaned)
         → Gold (Analytics)

Benefits:
- Raw data flexibility (Data Lake)
- Schema enforcement (Warehouse)
- ACID transactions (Delta/Iceberg)
- Time travel (data lineage)
- Cost-effective (cloud storage)
```

---

## 🎯 Medallion Architecture (3-Layer Pattern)

### Layer 1: Bronze (Raw Ingestion)

```
Purpose: Ingest data as-is, preserve history

Properties:
├─ Minimal transformation
├─ Append-only (no deletes)
├─ Full data lineage
├─ Partitioned by load_date

Example:
Table: bronze.customer_raw
├─ Columns: source_system, load_timestamp, raw_data (JSON)
├─ Partition: by load_date
├─ Schema: Flexible (JSON)
└─ Retention: 30 days (cost)

Quality Level: None (raw)
Latency: <1 hour (incremental loads)
```

### Layer 2: Silver (Cleaned & Validated)

```
Purpose: Clean, deduplicate, validate

Transformations:
├─ Remove duplicates
├─ Data type conversion
├─ Null handling
├─ Validation (reject invalid)
├─ Deduplication logic
└─ Data quality checks

Example:
Table: silver.customers
├─ Columns: customer_id, name, email, phone, created_at
├─ Partition: by created_date
├─ Schema: Strongly typed
├─ PK: customer_id (unique)
└─ Data quality: Monitored

Quality Level: High (validated, deduplicated)
Latency: 1-2 hours (transformation overhead)
```

### Layer 3: Gold (Analytics Ready)

```
Purpose: Business aggregates, denormalized for queries

Aggregations:
├─ Pre-compute metrics
├─ Dimensional tables
├─ Fact tables
├─ Slow-changing dimensions (SCD)

Examples:
Table: gold.customer_daily_metrics
├─ Columns: date, customer_id, total_orders, total_spent, ltv
├─ Partition: by date
├─ Grain: (date, customer_id)
└─ Freshness: Daily (computed after midnight)

Table: gold.orders_fact
├─ Columns: order_id, customer_id, product_id, quantity, amount
├─ Partition: by order_date
├─ Grain: (order_id)
└─ PK: order_id

Quality Level: Very High (consistent, tested)
Latency: <1ms (pre-computed)
```

### Medallion Data Flow

```
Raw Data (APIs, DBs, Files)
           ↓ (hourly)
Bronze Layer: bronze.events_raw
├─ No transformation
├─ Append-only
├─ Keep 30 days
           ↓ (nightly dbt job)
Silver Layer: silver.events
├─ Deduplicated
├─ Validated
├─ Type-correct
           ↓ (nightly dbt job)
Gold Layer: gold.user_daily_events
├─ Aggregated (user, event_type, count)
├─ Pre-computed
├─ Analytics-ready

Downstream:
gold.* → Dashboard (Tableau)
      → ML Model (feature engineering)
      → Reports (email)
```

---

## 📊 Table Format Comparison

```
Format      | Transactions | Time Travel | Partitioning | Community | Maturity
────────────|──────────────|─────────────|──────────────|───────────|──────
Parquet     | No           | No          | Yes          | Massive   | Very Mature
Delta Lake  | Yes (ACID)   | Yes         | Yes          | Large     | Mature
Iceberg     | Yes (ACID)   | Yes         | Advanced     | Growing   | Mature
Hudi        | Incremental  | Limited     | Yes          | Growing   | Developing

Parquet (Default):
├─ Columnar compression
├─ No transactions
├─ Simple format
├─ Best for: Immutable data, batch processing

Delta Lake (Recommended):
├─ ACID transactions on Parquet
├─ Time travel (query past versions)
├─ Data quality checks (constraints)
├─ Best for: Medallion architecture, Databricks

Iceberg (Enterprise):
├─ Distributed transactions
├─ Partition evolution (add columns safely)
├─ Optimized compaction
├─ Best for: Large-scale (Snowflake, Spark)
```

---

## 🔄 ETL vs. ELT Comparison

```
                  | ETL (Traditional)  | ELT (Modern)
──────────────────|────────────────────|──────────────────
Order of ops      | Transform → Load   | Load → Transform
Data quality      | Before warehouse   | In warehouse
Transformation    | Staging area       | SQL in warehouse
Latency           | High (slow)        | Low (fast)
Infrastructure    | Extra (staging)    | Minimal
Flexibility       | Lower (fixed logic)| Higher (SQL)
Cost              | Higher ($)         | Lower ($)

ETL Pipeline:
Source DB → Extract → Staging (Transform logic) → Load → Warehouse
            (Scripts/Talend)

Example (ETL):
```python
# Extract
source_data = db.query("SELECT * FROM source_table")

# Transform (in staging area)
cleaned = []
for row in source_data:
    if validate(row):  # Filter
        cleaned.append({
            'id': row['id'],
            'name': row['name'].strip(),
            'email': row['email'].lower()
        })

# Load
warehouse.insert('target_table', cleaned)
```

ELT Pipeline:
Source DB → Extract → Warehouse (Transform via SQL) → Aggregate
            (Raw load)      ↓
                        (dbt, SQL)

Example (ELT):
```sql
-- Load (raw)
INSERT INTO bronze.source_data
SELECT * FROM source_db.table;

-- Transform (in warehouse)
CREATE TABLE silver.customers AS
SELECT 
  id,
  TRIM(name) as name,
  LOWER(email) as email
FROM bronze.source_data
WHERE id IS NOT NULL
  AND email IS NOT NULL;
```

Modern recommendation: ELT
├─ Cloud storage cheap (S3)
├─ SQL powerful (Snowflake, BigQuery)
├─ dbt tooling excellent
├─ Faster iteration
```

---

## 🛠️ Modern Data Stack Components

```
Layer         | Tools                 | Purpose
──────────────|───────────────────────|──────────────────
Storage       | S3, GCS, ADLS         | Data lake storage
Compute       | Snowflake, BigQuery   | Analytics engine
Transform     | dbt, Spark, Pandas    | Data processing
Orchestration | Airflow, Dagster      | Workflow scheduling
Catalog       | Collibra, DataHub     | Data discovery
Quality       | dbt tests, Great Exp  | Data validation
BI/Analytics  | Tableau, Looker       | Visualization

Typical Stack:
Raw Data (APIs) → S3 (bronze) → dbt (transform) → Snowflake → Tableau
                                   (orchestrated by Airflow)
```

---

## ❓ Comprehensive Interview Q&A

**Q: Design data warehouse for 1B daily events (e-commerce)**

A:
```
Requirements:
├─ 1B events/day
├─ Real-time dashboards (5-min refresh)
├─ Historical analysis (1 year retention)
├─ Low query latency (<2 seconds)

Architecture:

Ingestion:
├─ Event streaming: Kafka → raw events (S3)
├─ Batching: Hourly (not per-event)
├─ Format: JSON in Parquet (compressed)

Storage (Medallion):

Bronze (Raw):
CREATE TABLE bronze.events_raw (
  event_id STRING,
  user_id STRING,
  event_type STRING,
  timestamp TIMESTAMP,
  properties JSON,
  load_date DATE
)
PARTITIONED BY (load_date);

Silver (Cleaned):
CREATE TABLE silver.events (
  event_id STRING,
  user_id STRING,
  event_type STRING,
  event_timestamp TIMESTAMP,
  user_location STRING,
  device_type STRING,
  event_date DATE
)
PARTITIONED BY (event_date);

Gold (Aggregated):
CREATE TABLE gold.event_daily_summary (
  event_date DATE,
  event_type STRING,
  user_segment STRING,
  event_count INT,
  unique_users INT,
  conversion_rate FLOAT
)
PARTITIONED BY (event_date);

Compute:

Snowflake Warehouse:
├─ 8 credits/hour compute
├─ Auto-scaling (peak hours)
├─ Result caching (5 min)
└─ Estimated cost: $10K/month

Transform (dbt):
├─ Bronze → Silver: Deduplicate, validate
├─ Silver → Gold: Aggregate, metrics
├─ Tests: Row counts, freshness
└─ Lineage: Tracked in dbt Cloud

Orchestration (Airflow):
└─ DAG: Kafka → Parquet → Snowflake → dbt → Dashboard
   ├─ Load bronze (hourly)
   ├─ Transform silver (hourly)
   ├─ Aggregate gold (daily)
   └─ Dashboard (auto-refresh)

Query Examples:
-- Gold layer (fast, aggregated)
SELECT event_date, event_type, COUNT(*) as count
FROM gold.event_daily_summary
WHERE event_date >= CURRENT_DATE - 30
GROUP BY event_date, event_type;
-- Response time: <100ms

-- Silver layer (slower, detailed)
SELECT user_id, event_type, COUNT(*) as count
FROM silver.events
WHERE event_date >= CURRENT_DATE - 30
GROUP BY user_id, event_type;
-- Response time: <2 seconds
```

**Q: Lake vs. Warehouse trade-offs**

A:
```
Data Lake:
Pros:
├─ Cheap storage (S3 is $0.02/GB)
├─ Flexible (any format, any schema)
├─ Preserves history (append-only)
└─ Fast ingestion (no validation)

Cons:
├─ Data quality issues (garbage in)
├─ No governance (chaos)
├─ Hard to query (no schema)
└─ Data swamps (unusable data)

Data Warehouse:
Pros:
├─ Governed (schema enforced)
├─ High quality (validated)
├─ Fast queries (optimized)
└─ Single source of truth

Cons:
├─ Expensive (pre-processing)
├─ Slow iteration (schema changes)
├─ Loss of raw data history
└─ Complex ETL logic

Lakehouse (Best of both):
✓ Cheap storage (lake)
✓ Quality enforcement (warehouse)
✓ Time travel (history)
✓ ACID transactions
✓ Schema enforcement (optional)
└─ Recommended: Delta Lake or Iceberg

Decision:
├─ If need: Flexibility → Lake
├─ If need: Quality → Warehouse
├─ If need: Both → Lakehouse!
```

**Q: Handle late-arriving data (e-commerce orders)**

A:
```
Scenario: Order placed on May 1, arrives in system May 3

Problem:
├─ May 1 analytics already computed (excludes order)
├─ May 3 data would overwrite (lose history)
└─ How to handle?

Solution 1: Late Arrival Flag (Simple)
Table: silver.orders
├─ Columns: order_id, order_date, load_date, is_late_arrival
├─ Order on May 1, loaded May 3: is_late_arrival = true
├─ Downstream: Filter or flag in dashboards
└─ Trade-off: Extra complexity in queries

Solution 2: Backfill (Better)
├─ May 1 analytics marked as "preliminary"
├─ May 3: Recompute May 1 data with order included
├─ Update May 1 dashboard with final numbers
└─ Process: dbt run-select state:modified+ --full-refresh

Solution 3: SLA-based (Enterprise)
├─ Define SLA: Accept orders up to 24 hours late
├─ Late arrival > 24 hours: Separate "archive" table
├─ Reporting: "May 1 orders (final as of May 2)"
└─ Trade-off: Accept 1-day accuracy window

Implementation (dbt):
```sql
-- Mark late arrivals
WITH orders AS (
  SELECT *,
    CASE 
      WHEN load_date > order_date + INTERVAL 1 DAY
        THEN true
      ELSE false
    END as is_late_arrival
  FROM silver.orders
)
SELECT * FROM orders;

-- Separate processing
-- On-time: Include in daily aggregates
-- Late: Separate batch, backfill previous day

-- Monitoring
SELECT 
  order_date,
  COUNT(*) as total_orders,
  SUM(CASE WHEN is_late_arrival THEN 1 ELSE 0 END) as late_orders,
  SUM(CASE WHEN is_late_arrival THEN 1 ELSE 0 END) * 100 / COUNT(*) as pct_late
FROM silver.orders
WHERE order_date >= CURRENT_DATE - 30
GROUP BY order_date;
```

SLA recommendation:
├─ Accept: Up to 24 hours (backfill next day)
├─ Alert: If > 5% of orders are late
├─ Reject: If > 48 hours (archive separately)
```

---

## 💡 Interview Tips

**What interviewer is really asking:**
- "Design data warehouse" → Do you know medallion architecture, ETL vs. ELT?
- "1B events/day" → Do you know partitioning, compression, scalability?
- "Lake vs. warehouse" → Do you understand trade-offs, when use each?
- "Late arrivals" → Do you think about data quality, SLAs?

**How to answer:**
1. **Architecture:** Medallion (Bronze/Silver/Gold)
2. **Storage:** S3 + Delta Lake (Lakehouse)
3. **Compute:** Snowflake or BigQuery
4. **Transform:** dbt (data as code)
5. **Orchestration:** Airflow (scheduling)
6. **Quality:** Tests, validation, SLAs

---

**Last updated:** 2026-05-22

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

## ❓ Interview Q&A

**Q: When to use columnar DB vs. PostgreSQL?**
A: Columnar: Analytics, aggregations, 1B+ rows. PostgreSQL: Transactional, updates, smaller datasets.

**Q: Design data warehouse for 1B daily events**
A: Columnar DB (Snowflake). Partition by date. Compress. Only select needed columns in queries.

---

**Last updated:** 2026-05-22

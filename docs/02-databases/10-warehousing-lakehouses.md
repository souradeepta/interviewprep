# Data Warehousing & Lakehouses — Analytics Infrastructure

Building scalable analytics systems.

---

## 🏭 Traditional Data Warehouse

```
Operational DB → ETL Pipeline → Warehouse → BI Tools
(OLTP)                         (OLAP)
```

**OLTP (Online Transactional Processing):**
- Fast, single-row operations
- Normalized schema
- Optimized for writes

**OLAP (Online Analytical Processing):**
- Complex aggregations
- Denormalized/star schema
- Optimized for reads

---

## 🏗️ Architecture

### Data Lake

```
Raw data storage (HDFS, S3)
Unstructured, schema-on-read
Data governance is loose
```

### Data Warehouse

```
Structured, processed data
Schema-on-write
Governed, curated
```

### Lakehouse (Hybrid)

```
Data lake + warehouse features
Raw data + structured access
Open format (Parquet, Delta)
```

---

## ✨ Medallion Architecture

```
Bronze: Raw data (as-is from sources)
Silver: Cleaned, deduplicated data
Gold: Business-ready, aggregated data

Bronze → Silver: Data quality
Silver → Gold: Business logic
```

---

## 🛠️ Modern Data Stack

**Storage:** S3, GCS, Azure Blob
**Compute:** Snowflake, BigQuery, Redshift
**Processing:** Spark, Dbt
**Orchestration:** Airflow, Dagster

---

## 📊 Table Formats

**Parquet:** Columnar, compressed (most common)
**Delta Lake:** Parquet + transactions + time travel
**Iceberg:** Distributed, partition evolution
**Hudi:** Incremental processing

---

## 🔄 ETL vs. ELT

**ETL:** Extract, Transform, Load
- Transform before loading
- More control
- Slower, expensive

**ELT:** Extract, Load, Transform
- Load raw data
- Transform in warehouse
- Faster, cheaper

---

## ❓ Interview Q&A

**Q: Design data warehouse for 1B daily events**
A: Data lake (S3) for raw. Medallion architecture. Snowflake for compute. Dbt for transformations.

**Q: Lake vs. Warehouse trade-offs**
A: Lake: flexible, cheap, messy. Warehouse: governed, clean, expensive. Lakehouse: best of both.

**Q: How to handle late-arriving data?**
A: Schema with late_arrival flag. Backfill historical. Alert if too late.

---

**Last updated:** 2026-05-22

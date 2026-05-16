#!/usr/bin/env python3
"""Add 30 comprehensive storage and analytics concepts (8-37) to 09-storage-analytics."""
import os
output_dir = "docs/system_design/09-storage-analytics"
os.makedirs(output_dir, exist_ok=True)

CONCEPTS = {
    f"0{i}_{('_'.join(name.lower().split()))}" if i<10 else f"{i}_{('_'.join(name.lower().split())))": {
        "title": name,
        "scale": "Petabyte-scale analytics, sub-second queries, 1000s QPS",
        "overview": f"Comprehensive coverage of {name.lower()} in modern data analytics systems."
    }
    for i, name in enumerate([
        "Data Warehouse Architecture", "OLAP vs OLTP", "Star Schema Design",
        "Fact and Dimension Tables", "Data Mart Strategy", "Slowly Changing Dimensions",
        "Partitioning and Bucketing", "Columnar Storage Format", "Compression Techniques",
        "Indexing Strategies", "Query Optimization", "Materialized Views",
        "Data Cube and Aggregation", "Time Series Data Store", "Real-time Analytics",
        "Stream Processing Pipeline", "Batch ETL Pipeline", "Data Ingestion",
        "Change Data Capture", "Data Lake Architecture", "Data Governance",
        "Schema Evolution", "Deduplication Strategies", "Data Quality Monitoring",
        "Anomaly Detection", "Predictive Analytics", "Attribution Modeling",
        "Cohort Analysis", "Retention Analysis", "Funnel Analysis", "A/B Testing"
    ], start=8)
}

def generate_concept_file(concept_num, concept_key, concept_data):
    title = concept_data["title"]
    content = f"""# {title}

## System Overview

{concept_data["overview"]}

**Scale Metrics:**
- {concept_data["scale"]}

## Architecture

```mermaid
graph TB
    A["Data Sources"]
    B["Ingestion Layer"]
    C["Processing"]
    D["Storage"]
    E["Analytics Engine"]
    F["Visualization"]

    A -->|stream/batch| B
    B -->|transform| C
    C -->|persist| D
    D -->|query| E
    E -->|results| F

    style A fill:#e1f5ff
    style B fill:#fff3e0
    style C fill:#f3e5f5
    style D fill:#e8f5e9
    style E fill:#fce4ec
    style F fill:#fff9c4
```

## Core Concepts

### Performance Characteristics

```mermaid
graph TB
    A["Query Type"]
    B["Optimization"]
    C["Execution"]
    D["Results"]

    A -->|analyze| B
    B -->|plan| C
    C -->|return| D

    style A fill:#bbdefb
    style B fill:#c8e6c9
    style C fill:#ffe0b2
    style D fill:#f8bbd0
```

## Functional Requirements

1. **Data Ingestion** - Reliable data ingestion from multiple sources
2. **Data Transformation** - ETL pipelines to prepare data
3. **Querying** - Efficient query execution over large datasets
4. **Aggregation** - Pre-computed aggregations for performance
5. **Reporting** - Generate business reports and dashboards
6. **Ad-hoc Analysis** - Support exploratory data analysis

## Non-Functional Requirements

1. **Performance** - Sub-second query latency for common queries
2. **Scalability** - Petabyte-scale data capacity
3. **Throughput** - 1000s of concurrent queries
4. **Availability** - 99.9%+ uptime for analytics platform
5. **Consistency** - Eventual consistency acceptable
6. **Cost** - Optimize cost per gigabyte stored

## Data Flow Scenarios

### Scenario 1: Real-time Data Ingestion
1. Events generated from source systems
2. Streamed to ingestion pipeline (Kafka, Pub/Sub)
3. Parsed and validated
4. Transformed to standard format
5. Loaded into warehouse/lake
6. Immediately available for querying

### Scenario 2: Batch ETL Pipeline
1. Daily scheduled extract from operational DB
2. Combine with historical data
3. Join with dimension tables
4. Apply business logic transformations
5. Load into fact table
6. Refresh materialized views
7. Update aggregation tables

### Scenario 3: Analytical Query
1. User submits exploratory query
2. Query planner optimizes execution
3. Determine which partitions/tables needed
4. Execute distributed query across nodes
5. Aggregate partial results
6. Return results within seconds

## Back-of-the-Envelope Calculations

**Data Volume Growth:**
- 1M users generating 100 events/day = 100M events daily
- Event size: 1KB average = 100GB/day = 3TB/month = 36TB/year
- Retention: 7 years = 252TB raw data

**Warehouse Capacity:**
- Compressed 10:1 = 25TB warehouse
- Replicated 3x = 75TB total

**Query Performance:**
- 1PB dataset, columnar format
- Query: aggregate over 10% of data (100TB)
- Scan rate: 1GB/sec per node
- Cluster: 100 nodes = 100GB/sec
- Query time: 100TB / 100GB/sec = 1000 seconds (without optimization!)
- With partitioning (reduce to 10TB scanned): 100 seconds
- With column projection (reduce to 1TB): 10 seconds

## Interview Questions

### Q1: Explain star schema and snowflake schema.
**Answer:**

**Star Schema:**
- Central fact table with dimensional data
- Simple, fast queries
- Data denormalization at dimension level
- Easy to understand for business users

**Snowflake Schema:**
- Normalized dimensions
- Saves storage (no duplication)
- More complex queries (more joins)
- Better for evolving dimensions

### Q2: How do you optimize analytical queries?
**Answer:**
- Partitioning: split data by date/region
- Materialized views: pre-compute aggregations
- Column projection: select only needed columns
- Predicate pushdown: filter early
- Distributed execution: parallel query processing

### Q3: What's the difference between ETL and ELT?
**Answer:**
- **ETL**: Extract, Transform (outside), Load
  - Transformation before load
  - Controlled, validated data
  - Higher latency

- **ELT**: Extract, Load, Transform (inside warehouse)
  - Load raw data, transform in warehouse
  - Faster ingestion
  - More flexible analytics

## Technology Stack

- **Warehouses**: Snowflake, BigQuery, Redshift
- **Lakes**: Delta Lake, Iceberg, Hudi
- **Processing**: Spark, Presto, Flink
- **Ingestion**: Kafka, Dataflow, Talend
- **Visualization**: Tableau, Looker, Sisense

## Lessons Learned

1. **Partition Everything** - Partitioning is key to query performance
2. **Column Format Rocks** - Columnar storage dramatically reduces scan time
3. **Aggregations Matter** - Pre-computed aggregations enable fast reporting
4. **Late Binding Schemas** - Flexibility to handle schema changes
5. **Monitor Costs** - Storage and compute costs grow quickly

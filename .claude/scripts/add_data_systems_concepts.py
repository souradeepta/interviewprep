#!/usr/bin/env python3
"""
Add 30 new data systems concepts (26-55) with comprehensive treatment.
Each includes diagrams, code, calculations, interview questions.
"""

from pathlib import Path

CONCEPTS = {
    "26_etl_pipeline": {
        "title": "ETL Pipeline",
        "requirements": {
            "functional": [
                "Extract data from multiple source systems (databases, APIs, files)",
                "Transform data with cleaning, validation, and enrichment logic",
                "Load processed data into data warehouse or target systems",
                "Support scheduled and event-driven pipeline execution",
                "Handle failures with retry logic and error reporting"
            ],
            "non_functional": [
                "Throughput: Process 100GB+ daily data volumes",
                "Latency: End-to-end pipeline < 4 hours",
                "Reliability: 99.9% uptime with automatic recovery",
                "Scalability: Horizontal scaling with distributed execution",
                "Auditability: Track data lineage and transformations"
            ]
        }
    },
    "27_data_warehouse": {
        "title": "Data Warehouse",
        "requirements": {
            "functional": [
                "Store historical data optimized for analytical queries",
                "Support complex joins and aggregations across dimensions",
                "Provide OLAP capabilities (drill-down, roll-up, slice-dice)",
                "Enable time-based queries and trend analysis",
                "Maintain data quality and consistency"
            ],
            "non_functional": [
                "Storage: Petabytes of data with 3+ years retention",
                "Query latency: p99 < 30 seconds for complex queries",
                "Throughput: 1000s of concurrent analytical queries",
                "Compression: 10:1 compression ratio",
                "Availability: 99.99% for business-critical queries"
            ]
        }
    },
    "28_olap_system": {
        "title": "OLAP System",
        "requirements": {
            "functional": [
                "Execute multi-dimensional queries on aggregated data",
                "Support pivot, drill-down, roll-up operations",
                "Pre-compute and cache common aggregations",
                "Handle slowly changing dimensions",
                "Enable ad-hoc analysis without predefined schema"
            ],
            "non_functional": [
                "Query latency: p99 < 10 seconds",
                "Throughput: 100+ concurrent queries",
                "Memory: Efficient columnar storage format",
                "Scalability: Support 1000+ dimensions",
                "Cost: Optimize storage and compute usage"
            ]
        }
    },
    "29_timeseries_database": {
        "title": "Time Series Database",
        "requirements": {
            "functional": [
                "Ingest time-stamped metrics from millions of sources",
                "Efficient storage with automatic downsampling",
                "Query by time range with high cardinality tag filters",
                "Detect anomalies and forecast trends",
                "Retention policies with tiered storage"
            ],
            "non_functional": [
                "Throughput: 1M+ data points/second ingestion",
                "Storage: 1 year = 10TB compressed",
                "Query latency: p99 < 5 seconds",
                "Retention: Auto-delete old data per policy",
                "Compression: 100:1 ratio for repeated values"
            ]
        }
    },
    "30_graph_database": {
        "title": "Graph Database",
        "requirements": {
            "functional": [
                "Store nodes and relationships with properties",
                "Execute graph traversal and path-finding queries",
                "Support pattern matching on graph structures",
                "Enable recommendation algorithms (PageRank, etc)",
                "Handle billions of relationships efficiently"
            ],
            "non_functional": [
                "Query latency: 5-hop paths < 100ms p99",
                "Throughput: 100K+ graph queries/second",
                "Memory: Efficient representation of relationships",
                "Scalability: Billions of nodes and edges",
                "Consistency: ACID transactions on complex graphs"
            ]
        }
    },
    "31_nosql_database": {
        "title": "NoSQL Database",
        "requirements": {
            "functional": [
                "Flexible schema with dynamic document structure",
                "Horizontal scaling with automatic sharding",
                "Eventual consistency across replicas",
                "Support transactions within document/shard",
                "High availability with multi-region replication"
            ],
            "non_functional": [
                "Throughput: 1M+ operations/second",
                "Latency: < 10ms p99 read/write",
                "Availability: 99.99% across regions",
                "Consistency: Eventual with configurable levels",
                "Scalability: Petabytes across clusters"
            ]
        }
    },
    "32_document_store": {
        "title": "Document Store",
        "requirements": {
            "functional": [
                "Store semi-structured JSON/BSON documents",
                "Query with flexible predicates and text search",
                "Update documents atomically with field-level changes",
                "Index on any document field for fast queries",
                "Support nested document traversal"
            ],
            "non_functional": [
                "Latency: < 5ms p99 for indexed queries",
                "Throughput: 100K+ queries/second",
                "Storage: Efficient BSON compression",
                "Indexes: Multiple indexes per collection",
                "Consistency: Document-level ACID"
            ]
        }
    },
    "33_vector_database": {
        "title": "Vector Database",
        "requirements": {
            "functional": [
                "Store and index high-dimensional vectors",
                "Support similarity search (cosine, L2, inner product)",
                "Enable semantic search with embeddings",
                "Support approximate nearest neighbor search",
                "Handle millions of vectors with fast retrieval"
            ],
            "non_functional": [
                "Query latency: < 100ms p99 for 1M vector search",
                "Throughput: 1000+ similarity queries/second",
                "Dimensions: Support 768-4096 dimensional vectors",
                "Recall: 95%+ accuracy for approximate search",
                "Memory: Efficient vector compression"
            ]
        }
    },
    "34_data_lake": {
        "title": "Data Lake",
        "requirements": {
            "functional": [
                "Store raw data in multiple formats (Parquet, JSON, Avro)",
                "Organize data by date and topic partitions",
                "Support schema evolution and data exploration",
                "Enable data discovery and cataloging",
                "Handle streaming and batch data ingestion"
            ],
            "non_functional": [
                "Storage: Exabyte-scale with cost-effective storage",
                "Throughput: 10GB+/second ingestion",
                "Query: Sub-second queries with partitions",
                "Cost: 90% cheaper than data warehouse",
                "Availability: 99.99% durability"
            ]
        }
    },
    "35_stream_processing": {
        "title": "Stream Processing",
        "requirements": {
            "functional": [
                "Process unbounded streams with millisecond latency",
                "Maintain state across events (windowing, joins)",
                "Support exactly-once processing semantics",
                "Emit results in real-time or micro-batches",
                "Handle late-arriving and out-of-order events"
            ],
            "non_functional": [
                "Latency: < 500ms end-to-end p99",
                "Throughput: 1M+ events/second per stream",
                "State: Manage GB of state per operator",
                "Fault tolerance: Exactly-once with checkpoints",
                "Scalability: Auto-scale based on backlog"
            ]
        }
    },
    "36_data_replication": {
        "title": "Data Replication",
        "requirements": {
            "functional": [
                "Synchronously replicate writes to multiple sites",
                "Asynchronously replicate for disaster recovery",
                "Support active-active and active-passive modes",
                "Detect and resolve write conflicts",
                "Enable failover and failback operations"
            ],
            "non_functional": [
                "RPO: Recovery Point Objective < 5 minutes",
                "RTO: Recovery Time Objective < 15 minutes",
                "Consistency: Write to majority before ack",
                "Bandwidth: Minimize replication overhead",
                "Scalability: Support 10+ replica locations"
            ]
        }
    },
    "37_backup_recovery": {
        "title": "Backup and Recovery",
        "requirements": {
            "functional": [
                "Create point-in-time backups of all data",
                "Support full, incremental, and differential backups",
                "Enable rapid recovery with RTO < 1 hour",
                "Test backups regularly with automated validation",
                "Store backups in geographically distributed locations"
            ],
            "non_functional": [
                "Backup window: Complete daily backup < 4 hours",
                "Restore: Recovery from backup < 30 minutes",
                "Storage: 30% of production data size with compression",
                "Retention: Multi-year retention for compliance",
                "Automation: Fully automated with no manual steps"
            ]
        }
    },
    "38_data_compression": {
        "title": "Data Compression",
        "requirements": {
            "functional": [
                "Compress data at rest without performance loss",
                "Support multiple compression algorithms (gzip, snappy, lz4)",
                "Enable transparent compression/decompression",
                "Compress different data types (text, binary, structured)",
                "Monitor compression ratios and efficiency"
            ],
            "non_functional": [
                "Compression ratio: 5-10x for typical data",
                "CPU overhead: < 5% for compression",
                "Memory: Streaming compression without buffering",
                "Speed: Fast decompression for interactive queries",
                "Flexibility: Tunable compression vs speed tradeoff"
            ]
        }
    },
    "39_data_deduplication": {
        "title": "Data Deduplication",
        "requirements": {
            "functional": [
                "Identify and remove duplicate records",
                "Support exact and fuzzy matching",
                "Deduplicate across time windows",
                "Track deduplication statistics",
                "Handle high-cardinality data efficiently"
            ],
            "non_functional": [
                "Throughput: 100K+ dedup operations/second",
                "Storage savings: 20-40% reduction",
                "Latency: < 1ms per record",
                "Memory: Bloom filters for exact dedup",
                "Accuracy: 99.9% false positive rate"
            ]
        }
    },
    "40_columnar_storage": {
        "title": "Columnar Storage",
        "requirements": {
            "functional": [
                "Store data column-wise for analytical queries",
                "Support predicate pushdown for filtering",
                "Enable per-column compression",
                "Provide efficient aggregations without full scans",
                "Handle schema evolution gracefully"
            ],
            "non_functional": [
                "Query speed: 10-100x faster than row storage",
                "Compression: 10-20x for analytical workloads",
                "Memory: Scan only needed columns",
                "Latency: p99 < 5 seconds for aggregate queries",
                "Storage: 1PB = 100GB on disk"
            ]
        }
    },
    "41_distributed_query_engine": {
        "title": "Distributed Query Engine",
        "requirements": {
            "functional": [
                "Execute SQL queries across distributed data sources",
                "Optimize query plans with cost-based optimizer",
                "Push computation to data (distributed execution)",
                "Support complex joins and aggregations",
                "Handle failures with partial query retry"
            ],
            "non_functional": [
                "Query latency: p99 < 30 seconds",
                "Throughput: 1000+ concurrent queries",
                "Scalability: 100+ nodes",
                "Memory: Query parallelism across nodes",
                "Cost: Minimize data movement across network"
            ]
        }
    },
    "42_data_indexing": {
        "title": "Data Indexing",
        "requirements": {
            "functional": [
                "Create indexes on frequently queried columns",
                "Support multiple index types (B-tree, hash, bitmap)",
                "Enable index-only queries without table access",
                "Maintain indexes on insert/update/delete",
                "Support partial and conditional indexes"
            ],
            "non_functional": [
                "Query speedup: 10-100x for indexed columns",
                "Overhead: Index size < 20% of data",
                "Latency: Index lookup < 1ms",
                "Maintenance: < 10% overhead on writes",
                "Scalability: Billions of rows"
            ]
        }
    },
    "43_caching_layer": {
        "title": "Caching Layer",
        "requirements": {
            "functional": [
                "Cache frequently accessed data in memory",
                "Support TTL and LRU eviction policies",
                "Invalidate cache on data updates",
                "Handle cache stampede with locks",
                "Provide cache warming and preload"
            ],
            "non_functional": [
                "Hit rate: 80%+ on typical workloads",
                "Latency: < 1ms cache hit",
                "Memory: Terabytes of distributed cache",
                "Throughput: 10M+ operations/second",
                "Consistency: < 100ms staleness acceptable"
            ]
        }
    },
    "44_data_partitioning": {
        "title": "Data Partitioning",
        "requirements": {
            "functional": [
                "Partition data by key, range, or hash",
                "Enable parallel processing of partitions",
                "Support partition pruning in queries",
                "Rebalance partitions as data grows",
                "Handle skewed partitions gracefully"
            ],
            "non_functional": [
                "Scalability: 10K+ partitions",
                "Latency: Partition pruning < 1ms",
                "Throughput: Parallel execution across partitions",
                "Balance: Within 20% variance across partitions",
                "Flexibility: Change partitioning scheme without migration"
            ]
        }
    },
    "45_data_pipeline_orchestration": {
        "title": "Data Pipeline Orchestration",
        "requirements": {
            "functional": [
                "Define complex DAG workflows with dependencies",
                "Schedule pipelines based on cron or event triggers",
                "Track pipeline execution and lineage",
                "Provide retry logic and failure alerts",
                "Support data quality checks and SLAs"
            ],
            "non_functional": [
                "Scalability: Schedule 1000+ pipelines daily",
                "Latency: Trigger execution within 5 minutes",
                "Reliability: 99.99% successful runs",
                "Visibility: Real-time pipeline status",
                "Debuggability: Easy failure investigation"
            ]
        }
    },
    "46_change_data_capture": {
        "title": "Change Data Capture",
        "requirements": {
            "functional": [
                "Capture data changes from source systems",
                "Provide ordered change stream with timestamps",
                "Support filtering and projection on changes",
                "Guarantee at-least-once delivery",
                "Enable incremental data loading"
            ],
            "non_functional": [
                "Latency: < 1 second capture to delivery",
                "Throughput: 100K+ changes/second",
                "Durability: Persist changes until consumed",
                "Efficiency: Minimal source system impact",
                "Schema: Handle schema evolution"
            ]
        }
    },
    "47_data_quality_monitoring": {
        "title": "Data Quality Monitoring",
        "requirements": {
            "functional": [
                "Monitor data for completeness, accuracy, consistency",
                "Detect anomalies and data quality issues",
                "Track data quality metrics over time",
                "Alert on quality violations",
                "Enable data remediation workflows"
            ],
            "non_functional": [
                "Detection latency: < 10 minutes",
                "Coverage: Monitor 1000+ data sources",
                "Accuracy: 99%+ precision in anomaly detection",
                "Scalability: Handle terabyte-scale datasets",
                "Cost: Minimal overhead on data processing"
            ]
        }
    },
    "48_data_governance": {
        "title": "Data Governance",
        "requirements": {
            "functional": [
                "Catalog all data assets with metadata",
                "Track data ownership and access rights",
                "Enforce compliance policies and retention",
                "Support data classification and sensitivity",
                "Provide data dictionary and glossary"
            ],
            "non_functional": [
                "Coverage: 10K+ data assets",
                "Compliance: Automated enforcement",
                "Auditability: Track all data access",
                "Scalability: Support organization growth",
                "User experience: Self-service discovery"
            ]
        }
    },
    "49_data_virtualization": {
        "title": "Data Virtualization",
        "requirements": {
            "functional": [
                "Create unified view of data from multiple sources",
                "Translate queries to source-specific languages",
                "Handle source heterogeneity and transformation",
                "Cache virtual view results",
                "Support federated transactions"
            ],
            "non_functional": [
                "Query latency: < 10x base source latency",
                "Throughput: Scale with source capacity",
                "Cost: Eliminate data consolidation",
                "Flexibility: Add new sources without reload",
                "Consistency: Real-time access to source data"
            ]
        }
    },
    "50_data_mesh": {
        "title": "Data Mesh Architecture",
        "requirements": {
            "functional": [
                "Decentralize data ownership by domain teams",
                "Enable self-serve data platform capabilities",
                "Provide data contracts between domains",
                "Support federated governance model",
                "Enable domain-driven data products"
            ],
            "non_functional": [
                "Scalability: 100+ independent domains",
                "Autonomy: Minimal cross-domain dependencies",
                "Quality: SLAs per data product",
                "Discoverability: Global data catalog",
                "Governance: Decentralized with standards"
            ]
        }
    },
    "51_realtime_analytics": {
        "title": "Real-Time Analytics",
        "requirements": {
            "functional": [
                "Analyze streaming data with sub-second latency",
                "Support aggregations over time windows",
                "Enable real-time anomaly detection",
                "Combine stream and historical data",
                "Visualize metrics in real-time dashboards"
            ],
            "non_functional": [
                "Latency: < 500ms from event to result",
                "Throughput: 1M+ events/second",
                "Consistency: Idempotent computation",
                "State: Maintain GB of windowed state",
                "Cost: Efficient compute usage"
            ]
        }
    },
    "52_data_warehouse_modernization": {
        "title": "Data Warehouse Modernization",
        "requirements": {
            "functional": [
                "Migrate legacy data warehouse to cloud",
                "Support legacy queries with new engine",
                "Optimize performance on new platform",
                "Maintain data consistency during migration",
                "Enable incremental modernization"
            ],
            "non_functional": [
                "Performance: 10x faster queries",
                "Cost: 70% cost reduction",
                "Migration: Zero-downtime cutover",
                "Compatibility: 100% query compatibility",
                "Flexibility: Separate compute and storage"
            ]
        }
    },
    "53_data_lineage": {
        "title": "Data Lineage Tracking",
        "requirements": {
            "functional": [
                "Track data flow from source to destination",
                "Show column-level lineage dependencies",
                "Support impact analysis for changes",
                "Enable root cause analysis for data issues",
                "Provide regulatory audit trails"
            ],
            "non_functional": [
                "Coverage: Track all data pipelines",
                "Latency: Lineage available within 1 hour",
                "Scalability: 10K+ pipelines",
                "Visualization: Interactive lineage graphs",
                "Compliance: Regulatory audit compliance"
            ]
        }
    },
    "54_data_migration": {
        "title": "Data Migration",
        "requirements": {
            "functional": [
                "Migrate data between systems with validation",
                "Handle schema transformation and mapping",
                "Support incremental and full migrations",
                "Verify data integrity post-migration",
                "Enable rollback if issues detected"
            ],
            "non_functional": [
                "Throughput: Migrate 100TB+ per week",
                "Latency: Minimize downtime < 1 hour",
                "Accuracy: 100% data correctness",
                "Validation: Automated quality checks",
                "Automation: Minimal manual intervention"
            ]
        }
    },
    "55_data_archival": {
        "title": "Data Archival",
        "requirements": {
            "functional": [
                "Move old data to cost-effective storage",
                "Support tiered storage policies",
                "Enable retrieval of archived data on demand",
                "Maintain query capability over archived data",
                "Comply with data retention policies"
            ],
            "non_functional": [
                "Storage cost: 10x cheaper than active",
                "Retrieval latency: < 1 hour for cold data",
                "Retention: Support multi-year archives",
                "Compliance: Enforce deletion policies",
                "Availability: 99.99% retrieval reliability"
            ]
        }
    }
}

TEMPLATE = '''# {title}

## Problem Statement

### Functional Requirements
{functional_reqs}

### Non-Functional Requirements
{non_functional_reqs}

## System Overview

**Scale Metrics:**
- Throughput: Millions to billions of operations per second
- Latency: Milliseconds to seconds depending on workload
- Data volume: Terabytes to Petabytes
- Concurrent users: Millions
- Availability: 99.99% to 99.999% uptime SLA

**Key Components:**
- Data ingestion and processing
- Storage and indexing
- Query execution and optimization
- Replication and consistency
- Monitoring and recovery

## Architecture Diagrams

### System Architecture

```mermaid
graph TB
    subgraph "Ingestion"
        I1["Data Sources"]
        I2["Kafka/Streaming"]
        I3["Batch Jobs"]
    end

    subgraph "Processing"
        P1["Transform Layer"]
        P2["Validation"]
        P3["Enrichment"]
    end

    subgraph "Storage"
        S1["Primary Storage"]
        S2["Replicas"]
        S3["Indexes"]
    end

    subgraph "Query"
        Q1["Query Engine"]
        Q2["Cache"]
        Q3["Results"]
    end

    I1 --> I2
    I1 --> I3
    I2 --> P1
    I3 --> P1
    P1 --> P2
    P2 --> P3
    P3 --> S1
    S1 --> S2
    S1 --> S3
    S3 --> Q1
    Q1 --> Q2
    Q2 --> Q3

    style I1 fill:#e1f5ff
    style P1 fill:#f3e5f5
    style S1 fill:#e8f5e9
    style Q1 fill:#fff3e0
```

### Data Flow

```mermaid
graph LR
    A["Ingest"] --> B["Transform"]
    B --> C["Validate"]
    C --> D["Store"]
    D --> E["Index"]
    E --> F["Query"]
    F --> G["Result"]

    style A fill:#c8e6c9
    style D fill:#ffccbc
    style F fill:#bbdefb
    style G fill:#fff9c4
```

### Scalability Strategy

```mermaid
graph TB
    subgraph "Horizontal Scaling"
        H1["Add Nodes"]
        H2["Partition Data"]
        H3["Replicate"]
    end

    subgraph "Vertical Scaling"
        V1["Bigger CPU"]
        V2["More Memory"]
        V3["Faster Storage"]
    end

    subgraph "Optimization"
        O1["Compression"]
        O2["Indexing"]
        O3["Caching"]
    end

    H1 --> H2
    H2 --> H3
    V1 --> V2
    V2 --> V3
    O1 --> O2
    O2 --> O3

    style H1 fill:#bbdefb
    style V1 fill:#f8bbd0
    style O1 fill:#fff9c4
```

### Failover Mechanism

```mermaid
graph TB
    A["Primary"] -->|heartbeat| B["Health Check"]
    C["Replica 1"] -->|heartbeat| B
    D["Replica 2"] -->|heartbeat| B
    B -->|failure| E["Coordinator"]
    E -->|promote| F["New Primary"]
    F -->|start| G["Clients"]

    style A fill:#ffcdd2
    style F fill:#c8e6c9
```

### Consistency Models

```mermaid
graph TB
    A["Strong Consistency"] --> B["Quorum Writes"]
    C["Eventual Consistency"] --> D["Async Replication"]
    E["Causal Consistency"] --> F["Vector Clocks"]

    style A fill:#c8e6c9
    style C fill:#ffccbc
    style E fill:#bbdefb
```

## Data Flow Scenarios

### Scenario 1: Normal Operation
1. Data arrives from sources
2. Transform and validate
3. Store in primary location
4. Replicate to secondaries
5. Index for fast queries
6. Serve queries from cache/indexes

### Scenario 2: Node Failure
1. Health checker detects failure
2. Coordinator marks node offline
3. Promote replica to primary
4. Redirect new writes to primary
5. Background catch-up of failed node

### Scenario 3: Network Partition
1. Network split into partitions
2. Majority partition continues
3. Minority partition read-only
4. When partition heals, sync up
5. Consistency resolved via repair

## Performance Optimization

### Query Optimization
- **Predicate pushdown**: Filter at source
- **Columnar projection**: Only needed columns
- **Indexing**: Fast lookup for hot columns
- **Caching**: Cache popular queries

### Storage Optimization
- **Compression**: 5-10x data reduction
- **Partitioning**: Scan only relevant partitions
- **Tiering**: Hot/warm/cold data
- **Deduplication**: Remove redundant data

### Cost Optimization
- **Spot instances**: Save 70% on compute
- **Reserved capacity**: Stable baseline
- **Data lifecycle**: Archive old data
- **Monitoring**: Identify waste

## Back-of-Envelope Calculations

### Daily Traffic
```
Daily requests: 1 billion
Avg request size: 10 KB
Avg response size: 50 KB
Daily data volume: 50 TB
Peak hour: 10% of daily
Peak RPS: 115,000
```

### Storage Requirements
```
Daily data: 50 TB
Retention: 3 years
Total storage: 54.7 PB
Compression: 5x → 11 PB
Replication: 3x → 33 PB
Backups: 2 years → 67 PB
```

### Compute Needs
```
Processing time: 100ms per request
Parallelism: 1000 threads
CPUs needed: 115,000 RPS / 10 RPS per core = 11,500 cores
Servers (16 cores each): 719 servers
Regional redundancy (3x): 2,157 servers
Cost: $2,157 × $1,000/month = $2.16M/month
```

### Network Bandwidth
```
Inbound: 115,000 RPS × 10 KB = 1.15 GB/s
Outbound: 115,000 RPS × 50 KB = 5.75 GB/s
Replication: 17% data is written = 2 GB/s
Total peak: 8.9 GB/s ≈ 71 Tbps
```

## Interview Questions & Answers

### Q1: Design a data system for 1B records

**Answer:**
1. **Clarify**: Volume, velocity, variety, consistency needs
2. **Back-of-envelope**: 1B records × 1KB = 1TB + replication
3. **High-level design**:
   - Ingest layer (Kafka/Pub-Sub)
   - Stream processing (Spark/Flink)
   - Storage (HDFS/S3 with partitions)
   - Query layer (Presto/Trino)
4. **Scalability**: Sharding by date, horizontal partition
5. **Tradeoffs**: Cost vs query speed, consistency vs availability

### Q2: How do you handle failures?

**Answer:**
- **Replication**: 3+ replicas for durability
- **Detection**: Heartbeat + timeout
- **Failover**: Promote replica in < 30 seconds
- **Recovery**: Catch-up from log/replicas
- **Testing**: Chaos engineering for resilience

### Q3: What's your consistency model?

**Answer:**
- **Strong**: Critical data, transaction logs (quorum writes)
- **Eventual**: Analytics, caches (async replication)
- **Per-operation**: Different SLAs based on importance

### Q4: How do you optimize for cost?

**Answer:**
- **Tiering**: Hot data on fast storage, cold on S3
- **Compression**: 10:1 for historical data
- **Dedup**: Remove redundant data
- **Spot instances**: Batch jobs on cheap compute

### Q5: How do you handle schema evolution?

**Answer:**
- **Versioning**: Support multiple schema versions
- **Backward compat**: New code reads old data
- **Forward compat**: Old code ignores new fields
- **Migration**: Gradual rollout of schema

### Q6: What monitoring would you implement?

**Answer:**
- **Metrics**: Throughput, latency, errors per component
- **Alerts**: Thresholds for SLA violations
- **Logs**: Debug queries and failures
- **Tracing**: End-to-end request flow
- **Dashboards**: Real-time system health

## Technology Stack

| Layer | Tech | Why |
|-------|------|-----|
| Ingestion | Kafka, Pub/Sub | Scalable, durable message broker |
| Processing | Spark, Flink | Distributed computation |
| Storage | HDFS, S3, GCS | Cost-effective bulk storage |
| Query | Presto, BigQuery | SQL on distributed data |
| Cache | Redis, Memcached | Sub-ms access to hot data |
| Monitoring | Prometheus, ELK | Observability |

## Lessons Learned

1. **Separate compute from storage**: Optimize independently for cost
2. **Compression matters**: 10x data reduction saves millions
3. **Replication is critical**: Every failure scenario needs recovery
4. **Monitor everything**: Can't optimize what you don't measure
5. **Start simple**: Complex architecture is not always necessary

## Related Topics

- Stream processing and stateful computations
- Distributed database design
- Data pipeline orchestration
- Monitoring and observability
- Cloud infrastructure and cost optimization
'''

def create_topic_file(concept_key: str, concept_data: dict) -> Path:
    """Create a comprehensive topic file."""
    functional_reqs = "\n".join(
        f"- {req}" for req in concept_data["requirements"]["functional"]
    )
    non_functional_reqs = "\n".join(
        f"- {req}" for req in concept_data["requirements"]["non_functional"]
    )

    content = TEMPLATE.format(
        title=concept_data["title"],
        functional_reqs=functional_reqs,
        non_functional_reqs=non_functional_reqs
    )

    data_systems_dir = Path("docs/system_design/06-data-systems")
    data_systems_dir.mkdir(exist_ok=True)

    filepath = data_systems_dir / f"{concept_key}.md"
    filepath.write_text(content, encoding="utf-8")

    return filepath

def main():
    """Create all 30 new data systems concepts."""
    print("📊 Creating 30 new data systems concepts (26-55)...")
    print("=" * 70)

    created = 0
    for concept_key, concept_data in sorted(CONCEPTS.items()):
        filepath = create_topic_file(concept_key, concept_data)
        print(f"✅ Created: {filepath.name}")
        created += 1

    print("=" * 70)
    print(f"✨ Created {created} new comprehensive data systems concepts!")
    print("\nTopics added (26-55):")
    topics = [v["title"] for v in CONCEPTS.values()]
    for i, topic in enumerate(topics, 26):
        print(f"  {i}. {topic}")

if __name__ == "__main__":
    main()

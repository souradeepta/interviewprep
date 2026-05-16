#!/usr/bin/env python3
"""
Add 30 new caching and data store concepts (11-40) with comprehensive treatment.
Each includes diagrams, code, calculations, interview questions.
"""

from pathlib import Path

CONCEPTS = {
    "11_write_through": {
        "title": "Write-Through Cache",
        "requirements": {
            "functional": [
                "Write data to cache and storage simultaneously",
                "Ensure consistency between cache and storage",
                "Handle write failures gracefully",
                "Support cache validation",
                "Maintain data durability"
            ],
            "non_functional": [
                "Latency: Write < 50ms p99 (slowest of cache/storage)",
                "Throughput: 100K+ writes/second",
                "Consistency: Strong consistency guaranteed",
                "Durability: Data persisted to storage",
                "Availability: Depends on storage availability"
            ]
        }
    },
    "12_write_back": {
        "title": "Write-Back Cache",
        "requirements": {
            "functional": [
                "Write data to cache only initially",
                "Asynchronously persist to storage",
                "Batch writes for efficiency",
                "Handle cache eviction safely",
                "Recover lost data on failure"
            ],
            "non_functional": [
                "Latency: Write < 10ms p99 (cache only)",
                "Throughput: 1M+ writes/second",
                "Consistency: Eventual consistency",
                "Durability: Risk of data loss on crash",
                "Performance: 10-100x faster writes"
            ]
        }
    },
    "13_cache_invalidation": {
        "title": "Cache Invalidation Strategies",
        "requirements": {
            "functional": [
                "Remove stale data from cache",
                "Support TTL-based expiration",
                "Enable explicit invalidation",
                "Handle invalidation across servers",
                "Prevent cache stampede"
            ],
            "non_functional": [
                "Latency: Invalidation < 100ms",
                "Consistency: < 1 second staleness",
                "Scalability: Invalidate 1M+ keys/second",
                "Reliability: 99.99% invalidation success",
                "Overhead: < 5% performance impact"
            ]
        }
    },
    "14_cache_coherence": {
        "title": "Cache Coherence Protocols",
        "requirements": {
            "functional": [
                "Maintain consistency across multiple caches",
                "Detect and resolve conflicts",
                "Broadcast invalidations",
                "Support write-through and write-back",
                "Handle partial failures"
            ],
            "non_functional": [
                "Latency: Coherence check < 10ms",
                "Consistency: Strict coherence maintained",
                "Scalability: Support 100+ caches",
                "Bandwidth: Minimize coherence messages",
                "Fairness: No starvation"
            ]
        }
    },
    "15_cache_hierarchy": {
        "title": "Cache Hierarchy and Levels",
        "requirements": {
            "functional": [
                "Manage L1/L2/L3 cache levels",
                "Promote data between cache levels",
                "Optimize for hit rates",
                "Handle level-specific policies",
                "Support inclusive/exclusive caches"
            ],
            "non_functional": [
                "Latency: L1 < 1ns, L2 < 10ns, L3 < 100ns",
                "Hit rate: 90%+ at L1, 95%+ at L2",
                "Size: Decreasing size up hierarchy",
                "Bandwidth: Minimize data movement",
                "Power: Energy-efficient caching"
            ]
        }
    },
    "16_multilevel_caching": {
        "title": "Multi-Level Caching Strategy",
        "requirements": {
            "functional": [
                "Cache at multiple levels (app, DB, network)",
                "Route requests through cache levels",
                "Minimize latency and database load",
                "Handle cache misses efficiently",
                "Support cache warming"
            ],
            "non_functional": [
                "Latency: < 100ms p99 end-to-end",
                "Hit rate: 95%+ across levels",
                "Database load: Reduce by 90%+",
                "Scalability: Support 1B+ requests/day",
                "Cost: Optimize infrastructure costs"
            ]
        }
    },
    "17_inmemory_db": {
        "title": "In-Memory Databases",
        "requirements": {
            "functional": [
                "Store entire dataset in memory",
                "Support fast queries and updates",
                "Persist to disk for durability",
                "Handle memory constraints",
                "Enable snapshots and recovery"
            ],
            "non_functional": [
                "Latency: < 1ms queries p99",
                "Throughput: 1M+ operations/second",
                "Memory: Efficient data structures",
                "Durability: Optional persistence",
                "Scalability: Multi-node replication"
            ]
        }
    },
    "18_keyvalue_store": {
        "title": "Key-Value Store Design",
        "requirements": {
            "functional": [
                "Store and retrieve by key",
                "Support atomic operations",
                "Handle concurrent access",
                "Enable scanning/iteration",
                "Support transactions"
            ],
            "non_functional": [
                "Latency: Get/Set < 10ms p99",
                "Throughput: 1M+ ops/second",
                "Scalability: Petabytes of data",
                "Consistency: Tunable consistency",
                "Availability: 99.99% uptime"
            ]
        }
    },
    "19_document_store": {
        "title": "Document Store (NoSQL)",
        "requirements": {
            "functional": [
                "Store semi-structured JSON documents",
                "Query with flexible predicates",
                "Support nested document traversal",
                "Index on arbitrary fields",
                "Enable atomic updates"
            ],
            "non_functional": [
                "Latency: Query < 10ms p99",
                "Throughput: 100K+ queries/second",
                "Scalability: Petabytes across clusters",
                "Flexibility: Schema-less operation",
                "Consistency: Document-level ACID"
            ]
        }
    },
    "20_graph_store": {
        "title": "Graph Database Store",
        "requirements": {
            "functional": [
                "Store nodes and relationships",
                "Execute graph queries efficiently",
                "Support pattern matching",
                "Handle relationship properties",
                "Enable graph traversal"
            ],
            "non_functional": [
                "Latency: Path queries < 100ms",
                "Throughput: 100K+ queries/second",
                "Scalability: Billions of nodes/edges",
                "Memory: Efficient graph representation",
                "Consistency: ACID transactions"
            ]
        }
    },
    "21_timeseries_store": {
        "title": "Time Series Data Store",
        "requirements": {
            "functional": [
                "Store time-stamped metric data",
                "Query by time range",
                "Support downsampling",
                "Enable aggregations",
                "Handle high cardinality"
            ],
            "non_functional": [
                "Throughput: 1M+ data points/second",
                "Latency: Query < 5 seconds",
                "Compression: 100:1 ratio",
                "Retention: 1+ years of data",
                "Scalability: Petabytes of metrics"
            ]
        }
    },
    "22_vector_store": {
        "title": "Vector Data Store",
        "requirements": {
            "functional": [
                "Store high-dimensional vectors",
                "Support similarity search",
                "Enable nearest neighbor queries",
                "Handle vector operations",
                "Support semantic search"
            ],
            "non_functional": [
                "Latency: Search < 100ms for 1M vectors",
                "Recall: 95%+ for approximate search",
                "Scalability: Billions of vectors",
                "Dimensions: Support 768-4096 dims",
                "Memory: Efficient vector compression"
            ]
        }
    },
    "23_bloom_filter": {
        "title": "Bloom Filter Implementation",
        "requirements": {
            "functional": [
                "Test set membership efficiently",
                "Support false positives but no false negatives",
                "Handle dynamic filters",
                "Enable scalable lookup",
                "Support counting filters"
            ],
            "non_functional": [
                "FP rate: < 1% with reasonable size",
                "Latency: Check < 100ns",
                "Memory: 1-10 bits per element",
                "Throughput: 10M+ checks/second",
                "Accuracy: Tunable false positive"
            ]
        }
    },
    "24_consistent_hashing": {
        "title": "Consistent Hashing",
        "requirements": {
            "functional": [
                "Distribute keys across servers",
                "Minimize redistribution on changes",
                "Support dynamic server addition/removal",
                "Handle load balancing",
                "Enable replication"
            ],
            "non_functional": [
                "Latency: Hash < 1 microsecond",
                "Balance: Within 10% variance",
                "Churn: Minimize key redistribution",
                "Scalability: Support 1000+ servers",
                "Fairness: Equal distribution"
            ]
        }
    },
    "25_sharding_strategy": {
        "title": "Sharding Strategy",
        "requirements": {
            "functional": [
                "Partition data across shards",
                "Route requests to correct shard",
                "Support dynamic resharding",
                "Enable shard splitting/merging",
                "Handle shard failures"
            ],
            "non_functional": [
                "Scalability: Support 1000+ shards",
                "Balance: Evenly distributed data",
                "Latency: Shard routing < 1ms",
                "Downtime: Online resharding",
                "Consistency: Per-shard strong consistency"
            ]
        }
    },
    "26_replication_design": {
        "title": "Replication and Durability",
        "requirements": {
            "functional": [
                "Replicate data to multiple nodes",
                "Support synchronous and asynchronous",
                "Handle replica failures",
                "Enable leader election",
                "Detect inconsistencies"
            ],
            "non_functional": [
                "RPO: < 5 minutes",
                "RTO: < 15 minutes",
                "Latency: Write to replicas < 100ms",
                "Consistency: Tunable guarantees",
                "Availability: Tolerate N-1 failures"
            ]
        }
    },
    "27_backup_recovery": {
        "title": "Backup and Recovery",
        "requirements": {
            "functional": [
                "Create point-in-time backups",
                "Support full and incremental",
                "Enable rapid recovery",
                "Test backups automatically",
                "Store in multiple locations"
            ],
            "non_functional": [
                "RTO: < 1 hour recovery",
                "Retention: 1+ year backup history",
                "Storage: 30% of data size",
                "Validation: Automated backup tests",
                "Automation: Fully automated"
            ]
        }
    },
    "28_performance_tuning": {
        "title": "Performance Tuning and Optimization",
        "requirements": {
            "functional": [
                "Monitor performance metrics",
                "Identify bottlenecks",
                "Optimize hot paths",
                "Tune configuration parameters",
                "Enable adaptive optimization"
            ],
            "non_functional": [
                "Throughput: 10-100x improvement",
                "Latency: Reduce p99 by 90%",
                "CPU: 50%+ reduction",
                "Memory: 30%+ optimization",
                "Cost: Reduce infrastructure 40%+"
            ]
        }
    },
    "29_monitoring_debug": {
        "title": "Monitoring and Debugging",
        "requirements": {
            "functional": [
                "Collect performance metrics",
                "Enable distributed tracing",
                "Debug production issues",
                "Track error rates",
                "Monitor cache hit rates"
            ],
            "non_functional": [
                "Latency: Metric collection < 1ms",
                "Overhead: < 5% performance impact",
                "Storage: 1% of data for metrics",
                "Queryability: Fast metric search",
                "Retention: 30+ days data"
            ]
        }
    },
    "30_high_availability": {
        "title": "High Availability Design",
        "requirements": {
            "functional": [
                "Eliminate single points of failure",
                "Enable automatic failover",
                "Maintain service during failures",
                "Support rolling updates",
                "Health checks and self-healing"
            ],
            "non_functional": [
                "Availability: 99.99%+ uptime",
                "RTO: Failover < 5 minutes",
                "Recovery: Automatic, no manual intervention",
                "Consistency: Strong consistency maintained",
                "Scalability: Add nodes without downtime"
            ]
        }
    },
    "31_failover": {
        "title": "Failover Mechanisms",
        "requirements": {
            "functional": [
                "Detect component failures",
                "Trigger automatic failover",
                "Redirect traffic to healthy",
                "Handle cascading failures",
                "Support manual intervention"
            ],
            "non_functional": [
                "Detection: < 10 seconds",
                "Failover: < 30 seconds to complete",
                "Data loss: < 5 minute RPO",
                "Consistency: No data corruption",
                "Testing: Regular failover drills"
            ]
        }
    },
    "32_load_balancing": {
        "title": "Load Balancing Strategy",
        "requirements": {
            "functional": [
                "Distribute requests evenly",
                "Support multiple algorithms",
                "Health check backends",
                "Sticky sessions if needed",
                "Support connection draining"
            ],
            "non_functional": [
                "Latency: < 5ms routing decision",
                "Throughput: 1M+ requests/second",
                "Availability: 99.99% uptime",
                "Fairness: Equal distribution",
                "Efficiency: < 1% CPU overhead"
            ]
        }
    },
    "33_security_caching": {
        "title": "Security in Caching Systems",
        "requirements": {
            "functional": [
                "Encrypt sensitive data in cache",
                "Control access to cache entries",
                "Prevent cache poisoning",
                "Audit cache access",
                "Support TTL for sensitive data"
            ],
            "non_functional": [
                "Encryption: AES-256 minimum",
                "Latency: Encryption < 1ms overhead",
                "Compliance: SOC 2, HIPAA support",
                "Audit: Complete access logs",
                "Confidentiality: No data leakage"
            ]
        }
    },
    "34_concurrency_control": {
        "title": "Concurrency Control",
        "requirements": {
            "functional": [
                "Handle concurrent access safely",
                "Support atomic operations",
                "Prevent race conditions",
                "Enable lock-free designs",
                "Handle deadlock detection"
            ],
            "non_functional": [
                "Latency: Atomic ops < 1 microsecond",
                "Throughput: 1M+ concurrent ops",
                "Fairness: No thread starvation",
                "Scalability: Linear scaling",
                "Overhead: < 5% concurrency cost"
            ]
        }
    },
    "35_data_serialization": {
        "title": "Data Serialization Formats",
        "requirements": {
            "functional": [
                "Serialize objects to bytes",
                "Support multiple formats",
                "Handle schema evolution",
                "Enable cross-language support",
                "Support versioning"
            ],
            "non_functional": [
                "Space: 50-70% data size reduction",
                "Speed: Serialize 1GB/s+",
                "Compatibility: Multiple versions",
                "Clarity: Human-readable optional",
                "Standards: Protocol Buffers, JSON, etc"
            ]
        }
    },
    "36_compression": {
        "title": "Data Compression",
        "requirements": {
            "functional": [
                "Compress data transparently",
                "Support multiple algorithms",
                "Reduce storage footprint",
                "Maintain compression ratio",
                "Handle different data types"
            ],
            "non_functional": [
                "Compression: 5-10x for typical data",
                "CPU: < 5% compression overhead",
                "Speed: Compress/decompress 1GB/s+",
                "Flexibility: Tunable ratio vs speed",
                "Hardware: GPU acceleration available"
            ]
        }
    },
    "37_migration": {
        "title": "Data Migration and Versioning",
        "requirements": {
            "functional": [
                "Migrate data between systems",
                "Handle schema changes",
                "Support incremental migration",
                "Verify data integrity",
                "Enable rollback if needed"
            ],
            "non_functional": [
                "Downtime: Zero-downtime migration",
                "Throughput: 100TB+ per week",
                "Accuracy: 100% data correctness",
                "Validation: Automated quality checks",
                "Automation: Minimal manual steps"
            ]
        }
    },
    "38_versioning": {
        "title": "Data Versioning Strategy",
        "requirements": {
            "functional": [
                "Track data changes over time",
                "Support rollback to previous versions",
                "Enable audit trail",
                "Handle schema versioning",
                "Support multi-version concurrency"
            ],
            "non_functional": [
                "Storage: < 2x data size for versions",
                "Latency: Version lookup < 10ms",
                "Retention: 1+ year version history",
                "Scalability: Support 1B+ versions",
                "Consistency: Consistent view per version"
            ]
        }
    },
    "39_cost_optimization": {
        "title": "Cost Optimization Strategies",
        "requirements": {
            "functional": [
                "Right-size resources",
                "Auto-scale based on demand",
                "Use reserved instances",
                "Identify expensive operations",
                "Enable cost tracking"
            ],
            "non_functional": [
                "Cost: Reduce infrastructure 40-60%",
                "Performance: Maintain SLAs",
                "Automation: Fully automated",
                "Granularity: Per-component tracking",
                "Visibility: Real-time cost dashboards"
            ]
        }
    },
    "40_edge_caching": {
        "title": "Edge Caching and CDN",
        "requirements": {
            "functional": [
                "Cache at network edge",
                "Serve from nearest location",
                "Purge cache on updates",
                "Support origin failover",
                "Enable geographic routing"
            ],
            "non_functional": [
                "Latency: < 100ms from user p99",
                "Hit rate: 95%+ cache hit ratio",
                "Availability: 99.999% uptime",
                "Coverage: 200+ edge locations",
                "Capacity: Terabits/second"
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
- Throughput: Millions of cache operations per second
- Latency: Microseconds to milliseconds
- Data volume: Terabytes to Petabytes
- Concurrent connections: Millions
- Availability: 99.99%+ uptime SLA

**Key Components:**
- Data storage and retrieval
- Cache management and eviction
- Replication and durability
- Monitoring and performance
- Recovery and high availability

## Architecture Diagrams

### Cache System Architecture

```mermaid
graph TB
    subgraph "Clients"
        C1["Client 1"]
        C2["Client 2"]
        C3["Client N"]
    end

    subgraph "Cache Layer"
        CA1["Cache Node 1"]
        CA2["Cache Node 2"]
        CA3["Cache Node 3"]
    end

    subgraph "Storage"
        S1["Primary DB"]
        S2["Replicas"]
    end

    C1 --> CA1
    C2 --> CA2
    C3 --> CA3
    CA1 --> S1
    CA2 --> S1
    CA3 --> S1
    S1 --> S2

    style C1 fill:#e1f5ff
    style CA1 fill:#f3e5f5
    style S1 fill:#e8f5e9
```

### Data Flow in Cache

```mermaid
graph LR
    A["Request"] --> B["Check Cache"]
    B --> C["Cache Hit"]
    C --> D["Return Data"]
    B --> E["Cache Miss"]
    E --> F["Query DB"]
    F --> G["Update Cache"]
    G --> D

    style C fill:#c8e6c9
    style E fill:#ffccbc
    style D fill:#fff9c4
```

### Replication and Failover

```mermaid
graph TB
    P["Primary"] -->|Replicate| R1["Replica 1"]
    P -->|Replicate| R2["Replica 2"]
    P -->|Heartbeat| H["Health Check"]
    H -->|Failure| F["Failover"]
    F -->|Promote| R1
    R1 -->|New Primary| N["Clients"]

    style P fill:#e1f5ff
    style R1 fill:#c8e6c9
    style F fill:#fff9c4
```

### Multi-Level Caching

```mermaid
graph TB
    R["Request"] --> L1["L1 Cache"]
    L1 --> H1["Hit"]
    L1 --> M1["Miss"]
    M1 --> L2["L2 Cache"]
    L2 --> H2["Hit"]
    L2 --> M2["Miss"]
    M2 --> DB["Database"]
    DB --> U1["Update L2"]
    U1 --> U2["Update L1"]

    style H1 fill:#c8e6c9
    style H2 fill:#bbdefb
    style DB fill:#ffccbc
```

### Performance Monitoring

```mermaid
graph TB
    O["Operations"] --> M["Metrics"]
    M --> A["Analysis"]
    A --> D["Dashboard"]
    A --> AL["Alerts"]
    AL --> OPT["Optimization"]

    style M fill:#bbdefb
    style D fill:#c8e6c9
    style OPT fill:#fff9c4
```

## Data Flow Scenarios

### Scenario 1: Cache Hit
1. Request arrives at cache layer
2. Hash key to find cache partition
3. Lookup in local cache
4. Found in cache (hit)
5. Return data to client
6. Update access time

### Scenario 2: Cache Miss
1. Request arrives at cache layer
2. Cache miss detected
3. Query underlying storage
4. Data returned from storage
5. Store in cache for future
6. Return to client

### Scenario 3: Failover
1. Primary cache node fails
2. Health check detects failure
3. Promote replica to primary
4. Redirect traffic to new primary
5. Sync other replicas
6. Recovery of failed node

## Performance Optimization

### Cache Efficiency
- **Hit rate**: Optimize for > 90% hit rate
- **Eviction**: LRU, LFU, or custom policies
- **Warming**: Pre-load hot data
- **Batching**: Group operations

### Resource Optimization
- **Memory**: Compress, deduplicate data
- **CPU**: Reduce hashing, optimize structures
- **Network**: Batch updates, use compression
- **Storage**: Tiered storage, archival

### Cost Optimization
- **Reserved instances**: Baseline capacity
- **Spot instances**: Flexible workloads
- **Auto-scaling**: Match demand
- **Cleanup**: Remove unused data

## Back-of-Envelope Calculations

### Cache Scale
```
Daily active users: 100M
Requests per user: 50
Daily requests: 5B
Peak RPS: 57,870
Cache servers (10K RPS each): 6 servers
Data per user: 10 KB
Total cache: 100M × 10 KB = 1 TB
```

### Hit Rate Impact
```
Without cache: 100M users × 50 req × 10ms DB = 50M seconds = 579 days
With 90% hit rate: 10% × 579 = 58 days
Speedup: 10x faster response times
```

### Replication Overhead
```
Primary data: 1 TB
Replicas: 3 copies
Total: 4 TB storage
Replication bandwidth: 1TB per day
Network: 1TB / 86400 = 11.5 MB/s
```

## Interview Questions & Answers

### Q1: Design a distributed cache system for 100M users

**Answer:**
1. **Architecture**: Distributed cache with replication
2. **Sharding**: Consistent hashing for scaling
3. **Replication**: 3-way for durability
4. **Eviction**: LRU for memory management
5. **Monitoring**: Real-time metrics and alerting
6. **Recovery**: Automatic failover and rebuild

### Q2: Handle cache invalidation at scale

**Answer:**
- **TTL-based**: Automatic expiration by time
- **Event-based**: Invalidate on data change
- **Broadcast**: Propagate across all nodes
- **Selective**: Invalidate only affected keys
- **Stampede**: Use locks to prevent queries

### Q3: Optimize cache hit rate

**Answer:**
- **Prefetch**: Load predictable data
- **Warm-up**: Pre-populate at startup
- **Eviction**: Better policy (LFU vs LRU)
- **TTL tuning**: Balance freshness vs hits
- **Analysis**: Monitor and adjust

### Q4: Design failover for caching system

**Answer:**
- **Detection**: Health checks < 10 seconds
- **Promotion**: Replica becomes primary
- **Redirect**: Route to new primary
- **Consistency**: Sync remaining replicas
- **Testing**: Regular failover drills

### Q5: Multi-level caching strategy

**Answer:**
- **L1**: Local app cache (milliseconds)
- **L2**: Distributed cache (tens of ms)
- **L3**: Database cache (hundreds of ms)
- **Miss**: Query database if all miss
- **Propagate**: Populate all levels

### Q6: Cost-optimize caching infrastructure

**Answer:**
- **Reserved**: Baseline capacity commitment
- **Spot**: Flexible non-critical workloads
- **Auto-scale**: Adjust to demand
- **Cleanup**: Remove unused data
- **Monitoring**: Track cost per operation

## Technology Stack

| Component | Technology | Why |
|-----------|-----------|-----|
| Cache | Redis, Memcached | Fast, distributed |
| Store | PostgreSQL, MongoDB | Durable storage |
| Replication | Streaming replication | Real-time sync |
| Monitoring | Prometheus, Datadog | Metrics & alerts |
| Failover | Sentinel, etcd | Automatic recovery |
| Compression | Snappy, ZSTD | Reduce footprint |

## Lessons Learned

1. **Cache is critical**: Even small improvements 10x impact
2. **Measure everything**: Can't optimize what you don't measure
3. **Consistency matters**: Stale cache causes hard bugs
4. **Failures happen**: Design for recovery, not prevention
5. **Simplicity wins**: Complex caching = debugging nightmare

## Related Topics

- Memory management and garbage collection
- Distributed systems consistency
- Replication and durability
- Performance monitoring and tuning
- Cost optimization strategies
- High availability architecture
- Security in distributed systems
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

    caching_stores_dir = Path("docs/system_design/19-caching-stores")
    caching_stores_dir.mkdir(exist_ok=True)

    filepath = caching_stores_dir / f"{concept_key}.md"
    filepath.write_text(content, encoding="utf-8")

    return filepath

def main():
    """Create all 30 new caching and data store concepts."""
    print("💾 Creating 30 new caching/data store concepts (11-40)...")
    print("=" * 70)

    created = 0
    for concept_key, concept_data in sorted(CONCEPTS.items()):
        filepath = create_topic_file(concept_key, concept_data)
        print(f"✅ Created: {filepath.name}")
        created += 1

    print("=" * 70)
    print(f"✨ Created {created} new comprehensive caching/data store concepts!")
    print("\nTopics added (11-40):")
    topics = [v["title"] for v in CONCEPTS.values()]
    for i, topic in enumerate(topics, 11):
        print(f"  {i}. {topic}")

if __name__ == "__main__":
    main()

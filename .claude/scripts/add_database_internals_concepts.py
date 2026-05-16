#!/usr/bin/env python3
"""
Add 30 new database internals concepts (06-35) with comprehensive treatment.
Each includes diagrams, code, calculations, interview questions.
"""

from pathlib import Path

CONCEPTS = {
    "06_acid_transactions": {
        "title": "ACID Transactions",
        "requirements": {
            "functional": [
                "Execute multiple operations atomically (all-or-nothing)",
                "Isolate concurrent transactions from each other",
                "Persist committed changes durably to disk",
                "Maintain consistency invariants across operations",
                "Support rollback to undo partial changes"
            ],
            "non_functional": [
                "Throughput: 10K+ transactions/second per instance",
                "Latency: < 10ms p99 for transaction commit",
                "Isolation: SERIALIZABLE without performance penalty",
                "Durability: Fsync to disk < 1ms overhead",
                "Scalability: Support 1000+ concurrent transactions"
            ]
        }
    },
    "07_write_ahead_logging": {
        "title": "Write-Ahead Logging",
        "requirements": {
            "functional": [
                "Log all changes before modifying data pages",
                "Ensure data recovery from any point in time",
                "Support crash recovery without data loss",
                "Enable undo/redo operations",
                "Manage log rotation and cleanup"
            ],
            "non_functional": [
                "Latency: Log write < 1ms overhead",
                "Throughput: Handle high transaction rates",
                "Storage: Logs retained for recovery period",
                "Recovery time: Full recovery < 5 minutes",
                "Reliability: Fsync guarantees durability"
            ]
        }
    },
    "08_buffer_pool": {
        "title": "Buffer Pool Management",
        "requirements": {
            "functional": [
                "Cache data pages in memory for fast access",
                "Evict pages using LRU or clock algorithm",
                "Write dirty pages to disk asynchronously",
                "Handle buffer replacement with minimal overhead",
                "Support configurable pool size"
            ],
            "non_functional": [
                "Hit rate: 95%+ for typical workloads",
                "Latency: Memory access < 1 microsecond",
                "Throughput: Not bottleneck for disk I/O",
                "Overhead: < 5% memory for page tracking",
                "Adaptivity: Tune eviction based on access patterns"
            ]
        }
    },
    "09_query_execution": {
        "title": "Query Execution Engine",
        "requirements": {
            "functional": [
                "Execute physical query plans efficiently",
                "Support multiple join algorithms (nested loop, hash, sort-merge)",
                "Pipeline results without materializing intermediate states",
                "Handle memory constraints with spilling to disk",
                "Support early termination for LIMIT queries"
            ],
            "non_functional": [
                "Latency: Complex query < 30 seconds p99",
                "Throughput: 1000+ queries/second",
                "Memory: Process queries larger than memory",
                "CPU: Minimize instruction count per row",
                "Efficiency: Cache-friendly data structures"
            ]
        }
    },
    "10_index_structures": {
        "title": "Index Structures",
        "requirements": {
            "functional": [
                "Maintain sorted order for range queries",
                "Support point lookups with O(log n) complexity",
                "Enable fast sequential scans",
                "Support key updates with minimal overhead",
                "Handle variable-length keys"
            ],
            "non_functional": [
                "Lookup latency: < 1ms for 1B row index",
                "Space overhead: 10-30% of data size",
                "Insert/update cost: 20-30% slower than sequential",
                "Range scan: 10x faster than full table scan",
                "Cache locality: Minimize random access"
            ]
        }
    },
    "11_storage_engine": {
        "title": "Storage Engine",
        "requirements": {
            "functional": [
                "Persist data reliably to disk",
                "Support efficient sequential and random access",
                "Manage space allocation and deallocation",
                "Provide crash recovery capabilities",
                "Handle concurrent access safely"
            ],
            "non_functional": [
                "Sequential throughput: 100+ MB/s",
                "Random I/O latency: < 10ms p99",
                "Space efficiency: Minimal fragmentation",
                "Recovery: Online or offline recovery",
                "Concurrency: Support 1000+ concurrent connections"
            ]
        }
    },
    "12_lock_manager": {
        "title": "Lock Manager",
        "requirements": {
            "functional": [
                "Grant and release locks on database objects",
                "Support multiple lock modes (shared, exclusive)",
                "Detect and resolve deadlocks",
                "Support lock escalation and demotion",
                "Handle lock timeouts"
            ],
            "non_functional": [
                "Lock acquisition latency: < 1ms",
                "Throughput: 100K+ lock operations/second",
                "Memory: O(n) space for n locks",
                "Deadlock detection: Within 1 second",
                "Fairness: No starvation or priority inversion"
            ]
        }
    },
    "13_catalog_statistics": {
        "title": "Catalog and Statistics",
        "requirements": {
            "functional": [
                "Maintain metadata about tables, columns, indexes",
                "Collect statistics on data distribution",
                "Track object sizes and row counts",
                "Support schema versioning",
                "Enable query optimizer statistics"
            ],
            "non_functional": [
                "Metadata access: < 1ms latency",
                "Statistics freshness: Update within 1 hour",
                "Cardinality accuracy: 95%+ for estimates",
                "Storage: Statistics < 1% of data",
                "Consistency: Transactional updates"
            ]
        }
    },
    "14_isolation_levels": {
        "title": "Isolation Levels",
        "requirements": {
            "functional": [
                "Implement READ UNCOMMITTED (dirty reads allowed)",
                "Implement READ COMMITTED (no dirty reads)",
                "Implement REPEATABLE READ (phantom reads possible)",
                "Implement SERIALIZABLE (no anomalies)",
                "Support custom isolation policies"
            ],
            "non_functional": [
                "Throughput vs consistency tradeoff configurable",
                "Performance: Serializable < 50% slower than Read Committed",
                "Fairness: No transaction starvation",
                "Correctness: Provably serializable isolation",
                "Flexibility: Per-transaction isolation selection"
            ]
        }
    },
    "15_garbage_collection": {
        "title": "Garbage Collection",
        "requirements": {
            "functional": [
                "Reclaim space from deleted rows",
                "Remove obsolete versions in MVCC",
                "Compact tables to eliminate fragmentation",
                "Vacuum dead tuples automatically",
                "Support partial and full vacuums"
            ],
            "non_functional": [
                "Impact: < 10% query performance overhead",
                "Frequency: Daily for active tables",
                "Space reclamation: 30-50% of deleted space",
                "Latency: Background operation, non-blocking",
                "Tuning: Configurable aggressiveness"
            ]
        }
    },
    "16_schema_evolution": {
        "title": "Schema Evolution",
        "requirements": {
            "functional": [
                "Add/drop columns without rebuilding table",
                "Rename columns and tables",
                "Change column types with automatic casting",
                "Modify constraints and defaults",
                "Support zero-downtime schema changes"
            ],
            "non_functional": [
                "Latency: Schema change < 1 second",
                "Downtime: Zero-downtime for large tables",
                "Compatibility: Support online DDL operations",
                "Rollback: Easy revert of failed changes",
                "Monitoring: Track schema change progress"
            ]
        }
    },
    "17_partition_pruning": {
        "title": "Partition Pruning",
        "requirements": {
            "functional": [
                "Identify partitions relevant to query",
                "Skip reading irrelevant partitions",
                "Support range, list, and hash partitioning",
                "Handle partition elimination at runtime",
                "Support dynamic partition elimination"
            ],
            "non_functional": [
                "Pruning latency: < 1ms for partition decision",
                "Effectiveness: Eliminate 80%+ partitions",
                "Accuracy: Never incorrectly eliminate partition",
                "Complexity: Support complex predicates",
                "Scalability: Support 1000+ partitions"
            ]
        }
    },
    "18_query_planning": {
        "title": "Query Planning",
        "requirements": {
            "functional": [
                "Convert SQL to logical query plan",
                "Apply logical optimizations (predicate pushdown, projection)",
                "Generate optimal physical execution plan",
                "Support multiple plan candidates",
                "Handle plan hints and directives"
            ],
            "non_functional": [
                "Planning latency: < 100ms for complex queries",
                "Plan quality: 95%+ optimal execution time",
                "Reproducibility: Same plan for same query",
                "Observability: Explain plan for debugging",
                "Caching: Cache query plans"
            ]
        }
    },
    "19_cardinality_estimation": {
        "title": "Cardinality Estimation",
        "requirements": {
            "functional": [
                "Estimate rows output by query plan nodes",
                "Account for filter selectivity",
                "Handle join cardinalities",
                "Support correlation detection",
                "Adapt estimates based on actual execution"
            ],
            "non_functional": [
                "Accuracy: 90%+ correct within 2x factor",
                "Latency: Estimation < 10ms",
                "Robustness: Handle edge cases gracefully",
                "Coverage: Support complex queries",
                "Feedback: Use runtime statistics for improvement"
            ]
        }
    },
    "20_cost_optimizer": {
        "title": "Cost-Based Optimizer",
        "requirements": {
            "functional": [
                "Assign cost to different execution plans",
                "Consider CPU, I/O, and network costs",
                "Select plan with lowest estimated cost",
                "Support custom cost models",
                "Handle plan changes due to statistics updates"
            ],
            "non_functional": [
                "Plan quality: Average 95% optimal cost",
                "Time: Planning < 1 second for complex query",
                "Accuracy: Cost model accurate within 20%",
                "Flexibility: Customizable cost functions",
                "Tuning: Auto-tune cost model parameters"
            ]
        }
    },
    "21_bloom_filters": {
        "title": "Bloom Filters in Databases",
        "requirements": {
            "functional": [
                "Quickly filter out non-matching rows",
                "Support false positives but no false negatives",
                "Enable early termination of scans",
                "Support set membership tests",
                "Handle dynamic filter updates"
            ],
            "non_functional": [
                "FP rate: < 1% with reasonable filter size",
                "Memory: 1-10 bits per element",
                "Latency: Filter check < 100ns",
                "Throughput: No bottleneck for query execution",
                "Accuracy: Tunable false positive rate"
            ]
        }
    },
    "22_btree_variants": {
        "title": "B-Tree Variants",
        "requirements": {
            "functional": [
                "Support B+ trees with improved range scan",
                "Support B* trees with better space utilization",
                "Handle bulk loading efficiently",
                "Support versioned B-trees for MVCC",
                "Enable lock-free concurrent access"
            ],
            "non_functional": [
                "Lookup: O(log n) with small constant",
                "Range scan: Sequential page access",
                "Space: 70-80% page utilization",
                "Concurrency: Support latch-free designs",
                "Scalability: Handle billions of keys"
            ]
        }
    },
    "23_hash_tables": {
        "title": "Hash Tables and Indexing",
        "requirements": {
            "functional": [
                "Support constant-time key lookups",
                "Handle hash collisions with chaining/probing",
                "Support dynamic resizing",
                "Enable fast hash joins",
                "Handle NULL values correctly"
            ],
            "non_functional": [
                "Lookup latency: O(1) average, < 1microsecond",
                "Load factor: 70-80% optimal",
                "Collision resolution: < 5% secondary probes",
                "Memory: Efficient hash table layout",
                "Scalability: Support 1B+ entries"
            ]
        }
    },
    "24_fulltext_search": {
        "title": "Full-Text Search",
        "requirements": {
            "functional": [
                "Index text documents for fast search",
                "Support phrase queries and wildcards",
                "Enable relevance ranking",
                "Handle stopwords and stemming",
                "Support multiple languages"
            ],
            "non_functional": [
                "Query latency: < 100ms for text search",
                "Throughput: Index 1000+ documents/second",
                "Index size: 30-50% of original data",
                "Relevance: Top-10 results 95% useful",
                "Scalability: Index terabytes of text"
            ]
        }
    },
    "25_spatial_indexing": {
        "title": "Spatial Indexing",
        "requirements": {
            "functional": [
                "Index spatial objects (points, polygons)",
                "Support range and nearest-neighbor queries",
                "Handle multi-dimensional data",
                "Enable geographical proximity searches",
                "Support spatial relationships (contains, overlaps)"
            ],
            "non_functional": [
                "Query latency: < 10ms for spatial queries",
                "Index size: 20-30% of data",
                "Scalability: Handle millions of spatial objects",
                "Accuracy: Correct spatial relationships",
                "Concurrency: Support concurrent spatial updates"
            ]
        }
    },
    "26_bitmap_indexes": {
        "title": "Bitmap Indexes",
        "requirements": {
            "functional": [
                "Store column values as bitmaps",
                "Support fast bitmap operations (AND, OR, NOT)",
                "Enable efficient aggregation",
                "Handle low-cardinality columns",
                "Support compressed bitmaps"
            ],
            "non_functional": [
                "Query speedup: 10-100x for aggregates",
                "Compression: 100:1 for sparse bitmaps",
                "Update latency: < 1ms for bitmap update",
                "Memory: Logarithmic in value range",
                "Scalability: Support high-cardinality columns"
            ]
        }
    },
    "27_covering_indexes": {
        "title": "Covering Indexes",
        "requirements": {
            "functional": [
                "Store additional columns in index",
                "Enable index-only scans",
                "Reduce table access for queries",
                "Support partial indexes on filtered data",
                "Include non-key columns efficiently"
            ],
            "non_functional": [
                "Query speedup: 5-10x for index-only scans",
                "Index size: 120-150% of key columns",
                "Update cost: 20-30% overhead for writes",
                "Effectiveness: Eliminate 50%+ table access",
                "Tuning: Auto-suggest covering indexes"
            ]
        }
    },
    "28_column_storage": {
        "title": "Column Storage Engines",
        "requirements": {
            "functional": [
                "Store data column-wise for compression",
                "Support efficient aggregations",
                "Handle sparse data efficiently",
                "Enable columnar operations",
                "Support columnar scans without decompression"
            ],
            "non_functional": [
                "Compression ratio: 10-20x vs row storage",
                "Query speed: 10-100x faster for analytics",
                "Write latency: Higher than row storage",
                "Update cost: Batch updates recommended",
                "Scalability: Petabytes of data"
            ]
        }
    },
    "29_inmemory_db": {
        "title": "In-Memory Databases",
        "requirements": {
            "functional": [
                "Store entire dataset in memory",
                "Support persistence to disk for durability",
                "Enable ultra-low latency queries",
                "Handle memory constraints with eviction",
                "Support real-time analytics"
            ],
            "non_functional": [
                "Latency: < 1ms p99 for queries",
                "Throughput: 1M+ transactions/second",
                "Durability: Fsync to disk configurable",
                "Memory: Efficient data structures",
                "Scalability: Multi-node replication"
            ]
        }
    },
    "30_time_travel": {
        "title": "Time Travel Queries",
        "requirements": {
            "functional": [
                "Query data as it existed at past point in time",
                "Support temporal queries with timestamps",
                "Enable audit trail of all changes",
                "Handle schema changes over time",
                "Support as-of queries"
            ],
            "non_functional": [
                "Retention: Multi-year historical data",
                "Query latency: Similar to current data queries",
                "Storage: 200-300% for historical versions",
                "Accuracy: Bit-perfect historical state",
                "Compliance: Enable audit requirements"
            ]
        }
    },
    "31_distributed_transactions": {
        "title": "Distributed Transactions",
        "requirements": {
            "functional": [
                "Execute transactions across multiple servers",
                "Ensure ACID across distributed nodes",
                "Implement two-phase commit protocol",
                "Handle coordinator failure gracefully",
                "Support rollback across servers"
            ],
            "non_functional": [
                "Latency: < 100ms for distributed commit",
                "Consistency: Strict serialization",
                "Availability: Tolerate 1 server failure",
                "Throughput: 1000+ transactions/second",
                "Recovery: Automatic failover"
            ]
        }
    },
    "32_consistency_checking": {
        "title": "Consistency Checking",
        "requirements": {
            "functional": [
                "Verify data consistency and integrity",
                "Detect corruption in indexes and tables",
                "Find orphaned or missing references",
                "Validate constraint violations",
                "Support repair mechanisms"
            ],
            "non_functional": [
                "Detection time: Scan large table < 1 hour",
                "Accuracy: Detect 99%+ of corruption",
                "False positives: < 1% of issues",
                "Repair: Minimize data loss",
                "Automation: Scheduled consistency checks"
            ]
        }
    },
    "33_checkpoint_recovery": {
        "title": "Checkpoint and Recovery",
        "requirements": {
            "functional": [
                "Create consistent database snapshots",
                "Enable recovery from any checkpoint",
                "Support incremental and full checkpoints",
                "Handle crash recovery automatically",
                "Track recovery progress"
            ],
            "non_functional": [
                "Checkpoint latency: < 1 minute for 1TB data",
                "Recovery time: < 5 minutes from crash",
                "Durability: Fsync guarantees",
                "Frequency: Hourly checkpoints sufficient",
                "Automation: Fully automatic process"
            ]
        }
    },
    "34_memory_management": {
        "title": "Memory Management",
        "requirements": {
            "functional": [
                "Allocate memory efficiently for queries",
                "Track memory usage per query/session",
                "Spill to disk when memory exhausted",
                "Support memory pools and limits",
                "Handle out-of-memory conditions gracefully"
            ],
            "non_functional": [
                "Allocation latency: < 1microsecond",
                "Fragmentation: < 10% waste",
                "Spill overhead: < 20% slowdown",
                "Limit enforcement: Strict guarantees",
                "Observability: Track memory usage"
            ]
        }
    },
    "35_connection_management": {
        "title": "Connection Management",
        "requirements": {
            "functional": [
                "Accept and authenticate database connections",
                "Manage connection pooling",
                "Handle connection timeouts",
                "Support session state management",
                "Enable connection limits per user"
            ],
            "non_functional": [
                "Connection latency: < 100ms to establish",
                "Pool size: 1000+ connections",
                "Reuse: Minimize connection overhead",
                "Fairness: No client starvation",
                "Monitoring: Track connection usage"
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
- Throughput: Millions of operations per second
- Latency: Microseconds to milliseconds
- Data volume: Terabytes to Petabytes
- Concurrent operations: Thousands to millions
- Availability: 99.99% to 99.999% uptime SLA

**Key Components:**
- Data structures and algorithms
- Concurrency control mechanisms
- Memory and storage management
- Query processing and optimization
- Monitoring and observability

## Architecture Diagrams

### System Architecture

```mermaid
graph TB
    subgraph "Query Layer"
        Q1["SQL Parser"]
        Q2["Query Optimizer"]
        Q3["Planner"]
    end

    subgraph "Execution Engine"
        E1["Executor"]
        E2["Join Engine"]
        E3["Aggregation"]
    end

    subgraph "Storage Layer"
        S1["Buffer Pool"]
        S2["Index Manager"]
        S3["Storage Engine"]
    end

    subgraph "Concurrency"
        C1["Lock Manager"]
        C2["MVCC"]
        C3["Transaction Log"]
    end

    Q1 --> Q2
    Q2 --> Q3
    Q3 --> E1
    E1 --> E2
    E2 --> E3
    E3 --> S1
    S1 --> S2
    S2 --> S3
    E1 --> C1
    C1 --> C2
    C2 --> C3

    style Q1 fill:#e1f5ff
    style E1 fill:#f3e5f5
    style S1 fill:#e8f5e9
    style C1 fill:#fff3e0
```

### Data Flow

```mermaid
graph LR
    A["Query Input"] --> B["Parse"]
    B --> C["Analyze"]
    C --> D["Optimize"]
    D --> E["Execute"]
    E --> F["Fetch"]
    F --> G["Result"]

    style A fill:#c8e6c9
    style D fill:#ffccbc
    style E fill:#bbdefb
    style G fill:#fff9c4
```

### Performance Characteristics

```mermaid
graph TB
    subgraph "Memory Layer"
        M1["CPU L1/L2"]
        M2["Main Memory"]
        M3["Disk Cache"]
    end

    subgraph "Speed"
        S1["Nanoseconds"]
        S2["Microseconds"]
        S3["Milliseconds"]
    end

    subgraph "Latency"
        L1["1-10ns"]
        L2["100ns-10us"]
        L3["10ms+"]
    end

    M1 --> L1
    M2 --> L2
    M3 --> L3

    style M1 fill:#c8e6c9
    style M2 fill:#ffccbc
    style M3 fill:#bbdefb
```

### Concurrency Control

```mermaid
graph TB
    A["Concurrent Transactions"] --> B["Lock Manager"]
    B --> C["Conflict Detection"]
    C -->|No Conflict| D["Execute"]
    C -->|Conflict| E["Wait or Abort"]
    D --> F["Commit"]
    E --> G["Retry"]

    style B fill:#fff3e0
    style D fill:#c8e6c9
    style F fill:#bbdefb
```

### Recovery Process

```mermaid
graph TB
    A["Crash Detected"] --> B["Read Log"]
    B --> C["Redo Committed"]
    C --> D["Undo Uncommitted"]
    D --> E["Verify Consistency"]
    E --> F["Ready for Queries"]

    style A fill:#ffcdd2
    style F fill:#c8e6c9
```

## Data Flow Scenarios

### Scenario 1: Query Execution
1. SQL query received and parsed
2. Optimizer analyzes query plan
3. Cost-based optimizer selects best plan
4. Executor runs physical plan
5. Buffer pool manages page access
6. Results streamed to client

### Scenario 2: Transaction with Conflict
1. Transaction A acquires lock on row
2. Transaction B tries to access same row
3. Lock manager blocks B until A commits
4. A commits and releases lock
5. B proceeds with row access

### Scenario 3: Index Lookup
1. Query asks for row with key = 'X'
2. Index traversal from root to leaf
3. Leaf page fetched from buffer pool
4. Key location found in O(log n) time
5. Row ID obtained from index
6. Data page fetched and returned

## Performance Optimization

### Query Optimization
- **Predicate pushdown**: Apply filters early
- **Join ordering**: Smallest intermediate results
- **Parallel execution**: Multi-threaded processing
- **Caching**: Avoid redundant computation

### Storage Optimization
- **Compression**: 5-10x space reduction
- **Partitioning**: Scan only relevant data
- **Indexing**: Fast key lookups
- **Denormalization**: Trade storage for speed

### Concurrency Optimization
- **Lock-free structures**: Minimize contention
- **MVCC**: Read without blocking writes
- **Batching**: Group operations for efficiency
- **Adaptive**: Tune based on workload

## Back-of-Envelope Calculations

### Query Performance
```
1 billion row table
Index on column: 30-level B-tree
Sequential scan: 1 billion rows × 8KB = 8TB disk read
Index lookup: log(1B) ≈ 30 page accesses = 30ms
Speedup: 8TB read ÷ 30ms = 10,000x faster
```

### Buffer Pool Sizing
```
Cache 10% of 1TB database = 100GB
Page size: 8KB
Number of pages: 100GB ÷ 8KB = 12.8M pages
Hit rate: 95% = 95% memory access, 5% disk access
Memory bandwidth: 100GB/s
Expected latency: 95% × 1us + 5% × 10ms ≈ 500us
```

### Concurrency Throughput
```
Transactions per second: 10K
Contention: 10% of transactions conflict
Lock wait time: 10ms average
Throughput impact: 10K × (1 - 0.1) + (10K × 0.1) × (1 - 10ms overhead)
Effective: ~9,000 TPS due to contention
```

### Recovery Time
```
Database size: 1TB
Redo speed: 100MB/s
Recovery time: 1TB ÷ 100MB/s = 10,000 seconds ≈ 2.8 hours
With optimization (parallel redo): 2.8 hours ÷ 8 cores = 21 minutes
With incremental checkpoints: 10 minutes + redo time
```

## Interview Questions & Answers

### Q1: Design an index for fast lookups

**Answer:**
1. **Clarify**: Cardinality, range queries, update frequency
2. **Options**:
   - Hash index: O(1) point lookups, no range
   - B-tree: O(log n), good for range, updates
   - LSM tree: O(log n), optimized for writes
3. **Deep dive**: B-tree with 10-20x branching factor
4. **Implementation**: Internal/leaf node structure
5. **Tradeoffs**: Space vs speed, update cost

### Q2: Handle 100 concurrent transactions

**Answer:**
- **Locking**: 2-phase locking with deadlock detection
- **MVCC**: Readers don't block writers
- **Isolation**: REPEATABLE READ sufficient for most
- **Monitoring**: Track lock contention and timeouts
- **Optimization**: Hot row batching, range locks

### Q3: What happens during crash recovery?

**Answer:**
1. **Redo phase**: Replay committed changes from log
2. **Undo phase**: Remove uncommitted changes
3. **Verify**: Check consistency, rebuild indexes
4. **Time**: Proportional to active transaction log
5. **Optimization**: Incremental checkpoints reduce time

### Q4: How do you optimize slow queries?

**Answer:**
1. **Profile**: Identify bottleneck (CPU, I/O, lock)
2. **Statistics**: Update table/index statistics
3. **Indexes**: Add index on filter columns
4. **Plan**: Review explain plan
5. **Denormalization**: Cache frequently joined data
6. **Sharding**: Partition large tables

### Q5: Design a distributed transaction system

**Answer:**
- **Coordinator**: Two-phase commit protocol
- **Replicas**: Write to majority for durability
- **Timeout**: Abort if no response < 5 seconds
- **Recovery**: Coordinator failure detection
- **Optimization**: One-phase commit for single region

### Q6: How to reduce query latency from 100ms to 10ms?

**Answer:**
- **Profile**: Where is time spent? (network, CPU, I/O)
- **Caching**: Cache result of expensive subqueries
- **Index**: Add covering index for index-only scan
- **Parallel**: Parallelize independent operations
- **Code**: Reduce allocations, optimize hot paths

## Technology Stack

| Component | Technology | Why |
|-----------|-----------|-----|
| Storage Engine | B-tree, LSM tree | Balance reads/writes |
| Buffer Pool | Clock algorithm | Simple, effective eviction |
| Lock Manager | Deadlock detection | Prevent deadlock cycles |
| Query Optimizer | Cost-based | Choose optimal plan |
| Recovery | WAL + Checkpoints | Durability with speed |

## Lessons Learned

1. **Small optimizations matter**: 1% per component = 10x overall
2. **Statistics are critical**: Bad cardinality estimates = bad plans
3. **Contention is killer**: Lock-free designs essential at scale
4. **Measure everything**: Can't optimize what you don't measure
5. **Trade-offs**: Always a tradeoff between consistency, latency, throughput

## Related Topics

- Query optimization and cost-based planning
- Concurrency control and isolation levels
- Storage structures and indexing
- Transaction processing and recovery
- Distributed database systems
- Performance tuning and monitoring
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

    db_internals_dir = Path("docs/system_design/12-database-internals")
    db_internals_dir.mkdir(exist_ok=True)

    filepath = db_internals_dir / f"{concept_key}.md"
    filepath.write_text(content, encoding="utf-8")

    return filepath

def main():
    """Create all 30 new database internals concepts."""
    print("🗄️  Creating 30 new database internals concepts (06-35)...")
    print("=" * 70)

    created = 0
    for concept_key, concept_data in sorted(CONCEPTS.items()):
        filepath = create_topic_file(concept_key, concept_data)
        print(f"✅ Created: {filepath.name}")
        created += 1

    print("=" * 70)
    print(f"✨ Created {created} new comprehensive database internals concepts!")
    print("\nTopics added (06-35):")
    topics = [v["title"] for v in CONCEPTS.values()]
    for i, topic in enumerate(topics, 6):
        print(f"  {i}. {topic}")

if __name__ == "__main__":
    main()

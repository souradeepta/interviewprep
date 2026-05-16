# Vector Data Store

## Problem Statement

### Functional Requirements
- Store high-dimensional vectors
- Support similarity search
- Enable nearest neighbor queries
- Handle vector operations
- Support semantic search

### Non-Functional Requirements
- Latency: Search < 100ms for 1M vectors
- Recall: 95%+ for approximate search
- Scalability: Billions of vectors
- Dimensions: Support 768-4096 dims
- Memory: Efficient vector compression

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

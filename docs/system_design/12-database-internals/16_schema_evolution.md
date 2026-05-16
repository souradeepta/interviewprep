# Schema Evolution

## Problem Statement

### Functional Requirements
- Add/drop columns without rebuilding table
- Rename columns and tables
- Change column types with automatic casting
- Modify constraints and defaults
- Support zero-downtime schema changes

### Non-Functional Requirements
- Latency: Schema change < 1 second
- Downtime: Zero-downtime for large tables
- Compatibility: Support online DDL operations
- Rollback: Easy revert of failed changes
- Monitoring: Track schema change progress

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


## Code Implementation

### Python
```python
import asyncio
import aiohttp
from dataclasses import dataclass
from typing import Optional, List
import time, logging

logger = logging.getLogger(__name__)

@dataclass
class ServiceConfig:
    host: str = "localhost"
    port: int = 8080
    timeout_seconds: float = 5.0
    max_retries: int = 3

class ServiceClient:
    """Generic service client with retry and circuit breaker."""
    def __init__(self, config: ServiceConfig):
        self.config = config
        self.base_url = f"http://{config.host}:{config.port}"
        self._failures = 0
        self._circuit_open = False
        self._last_failure: Optional[float] = None

    def _is_circuit_open(self) -> bool:
        if not self._circuit_open:
            return False
        # Half-open after 60s — allow one request through
        if time.time() - self._last_failure > 60:
            self._circuit_open = False
            return False
        return True

    async def call(self, endpoint: str, payload: dict) -> Optional[dict]:
        if self._is_circuit_open():
            logger.warning("Circuit open — fast fail")
            return None

        timeout = aiohttp.ClientTimeout(total=self.config.timeout_seconds)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            for attempt in range(self.config.max_retries):
                try:
                    async with session.post(
                        f"{self.base_url}{endpoint}", json=payload
                    ) as resp:
                        resp.raise_for_status()
                        self._failures = 0              # reset on success
                        return await resp.json()
                except Exception as e:
                    logger.warning(f"Attempt {attempt+1} failed: {e}")
                    if attempt < self.config.max_retries - 1:
                        await asyncio.sleep(2 ** attempt)  # exponential backoff
            # All retries exhausted
            self._failures += 1
            if self._failures >= 5:                     # open circuit
                self._circuit_open = True
                self._last_failure = time.time()
            return None
```

### Java
```java
import java.net.http.*;
import java.net.URI;
import java.time.Duration;
import java.util.concurrent.atomic.*;
import java.util.concurrent.CompletableFuture;

/** Generic resilient service client with circuit breaker + retry. */
public class ServiceClient {
    private final String baseUrl;
    private final HttpClient http;
    private final AtomicInteger failures = new AtomicInteger(0);
    private final AtomicBoolean circuitOpen = new AtomicBoolean(false);
    private volatile long lastFailureTime;

    public ServiceClient(String host, int port) {
        this.baseUrl = "http://" + host + ":" + port;
        this.http = HttpClient.newBuilder()
            .connectTimeout(Duration.ofSeconds(5))
            .build();
    }

    private boolean isCircuitOpen() {
        if (!circuitOpen.get()) return false;
        // Half-open after 60s
        if (System.currentTimeMillis() - lastFailureTime > 60_000) {
            circuitOpen.set(false);
            return false;
        }
        return true;
    }

    public CompletableFuture<String> call(String path, String jsonBody) {
        if (isCircuitOpen())
            return CompletableFuture.failedFuture(
                new RuntimeException("Circuit open"));

        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create(baseUrl + path))
            .header("Content-Type", "application/json")
            .POST(HttpRequest.BodyPublishers.ofString(jsonBody))
            .timeout(Duration.ofSeconds(5))
            .build();

        return http.sendAsync(request, HttpResponse.BodyHandlers.ofString())
            .thenApply(resp -> {
                if (resp.statusCode() >= 500) throw new RuntimeException("Server error");
                failures.set(0);  // reset on success
                return resp.body();
            })
            .exceptionally(ex -> {
                if (failures.incrementAndGet() >= 5) {
                    circuitOpen.set(true);
                    lastFailureTime = System.currentTimeMillis();
                }
                return null;
            });
    }
}
```

## Back-of-the-Envelope Calculations

**System Load Estimation:**
- 1M daily active users × 10 requests/day = 10M requests/day
- Peak QPS = 10M / 86400 × 3 (peak factor) ≈ 350 QPS
- API server capacity: 1000 QPS/server → 1 server sufficient at peak
- With 2x redundancy: 2 servers minimum

**Storage Estimation:**
- 1M users × 10KB average data = 10GB structured data
- Annual growth: 10GB × 365 = 3.65TB/year
- With 3x replication: 11TB/year
- SSD cost ($0.10/GB): $1,100/year

**Bandwidth:**
- 350 QPS × 10KB response = 3.5MB/sec outbound
- Monthly egress: 3.5MB × 86400 × 30 = 9TB/month
## Follow-up Questions

1. **How would you handle this at 10x the scale described?**
   - What breaks first? (typically: single DB, single cache node, single region)
   - What architectural changes are required?

2. **What are the consistency vs. availability trade-offs in your design?**
   - Where did you accept eventual consistency?
   - Which operations require strong consistency and why?

3. **How would you debug a sudden latency spike in production?**
   - What metrics would you look at first?
   - What's your runbook for the top 3 likely causes?

4. **How does your design handle partial failures?**
   - What happens if one component is slow (not down)?
   - How do you prevent cascading failures?

5. **What would you change if you had to build this in one week vs. six months?**
   - What corners can safely be cut initially?
   - What must be right from day one?

6. **How would you migrate from the current design to a better one without downtime?**
   - What's the strangler-fig or blue-green strategy here?
   - How do you validate correctness during migration?
# Data Compression

## Problem Statement

### Functional Requirements
- Compress data at rest without performance loss
- Support multiple compression algorithms (gzip, snappy, lz4)
- Enable transparent compression/decompression
- Compress different data types (text, binary, structured)
- Monitor compression ratios and efficiency

### Non-Functional Requirements
- Compression ratio: 5-10x for typical data
- CPU overhead: < 5% for compression
- Memory: Streaming compression without buffering
- Speed: Fast decompression for interactive queries
- Flexibility: Tunable compression vs speed tradeoff

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
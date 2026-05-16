## System Overview

**Scale Metrics:**
- **Throughput:** Variable based on system type
- **Key Components:** Message broker, producers, consumers
- **Primary Use Case:** Event streaming and message processing

## Problem Statement

### Functional Requirements
- Buffer individual messages into batches to reduce network round-trips
- Flush batches based on configurable size (bytes) and time (linger_ms) thresholds
- Compress batches using LZ4, Snappy, or ZSTD before network transmission
- Aggregate stream records into micro-batches for downstream processing
- Track per-batch delivery status and retry failed batches atomically

### Non-Functional Requirements
- **Latency:** P99 < 100ms (depends on system type)
- **Throughput:** 1M+ messages/sec (variable by system)
- **Availability:** 99.99% uptime
- **Consistency:** Exactly-once or at-least-once (configurable)
- **Scalability:** Handle 10x growth seamlessly

## Architecture

### High-Level Design

```mermaid
graph TB
    Producers["Producers<br/>Apps, Services"]
    Brokers["Message Brokers<br/>Kafka, RabbitMQ, Redis"]
    Consumers["Consumers<br/>Processors, Services"]
    Storage["Persistent Storage<br/>Disk, Replication"]
    Cache["Cache Layer<br/>In-memory"]
    Monitor["Monitoring<br/>Metrics, Alerts"]

    Producers -->|Send Messages| Brokers
    Brokers -->|Store| Storage
    Brokers -->|Cache| Cache
    Brokers -->|Consume| Consumers
    Brokers -->|Metrics| Monitor
    Consumers -->|Acknowledge| Brokers
    Storage -->|Replicate| Storage

    style Producers fill:#99ccff
    style Brokers fill:#ffcc99
    style Consumers fill:#99ff99
    style Storage fill:#ff99cc
    style Cache fill:#ffff99
    style Monitor fill:#cc99ff
```

### Core Components

#### Message Broker
- **Function:** Store, manage, and distribute messages
- **Implementations:** Kafka, RabbitMQ, Redis, AWS SQS, GCP Pub/Sub
- **Key Features:** Persistence, replication, partitioning, consumer groups

#### Producers
- **Function:** Send messages to broker
- **Patterns:** Synchronous, asynchronous, batched
- **Concerns:** Acknowledgments, retries, compression

#### Consumers
- **Function:** Receive and process messages
- **Patterns:** Pull vs push, concurrent processing, batch consumption
- **Concerns:** Offset management, lag, ordering, error handling

#### State Management
- **Function:** Track consumer progress and processed messages
- **Approaches:** Offset storage, deduplication cache, exactly-once semantics
- **Storage:** External databases, broker-internal stores

## Data Flow Scenarios

### Scenario 1: Message Publishing
1. Producer sends message with optional key
2. Broker receives and writes to disk
3. Broker replicates to replica nodes
4. Broker acknowledges to producer
5. Message available to consumers

### Scenario 2: Message Consumption
1. Consumer requests messages (pull) or receives (push)
2. Broker delivers batch of messages
3. Consumer processes message
4. Consumer sends acknowledgment
5. Broker updates offset

### Scenario 3: Consumer Group Rebalancing
1. New consumer joins group
2. Broker triggers rebalancing
3. Partitions reassigned to consumers
4. Consumers reset offsets
5. Processing resumes with new distribution

## Scalability Strategies

### Broker Scaling

**Horizontal Scaling:**
- Add broker nodes to cluster
- Distribute partitions across nodes
- Automatic rebalancing
- Increases throughput and fault tolerance

**Vertical Scaling:**
- Increase CPU, memory, disk
- Better compression, faster processing
- Limited by single-node hardware

### Partition Strategy

**Key Selection:**
- Hash-based: Distribute evenly across partitions
- Range-based: Ordered partitions for range queries
- Custom: Domain-specific partitioning logic

**Rebalancing:**
- Add partitions when single partition becomes hot
- Split hot partitions across multiple nodes
- Monitor per-partition throughput

### Consumer Scaling

**Parallel Consumption:**
- One consumer per partition (max)
- Multiple threads per consumer
- Consumer groups distribute load

**Handling Slow Consumers:**
- Increase consumer instances
- Optimize processing logic
- Use faster hardware
- Implement timeout and skip

## High Availability & Reliability

### Replication Strategy

**In-Broker Replication:**
- Multiple copies per partition
- Leader handles writes
- Followers handle reads
- Automatic failover on leader failure

**Cross-Datacenter Replication:**
- Async replication to backup region
- RTO/RPO tradeoffs
- Active-active or active-passive

### Failure Scenarios

**Broker Failure:**
- Detection: Health checks, heartbeats
- Recovery: Replica promotion, partition rebalancing
- Time: 10-30 seconds

**Network Partition:**
- Split-brain scenarios
- Quorum-based decisions
- Consistency vs availability tradeoffs

**Message Loss Prevention:**
- Ack=all (all replicas)
- Min.insync.replicas = 2+
- Periodic backups
- Point-in-time recovery

## Data Consistency

### Delivery Semantics

**At-Most-Once:**
- No duplicates, possible message loss
- Fastest, least reliable
- Use: Non-critical events

**At-Least-Once:**
- No message loss, possible duplicates
- Requires idempotency
- Use: Most applications

**Exactly-Once:**
- No loss, no duplicates
- Slowest, most reliable
- Use: Financial, critical operations

### Ordering Guarantees

**Per-Partition:**
- Single partition = strict ordering
- Trade-off: Limited parallelism

**Per-Key:**
- Hash key to partition
- All messages for key go to same partition
- Enables parallel processing with ordering

**Global Ordering:**
- Single partition (no parallelism)
- Very expensive to maintain
- Usually not needed

## Performance Optimization

### Throughput Optimization

**Batching:**
- Linger time: Wait up to X ms for batch
- Batch size: Send when batch reaches N messages
- Compression: Reduce network bandwidth
- Impact: 10-100x throughput improvement

**Connection Pooling:**
- Reuse connections (don't create per request)
- Reduces overhead, improves latency
- Improves CPU efficiency

**Async Processing:**
- Non-blocking sends
- Pipelining: Multiple in-flight requests
- Callbacks for acknowledgments

### Latency Optimization

**Local Caching:**
- Cache hot messages in memory
- Reduces broker round trips
- Configurable TTL

**Network Optimization:**
- Co-locate producers/brokers
- Reduce network hops
- Multiple broker replicas per region

**Codec Selection:**
- No compression: Fastest
- Snappy: Good compression ratio, fast
- GZIP: Best compression, slower
- LZ4: Fast, moderate compression

## Security

### Authentication & Authorization

**SASL/SSL:**
- Username/password authentication
- Mutual TLS for transport security
- ACLs for topic access control

**OAuth2:**
- Token-based authentication
- Integration with identity providers
- Fine-grained authorization

### Encryption

**In Transit:**
- TLS 1.3 for all connections
- Certificate pinning for sensitive clients

**At Rest:**
- Disk encryption
- Key management (KMS)
- Per-message encryption

### Compliance

**GDPR:**
- Message retention policies
- Right to deletion
- Data residency requirements

**PCI-DSS:**
- Encryption for payment data
- Access controls
- Audit logging

## Monitoring & Observability

### Key Metrics

**Throughput:**
- Messages/sec
- Bytes/sec
- Partition lag

**Latency:**
- End-to-end latency
- Broker latency
- Consumer processing time

**Reliability:**
- Replication lag
- Broker availability
- Message loss events

### Alerting

- Alert on consumer lag > threshold
- Alert on broker latency > P99 target
- Alert on replication lag
- Alert on broker unavailability

### Tracing

- Distributed tracing per message
- Correlation IDs
- Performance bottleneck identification

## Technology Stack

| Component | Options | Recommendation |
|-----------|---------|-----------------|
| **Broker** | Kafka, RabbitMQ, Redis, Pulsar, NATS | Kafka for scalability, RabbitMQ for reliability |
| **Storage** | Disk, Cloud Object Storage | Local disk (fast), S3 for cold storage |
| **Serialization** | Avro, Protobuf, JSON | Avro/Protobuf (schema, compression) |
| **Client Library** | Producer, Consumer SDKs | Official language-specific SDKs |
| **Schema Registry** | Confluent, AWS Glue | Confluent (mature, widely adopted) |
| **Monitoring** | Prometheus, Grafana, DataDog | Prometheus + Grafana (open source) |
| **Orchestration** | Kubernetes, Docker Compose | Kubernetes (production scale) |

## Capacity Planning

### Resource Estimation

**Broker Resources (per 1M msg/sec):**
- CPU: 8+ cores
- Memory: 32GB+ (depends on cache)
- Disk: Depends on retention (100GB+ per day)
- Network: 1+ Gbps

**Consumer Resources (processing 1M msg/sec):**
- CPU: 4-8 cores
- Memory: 16GB+
- Throughput: Process 100K-1M msg/sec per instance

### Cost Calculation

**Broker Costs:**
- Infrastructure: $5K-20K/month for 1M msg/sec
- Storage: $0.10/GB/month (AWS S3 pricing)
- Network egress: $0.12/GB

**Total Monthly Cost:**
- Typical: $10K-50K for mid-scale system
- Large scale: $100K-1M+ per month

## Lessons Learned

1. **Consumer Groups are Powerful:** Use them for scalability and fault tolerance, not just load balancing

2. **Exactly-Once is Expensive:** Use at-least-once with idempotency for most use cases

3. **Consumer Lag is Critical:** Monitor it religiously—it's your early warning system

4. **Partitioning Strategy Matters:** Poor key selection creates hot partitions and limits scalability

5. **Monitoring is Non-Optional:** Without visibility, operational issues become crises

## Common Interview Questions

1. **Design a scalable message queue for 1M messages/sec**
   - Discuss partitioning, replication, consumer groups
   - Address failure scenarios and recovery
   - Explain consistency tradeoffs

2. **How would you handle exactly-once delivery?**
   - Idempotency keys, deduplication, transactions
   - Cost vs benefit analysis
   - Real-world examples (payment systems)

3. **What happens when a consumer fails?**
   - Rebalancing, offset management
   - Recovery procedures
   - Time to recovery

4. **How do you scale a slow consumer?**
   - Add more instances
   - Optimize processing logic
   - Consider batching or windowing
   - Monitor and alert on lag

5. **Design a system with per-message ordering**
   - Key selection, partition strategy
   - Tradeoffs with throughput
   - Alternative approaches

6. **How would you migrate from one broker to another?**
   - Dual writes, validation, cutover
   - Downtime minimization
   - Rollback strategy

## Related Systems

- **Kafka** → For high-throughput, scalable event streaming
- **RabbitMQ** → For reliable, complex message routing
- **Redis Streams** → For fast, simple event streaming
- **AWS Kinesis** → For managed, AWS-integrated streaming
- **GCP Pub/Sub** → For serverless, GCP-integrated messaging

---

**Difficulty:** Intermediate
**Time to Master:** 2-4 weeks
**Prerequisite Knowledge:** Distributed systems, message queues
**Common in Interviews:** Yes - Medium to Hard


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

**Throughput:**
- Kafka throughput per broker: 100MB/sec write
- 1KB messages → 100K msgs/sec per broker
- 10 brokers → 1M msgs/sec cluster throughput
- At 500B messages/day: 500B / 86400 = ~5.8M msgs/sec peak

**Storage:**
- 1M msgs/sec × 1KB = 1GB/sec raw
- 7-day retention: 7 × 86400 × 1GB = 604TB
- With 3x replication: 1.8PB total
- Compression (3:1): reduces to 600TB

**Latency:**
- Produce (acks=1): <5ms p99
- End-to-end (produce → consume): 10-20ms typical
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
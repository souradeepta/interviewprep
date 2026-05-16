# Data Governance

## System Overview

Comprehensive coverage of data governance in modern data analytics systems.

**Scale Metrics:**
- Petabyte-scale analytics, sub-second queries, 1000s QPS

## Architecture

```mermaid
graph TB
    A["Data Sources"]
    B["Ingestion"]
    C["Processing"]
    D["Storage"]
    E["Analytics"]
    F["Visualization"]

    A -->|stream/batch| B
    B -->|transform| C
    C -->|persist| D
    D -->|query| E
    E -->|results| F
```

## Core Concepts

Key aspects of data governance:
- Performance optimization strategies
- Scalability considerations
- Real-world implementation patterns
- Trade-offs and best practices

## Functional Requirements

1. **Data Ingestion** - Multiple data sources
2. **Transformation** - ETL/ELT pipelines
3. **Querying** - Efficient analytics queries
4. **Aggregation** - Pre-computed results
5. **Reporting** - Dashboards and reports
6. **Analysis** - Exploratory analytics

## Non-Functional Requirements

1. **Performance** - Sub-second query latency
2. **Scalability** - Petabyte capacity
3. **Throughput** - 1000s concurrent queries
4. **Availability** - 99.9%+ uptime
5. **Consistency** - Eventual consistency
6. **Cost** - Optimize $/GB

## Back-of-the-Envelope

- 1M users, 100 events/user/day = 100M events
- 1KB per event = 100GB/day
- 3TB/month, 36TB/year
- 10:1 compression = 3.6TB compressed
- 7-year retention = 25TB

## Interview Questions

### Q1: Core design principles?
**Answer:** Focus on partitioning, columnar storage, materialized views, and query optimization to achieve sub-second latency at scale.

### Q2: Performance optimization?
**Answer:** Combine partitioning, column projection, predicate pushdown, and distributed execution for optimal query performance.

### Q3: Scalability strategy?
**Answer:** Horizontal scaling with distributed query execution, data partitioning, and caching layers.

## Technology Stack

- **Warehouses**: Snowflake, BigQuery, Redshift
- **Lakes**: Delta Lake, Iceberg
- **Processing**: Spark, Presto
- **Ingestion**: Kafka, Dataflow
- **Viz**: Tableau, Looker

## Lessons Learned

1. Partition everything - critical for performance
2. Columnar storage - 10x scan speedup
3. Materialized views - fast reporting
4. Monitor costs - storage grows quickly
5. Test at scale - plan ahead


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
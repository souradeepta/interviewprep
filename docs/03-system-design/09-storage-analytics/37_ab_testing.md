# A/B Testing

## System Overview

Comprehensive coverage of A/B testing in modern data analytics systems.

**Scale Metrics:**
- Petabyte-scale analytics, sub-second queries, 1000s QPS

## Architecture

```mermaid
graph TB
    A["Users"]
    B["Randomization"]
    C["Control/Variant"]
    D["Metrics Collection"]
    E["Analysis"]
    F["Decision"]

    A -->|assign| B
    B -->|allocate| C
    C -->|track| D
    D -->|analyze| E
    E -->|conclude| F
```

## Core Concepts

Key aspects of A/B testing:
- Proper randomization and assignment
- Sample size calculation for statistical power
- Metric definition and collection
- Statistical significance testing
- Multiple comparison correction
- Confidence interval estimation

## Functional Requirements

1. **Randomization** - Fair user assignment to variants
2. **Tracking** - Reliable metric collection
3. **Analysis** - Statistical significance testing
4. **Reporting** - Clear results presentation
5. **Monitoring** - Real-time experiment tracking
6. **Compliance** - User privacy protection

## Non-Functional Requirements

1. **Accuracy** - Statistically valid results
2. **Speed** - Quick experiment setup
3. **Reliability** - No data loss during experiment
4. **Scalability** - Handle millions of users
5. **Cost** - Efficient metric collection
6. **Privacy** - Comply with data protection

## Back-of-the-Envelope

- 10M daily active users
- 50% allocated to experiment
- 5M per variant (5M control, 5M variant)
- 10% baseline conversion rate
- 50K daily conversions per variant
- 2-week experiment duration = 700K conversions per variant

## Interview Questions

### Q1: How do you calculate sample size?
**Answer:** Use power analysis: need enough samples to detect minimum effect size with 80% power and 5% significance level.

### Q2: How do you handle multiple comparisons?
**Answer:** Bonferroni correction divides significance threshold by number of tests.

### Q3: What are common pitfalls?
**Answer:** Peeking at results, not accounting for multiple comparisons, insufficient sample size, and user overlap.

## Technology Stack

- **Platforms**: Optimizely, LaunchDarkly, VWO
- **Analytics**: R, Python, Tableau
- **Stats**: scipy.stats, statsmodels

## Lessons Learned

1. Power calculation essential - prevents underpowered tests
2. Longer experiments better - captures user heterogeneity
3. Monitor for bugs - data quality issues hidden at scale
4. Consider novelty effect - short-term behavior changes
5. Statistical vs practical significance - 1% improvement might not matter


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
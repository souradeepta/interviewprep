# Circuit Breaker

**Level:** L3-L5+
**Time to read:** ~30 min

## Problem Statement

When a downstream service is slow or failing, naive retry logic makes things worse: threads pile up waiting for timeouts, exhausting the thread pool and taking the caller down as well. The circuit breaker pattern is an automatic protective switch that detects sustained failure and stops sending traffic to an unhealthy dependency, giving it time to recover without cascading failures upstream.

The name comes from electrical engineering: a circuit breaker trips when current exceeds a safe threshold, protecting the wiring. When the fault is cleared, the breaker resets and current flows again.

## Functional Requirements

- Track per-dependency error rates and latency over a rolling time window
- Automatically open (trip) the circuit when the error rate exceeds a threshold
- Stop forwarding requests to the dependency while the circuit is open
- After a recovery timeout, probe the dependency with limited traffic (half-open)
- Close the circuit when probes succeed; re-open if probes fail

## Non-Functional Requirements

- **Scale:** 100K RPS per service, each call potentially guarded by a circuit breaker
- **Latency:** Circuit breaker overhead must be <1ms per request (in-memory state machine)
- **Availability:** Circuit state must survive process restart (durable or fast-rebuild)
- **Consistency:** Per-instance or per-cluster state acceptable; eventual convergence fine

---

## Tier 1: L3-L4 Design (the basic interview answer)

### Back-of-Envelope

```
Service: 100K RPS calling Payment API
Failure scenario: Payment API starts timing out at 500ms (normally 20ms P99)
Without circuit breaker:
  - Thread pool: 200 threads
  - Concurrent requests: 100K * 0.5s = 50K in-flight
  - Thread exhaustion: 50K >> 200 threads → service dies in ~1 second

With circuit breaker (60s error window, 50% threshold):
  - After 60s window closes with 50% errors, circuit opens
  - Requests fast-fail with CircuitOpenError in <1ms
  - Thread pool never saturates
  - Recovery: after 30s timeout, 5 probe requests sent to Payment API
  - If probes succeed → circuit closes; if fail → stay open another 30s

State storage:
  - Per-circuit state: 50 bytes (state + counters + timestamps)
  - 100 dependencies * 50 bytes = 5 KB total RAM (trivial)
```

### Architecture Diagram

```
                    +-----------+
Client Request ---> | Circuit   |
                    | Breaker   |
                    | State:    |
                    | CLOSED    |
                    +-----------+
                         |
             +-----------+-----------+
             |                       |
        [State: CLOSED]       [State: OPEN]
             |                       |
             v                       v
    Forward to                Fast-fail with
    Dependency               CircuitOpenError
             |                (skip network call)
             v
    Success? → count success
    Error?   → count failure
    P99 >threshold? → count slow

         [Error rate > 50% over 60s] → OPEN

                    [OPEN state]
                         |
                [Wait recovery_timeout=30s]
                         |
                         v
                   [HALF-OPEN state]
                         |
              Allow N=5 probe requests
                         |
               +---------+---------+
               |                   |
          All probes           Any probe
           succeed               fails
               |                   |
               v                   v
           CLOSED               OPEN
          (normal)           (reset timer)

State Machine:
  CLOSED    → OPEN       when: error_rate > threshold during window
  OPEN      → HALF-OPEN  when: recovery_timeout elapses
  HALF-OPEN → CLOSED     when: all probe requests succeed
  HALF-OPEN → OPEN       when: any probe request fails
```

### Data Model

```python
from dataclasses import dataclass, field
from enum import Enum
import time

class State(Enum):
    CLOSED    = "CLOSED"
    OPEN      = "OPEN"
    HALF_OPEN = "HALF_OPEN"

@dataclass
class CircuitBreakerState:
    name: str                        # Dependency identifier, e.g., "payment-api"
    state: State = State.CLOSED

    # Rolling window counters (reset every window_seconds)
    window_seconds: int = 60
    window_start: float = field(default_factory=time.time)
    success_count: int = 0
    failure_count: int = 0
    slow_count: int = 0              # Latency > slow_threshold_ms

    # Thresholds
    error_rate_threshold: float = 0.50   # 50% errors → open
    slow_threshold_ms: float = 200.0     # Requests slower than this count as slow
    min_requests_in_window: int = 10     # Don't open on 1 failure out of 1 request

    # Recovery
    recovery_timeout_seconds: float = 30.0
    opened_at: float = 0.0           # When circuit was opened
    probe_limit: int = 5             # Max probes in HALF_OPEN
    probes_sent: int = 0
    probes_succeeded: int = 0

# Redis hash for cluster-shared state (optional — see Tier 2):
# HSET circuit:payment-api state OPEN opened_at 1716912345 ...
```

### API Design

```
# Internal circuit breaker API (used by service mesh or SDK)

GET  /circuits
  Response: [{ name, state, error_rate, last_state_change }]

GET  /circuits/{name}
  Response: { name, state, window_errors, window_requests, opened_at, recovery_in_seconds }

POST /circuits/{name}/force-open
  Body: { reason: "maintenance" }
  Response: { state: "OPEN" }

POST /circuits/{name}/force-close
  Body: { reason: "rollback complete" }
  Response: { state: "CLOSED" }

POST /circuits/{name}/reset
  Response: { state: "CLOSED", counters_reset: true }

# Webhook: circuit state changes trigger alerts
POST <configured_webhook_url>
  Body: { circuit: "payment-api", from: "CLOSED", to: "OPEN",
          error_rate: 0.63, window_requests: 4500, timestamp: "..." }
```

### Basic Scaling

- Keep circuit breaker state in-process (memory) for lowest overhead — <1ms per check
- Share state across instances via Redis if you need cluster-level circuit opening
- One circuit breaker per dependency per service (not per endpoint — too granular at L4)
- Use a thread-safe ring buffer or sliding window for the rolling counter, not locks
- Expose circuit state via /health endpoint so load balancers can route around broken services

---

## Tier 2: L5+ Design (the staff interview answer)

### Capacity Planning (Real Numbers)

```
Service: 50 instances, each at 100K RPS, 20 dependencies

Per-instance in-memory state:
  - 20 circuits * 200 bytes per circuit = 4 KB RAM (trivial)
  - Rolling window (ring buffer, 60 slots of 1-second buckets):
    20 circuits * 60 slots * 16 bytes = ~20 KB RAM

Redis shared state (optional, for cluster awareness):
  - 20 circuits * 200 bytes = 4 KB total in Redis
  - Update frequency: 1 write/sec per circuit per instance (50 instances * 20 circuits = 1K writes/sec)
  - Redis write throughput easily handles this

Probe traffic when HALF-OPEN:
  - N=5 probes * 50 instances = 250 probes total per circuit per recovery cycle
  - If dependency handles 10K RPS normally, 250 probes is 2.5% load — safe

Telemetry:
  - 20 circuits * 50 instances = 1000 circuit-state metrics per collection interval
  - At 15s Prometheus scrape: 1000 / 15 = 67 metric vectors/sec → negligible
```

### Failure Modes

```
Failure: Thundering herd on circuit close
  Impact: All 50 instances close simultaneously → 50 * 100K = 5M RPS hits recovered dep
  Mitigation:
    - Stagger recovery timeout with jitter: recovery_timeout = 30s + random(0, 10s)
    - HALF-OPEN state limits traffic: only N=5 probes per instance, not full RPS
    - Exponential backoff on re-open: 30s → 60s → 120s recovery timeout after repeated opens

Failure: Circuit opens on a transient network blip (false positive)
  Impact: Healthy dependency gets blocked; users see errors unnecessarily
  Mitigation:
    - Minimum request volume: don't open on 1 error out of 1 request
    - Use 2-minute rolling window instead of 1-minute for lower false positive rate
    - Distinguish retryable vs non-retryable errors: 429, 503 count as errors;
      400 Bad Request should NOT count (it's a client bug, not dep failure)
    - Half-open probes quickly verify actual health before committing to CLOSED

Failure: Slow dependency instead of failing dependency
  Impact: 50% error threshold never triggered, but threads pile up on 500ms responses
  Mitigation:
    - Add slow_call_rate threshold: if >50% of calls exceed slow_threshold_ms → open
    - Set aggressive per-request timeouts (200ms for Payment, 50ms for User lookup)
    - Track P99 latency in sliding window; open on latency spike even without errors

Failure: Circuit breaker state lost on instance restart
  Impact: New instance starts with CLOSED state even though dep is still failing
  Mitigation:
    - New instance starts with a "WARMING" mode: smaller minimum request volume (N=2)
      before opening, so it quickly detects ongoing failures within seconds
    - Or load state from Redis on startup — instance inherits cluster consensus
```

### Consistency Boundaries

```
Per-instance vs cluster-level circuits:
  - Per-instance (default): each pod has its own circuit state
    Pro: zero coordination overhead, fastest response
    Con: 50 pods may have 50 different circuit states; some see dep as healthy, others don't
    Use when: dependency failure is evenly distributed (e.g., whole dep is down)

  - Cluster-level: circuit state in Redis, all instances share one view
    Pro: consistent behavior; one instance's probe informs all others
    Con: Redis becomes a dependency for every API call; adds 0.5ms overhead
    Use when: dependency failure is selective (e.g., only some shards are failing)

Recommendation for L5+ answer:
  - Use per-instance circuits with cluster-level aggregation for alerting
  - If >30% of instances report OPEN for same circuit → page on-call
  - Reserve Redis-backed circuits for API gateways that need uniform behavior
```

### Cost Model

```
Without circuit breaker (cascade failure scenario):
  - Service uses 200 threads; Payment API at 500ms timeout
  - Thread exhaustion in 1s → service goes down → upstream services go down
  - MTTR: 15 minutes (detection + rollback) * 20 affected services = hours of downtime
  - Cost: $50K/hour revenue loss * 2 hours = $100K per incident

With circuit breaker:
  - Failure isolated to Payment API; upstream services return degraded (non-payment) responses
  - MTTR for payment: 15 minutes; rest of service unaffected
  - Cost of circuit breaker: ~0 (pure in-memory; no additional infrastructure)
  - Cost saved per incident: $90K+

Adaptive thresholds (ML-based, advanced):
  - Track baseline error rate per circuit per time-of-day (weekday vs weekend)
  - Open circuit when current rate > 3 standard deviations above baseline
  - Reduces false positives by 40% (from 2/week to 1.2/week at 100K RPS scale)
  - Implementation: 1 Prometheus recording rule + 1 alertmanager webhook → circuit API
```

---

## Trade-off Comparison

| Approach                     | Pros                                             | Cons                                                  | Best For                               |
|------------------------------|--------------------------------------------------|-------------------------------------------------------|----------------------------------------|
| In-process circuit breaker   | Zero overhead, no dependencies                   | State not shared across instances                     | Most microservices (default choice)    |
| Redis-backed circuit breaker | Cluster-consistent state                         | Adds Redis as critical dependency to every call       | API gateways, uniform rate limiting    |
| Service mesh (Envoy/Istio)   | Language-agnostic, transparent to app code       | Operational complexity, requires service mesh infra   | Polyglot orgs, platform teams          |
| Timeout-only (no circuit)    | Simple to implement                              | Threads pile up; cascades on sustained failures       | Never sufficient alone                 |
| Bulkhead + circuit breaker   | Thread pool isolation + failure detection        | More configuration, more overhead                    | Services with heterogeneous dependency latencies |
| Adaptive threshold (ML)      | Fewer false positives, adapts to traffic patterns| Complex to implement and operate                      | Very high-scale platforms (>1M RPS)   |

## Follow-up Questions (escalating difficulty, 7 minimum)

1. **(L3)** What are the three states of a circuit breaker?
   → CLOSED (normal operation, traffic flows), OPEN (circuit tripped, all requests fast-fail), HALF-OPEN (recovery probe — limited traffic allowed to test dependency health).

2. **(L3)** Why does a circuit breaker use a time window rather than a total error count?
   → A total count never resets, so an occasional error from months ago would keep the circuit permanently close to opening. A rolling time window (e.g., 60 seconds) means only recent errors count, letting the circuit reflect the dependency's current health rather than historical bad days.

3. **(L4)** How do you choose the error rate threshold and window size?
   → Start with 50% error rate over 60 seconds with a minimum of 10 requests. Tune based on: how noisy the dependency is normally (high baseline error rate means higher threshold), how fast you need to react (shorter window = faster detection but more false positives), and what degraded mode your service supports. Track false positive rate (circuit opens when dep is actually healthy) and adjust threshold upward if too many.

4. **(L4)** What types of errors should NOT count toward the circuit breaker threshold?
   → 4xx client errors (400, 401, 404) indicate a bug in the caller, not a failure in the dependency. Counting them would open the circuit due to caller bugs rather than downstream failure. Only 5xx server errors, connection timeouts, and connection refused should count. Also exclude intentional rate-limit errors (429) if your design uses them for backpressure rather than failure.

5. **(L5)** How does the bulkhead pattern complement circuit breakers?
   → A circuit breaker stops sending traffic to a failing dependency. A bulkhead limits how many concurrent threads/requests can be in-flight to any given dependency. Together: the bulkhead prevents thread exhaustion (even before the circuit opens) while the circuit breaker prevents wasted retries on a clearly failing dep. For example, limit the Payment API thread pool to 20 threads (bulkhead) and open the circuit after 50% errors in 60 seconds (circuit breaker). The bulkhead protects from slow degradation; the circuit breaker handles acute failure.

6. **(L5)** How would you implement a circuit breaker that adapts its threshold based on time-of-day traffic patterns?
   → Store a baseline error rate per circuit per hour-of-week (7 days * 24 hours = 168 slots). At each measurement window, compute z-score: `z = (current_error_rate - baseline_mean) / baseline_stddev`. Open the circuit when z > 3 (3 standard deviations above baseline). This allows a 2% error rate at normal load but opens at 4% during a traffic peak when 2% was the historical baseline. Update baselines using exponential moving average with decay factor 0.95 to weight recent data more. This reduces false positives by ~40% at scale.

7. **(L5+)** In a service mesh where Envoy proxies handle circuit breaking, what is the tradeoff vs. application-level circuit breakers?
   → Service mesh circuit breakers (Envoy outlier detection) operate at the connection/request level and are language-agnostic, but they lack application semantics: they cannot distinguish 400 vs 500, they cannot consider business-specific slow call thresholds, and they cannot trigger application-level fallback behavior (e.g., return cached response). Application-level circuit breakers (Resilience4j, custom) have full access to response content and can trigger fallbacks, but must be implemented in every language your org uses. Best practice for L5+ orgs: use service mesh for infrastructure-level protection (connection failures, egress timeouts) and application-level circuit breakers for business-semantic protection (error type classification, graceful degradation). They stack, providing defense in depth.

## Anti-patterns / Things NOT to Say

- **"Set the error threshold to 100% so the circuit only opens on complete outages"** — At 100%, every request must fail before the circuit opens, by which time your thread pool is already exhausted. The purpose of the circuit breaker is early detection. 50% is a common starting point; tune down to 30% for critical dependencies.
- **"Use the same circuit breaker for all endpoints of a dependency"** — This is actually correct for L4, but at L5+ you should know when per-endpoint circuits make sense. If `/health` is always fast but `/compute-risk` is slow under load, a single circuit for the entire dep would trip on `/compute-risk` slowness and also block `/health` checks. Separate circuits for endpoints with very different SLAs is appropriate.
- **"Circuit breakers eliminate the need for retries"** — They work together. Retries handle transient errors (single bad packet, brief hiccup). Circuit breakers handle sustained failures (dep is down for minutes). Use retries with exponential backoff + jitter for transient errors; let the circuit breaker stop retries during sustained outages. Without circuit breakers, retries on a dead dependency create retry storms.
- **"Circuit breaker state should be strongly consistent across all instances"** — Strong consistency requires coordination overhead on every request (Redis write + read). For most services, per-instance circuits with aggregate alerting are sufficient. The extra latency of strong consistency is almost never worth it. Accept that different instances may see different circuit states for up to 60 seconds.
- **"Open the circuit immediately on the first error"** — This causes false positives from transient errors. Always require a minimum request volume (e.g., N=10) and sustained error rate (e.g., 50% over 60s) before opening. One 503 response should never trip the circuit.

## Python Implementation (sketch)

```python
import time
import threading
from collections import deque
from enum import Enum

class State(Enum):
    CLOSED    = "CLOSED"
    OPEN      = "OPEN"
    HALF_OPEN = "HALF_OPEN"

class CircuitBreaker:
    """Thread-safe circuit breaker with sliding window error rate tracking."""

    def __init__(self, name: str, error_threshold: float = 0.5,
                 window_seconds: int = 60, min_requests: int = 10,
                 recovery_timeout: float = 30.0, probe_limit: int = 5,
                 slow_threshold_ms: float = 200.0):
        self.name = name
        self.error_threshold = error_threshold
        self.window_seconds = window_seconds
        self.min_requests = min_requests
        self.recovery_timeout = recovery_timeout
        self.probe_limit = probe_limit
        self.slow_threshold_ms = slow_threshold_ms

        self._state = State.CLOSED
        self._lock = threading.Lock()
        # Ring buffer: (timestamp, is_success)
        self._window: deque = deque()
        self._opened_at: float = 0.0
        self._probes_sent: int = 0

    @property
    def state(self) -> State:
        with self._lock:
            return self._evaluate_state()

    def _evaluate_state(self) -> State:
        """Must be called with self._lock held."""
        if self._state == State.OPEN:
            if time.monotonic() - self._opened_at >= self.recovery_timeout:
                self._state = State.HALF_OPEN
                self._probes_sent = 0
        return self._state

    def call(self, fn, *args, **kwargs):
        """Execute fn through the circuit breaker."""
        with self._lock:
            state = self._evaluate_state()

            if state == State.OPEN:
                raise CircuitOpenError(f"Circuit {self.name} is OPEN")

            if state == State.HALF_OPEN:
                if self._probes_sent >= self.probe_limit:
                    raise CircuitOpenError(f"Circuit {self.name} probe limit reached")
                self._probes_sent += 1

        start = time.monotonic()
        try:
            result = fn(*args, **kwargs)
            elapsed_ms = (time.monotonic() - start) * 1000
            is_slow = elapsed_ms > self.slow_threshold_ms
            self._record(success=not is_slow)
            return result
        except Exception as exc:
            self._record(success=False)
            raise

    def _record(self, success: bool):
        now = time.monotonic()
        cutoff = now - self.window_seconds

        with self._lock:
            self._window.append((now, success))
            # Evict old entries
            while self._window and self._window[0][0] < cutoff:
                self._window.popleft()

            total = len(self._window)
            if total < self.min_requests:
                return  # Not enough data to make a decision

            failures = sum(1 for _, ok in self._window if not ok)
            error_rate = failures / total

            if self._state == State.CLOSED and error_rate >= self.error_threshold:
                self._state = State.OPEN
                self._opened_at = now
                print(f"[CircuitBreaker] {self.name} OPENED (error_rate={error_rate:.2f})")

            elif self._state == State.HALF_OPEN:
                if success:
                    # Check if all probes succeeded
                    if self._probes_sent >= self.probe_limit:
                        self._state = State.CLOSED
                        self._window.clear()
                        print(f"[CircuitBreaker] {self.name} CLOSED (recovery success)")
                else:
                    self._state = State.OPEN
                    self._opened_at = now
                    print(f"[CircuitBreaker] {self.name} re-OPENED (probe failed)")

class CircuitOpenError(Exception):
    pass
```

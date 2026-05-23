# Distributed Tracing & Observability

Track requests across microservices and databases to diagnose latency issues, identify bottlenecks, and understand system behavior at scale.

---

## ⚖️ Tracing Strategy Trade-offs

### Sampling Strategy Comparison

| Strategy | Coverage | Cost | Latency Overhead | Miss Rate | Best For |
|----------|----------|------|---|---|---|
| **Full (100%)** | All requests | Very High | 5–15ms | 0% | Dev/staging |
| **Head-based %** | Random 1–10% | Low | <1ms | 90–99% | General prod |
| **Tail-based** | Slow + error only | Medium | <1ms | Low for outliers | Latency debugging |
| **Adaptive** | Dynamic rate | Medium | <1ms | Adjusts live | Production at scale |
| **Per-user** | VIP users 100% | Medium | <1ms | OK for most | Enterprise SLAs |

### Tool Comparison

| Tool | Deploy | Storage | UI | Best For |
|------|--------|---------|----|----------|
| **Jaeger** | Self-hosted | Cassandra / Elasticsearch | Good | Open-source, Kubernetes |
| **Zipkin** | Self-hosted | MySQL / Elasticsearch | Basic | Simple setups |
| **OpenTelemetry** | Vendor-agnostic | Any backend | N/A (protocol only) | Standardization |
| **Datadog APM** | SaaS | Managed | Excellent | Enterprises |
| **AWS X-Ray** | Managed | Managed | Good | AWS-native stacks |
| **Tempo + Grafana** | Self-hosted | Object storage | Excellent | Prometheus shops |

### Overhead Budget

```
Per-request tracing cost:
  Span creation:       ~0.1ms CPU, ~200 bytes memory
  Context propagation: ~0.01ms (just header add/read)
  Async export:        ~0ms impact (background goroutine)
  Backend write:       ~1–5ms (if synchronous — avoid!)
  
At 10K RPS with 5 spans/req:
  Spans/sec:    50K
  Memory/sec:   10MB (transient)
  Disk/sec:     ~25MB (with metadata)
  Storage/day:  ~2 TB at full rate → Use sampling!
```

---

## 🏗️ Architecture Patterns

### Pattern 1: OpenTelemetry Pipeline (Standard)

```
App Service A              App Service B
     │                          │
  [OTel SDK]               [OTel SDK]
     │                          │
     └──────────┬───────────────┘
                ↓
         [OTel Collector]        ← Receives, processes, batches
                ↓
    ┌───────────┴───────────┐
    │                       │
 [Jaeger]            [Prometheus]
  (traces)             (metrics)
    │                       │
    └──────────┬────────────┘
               ↓
           [Grafana]           ← Unified observability UI
```

### Pattern 2: Trace Propagation Across Services

```
Incoming HTTP request
  Headers: { x-trace-id: "abc123", x-span-id: "span1" }
       │
  [API Gateway]  → creates child span "gateway_check"
       │              carries: trace_id=abc123, parent=span1
       ↓
  [Auth Service] → creates child span "auth_validate"
       │              carries: trace_id=abc123, parent=gateway_check
       ↓
  [DB Query]     → creates child span "db_select_user"
       │              carries: trace_id=abc123, parent=auth_validate
       ↓
  All spans share trace_id → reconstructed as a single trace tree
```

### Pattern 3: Tail-Based Sampling

```
All spans buffered 30 sec in collector:

Request A: 45ms total  → DROP (below threshold)
Request B: 3200ms total → KEEP (slow, send to Jaeger)
Request C: 120ms, error → KEEP (has error)
Request D: 80ms total  → DROP

Result: Only ~5% of spans stored, but 100% of problems captured
Cost: 20x less storage vs. full tracing
```

---

## 📊 Span Model & Instrumentation

### Span Fields

```python
import uuid
import time
from typing import Optional, Dict, List

class Span:
    def __init__(self, name: str, trace_id: str, parent_span_id: Optional[str] = None):
        self.name = name
        self.trace_id = trace_id
        self.span_id = uuid.uuid4().hex[:16]
        self.parent_span_id = parent_span_id
        self.start_time = time.time()
        self.end_time: Optional[float] = None
        self.tags: Dict[str, str] = {}
        self.logs: List[dict] = []
        self.status = "ok"  # ok | error

    def set_tag(self, key: str, value: str):
        self.tags[key] = value

    def log_event(self, message: str, **fields):
        self.logs.append({"ts": time.time(), "msg": message, **fields})

    def set_error(self, exc: Exception):
        self.status = "error"
        self.set_tag("error", "true")
        self.log_event("error", message=str(exc), type=type(exc).__name__)

    def finish(self) -> float:
        self.end_time = time.time()
        return self.duration_ms()

    def duration_ms(self) -> float:
        end = self.end_time or time.time()
        return (end - self.start_time) * 1000

    def to_dict(self) -> dict:
        return {
            "traceId": self.trace_id,
            "spanId": self.span_id,
            "parentSpanId": self.parent_span_id,
            "name": self.name,
            "startTime": int(self.start_time * 1e9),  # nanoseconds
            "duration": int(self.duration_ms() * 1e6),  # nanoseconds
            "tags": self.tags,
            "logs": self.logs,
            "status": self.status,
        }
```

### Tracer with Context Propagation

```python
import contextvars
from typing import Optional

_current_span: contextvars.ContextVar[Optional[Span]] = contextvars.ContextVar(
    "_current_span", default=None
)

class Tracer:
    def __init__(self, service_name: str, exporter=None):
        self.service_name = service_name
        self.exporter = exporter or PrintExporter()
        self._spans: List[Span] = []

    def start_span(self, name: str, parent: Optional[Span] = None) -> Span:
        # Inherit from context if not provided
        if parent is None:
            parent = _current_span.get()

        trace_id = parent.trace_id if parent else uuid.uuid4().hex
        parent_id = parent.span_id if parent else None
        span = Span(name, trace_id, parent_id)
        span.set_tag("service", self.service_name)
        return span

    def finish_span(self, span: Span):
        span.finish()
        self._spans.append(span)
        self.exporter.export(span)

    def trace(self, name: str):
        """Decorator for automatic span lifecycle management."""
        def decorator(fn):
            def wrapper(*args, **kwargs):
                parent = _current_span.get()
                span = self.start_span(name, parent=parent)
                token = _current_span.set(span)
                try:
                    result = fn(*args, **kwargs)
                    return result
                except Exception as e:
                    span.set_error(e)
                    raise
                finally:
                    _current_span.reset(token)
                    self.finish_span(span)
            return wrapper
        return decorator

class PrintExporter:
    def export(self, span: Span):
        print(f"[TRACE] {span.name:<30} {span.duration_ms():.1f}ms  trace={span.trace_id[:8]} status={span.status}")

# ── Demo ──────────────────────────────────────────────────────────────────────
tracer = Tracer("order-service")

@tracer.trace("handle_order")
def handle_order(order_id: int):
    validate_order(order_id)
    charge_payment(order_id)

@tracer.trace("validate_order")
def validate_order(order_id: int):
    time.sleep(0.02)   # simulate 20ms DB read

@tracer.trace("charge_payment")
def charge_payment(order_id: int):
    time.sleep(0.15)   # simulate 150ms payment gateway

handle_order(42)
```

**Expected output:**
```
[TRACE] validate_order                 20.4ms  trace=3f7a91c2 status=ok
[TRACE] charge_payment                150.2ms  trace=3f7a91c2 status=ok
[TRACE] handle_order                  171.3ms  trace=3f7a91c2 status=ok
```

---

## 🔍 Sampling Strategies

### Head-Based (Simple %)

```python
import random

class HeadSampler:
    def __init__(self, rate: float = 0.01):  # 1% default
        self.rate = rate

    def should_sample(self) -> bool:
        return random.random() < self.rate
```

### Tail-Based (Keep Slow + Errors)

```python
import time
from collections import defaultdict

class TailSampler:
    """Buffer spans for N seconds, then decide based on outcome."""

    def __init__(self, buffer_secs=30, latency_threshold_ms=500):
        self.buffer: Dict[str, List[Span]] = defaultdict(list)
        self.buffer_secs = buffer_secs
        self.latency_threshold_ms = latency_threshold_ms

    def add_span(self, span: Span):
        self.buffer[span.trace_id].append(span)

    def flush(self) -> List[List[Span]]:
        """Return traces that should be kept."""
        kept = []
        for trace_id, spans in list(self.buffer.items()):
            root = next((s for s in spans if s.parent_span_id is None), None)
            if root and self._should_keep(spans, root):
                kept.append(spans)
        self.buffer.clear()
        return kept

    def _should_keep(self, spans: List[Span], root: Span) -> bool:
        # Keep if any span has an error
        if any(s.status == "error" for s in spans):
            return True
        # Keep if total latency exceeds threshold
        if root.duration_ms() > self.latency_threshold_ms:
            return True
        return False
```

---

## 📈 Performance Metrics to Track

### Key Tracing Metrics

```
Latency breakdown (p50 / p95 / p99):
  API handler:      12ms / 45ms / 120ms
  Auth check:        3ms /  8ms /  25ms
  DB query:          5ms / 20ms / 200ms  ← watch this
  Cache hit:        <1ms /  2ms /   5ms
  External call:    50ms / 150ms / 500ms

RED metrics per service:
  Rate:    requests/sec
  Errors:  error_count / total_count  (target: <0.1%)
  Duration: p99 latency              (target: <500ms)
```

---

## ❓ Interview Q&A

**Q1: Request takes 5 seconds end-to-end. How do you debug?**

A: With distributed tracing, pull the trace for that request ID:
```
Trace tree:
  handle_request       5020ms  ← total
  ├─ auth_check           8ms  ✓
  ├─ fetch_user          12ms  ✓
  ├─ load_recommendations 4900ms  ← BOTTLENECK
  │   ├─ db_query_recs   4850ms  ← sequential N+1!
  │   └─ sort_results      50ms
  └─ serialize_response    100ms
```
Root cause: N+1 query in `load_recommendations` — 50 individual DB calls.
Fix: Batch query `SELECT * FROM recs WHERE user_id IN (...)`.

**Q2: You want 100% coverage for errors but only 1% for normal traffic. Design it.**

A: Tail-based sampling:
1. Buffer all spans in the OTel Collector for 30 seconds
2. At flush time, inspect each trace:
   - If any span has `status=error` → export 100%
   - If root span > 500ms → export 100%
   - Otherwise → export 1% (random)
3. Cost: 2× storage vs. 1% flat (worth it for full error coverage)
Tooling: Grafana Tempo's tail-based sampling, or OTel Collector's `tailsampling` processor.

**Q3: How do you propagate trace context across a Kafka message?**

A: Inject span context into message headers using W3C TraceContext format:
```python
# Producer (inject)
headers = {}
span.context.inject(headers)  # adds traceparent header
producer.send("orders", value=payload, headers=list(headers.items()))

# Consumer (extract)
ctx = propagate.extract(dict(msg.headers))
with tracer.start_as_current_span("process_order", context=ctx):
    process(msg.value)
```
This links the consumer span as a child of the producer span across the async boundary.

**Q4: Tracing is adding 15ms to every request. How to get it under 1ms?**

A: The culprit is synchronous span export. Fix:
1. **Async export**: batch spans in memory, flush every 5 seconds in background thread
2. **Reduce span count**: only instrument service boundaries (not every function call)
3. **UDP transport**: instead of HTTP, use UDP to Jaeger agent (fire-and-forget, 0ms block)
4. **Sampling**: 1% head sampling eliminates 99% of export work

**Q5: How would you build alerting on trace data?**

A: Two approaches:
- **Metric-derived**: Export RED metrics (rate, error, duration) from spans to Prometheus → alert on p99 > 500ms
- **Trace-derived**: Query Jaeger/Tempo for error traces every 60s → PagerDuty if error rate rises
Best practice: derive metrics from traces (Tempo + Prometheus exemplars), then alert on metrics — trace data is for diagnosis, not alerting.

**Q6: Sampling means you might miss a rare bug. How to guarantee capture of important traces?**

A: Force-sample strategy:
1. Add `x-force-trace: true` header in your test suite and canary requests — sampler checks this
2. Always sample requests carrying correlation IDs from support tickets
3. Always sample the first N requests per new deploy (detect regressions)
4. Log correlation IDs in application logs — even unsampled requests leave a breadcrumb

---

## 🧪 Practical Exercises

### Exercise 1: Build a Flame Graph from Raw Spans (Easy)

**Problem:** Given a list of spans (trace_id, span_id, parent_id, name, start_ms, end_ms), reconstruct the call tree and compute % time in each span.

**Solution:**

```python
from typing import List, Optional, Dict
from dataclasses import dataclass, field

@dataclass
class SpanData:
    span_id: str
    parent_id: Optional[str]
    name: str
    start_ms: float
    end_ms: float
    children: List['SpanData'] = field(default_factory=list)

    @property
    def duration(self) -> float:
        return self.end_ms - self.start_ms

def build_flame_graph(spans: List[dict]) -> SpanData:
    """Build a tree from flat span list."""
    nodes = {s["span_id"]: SpanData(**{k: s[k] for k in s if k != "children"}) for s in spans}
    root = None
    for node in nodes.values():
        if node.parent_id is None:
            root = node
        elif node.parent_id in nodes:
            nodes[node.parent_id].children.append(node)
    return root

def print_flame(span: SpanData, total: float, depth: int = 0):
    pct = span.duration / total * 100
    bar = "█" * int(pct / 2)
    indent = "  " * depth
    print(f"{indent}{span.name:<30} {span.duration:6.0f}ms  {pct:5.1f}%  {bar}")
    for child in sorted(span.children, key=lambda s: s.start_ms):
        print_flame(child, total, depth + 1)

# Test data
spans = [
    {"span_id": "s1", "parent_id": None,  "name": "handle_request",       "start_ms": 0,   "end_ms": 520},
    {"span_id": "s2", "parent_id": "s1",  "name": "auth_check",            "start_ms": 1,   "end_ms": 9},
    {"span_id": "s3", "parent_id": "s1",  "name": "load_recommendations",  "start_ms": 10,  "end_ms": 490},
    {"span_id": "s4", "parent_id": "s3",  "name": "db_query_recs",         "start_ms": 10,  "end_ms": 450},
    {"span_id": "s5", "parent_id": "s3",  "name": "sort_results",          "start_ms": 451, "end_ms": 490},
    {"span_id": "s6", "parent_id": "s1",  "name": "serialize_response",    "start_ms": 491, "end_ms": 520},
]

root = build_flame_graph(spans)
print_flame(root, root.duration)
```

**Expected output:**
```
handle_request                  520ms  100.0%  ██████████████████████████████████████████████████
  auth_check                      8ms    1.5%  
  load_recommendations           480ms   92.3%  ██████████████████████████████████████████████
    db_query_recs                440ms   84.6%  ██████████████████████████████████████████
    sort_results                  39ms    7.5%  ███
  serialize_response              29ms    5.6%  ██
```

---

### Exercise 2: Tail-Based Sampler (Medium)

**Problem:** 100K requests/sec. Only store traces with p99 latency (>500ms) or errors. Build the sampler with configurable thresholds.

**Solution:**

```python
import time, uuid, random
from collections import defaultdict
from typing import List, Dict

class TailBasedSampler:
    def __init__(self, latency_ms: float = 500, error_sample_rate: float = 1.0,
                 normal_sample_rate: float = 0.01, buffer_secs: float = 5):
        self.latency_ms = latency_ms
        self.error_rate = error_sample_rate
        self.normal_rate = normal_sample_rate
        self.buffer_secs = buffer_secs
        self.buffer: Dict[str, dict] = {}   # trace_id → {spans, created_at}

    def record_span(self, trace_id: str, name: str, duration_ms: float, error: bool = False):
        if trace_id not in self.buffer:
            self.buffer[trace_id] = {"spans": [], "has_error": False,
                                     "max_duration": 0, "created_at": time.time()}
        entry = self.buffer[trace_id]
        entry["spans"].append({"name": name, "duration_ms": duration_ms})
        entry["has_error"] |= error
        entry["max_duration"] = max(entry["max_duration"], duration_ms)

    def flush(self) -> Dict[str, List]:
        """Decide which traces to keep."""
        kept, dropped = {}, 0
        now = time.time()
        for trace_id, data in list(self.buffer.items()):
            if now - data["created_at"] < self.buffer_secs:
                continue  # not ready yet
            if data["has_error"] and random.random() < self.error_rate:
                kept[trace_id] = data
            elif data["max_duration"] > self.latency_ms:
                kept[trace_id] = data
            elif random.random() < self.normal_rate:
                kept[trace_id] = data
            else:
                dropped += 1
            del self.buffer[trace_id]
        return kept, dropped

# Simulate 1000 requests
sampler = TailBasedSampler(latency_ms=500)
for i in range(1000):
    tid = uuid.uuid4().hex
    is_slow  = (i % 50 == 0)   # 2% slow
    is_error = (i % 100 == 0)  # 1% errors
    dur = random.gauss(600 if is_slow else 80, 20)
    sampler.record_span(tid, "api", dur, error=is_error)
    # Force buffer to age
    sampler.buffer[tid]["created_at"] -= 10

kept, dropped = sampler.flush()
print(f"Kept: {len(kept)} / 1000   Dropped: {dropped}")
```

---

### Exercise 3: Correlation ID Middleware (Hard)

**Problem:** Build a middleware that injects a correlation ID into every request, propagates it to downstream HTTP calls, and logs it so support can find traces without a trace UI.

**Solution:**

```python
import uuid, logging, contextvars
from functools import wraps
from typing import Optional

logger = logging.getLogger("app")
logging.basicConfig(level=logging.INFO, format="%(message)s")

# Thread/async-safe correlation ID store
_correlation_id: contextvars.ContextVar[str] = contextvars.ContextVar("_correlation_id", default="")

def get_correlation_id() -> str:
    return _correlation_id.get()

class CorrelationMiddleware:
    """WSGI-style middleware — also works as decorator pattern."""
    HEADER = "X-Correlation-ID"

    def __call__(self, request_headers: dict, handler):
        cid = request_headers.get(self.HEADER) or uuid.uuid4().hex
        token = _correlation_id.set(cid)
        try:
            logger.info(f"[{cid}] START {request_headers.get('path', '/')}")
            response = handler()
            logger.info(f"[{cid}] END")
            return response, {self.HEADER: cid}
        finally:
            _correlation_id.reset(token)

def outgoing_headers() -> dict:
    """Call this before any downstream HTTP request."""
    return {CorrelationMiddleware.HEADER: get_correlation_id()}

# Simulate request lifecycle
mw = CorrelationMiddleware()

def my_handler():
    cid = get_correlation_id()
    logger.info(f"[{cid}] Calling payment service with headers={outgoing_headers()}")
    logger.info(f"[{cid}] Calling inventory service")
    return {"status": "ok"}

# Simulate two concurrent requests
for path in ["/checkout", "/profile"]:
    response, headers = mw({"path": path}, my_handler)
    print(f"Response headers: {headers}\n")
```

---

## 💡 When to Use

| Situation | Recommendation |
|-----------|---------------|
| Microservices with shared latency budget | Distributed tracing essential |
| Monolith < 5 services | Structured logging sufficient |
| Latency SLA < 200ms | Async sampling only (tail-based) |
| Debugging rare production bugs | Force-sample + correlation IDs |
| Compliance/audit requirements | Full tracing on critical paths |

---

**Last updated:** 2026-05-22

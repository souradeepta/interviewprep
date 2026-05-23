# Distributed Tracing & Observability

Track requests across microservices and databases to diagnose latency issues and bottlenecks in distributed systems.

---

## ⚖️ Tracing Strategy Trade-offs

### Sampling vs. Full Tracing

| Strategy | Coverage | Cost | Latency Impact | Best For |
|----------|----------|------|---|---|
| **Full** | 100% | High | 5-10ms | Critical requests |
| **Percentage** | X% (1-10%) | Low | <1ms | General debugging |
| **Head** | Per request start | Medium | <1ms | Error analysis |
| **Tail** | Slow requests only | Low | <1ms | Latency debugging |

### Tracing Components

```
Request flow with tracing:
  
Client
  ↓ (span: client_request)
API Gateway
  ↓ (span: auth_check)
Auth Service
  ↓ (span: db_query)
Database
  
Each span:
  - Start time
  - End time
  - Duration (latency)
  - Tags (user_id, endpoint)
  - Logs (errors, events)
  - Parent span ID (causality)
```

---

## 🏗️ Tracing Implementation

### Trace Context Propagation

```python
import uuid
import time

class TracingContext:
    def __init__(self):
        self.trace_id = str(uuid.uuid4())
        self.span_id = str(uuid.uuid4())
        self.parent_span_id = None
        self.timestamp = time.time()
        self.tags = {}
    
    def propagate_headers(self):
        """Return headers for downstream calls"""
        return {
            'x-trace-id': self.trace_id,
            'x-span-id': self.span_id,
            'x-parent-span-id': self.parent_span_id
        }

class Span:
    def __init__(self, name, trace_id, parent_span_id=None):
        self.name = name
        self.trace_id = trace_id
        self.span_id = str(uuid.uuid4())
        self.parent_span_id = parent_span_id
        self.start_time = time.time()
        self.end_time = None
        self.tags = {}
        self.logs = []
    
    def set_tag(self, key, value):
        """Add tag to span"""
        self.tags[key] = value
    
    def log_event(self, message, fields=None):
        """Log event in span"""
        self.logs.append({
            'timestamp': time.time(),
            'message': message,
            'fields': fields or {}
        })
    
    def end(self):
        """End span"""
        self.end_time = time.time()
        return self.duration()
    
    def duration(self):
        """Get span duration in ms"""
        if self.end_time:
            return (self.end_time - self.start_time) * 1000
        return 0

# Test
trace_id = str(uuid.uuid4())

# Span 1: API request
span1 = Span('api_request', trace_id)
time.sleep(0.1)
span1.end()

# Span 2: Database query (child of span1)
span2 = Span('db_query', trace_id, parent_span_id=span1.span_id)
time.sleep(0.2)
span2.end()

print(f"Trace ID: {trace_id}")
print(f"Span 1 (api_request): {span1.duration():.0f}ms")
print(f"Span 2 (db_query): {span2.duration():.0f}ms (parent: {span2.parent_span_id[:8]}...)")
```

---

## ❓ Interview Q&A

**Q1: Request takes 5 seconds - debug where it's slow**

A:
- With distributed tracing:
  - Trace shows spans: API → Auth (100ms) → DB (4800ms) → Cache (50ms)
  - DB is bottleneck (4800ms / 5000ms = 96%)
  
- Solution:
  1. Optimize query (add index, reduce result set)
  2. Cache result (TTL 5 min)
  3. Move to async (return quicker, process later)

**Q2: Tracing adds 10% latency - how to reduce?**

A:
- Cause: Synchronous tracing writes (every span waits)
- Solutions:
  1. Async writes:
     - Queue spans in background
     - Don't block request
     - Latency impact: < 1ms
  
  2. Sampling:
     - Trace 1% of requests
     - Reduce I/O by 99%
     - Trade: Miss some issues
  
  3. Batch writes:
     - Collect 100 spans
     - Write once to backend
     - Reduce writes by 100x

---

**Last updated:** 2026-05-22

# Stream Processing & Complex Event Processing

**Level:** L4-L5
**Time to read:** ~30 min

Process continuous event streams in real-time for fraud detection, aggregations, event-driven workflows, and stateful computations at scale.

---

## ⚖️ Stream Processing Trade-offs

| Framework | Latency | Throughput | State Mgmt | Fault Tolerance | Best For |
|-----------|---------|------------|-----------|-----------------|---------|
| **Kafka Streams** | 10–100ms | 1M/sec | RocksDB | At-least-once/EOS | JVM microservices |
| **Apache Flink** | 1–10ms | 10M+/sec | Distributed RocksDB | Exactly-once | Complex CEP, low latency |
| **Spark Structured Streaming** | 100ms–1s | 500K/sec | In-memory | At-least-once | Batch + streaming unified |
| **ksqlDB** | 100ms | 1M/sec | Kafka topics | Exactly-once | SQL-based streaming |
| **Apache Beam** | Varies | Varies | Runner-dependent | Runner-dependent | Multi-runner portability |
| **Redis Streams** | <1ms | 500K/sec | Redis RAM | At-least-once | Simple, low-latency |

### Windowing Strategy Comparison

| Window Type | Memory | Latency | Use Case |
|-------------|--------|---------|---------|
| **Tumbling** | O(window_size) | window_duration | Non-overlapping periods |
| **Sliding** | O(window_size × slide_count) | slide_interval | Moving averages |
| **Session** | O(event_count) | activity-dependent | User sessions |
| **Global** | O(all events) | trigger-based | Streaming aggregates |

---

## 🏗️ Architecture Patterns

### Pattern 1: Windowing Types

```
Tumbling Window (size = 3):
  Events: A B C D E F G H I
          ├──────┤├──────┤├───────┤
           [ABC]   [DEF]   [GHI]
  Each event in exactly one window.

Sliding Window (size = 5, slide = 2):
  Events: A B C D E F G H
          ├────────────┤
              ├────────────┤
                  ├────────────┤
  [ABCDE] [CDEFG] [EFGHI]
  Events appear in multiple windows.

Session Window (gap = 30 min):
  Click at 1:00, 1:15, 1:40 → gap > 30m → 2:30, 2:45
  Session 1: [1:00, 1:15, 1:40]
  Session 2: [2:30, 2:45]
```

### Pattern 2: Stateful Stream Processing

```
Fraud Detection Pipeline:

  Kafka Topic: purchases
      │
      ▼
  [Keyby user_id]  ← partition by key for stateful processing
      │
      ▼
  [Stateful Operator]
  State: RocksDB (per user):
    {
      "user_id": "alice",
      "purchases_1h": [{"amount": 1500, "ts": T1},
                       {"amount": 1200, "ts": T2}],
      "last_alert": None
    }
      │
      ▼
  [Rule Engine]
  If count(purchases > $1000 in last 1h) >= 3:
      → Emit FraudAlert event
      │
      ▼
  Kafka Topic: fraud_alerts
```

### Pattern 3: Lambda Architecture (Batch + Stream)

```
Data Source
     │
     ├──────────────────────────────────────────►
     │                                         Kafka
     │                               ┌──────────┤
     │                               │          │
     ▼                               ▼          ▼
Batch Layer                   Speed Layer   Serving Layer
(Spark/Hive)                  (Flink/Redis)    │
 - Full accuracy               - Low latency   Query Router
 - Historical joins            - Approx result  │
 - Run nightly                 - Real-time      ├── Recent: Speed
     │                               │          └── Historical: Batch
     └───────────────────────────────┘
           Both write to Serving Layer
```

---

## 📊 Stream Processing Implementation

```python
import time
import threading
import heapq
from collections import defaultdict, deque
from typing import Callable, Optional, List, Any
from dataclasses import dataclass, field

# ── Event Model ───────────────────────────────────────────────────────────────

@dataclass
class Event:
    key: str
    value: Any
    timestamp: float = field(default_factory=time.time)
    event_type: str = "generic"


# ── Window Implementations ────────────────────────────────────────────────────

class TumblingWindow:
    """Non-overlapping fixed-size time windows."""

    def __init__(self, size_sec: float, aggregate_fn: Callable):
        self.size_sec = size_sec
        self.aggregate_fn = aggregate_fn
        self._windows: dict = defaultdict(list)   # key → events in current window
        self._results: list = []
        self._window_ends: dict = {}              # key → current window end time

    def add(self, event: Event) -> Optional[dict]:
        key = event.key
        if key not in self._window_ends:
            self._window_ends[key] = event.timestamp + self.size_sec

        if event.timestamp >= self._window_ends[key]:
            # Window closed — emit aggregate
            result = self._emit(key)
            self._window_ends[key] = event.timestamp + self.size_sec
            self._windows[key] = [event]
            return result
        else:
            self._windows[key].append(event)
            return None

    def _emit(self, key: str) -> dict:
        events = self._windows.get(key, [])
        result = {
            "key": key,
            "window_end": self._window_ends[key],
            "count": len(events),
            "aggregate": self.aggregate_fn(events),
        }
        self._results.append(result)
        return result


class SlidingWindow:
    """Overlapping windows with configurable slide interval."""

    def __init__(self, size_sec: float, slide_sec: float, aggregate_fn: Callable):
        self.size_sec = size_sec
        self.slide_sec = slide_sec
        self.aggregate_fn = aggregate_fn
        self._events: dict = defaultdict(deque)

    def add(self, event: Event) -> dict:
        key = event.key
        now = event.timestamp
        self._events[key].append(event)
        # Evict events outside the window
        while self._events[key] and self._events[key][0].timestamp < now - self.size_sec:
            self._events[key].popleft()

        window_events = list(self._events[key])
        return {
            "key": key,
            "timestamp": now,
            "count": len(window_events),
            "aggregate": self.aggregate_fn(window_events),
        }


class SessionWindow:
    """Groups events separated by less than session_gap_sec."""

    def __init__(self, session_gap_sec: float):
        self.session_gap_sec = session_gap_sec
        self._last_seen: dict = {}
        self._sessions: dict = defaultdict(list)
        self._completed: list = []

    def add(self, event: Event) -> Optional[dict]:
        key = event.key
        now = event.timestamp
        last = self._last_seen.get(key, 0)

        if last and (now - last > self.session_gap_sec):
            # Session expired — emit
            result = {
                "key": key,
                "events": list(self._sessions[key]),
                "session_duration": last - self._sessions[key][0].timestamp,
                "event_count": len(self._sessions[key]),
            }
            self._completed.append(result)
            self._sessions[key] = []
            return result

        self._sessions[key].append(event)
        self._last_seen[key] = now
        return None


# ── Stateful Fraud Detector ────────────────────────────────────────────────────

class FraudDetector:
    """
    Detects: N purchases over threshold within time window.
    State: per-user sliding list of recent purchases.
    """

    def __init__(
        self,
        window_sec: float = 3600,
        threshold_amount: float = 1000,
        min_count: int = 3,
        alert_fn: Optional[Callable] = None,
    ):
        self.window_sec = window_sec
        self.threshold_amount = threshold_amount
        self.min_count = min_count
        self.alert_fn = alert_fn or print

        # State: user_id → deque of (timestamp, amount)
        self._state: dict = defaultdict(deque)
        self._alerts: list = []

    def process(self, event: Event) -> Optional[dict]:
        user_id = event.key
        amount = event.value.get("amount", 0)
        now = event.timestamp

        # Evict old events
        buf = self._state[user_id]
        while buf and buf[0][0] < now - self.window_sec:
            buf.popleft()

        # Add new event
        if amount >= self.threshold_amount:
            buf.append((now, amount))

        # Check rule
        if len(buf) >= self.min_count:
            alert = {
                "type": "FRAUD_ALERT",
                "user_id": user_id,
                "purchase_count": len(buf),
                "total_amount": sum(a for _, a in buf),
                "window_sec": self.window_sec,
                "detected_at": now,
            }
            self._state[user_id].clear()  # Reset after alert
            self.alert_fn(f"🚨 FRAUD: {alert}")
            self._alerts.append(alert)
            return alert

        return None

    def get_alerts(self) -> list:
        return list(self._alerts)


# Demo
print("=== Tumbling Window ===")
agg = TumblingWindow(size_sec=10, aggregate_fn=lambda evts: sum(e.value for e in evts))
events = [Event("user1", i * 10, timestamp=float(i)) for i in range(25)]
for evt in events:
    result = agg.add(evt)
    if result:
        print(f"  Window: count={result['count']}, sum={result['aggregate']}")

print("\n=== Session Window ===")
sw = SessionWindow(session_gap_sec=30)
clicks = [
    Event("alice", "click_home",    timestamp=0.0),
    Event("alice", "click_product", timestamp=15.0),
    Event("alice", "click_cart",    timestamp=25.0),
    Event("alice", "click_home",    timestamp=200.0),  # New session (gap > 30s)
    Event("alice", "click_product", timestamp=210.0),
]
for click in clicks:
    result = sw.add(click)
    if result:
        print(f"  Session ended: {result['event_count']} events, duration={result['session_duration']:.1f}s")

print("\n=== Fraud Detection ===")
fraud = FraudDetector(window_sec=60, threshold_amount=1000, min_count=3)
purchases = [
    Event("bob", {"amount": 1500}, timestamp=0.0),
    Event("bob", {"amount": 1200}, timestamp=10.0),
    Event("bob", {"amount": 1100}, timestamp=20.0),   # ← triggers alert
    Event("alice", {"amount": 500}, timestamp=5.0),   # Safe
]
for p in purchases:
    fraud.process(p)

print(f"Total fraud alerts: {len(fraud.get_alerts())}")
```

---

## 🔧 Kafka Streams Configuration

```java
// Fraud detection with Kafka Streams (pseudocode — Java API)
Properties props = new Properties();
props.put(StreamsConfig.APPLICATION_ID_CONFIG, "fraud-detector");
props.put(StreamsConfig.BOOTSTRAP_SERVERS_CONFIG, "kafka:9092");
props.put(StreamsConfig.DEFAULT_KEY_SERDE_CLASS_CONFIG, Serdes.String().getClass());
props.put(StreamsConfig.DEFAULT_VALUE_SERDE_CLASS_CONFIG, JsonSerde.class);
props.put(StreamsConfig.PROCESSING_GUARANTEE_CONFIG, StreamsConfig.EXACTLY_ONCE_V2);

StreamsBuilder builder = new StreamsBuilder();

KStream<String, Purchase> purchases = builder.stream("purchases");

purchases
    .filter((userId, purchase) -> purchase.getAmount() >= 1000)
    .groupByKey()
    .windowedBy(SlidingWindows.ofTimeDifferenceAndGrace(
        Duration.ofHours(1), Duration.ofMinutes(5)))
    .count()
    .filter((windowedKey, count) -> count >= 3)
    .toStream()
    .map((windowedKey, count) -> new KeyValue<>(
        windowedKey.key(),
        new FraudAlert(windowedKey.key(), count)))
    .to("fraud-alerts");

KafkaStreams streams = new KafkaStreams(builder.build(), props);
streams.start();
```

### Apache Flink Configuration (Python)

```python
# PyFlink fraud detection (simplified)
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.window import TumblingProcessingTimeWindows
from pyflink.common.time import Time

env = StreamExecutionEnvironment.get_execution_environment()
env.set_parallelism(4)

# Source: Kafka consumer
purchases = env.add_source(
    FlinkKafkaConsumer("purchases", JsonDeserializationSchema(), kafka_props)
)

fraud_alerts = (
    purchases
    .filter(lambda p: p["amount"] >= 1000)
    .key_by(lambda p: p["user_id"])
    .window(TumblingProcessingTimeWindows.of(Time.hours(1)))
    .process(FraudWindowFunction())  # Custom ProcessWindowFunction
    .filter(lambda alert: alert["count"] >= 3)
)

fraud_alerts.add_sink(FlinkKafkaProducer("fraud-alerts", ...))
env.execute("Fraud Detection Job")
```

---

## ❓ Interview Q&A

**Q1: Detect fraud — 3 purchases over $1,000 within 1 hour. Design the system.**

A: Stream processing pipeline:
1. **Source**: Kafka topic `purchases` (JSON: user_id, amount, timestamp)
2. **Key by**: `user_id` — ensures all events for a user go to the same partition
3. **State**: Sliding window (1 hour) per user, track amounts ≥ $1,000 using RocksDB (Flink/Kafka Streams)
4. **Rule**: Count events in window ≥ 3 → emit FraudAlert
5. **Sink**: Kafka `fraud_alerts` topic → Notification service
6. **Fault tolerance**: Flink checkpointing every 30s to S3; on restart, replay from last checkpoint
7. **Latency**: Alert within <100ms of triggering event

**Q2: You need exactly-once semantics across Kafka and a database. How?**

A: Transactional producers + idempotent consumers:
1. **Kafka Streams EOS** (`processing.guarantee = exactly_once_v2`): uses Kafka transactions internally
2. **Kafka + DB**: use the outbox pattern — write to DB and an `outbox` table in one transaction; CDC reads outbox and publishes to Kafka; consumer marks offset only after successful DB write
3. **Flink + Postgres**: Two-phase commit sink; Flink's checkpoint protocol coordinates commit across Kafka and Postgres atomically

**Q3: Your stream processing job falls behind — 10-second lag growing to 10 minutes. Debug process.**

A: In order:
1. **Identify bottleneck**: Check operator backpressure in Flink UI / Kafka consumer lag metrics
2. **Slow source**: Increase Kafka partitions (= Flink parallelism); increase consumer group size
3. **Slow operator**: Profile the `ProcessFunction` — expensive state reads? Add bloom filter cache for hot keys
4. **State backend**: If RocksDB is slow, check disk I/O; consider in-memory state for hot data
5. **Skew**: One key getting 90% of events? Add sub-key (user_id + hash suffix) to spread load

**Q4: How do you handle late-arriving events in windowed computations?**

A: Three strategies:
1. **Allowed lateness** (Flink/Beam): keep window open for extra duration (e.g., 5 min) to accept late events; re-trigger aggregate when late event arrives
2. **Watermarks**: Define "watermark = max_seen_event_time - 5 min"; events behind watermark are considered late; window fires when watermark passes window end
3. **Side output**: Route late events to a separate "corrections" stream; apply corrections to downstream aggregates asynchronously (eventual consistency trade-off vs. real-time accuracy)

**Q5: How do you test a stream processing job before deploying to production?**

A: Four testing levels:
1. **Unit tests**: Test individual `ProcessFunction`/operator logic with mock state
2. **Integration tests**: Use embedded Kafka (Testcontainers), run job end-to-end in tests
3. **Shadow mode**: Run new job against production traffic in parallel, compare output to current job; alert on any divergence
4. **Canary**: Route 5% of Kafka partitions to new job; validate output quality before full rollout
5. **Chaos testing**: Kill task managers mid-checkpoint; verify exactly-once semantics hold and results are identical to normal run

---

## 🧪 Practical Exercises

### Exercise 1: Moving Average Stream (Easy)

**Problem:** Compute rolling average over a sliding window of N events.

```python
from collections import deque

class MovingAverageStream:
    def __init__(self, window_size: int):
        self.window_size = window_size
        self._window = deque(maxlen=window_size)
        self._sum = 0.0

    def next(self, value: float) -> float:
        if len(self._window) == self.window_size:
            self._sum -= self._window[0]
        self._window.append(value)
        self._sum += value
        return self._sum / len(self._window)


ma = MovingAverageStream(window_size=3)
for val in [1, 10, 3, 5, 8, 7, 2]:
    avg = ma.next(val)
    print(f"  Value: {val}, MA(3): {avg:.2f}")
```

---

### Exercise 2: Stream Join (Medium)

**Problem:** Join click events with purchase events within a 1-hour correlation window.

```python
class StreamJoiner:
    """
    Correlates clicks with purchases within a time window.
    Detects: user clicked product X then bought X within window.
    """

    def __init__(self, correlation_window_sec: float = 3600):
        self.window = correlation_window_sec
        self._clicks: dict = defaultdict(deque)       # user → clicks
        self._matches: list = []

    def add_click(self, user_id: str, product_id: str, timestamp: float):
        self._evict(self._clicks[user_id], timestamp)
        self._clicks[user_id].append((timestamp, product_id))

    def add_purchase(self, user_id: str, product_id: str, timestamp: float) -> Optional[dict]:
        self._evict(self._clicks[user_id], timestamp)
        for click_ts, click_product in self._clicks[user_id]:
            if click_product == product_id:
                match = {
                    "user_id": user_id,
                    "product_id": product_id,
                    "click_ts": click_ts,
                    "purchase_ts": timestamp,
                    "latency_sec": timestamp - click_ts,
                }
                self._matches.append(match)
                return match
        return None

    def _evict(self, buf: deque, now: float):
        while buf and buf[0][0] < now - self.window:
            buf.popleft()

    def conversion_rate(self) -> float:
        return len(self._matches)  # More useful with click total


joiner = StreamJoiner(correlation_window_sec=3600)
t = time.time()

joiner.add_click("alice", "widget-42", t)
joiner.add_click("alice", "gadget-7",  t + 300)
result = joiner.add_purchase("alice", "widget-42", t + 1800)  # Matches first click

if result:
    print(f"Conversion: {result['user_id']} bought {result['product_id']} "
          f"{result['latency_sec']:.0f}s after clicking")
```

---

### Exercise 3: Distributed Aggregation with Watermarks (Hard)

**Problem:** Process out-of-order events using event-time watermarks.

```python
import heapq

class WatermarkProcessor:
    """
    Processes out-of-order events using event-time windowing.
    Emits window results only when watermark advances past window end.
    """

    def __init__(self, window_sec: float, max_lateness_sec: float = 30):
        self.window_sec = window_sec
        self.max_lateness = max_lateness_sec
        self._max_event_time: float = 0
        self._windows: dict = defaultdict(list)  # window_start → events
        self._emitted: set = set()
        self._results: list = []

    @property
    def watermark(self) -> float:
        """Watermark = max event time seen - max lateness."""
        return self._max_event_time - self.max_lateness

    def process(self, event: Event) -> List[dict]:
        ts = event.timestamp
        self._max_event_time = max(self._max_event_time, ts)

        # Assign to window
        window_start = (ts // self.window_sec) * self.window_sec
        self._windows[window_start].append(event)

        # Emit windows whose end time is before the watermark
        emitted = []
        for w_start in sorted(self._windows.keys()):
            w_end = w_start + self.window_sec
            if w_end <= self.watermark and w_start not in self._emitted:
                result = {
                    "window_start": w_start,
                    "window_end": w_end,
                    "count": len(self._windows[w_start]),
                    "values": [e.value for e in self._windows[w_start]],
                    "watermark_at_emit": self.watermark,
                }
                self._emitted.add(w_start)
                self._results.append(result)
                emitted.append(result)
                del self._windows[w_start]

        return emitted


# Demo: events arrive out of order
processor = WatermarkProcessor(window_sec=60, max_lateness_sec=10)
t0 = 1000.0  # synthetic timestamps

events = [
    Event("sensor-1", 55, timestamp=t0 + 55),   # t=55
    Event("sensor-1", 72, timestamp=t0 + 72),   # t=72
    Event("sensor-1", 48, timestamp=t0 + 48),   # late! but within lateness window
    Event("sensor-1", 130, timestamp=t0 + 130), # advances watermark to 120
    Event("sensor-1", 65, timestamp=t0 + 65),   # very late — dropped (window already emitted)
]

for evt in events:
    results = processor.process(evt)
    print(f"  t={evt.timestamp-t0:.0f}, val={evt.value}, watermark={processor.watermark:.0f}", end="")
    if results:
        for r in results:
            print(f" → EMIT window [{r['window_start']-t0:.0f},{r['window_end']-t0:.0f}): count={r['count']}", end="")
    print()

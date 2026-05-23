# Stream Processing & Complex Event Processing

Process continuous event streams in real-time for anomaly detection, aggregations, and event-driven workflows.

---

## ⚖️ Stream Processing Trade-offs

| Framework | Latency | Throughput | State | Ease |
|-----------|---------|-----------|-------|------|
| **Kafka Streams** | 100ms | 1M/sec | Internal | Medium |
| **Flink** | 10ms | 10M/sec | Distributed | Hard |
| **Spark Streaming** | 500ms | 100K/sec | RDD | Medium |
| **ksqlDB** | 100ms | 1M/sec | Stateful | Easy |

---

## 🏗️ Stream Processing Patterns

### Pattern 1: Windowing

```
Tumbling window (fixed):
  Event stream: A B C D E F G H I J
  Window (size 3): [ABC] [DEF] [GHI] [J]

Sliding window (overlap):
  Window (size 3, slide 1): [ABC] [BCD] [CDE] ...

Benefits:
  - Bounded computation
  - State management
```

### Pattern 2: Join Streams

```
User clicks stream:
  user_id | timestamp | product_id

Purchase stream:
  user_id | timestamp | amount

Stream join (within 1 hour):
  Find: user clicked product X, then bought X
  
Detect: Conversion, add-to-cart → purchase flow
```

### Pattern 3: State Management

```
Calculate: Running average of request latency

State: sum, count
New request: latency = 50ms
  sum += 50
  count += 1
  average = sum / count

On failure:
  Checkpoint state
  Resume from checkpoint
```

---

## ❓ Interview Q&A

**Q1: Detect fraud: 3 purchases > $1000 within 1 hour**

A:
- Stream: purchase events
- Window: 1 hour, sliding
- State: per user, list of purchases in window
- Logic:
  ```
  if purchases > 3 and all amount > 1000:
    alert("fraud")
  ```

**Q2: Stream processing adds latency, solution?**

A:
- Causes:
  1. Windowing (wait for window to close)
  2. Batch processing
  
- Solutions:
  1. Smaller windows (100ms vs. 1 hour)
  2. Use Flink (10ms latency)
  3. Process individual events (no window)

---

**Last updated:** 2026-05-22

# Message Queue

**Level:** L3-L5+
**Time to read:** ~30 min

## Problem Statement

Direct synchronous calls between services create tight coupling: if the downstream service is slow
or down, the caller blocks or fails. Message queues decouple producers from consumers by
introducing an intermediary buffer where messages are stored until a consumer is ready to process
them. This enables asynchronous processing, load leveling, and retry logic without the producer
needing to know anything about the consumer.

The design challenge is choosing the right semantics (at-most-once, at-least-once, exactly-once),
durability requirements (in-memory vs. disk-backed), and scaling model (push vs. pull, single
consumer vs. competing consumers vs. broadcast fan-out) based on the specific use case.

## Functional Requirements

- Producers publish messages to named queues or topics
- Consumers receive messages (pull or push) and acknowledge successful processing
- Failed messages are retried and eventually moved to a Dead Letter Queue (DLQ)
- Messages have configurable TTL; expired messages are automatically discarded
- Support ordered delivery within a partition

## Non-Functional Requirements

- **Scale:** 1M messages/sec publish throughput; 500K consumers across all queues
- **Latency:** P99 < 5 ms end-to-end (producer → consumer delivery) for in-memory queues;
  P99 < 100 ms for durable (disk-backed) queues
- **Availability:** 99.99%; no message loss for durable queues (at-least-once guarantee)
- **Consistency:** At-least-once delivery by default; exactly-once achievable via idempotency key

---

## Tier 1: L3-L4 Design (the basic interview answer)

### Back-of-Envelope

```
Publish rate:    1M messages/sec
Message size:    avg 1 KB (typical event payload)
Throughput:      1M * 1 KB = 1 GB/sec ingest
Storage/day:     1 GB/sec * 86400 sec = 86 TB/day  (before replication)
Replication:     3× for durability                  = 258 TB/day raw disk write
Retention:       7-day default                      = 258 * 7 = 1.8 PB total disk
Partitions:      Kafka partition can handle ~100 MB/sec throughput
                 1 GB/sec / 100 MB = 10 partitions minimum → use 50 for headroom
Brokers:         50 partitions, 3 replicas = 150 partition-replicas
                 Each broker holds ~30 partition-replicas at 3 TB each = 90 TB/broker
                 Brokers needed: 5-10 brokers (with 90 TB NVMe each)
```

### Architecture Diagram

```
 Producers (order-svc, payment-svc, user-svc)
      |          |          |
      +----------+----------+
                 |
      +----------v----------+
      |   Message Broker    |
      |  (Kafka Cluster)    |
      |                     |
      | Partition 0  ──────►|──► Consumer Group A (email-svc)
      | Partition 1  ──────►|──► Consumer Group A
      | Partition 2  ──────►|──► Consumer Group B (analytics-svc)
      | ...                 |
      +---------------------+
              |
        Dead Letter Queue
        (failed after N retries)
              |
         +----v----+
         | DLQ     |   ← alerting + manual inspection
         +---------+

Queue vs Topic:
  Queue:  1 message → 1 consumer (competing consumers, load balanced)
  Topic:  1 message → N consumer groups (broadcast fan-out)
```

### Data Model

```
# Kafka logical model (on-disk segment files, not a DB)
Topic: "order.created"
  Partition 0:  [offset 0][offset 1]...[offset 1_000_000]
  Partition 1:  [offset 0][offset 1]...[offset 1_000_000]

Message envelope:
  {
    key:       "order_id:78901"      -- determines partition assignment
    value:     { order_id, user_id, total_cents, items: [...] }
    headers:   { idempotency_key, source_service, schema_version }
    timestamp: 1717000000000
    offset:    12345678              -- monotonically increasing per partition
  }

Consumer offset tracking (stored in __consumer_offsets topic):
  consumer_group_id + topic + partition → last_committed_offset
```

### API Design

```
# Producer API
POST /topics/{topic_name}/messages
  Body: {
    key: "user_id:123",          -- optional; used for partitioning
    value: { ... },              -- arbitrary JSON payload
    headers: {
      idempotency_key: "uuid",
      ttl_seconds: 3600
    }
  }
  Response: 201 { partition: 3, offset: 456789 }

# Consumer API (pull model)
GET /topics/{topic_name}/messages?group_id=email-svc&partition=3&offset=456789&max=100
  Response: 200 { messages: [...], next_offset: 456889 }

POST /topics/{topic_name}/ack
  Body: { group_id: "email-svc", partition: 3, offset: 456889 }
  Response: 204

# DLQ
GET /dlq/{topic_name}/messages?limit=100
POST /dlq/{topic_name}/replay        -- requeue DLQ messages to original topic

# Admin
POST /topics   Body: { name, partitions, replication_factor, retention_ms }
GET  /topics/{name}/lag?group_id=email-svc
  Response: { total_lag: 45000, per_partition: { "0": 22000, "1": 23000 } }
```

### Basic Scaling

- **Partitioning:** Increase partition count to scale throughput linearly; each partition is an
  ordered, append-only log consumed by one consumer per group at a time
- **Consumer groups:** Each service has its own consumer group; all groups receive all messages
  independently (fan-out); within a group, partitions are assigned to specific consumers
- **Retention policy:** Set topic `retention.ms` and `retention.bytes` to cap disk usage;
  old segments are deleted automatically
- **Replication factor:** 3 across 3 AZs; use `min.insync.replicas=2` to prevent silent data loss

---

## Tier 2: L5+ Design (the staff interview answer)

### Capacity Planning (Real Numbers)

```
Kafka broker sizing (per broker, AWS m6i.8xlarge or equivalent):
  CPU:    32 vCPUs; broker is I/O-bound, CPU headroom > 60% typical
  RAM:    128 GB; allocate 6 GB heap to JVM, rest for OS page cache
          OS page cache is critical: consumers reading recent data hit RAM, not disk
  Disk:   8 TB NVMe SSD per broker; write throughput: 1 GB/sec / 5 brokers = 200 MB/sec
          NVMe can sustain 3-4 GB/sec → 15-20× headroom
  Net:    25 Gbps; replication traffic: 1 GB/sec * 3 replicas / 5 brokers = 600 MB/sec/broker

ZooKeeper / KRaft:
  3-node quorum for metadata (topics, partition leaders, ISR list)
  KRaft (Kafka 3.x) eliminates ZooKeeper dependency; reduces ops overhead

Consumer lag budget:
  Acceptable lag: < 10K messages (< 10 seconds at 1K msg/sec per consumer)
  Alert at:       lag > 50K messages (consumer falling behind → scale out)
  Auto-scale:     Add consumer instances when lag > threshold (KEDA in Kubernetes)
```

### Failure Modes

```
FAILURE: Broker goes down (leader for 10 partitions)
  Detection:     ZooKeeper/KRaft session expires in 6 sec
  Mitigation:    Controller elects new leaders from ISR (in-sync replicas)
                 Re-election: < 30 sec for 10 partitions
  Client impact: Producers get NotLeaderOrFollowerException → retry → connects to new leader
  Data risk:     With min.insync.replicas=2, no loss if at least 1 ISR was in sync at failure

FAILURE: Consumer crashes mid-processing (message not ACKed)
  Mitigation:    Broker re-delivers to another consumer in group after session timeout (default 30s)
  Risk:          Message processed twice (at-least-once) → consumer must be idempotent

FAILURE: Poison pill message (always causes consumer crash)
  Detection:     Message exceeds max retry count (e.g., 3 retries)
  Mitigation:    Move to DLQ with error metadata (exception, stack trace, attempt count)
                 Alert on-call; DLQ consumer exposes replay API

FAILURE: Consumer lag spikes (slow consumer, spike in produce rate)
  Mitigation:    Scale out consumer group (add instances, partitions auto-rebalance)
                 Enable back-pressure: producer slows down if consumer lag > threshold
                 Use `max.poll.records` tuning to control batch size
```

### Consistency Boundaries

```
AT-MOST-ONCE (fire-and-forget):
  Producer acks=0; consumer processes before committing offset
  Use for: metrics, logs, analytics where loss is acceptable
  Risk:    Broker crash before write → message lost silently

AT-LEAST-ONCE (default, recommended):
  Producer acks=all; consumer commits offset AFTER processing
  Use for: order events, notifications, most business events
  Risk:    Consumer crashes after processing but before committing → reprocessed

EXACTLY-ONCE (Kafka Transactions + idempotency):
  Producer uses transactional API (enable.idempotence=true + transactional.id)
  Consumer reads with isolation.level=read_committed
  Use for: payment events, financial ledger updates, inventory deduction
  Cost:    ~20-30% throughput reduction; requires all consumers to honor transactions

APPLICATION-LEVEL EXACTLY-ONCE (simpler, more portable):
  Consumer checks idempotency_key in DB before processing
  Atomic: DB.insert(idempotency_key) + business logic in same transaction
  Works with any broker (SQS, RabbitMQ); no broker-level transaction needed
```

### Cost Model

```
Kafka (self-hosted on AWS):
  5× m6i.8xlarge brokers: 5 * $1.60/hr * 8760        = $70K/yr compute
  Storage: 1.8 PB * $0.10/GB/month * 12               = $2.2M/yr  ← dominant cost
  Mitigation: S3 Tiered Storage (Kafka 3.6+): keep 1 day hot, rest on S3
    Hot storage (1 day): 258 TB * $0.10 * 12          = $310K/yr
    Cold storage (6 days): 1.55 PB * $0.023 * 12      = $428K/yr
    Total with tiering:                                = $808K/yr  (63% reduction)

Managed (AWS MSK):
  5-broker cluster m5.4xlarge: 5 * $0.80/hr * 8760    = $35K/yr compute
  Storage surcharge: 1.8 PB * $0.10/GB * 12           = $2.2M/yr
  MSK total:                                           = $2.24M/yr (no ops savings here)

Per-message cost:
  1M msg/sec * 86400 * 365 = 31.5 trillion messages/year
  $808K / 31.5T            = $0.000000026/message ($26 per billion messages)
```

---

## Trade-off Comparison

| Approach | Pros | Cons | Best For |
|----------|------|------|----------|
| Redis Lists (in-memory queue) | Sub-millisecond latency; simple ops; no broker cluster | Data lost on restart without AOF; limited throughput (~1M ops/sec single node); no consumer groups | Job queues, task dispatch, real-time pipelines where loss is acceptable |
| Kafka (durable, partitioned log) | Durable; replay; fan-out via consumer groups; high throughput | Operational complexity; JVM; minutes to set up; at-least-once by default | Event streaming, audit log, ETL pipelines, high-throughput event buses |
| AWS SQS (managed queue) | Zero ops; scales automatically; DLQ built-in | No fan-out (use SNS+SQS); 300K msg/sec limit; no ordering (FIFO queue limited to 3K/sec) | AWS-native workloads, serverless consumers (Lambda), simple job queues |
| RabbitMQ (AMQP broker) | Rich routing (exchanges, bindings); push delivery; mature | Not designed for replay; disk usage grows unbounded without consumers; clustering complex | Complex routing logic, priority queues, RPC patterns |

## Follow-up Questions (escalating difficulty)

1. **(L3)** What is the difference between a queue and a topic (pub/sub)?
   → A queue delivers each message to exactly one consumer (competing consumers model). A topic
   (pub/sub) delivers each message to all subscribed consumer groups independently. Kafka models
   everything as topics; queuing behavior is achieved by having all consumers in one group.

2. **(L3)** What is a Dead Letter Queue and why do you need one?
   → A DLQ holds messages that failed processing after N retries. Without a DLQ, a poison-pill
   message blocks the queue forever (consumer keeps crashing). The DLQ lets you isolate bad
   messages, inspect them, fix the consumer bug, and replay when ready.

3. **(L4)** How do you implement priority queues on top of Kafka?
   → Kafka doesn't natively support priority. Common approaches: (1) Use separate topics per
   priority level (high/medium/low); consumer polls high-priority first, falls back to lower.
   (2) Use a separate in-memory priority queue (Redis ZSET) in front of Kafka for the hot path.

4. **(L4)** How does consumer back-pressure work and why does it matter?
   → If producers publish faster than consumers can process, messages accumulate (lag grows).
   Back-pressure signals the producer to slow down or buffers to fill up and block producers.
   In Kafka, back-pressure is indirect: monitor consumer lag, trigger auto-scaling of consumers,
   or use application-level rate limiting on producers.

5. **(L5)** Explain Kafka's exactly-once semantics (EOS). What are the trade-offs?
   → EOS requires: (1) Idempotent producer (retries don't duplicate); (2) Transactional producer
   API — writes to multiple partitions atomically; (3) Consumer reads with isolation.level=
   read_committed (skips uncommitted messages). Trade-off: ~20-30% throughput reduction, higher
   latency (transaction coordinator round-trip), and all participants must use the transactional
   API — mixing with non-transactional consumers breaks guarantees.

6. **(L5)** How would you implement a delay queue (process message after N minutes)?
   → Option A: Separate delay topics per time bucket (delay_1m, delay_5m, delay_1h); producer
   chooses bucket; consumer re-publishes to main topic when delay expires. Option B: Store
   delayed messages in Redis ZSET with score=process_at_timestamp; a scheduler polls and
   publishes ready messages. Option B is simpler for variable delays.

7. **(L5+)** How does Kafka handle rebalancing and what is the "stop-the-world" problem?
   → When a consumer joins/leaves a group, the group coordinator triggers rebalancing: all
   consumers stop consuming during partition reassignment (stop-the-world). For large groups
   this can pause processing for 30+ seconds. Mitigation: Kafka's incremental cooperative
   rebalancing (KAFKA-8421, Kafka 2.4+) only revokes partitions being moved, not all partitions,
   reducing pause to near-zero.

## Anti-patterns / Things NOT to Say

- **"Use a database table as a queue (polling pattern)"** — DB polling creates lock contention,
  high CPU from constant SELECT loops, and doesn't scale past ~1K messages/sec without
  degrading DB performance. Use a real message broker.
- **"Commit the offset before processing the message"** — This gives at-most-once: if the
  consumer crashes after commit but before processing, the message is permanently skipped.
  Always commit offset AFTER successful processing (at-least-once semantics).
- **"One Kafka topic with 1000 partitions for everything"** — Each partition has overhead: open
  file handles, leader election state, replication. 1000 partitions * 3 replicas = 3000 open
  files; cluster metadata grows large; controller election slows. Keep partition count proportional
  to throughput need; typical: 10-50 per topic.
- **"Consumers should be stateful and track deduplication in memory"** — In-memory dedup state
  is lost on restart. Dedup state must be persisted (Redis, DB) keyed by idempotency_key with TTL
  matching the dedup window.
- **"Message order is guaranteed across partitions"** — Kafka only guarantees ordering within
  a single partition. If you need global ordering, you need a single partition — which means
  single-threaded consumption and no horizontal scaling.

## Python Implementation (sketch)

```python
import json
import time
import redis
from dataclasses import dataclass
from typing import Optional

@dataclass
class Message:
    topic: str
    key: str
    value: dict
    idempotency_key: str
    ttl_seconds: int = 3600

class SimpleRedisQueue:
    """In-memory queue using Redis Lists with idempotency and DLQ support."""

    def __init__(self, host: str = "localhost", port: int = 6379):
        self.r = redis.Redis(host=host, port=port, decode_responses=True)
        self.MAX_RETRIES = 3

    def publish(self, msg: Message) -> bool:
        payload = json.dumps({
            "key": msg.key,
            "value": msg.value,
            "idempotency_key": msg.idempotency_key,
            "enqueued_at": time.time(),
            "ttl_seconds": msg.ttl_seconds,
            "retry_count": 0,
        })
        self.r.lpush(msg.topic, payload)
        return True

    def consume(self, topic: str, timeout: int = 5) -> Optional[dict]:
        """Blocking pop from queue (pull model)."""
        result = self.r.brpop(topic, timeout=timeout)
        if result is None:
            return None
        _, raw = result
        msg = json.loads(raw)

        # TTL check
        age = time.time() - msg["enqueued_at"]
        if age > msg["ttl_seconds"]:
            print(f"[EXPIRED] {msg['idempotency_key']}")
            return None
        return msg

    def ack(self, idempotency_key: str, dedup_window: int = 86400) -> None:
        """Mark message as processed (idempotency check)."""
        self.r.setex(f"ack:{idempotency_key}", dedup_window, "1")

    def is_duplicate(self, idempotency_key: str) -> bool:
        return self.r.exists(f"ack:{idempotency_key}") == 1

    def nack(self, topic: str, msg: dict) -> None:
        """Re-queue or send to DLQ after failure."""
        msg["retry_count"] = msg.get("retry_count", 0) + 1
        if msg["retry_count"] >= self.MAX_RETRIES:
            self.r.lpush(f"dlq:{topic}", json.dumps(msg))
            print(f"[DLQ] {msg['idempotency_key']} after {self.MAX_RETRIES} retries")
        else:
            # Exponential backoff: delay re-queue
            delay = 2 ** msg["retry_count"]
            time.sleep(delay)
            self.r.lpush(topic, json.dumps(msg))


# Usage
queue = SimpleRedisQueue()
queue.publish(Message(
    topic="order.created",
    key="order_id:78901",
    value={"order_id": 78901, "total_cents": 4999},
    idempotency_key="ord-78901-v1",
))

msg = queue.consume("order.created")
if msg and not queue.is_duplicate(msg["idempotency_key"]):
    # process order...
    queue.ack(msg["idempotency_key"])
```

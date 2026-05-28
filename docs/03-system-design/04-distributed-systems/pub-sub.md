# Pub-Sub (Publish-Subscribe) System

**Level:** L3-L5+
**Time to read:** ~30 min

## Problem Statement

A publish-subscribe system decouples message producers (publishers) from consumers (subscribers)
through a broker layer. Publishers emit events without knowing who will receive them; subscribers
declare interest in topics and receive matching events asynchronously. This pattern is foundational
to every large-scale distributed system — event-driven microservices, real-time analytics pipelines,
notification systems, and audit logging all rely on it.

In interviews, pub-sub surfaces as both a standalone design ("design Kafka") and as a sub-component
("how would you propagate order events to 12 downstream services?"). Understanding the full spectrum
— from simple queue semantics to partitioned, durable, exactly-once logs — is essential at L4+ level.

## Functional Requirements

- Publishers can send messages to named topics
- Subscribers can subscribe to one or more topics and receive messages
- Messages are durably stored so late subscribers or replays are possible
- Support at-least-once delivery; optionally exactly-once
- Consumer groups allow parallel consumption without duplicate processing across the group
- Dead-letter queue (DLQ) captures messages that consistently fail processing

## Non-Functional Requirements

- **Scale:** 1M messages/sec ingestion; 10K topics; 10K consumers; 10 TB/day data
- **Latency:** P99 end-to-end < 100ms for hot paths (real-time); batch consumers tolerate seconds
- **Availability:** 99.99% (four nines); broker failures transparent to producers within 30s
- **Consistency:** At-least-once by default; exactly-once requires idempotent consumers + transactions

---

## Tier 1: L3-L4 Design (the basic interview answer)

### Back-of-Envelope

```
Ingestion:
  1M messages/sec × 1 KB avg message = 1 GB/sec raw throughput
  Retention 7 days: 1 GB/sec × 86400 sec/day × 7 days = ~600 TB

Fan-out:
  1 publisher on a topic → average 10 consumer groups reading independently
  Each message read 10 times = 10 GB/sec total read throughput

Broker nodes (Kafka-style):
  Single broker can handle ~100 MB/sec with replication overhead
  Needed: 1 GB/sec ÷ 100 MB/sec ≈ 10 brokers for write
  With 3× replication: ~30 broker nodes total
  600 TB storage ÷ 10 TB/disk = 60 disks (spread across 30 nodes, ~2 disks/node for data)
```

### Architecture Diagram

```
Publishers                  Brokers (Kafka Cluster)             Consumers
                                                          
[Service A] ─────────┐    ┌─────────────────────────┐    ┌─── [Consumer Group X]
                     │    │  ┌─────────┐             │    │    [Worker 1]
[Service B] ─────────┼───►│  │Topic: T1│ Part 0 ─────┼────┤    [Worker 2]
                     │    │  │         │ Part 1 ─────┼────┼─── [Consumer Group Y]
[Service C] ─────────┘    │  │         │ Part 2 ─────┼────┤    [Worker 1]
                          │  └─────────┘             │    │    [Worker 2]
                          │                          │    │    [Worker 3]
                          │  ┌─────────┐             │    │
                          │  │Topic: T2│ Part 0 ─────┼────└─── [Consumer Group Z]
                          │  └─────────┘             │         [Worker 1]
                          │                          │
                          │  ZooKeeper / KRaft       │
                          │  (controller election,   │
                          │   partition assignment)  │
                          └─────────────────────────┘
                              
Offset tracking: each consumer group tracks (topic, partition, offset) independently
```

### Data Model

```sql
-- Topic registry (stored in ZooKeeper / internal topic)
CREATE TABLE topics (
    topic_name     VARCHAR(256) PRIMARY KEY,
    partition_count INT NOT NULL DEFAULT 1,
    replication_factor INT NOT NULL DEFAULT 3,
    retention_ms   BIGINT DEFAULT 604800000, -- 7 days
    created_at     TIMESTAMP DEFAULT NOW()
);

-- Message log (conceptual; physically stored as segment files on disk)
-- Each partition is an append-only log:
--   segment_0.log  [offset 0 .. 999999]
--   segment_1.log  [offset 1000000 .. 1999999]
--   ...
-- Record format (binary):
CREATE TABLE message_log (
    topic_name  VARCHAR(256),
    partition   INT,
    offset      BIGINT,          -- monotonically increasing per partition
    key         BYTES,           -- used for partitioning; nullable
    value       BYTES,           -- payload (JSON, Avro, Protobuf)
    headers     JSONB,           -- metadata (trace-id, content-type, etc.)
    timestamp   BIGINT,          -- epoch ms (producer or broker time)
    PRIMARY KEY (topic_name, partition, offset)
);

-- Consumer group offsets (stored in __consumer_offsets internal topic)
CREATE TABLE consumer_offsets (
    group_id    VARCHAR(256),
    topic_name  VARCHAR(256),
    partition   INT,
    committed_offset BIGINT,
    updated_at  TIMESTAMP,
    PRIMARY KEY (group_id, topic_name, partition)
);
```

### API Design

```
# Producer API
POST /topics/{topic}/messages
  Body: { "key": "user-123", "value": {...}, "headers": {"trace-id": "abc"} }
  Response: { "partition": 2, "offset": 100042, "timestamp": 1716900000000 }

POST /topics/{topic}/messages/batch
  Body: { "messages": [ {...}, {...} ] }  -- up to 1000 messages
  Response: { "results": [ {"partition": 0, "offset": 5001}, ... ] }

# Consumer API (pull model)
GET /consumer-groups/{group}/topics/{topic}/partitions/{partition}/messages
  Query: ?offset=5000&max_records=500&timeout_ms=1000
  Response: { "messages": [...], "next_offset": 5500 }

POST /consumer-groups/{group}/offsets/commit
  Body: { "offsets": [{"topic": "T1", "partition": 0, "offset": 5499}] }
  Response: { "status": "committed" }

# Admin API
POST /topics          -- create topic
DELETE /topics/{name} -- delete topic
GET /topics/{name}/lag?group={group}  -- consumer lag per partition
```

### Basic Scaling

- **Partition for parallelism:** Increase partition count so multiple consumers in a group work in parallel; one partition → one active consumer per group
- **Replication for durability:** Each partition replicated to 3 brokers (leader + 2 ISR followers); producer acks=all before returning
- **Retention + compaction:** Time-based retention (7 days) for event streams; log compaction (keep latest per key) for changelog topics (e.g., user profile updates)
- **Consumer lag monitoring:** Alert when committed offset falls > N minutes behind leader offset; scale consumer group horizontally

---

## Tier 2: L5+ Design (the staff interview answer)

### Capacity Planning (Real Numbers)

```
Write path (hot):
  Target: 1M msg/sec × 1 KB = 1 GB/sec
  Per broker: 100 MB/sec sustainable (NVMe + page cache)
  Leader brokers needed: 10
  With 3× replication (async followers): followers add 200 MB/sec each = 200 MB/sec × 20 followers
  Total cluster write: ~5 GB/sec network egress

Read path (fan-out to 10 consumer groups):
  10 groups × 1 GB/sec = 10 GB/sec read from page cache (zero-copy sendfile)
  Consumers that fall behind page cache hit disk: worst-case 10 GB/sec disk read
  Solution: tiered storage — cold offsets (>1h old) moved to S3; brokers become stateless for cold reads

Memory per broker:
  Page cache: 64 GB RAM per broker → caches ~64 s of hot data at 1 GB/sec
  Heap (JVM): 6 GB (keep small to avoid GC pauses)
  OS page cache handles all log I/O

Storage per broker (7-day retention, 1/10 of data = 60 TB / 10 leaders):
  6 TB per leader node (RAID-0 NVMe, 2× 4 TB drives)
  With 3× replication: each byte written to 3 nodes → 18 TB raw per replicated shard

Consumer group rebalancing:
  Triggered on: consumer joins/leaves, partition reassignment, session timeout
  Protocol: Group Coordinator (a broker) runs SYNC_GROUP / JOIN_GROUP rounds
  During rebalance: all consumers in group stop consuming (stop-the-world)
  Mitigation: incremental cooperative rebalancing (Kafka 2.4+) — only reassign partitions that moved
  Rebalance time: <5s for 1K partitions with cooperative protocol
```

### Failure Modes

```
Scenario 1: Leader broker dies
  - ZooKeeper/KRaft detects missed heartbeats (session.timeout = 6s)
  - Controller elects new leader from ISR (in-sync replicas)
  - Producers retry for ~30s; consumers pause and reconnect
  - Messages NOT in ISR at time of failure: lost if acks=1, safe if acks=all

Scenario 2: Consumer crashes mid-batch
  - Messages processed but not committed → redelivered on restart (at-least-once)
  - Fix: idempotent consumer (upsert by message offset, or dedup by message key+hash)
  - Fix: exactly-once with transactional producer + consumer (atomic write of result + offset)

Scenario 3: Broker disk full
  - Kafka stops accepting writes to partitions on that broker
  - Producers get NOT_ENOUGH_REPLICAS errors
  - Alert on disk usage >75%; auto-migrate partitions to less-full brokers (Cruise Control)

Scenario 4: Poison pill message (consumer crashes on specific message)
  - Consumer retries indefinitely → partition stops making progress
  - Fix: max retry count (e.g., 5); after threshold, forward to Dead Letter Queue (DLQ)
  - DLQ is just another Kafka topic; separate consumer alerts on DLQ lag
  - Fix: circuit breaker — consumer skips offset after N failures, records to error log

Scenario 5: Fan-out to 10K slow consumers
  - Each consumer reads independently; slow consumers fall behind page cache
  - Catch-up reads from disk compete with hot reads → disk I/O saturation
  - Fix: tiered storage (S3) for cold reads, keeping disk I/O for hot path
  - Fix: throttle slow consumers via quota (broker-side byte rate limit per group)
```

### Consistency Boundaries

```
Delivery semantics comparison:
  At-most-once:  acks=0, no retry → fire-and-forget, ~0 latency, data loss possible
  At-least-once: acks=all, retry on timeout → duplicates possible, consumer must dedup
  Exactly-once:  transactional producer (PID + epoch + sequence) + read_committed consumers
                 Overhead: ~20% throughput reduction; latency +5ms for coordinator round-trip

Message ordering:
  Within a partition: strict total order (offsets are monotonically increasing)
  Across partitions: no ordering guarantee
  Design implication: all messages for the same entity (e.g., user_id) must hash to same partition
  Key choice: use entity ID as message key → consistent hashing to partition

Exactly-once across systems (e.g., Kafka → DB):
  Pattern: write to DB with offset as idempotency key
  INSERT INTO orders (id, ...) VALUES (...) ON CONFLICT (kafka_offset) DO NOTHING;
  Then commit Kafka offset only after DB ack → exactly-once semantics end-to-end
```

### Cost Model

```
Kafka on AWS (MSK or self-managed EC2):

Broker nodes: 10 × r6i.4xlarge ($1.008/hr) = $10.08/hr = $7,260/month
Storage (EBS gp3): 600 TB × $0.08/GB/month = $48,000/month
  -- Optimization: use tiered storage, keep only 1 TB on EBS → $80/month on EBS
  -- Cold data on S3: 600 TB × $0.023/GB/month = $13,800/month
Network egress (fan-out 10 GB/sec): 10 GB/sec × 86400 × 30 × $0.09/GB ≈ $2.3M/month
  -- Optimization: place consumers in same AZ/region; inter-AZ traffic at $0.01/GB
  -- Inter-AZ cost: 1 GB/sec × 86400 × 30 × $0.01 ≈ $26K/month

ZooKeeper/KRaft controllers: 3 × m6i.xlarge = $0.192/hr × 3 = $416/month

Total self-managed: ~$55K/month at scale
Dominant cost driver: network egress (fan-out) — minimize with consumer colocation
Optimization: Kafka MirrorMaker for geo-replication only to consumers in other regions
```

---

## Trade-off Comparison

| Approach | Pros | Cons | Best For |
|----------|------|------|----------|
| **Kafka (partitioned log)** | High throughput (1M msg/sec), replay, consumer groups, durable | Operational complexity, JVM tuning, rebalance latency | Event streaming, audit logs, CDC pipelines |
| **RabbitMQ (traditional broker)** | Rich routing (exchanges, binding keys), push model, low latency, easy ops | No replay after ACK, queues not infinitely scalable, worse throughput | Task queues, RPC patterns, complex routing logic |
| **Redis Pub/Sub** | Ultra-low latency (<1ms), zero setup | No persistence (fire-and-forget), no consumer groups, no replay | Ephemeral notifications, live leaderboards, chat presence |
| **AWS SNS + SQS (fan-out pattern)** | Managed, auto-scale, 1 SNS topic → many SQS queues | No replay from SNS, SQS max 14-day retention, cost at scale | Serverless architectures, simple fan-out to Lambda |
| **Google Pub/Sub** | Global, exactly-once, managed, seek (replay) | Higher latency vs Kafka, vendor lock-in | Multi-region Google Cloud pipelines |

## Follow-up Questions (escalating difficulty)

1. **(L3)** What is the difference between a topic and a queue?
   → A queue delivers each message to exactly one consumer (competing consumers); a topic delivers each message to all subscribers independently. Kafka topics with consumer groups give you both behaviors simultaneously.

2. **(L3)** What happens if a consumer is slow and falls behind?
   → Consumer lag increases. The broker retains messages per the retention policy (e.g., 7 days). The consumer catches up on its own schedule. If it falls too far behind (past retention), it loses messages.

3. **(L4)** How do you ensure message ordering in Kafka?
   → Use the same partition key for all messages belonging to the same entity (e.g., user_id). All messages with the same key land on the same partition, which has strict total order. Never use multiple partitions for ordered streams without careful key design.

4. **(L4)** Explain at-least-once vs exactly-once semantics. When would you accept duplicates?
   → At-least-once: producer retries on timeout; consumer may receive duplicates. Acceptable for idempotent operations (e.g., updating a counter with max value). Exactly-once requires Kafka transactions (PID + epoch) and idempotent consumer writes; adds ~20% overhead. Use exactly-once for financial transactions, not for analytics.

5. **(L5)** You have a publisher writing 10K messages/sec to a topic with 1M subscribers. How do you handle fan-out?
   → Fan-out-on-read: each subscriber's consumer group reads the partition log independently (zero extra broker work). Brokers use Linux sendfile (zero-copy) for disk→network. The log is read N times but only written once. For push-based fan-out (e.g., mobile push notifications), a separate notification service reads from Kafka and batches pushes via APNs/FCM.

6. **(L5)** How does Kafka handle back-pressure?
   → Producers have a configurable buffer (buffer.memory). When the buffer is full, the send() call blocks (max.block.ms). Brokers enforce per-producer/consumer byte-rate quotas; exceeding the quota causes throttle delays injected by the broker. Consumers pull at their own pace — no push-based back-pressure needed on the read side.

7. **(L5+)** Design a geo-replicated pub-sub system with cross-region failover under 30 seconds.
   → Use MirrorMaker 2 (MM2) for active-active or active-passive replication. MM2 translates consumer offsets between clusters. For <30s failover: consumers are pre-configured with fallback bootstrap servers in the secondary region; on primary failure, DNS (Route53 health check) flips within 10-15s; consumers reconnect and MM2's offset mapping lets them resume from the equivalent offset in the secondary cluster. Total RTO: ~25s.

## Anti-patterns / Things NOT to Say

- **"Use a single partition for ordering"** — A single partition limits throughput to one broker. Use key-based partitioning to distribute load while preserving per-entity order. If you truly need global order, a single partition is acceptable only at low volume (<10 MB/sec).
- **"Increase partitions on an existing topic freely"** — Adding partitions to an existing topic breaks the key→partition mapping for messages already produced. Existing data won't be redistributed. Plan partition counts at topic creation (estimate 10× your initial throughput for headroom).
- **"Consumers should ACK immediately and process asynchronously"** — This creates at-most-once semantics; if the async processing fails, the message is lost. Always process before committing the offset.
- **"Kafka guarantees exactly-once out of the box"** — Exactly-once requires explicit configuration: `enable.idempotence=true`, `transactional.id` on producer, and `isolation.level=read_committed` on consumer. The default is at-least-once.
- **"Use Kafka for request-reply RPC"** — Kafka is optimized for one-way event streaming. For request-reply, the latency overhead (producer → broker → consumer → reply producer → reply broker → requester) adds 20-100ms even under ideal conditions. Use gRPC or a message queue with reply-to queues for RPC.

## Python Implementation (sketch)

```python
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

@dataclass
class Message:
    key: Optional[str]
    value: bytes
    offset: int = 0
    timestamp: float = field(default_factory=time.time)

class Partition:
    """Append-only log segment; simulates a Kafka partition."""

    def __init__(self):
        self._log: List[Message] = []
        self._lock = threading.Lock()

    def append(self, msg: Message) -> int:
        with self._lock:
            msg.offset = len(self._log)
            self._log.append(msg)
            return msg.offset

    def read(self, offset: int, max_records: int = 100) -> List[Message]:
        with self._lock:
            return self._log[offset: offset + max_records]

    def __len__(self) -> int:
        return len(self._log)


class Broker:
    """Minimal in-memory pub-sub broker with consumer group offset tracking."""

    def __init__(self, num_partitions: int = 4):
        self.partitions: List[Partition] = [Partition() for _ in range(num_partitions)]
        # group_id -> partition_id -> committed_offset
        self._offsets: Dict[str, Dict[int, int]] = defaultdict(lambda: defaultdict(int))
        self._lock = threading.Lock()

    def _partition_for(self, key: Optional[str]) -> int:
        if key is None:
            # Round-robin via thread-local counter (simplified)
            return int(time.time() * 1000) % len(self.partitions)
        return hash(key) % len(self.partitions)

    def publish(self, key: Optional[str], value: bytes) -> tuple[int, int]:
        part_id = self._partition_for(key)
        offset = self.partitions[part_id].append(Message(key=key, value=value))
        return part_id, offset

    def poll(self, group_id: str, partition_id: int,
             max_records: int = 100) -> List[Message]:
        offset = self._offsets[group_id][partition_id]
        msgs = self.partitions[partition_id].read(offset, max_records)
        return msgs

    def commit(self, group_id: str, partition_id: int, offset: int) -> None:
        with self._lock:
            self._offsets[group_id][partition_id] = offset + 1

    def lag(self, group_id: str) -> Dict[int, int]:
        result = {}
        for pid, part in enumerate(self.partitions):
            committed = self._offsets[group_id][pid]
            result[pid] = len(part) - committed
        return result


def consumer_worker(broker: Broker, group_id: str, partition_id: int,
                    handler: Callable[[Message], None], stop: threading.Event):
    """Long-poll consumer loop with at-least-once semantics."""
    while not stop.is_set():
        msgs = broker.poll(group_id, partition_id, max_records=50)
        if not msgs:
            time.sleep(0.05)  # 50ms back-off when no messages
            continue
        for msg in msgs:
            handler(msg)                         # process first
            broker.commit(group_id, partition_id, msg.offset)  # then commit


# Demo
if __name__ == "__main__":
    broker = Broker(num_partitions=3)

    received: List[str] = []
    stop = threading.Event()

    def handle(msg: Message):
        received.append(msg.value.decode())

    # Start one consumer per partition (simulates consumer group)
    threads = [
        threading.Thread(target=consumer_worker,
                         args=(broker, "group-A", pid, handle, stop), daemon=True)
        for pid in range(3)
    ]
    for t in threads:
        t.start()

    # Publish 12 messages with different keys
    for i in range(12):
        broker.publish(key=f"user-{i % 4}", value=f"event-{i}".encode())

    time.sleep(0.5)
    stop.set()

    print(f"Received {len(received)} messages: {sorted(received)}")
    print(f"Lag after processing: {broker.lag('group-A')}")
```

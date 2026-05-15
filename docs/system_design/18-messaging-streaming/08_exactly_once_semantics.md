# Exactly-Once Semantics in Distributed Systems

## Problem Statement

Design systems that process each message exactly once despite network failures, crashes, and retries — understanding the fundamental CAP-theorem trade-offs and practical implementation patterns.

## Architecture Diagram

```mermaid
graph TB
    subgraph EOS["Exactly-Once End-to-End"]
        P["Transactional\nProducer\n(idempotent)"]
        KB["Kafka Broker\n(transaction log)"]
        TC["Transaction\nCoordinator"]
        C["Consumer\nisolation=read_committed"]
        DB["Database\n(idempotency key)"]
    end

    P -->|begin_transaction| TC
    P -->|produce| KB
    C -->|consume + process| DB
    DB -->|commit offset| TC
    TC -->|commit transaction| KB
    TC -->|mark committed| KB
```

## Flow Diagram

```mermaid
sequenceDiagram
    participant P as Producer
    participant TC as Transaction Coordinator
    participant K as Kafka Partition
    participant C as Consumer
    participant DB as Database

    P->>TC: initTransactions(transactional.id="app-0")
    TC-->>P: ProducerID=42, epoch=1

    P->>TC: beginTransaction()
    P->>K: Produce record (PID=42, seq=0)
    P->>K: Produce record (PID=42, seq=1)
    P->>TC: commitTransaction()
    TC->>K: Write COMMIT marker
    K-->>TC: ACK
    TC-->>P: Transaction committed

    C->>K: Fetch (isolation=read_committed)
    K-->>C: Records (filtered: only committed)
    C->>DB: BEGIN; INSERT ...; UPDATE offset ...; COMMIT;
    Note over C,DB: Atomic: process + offset in same DB txn
```

## Design

### Kafka EOS Stack

```
Layer 1: Idempotent producer
  - Prevents duplicate writes within a session
  - ProducerID + sequence number per partition
  - Broker deduplicates: same (PID, partition, seq) = noop
  - Survives: producer retry, leader failover

Layer 2: Transactional producer
  - Survives producer restart (stable transactional.id)
  - Atomic multi-partition writes
  - Atomic: read(source) + write(sink) in one transaction

Layer 3: Read_committed consumers
  - Skip messages in open/aborted transactions
  - Only see committed data
  - Isolation: no dirty reads

End-to-end with database:
  1. BEGIN TRANSACTION (DB)
  2. Process message
  3. Write result to DB
  4. Commit consumer offset to DB (not Kafka)
  5. COMMIT (DB)
  = Atomic: process + offset in same DB txn
  = On crash: reprocess same message, idempotent writes prevent duplication
```

### Outbox Pattern

```
Problem: Write to DB and publish to Kafka atomically

Solution:
  1. BEGIN DB TRANSACTION
  2. UPDATE domain state
  3. INSERT INTO outbox (event_type, payload, created_at)
  4. COMMIT DB TRANSACTION

  Outbox relay (separate process):
  5. SELECT * FROM outbox WHERE published=false ORDER BY id
  6. Publish to Kafka
  7. UPDATE outbox SET published=true WHERE id=?

Guarantees:
  - Event published iff DB change committed
  - At-least-once (relay may retry)
  - Consumer idempotency handles duplicates

Tools: Debezium (CDC), Transactional Outbox libraries
```

### Saga Pattern

```
Long-running distributed transaction across services:
  Step 1: CreateOrder (OrderService) -> emit OrderCreated
  Step 2: ReserveInventory (InventoryService) -> emit InventoryReserved
  Step 3: ChargePayment (PaymentService) -> emit PaymentProcessed
  Step 4: ShipOrder (ShippingService) -> emit OrderShipped

On failure (compensation):
  PaymentFailed -> emit: CancelInventoryReservation, CancelOrder

Choreography: services react to events (no central coordinator)
Orchestration: central saga orchestrator sends commands
```

## Common Questions & Answers

**Q: Is exactly-once semantics truly achievable?** A: Within a single system (Kafka, database): yes. Across systems: requires careful design (idempotency keys, two-phase commit, Saga). True global EOS over unreliable networks = impossible (FLP impossibility), but practical EOS is achievable.

**Q: What is the cost of Kafka EOS?** A: ~20% throughput reduction. Extra round-trips for transaction coordinator. `read_committed` consumers skip transaction markers (small overhead). Acceptable for critical data pipelines, overkill for logging.

**Q: How does the Outbox Pattern prevent the dual-write problem?** A: Dual-write (write DB + write Kafka separately) is unsafe: one can fail. Outbox uses a single DB transaction for both state + event. Relay publishes with at-least-once; consumer idempotency makes it exactly-once end-to-end.

**Q: When should you NOT use exactly-once?** A: High-throughput metrics/logging (accept duplicates). Idempotent operations (dedup is free). Simple read-heavy workloads. Non-critical notifications. EOS adds latency and complexity — use it only when correctness matters.

**Q: How does two-phase commit (2PC) differ from Kafka transactions?** A: 2PC: distributed coordinator locks all participants, blocking. Kafka: coordinator is co-located (same broker), non-blocking. 2PC across different systems (e.g., Kafka + Postgres) is complex and avoided in practice.

## Back-of-Envelope Calculations

```
Kafka EOS overhead:
  Non-transactional: 1M msg/s baseline
  Idempotent only: 950K msg/s (-5%)
  Transactional: 800K msg/s (-20%)
  
  Additional latency: +5-20ms per transaction (coordinator RTT)

Outbox table throughput:
  10K events/s -> 10K inserts/s to outbox table
  Postgres IOPS: ~50K/s -> margin comfortable
  Relay polling: SELECT ... LIMIT 1000 every 10ms = 100K events/s
  
Idempotency table TTL:
  At 10K msg/s, 5-minute window: 3M dedup entries
  At 100 bytes/entry: 300MB RAM (use Redis for this)

Saga compensation rate:
  1% failure rate, 1K tx/s = 10 compensations/s
  Each compensation = 2-3 additional events
  Negligible extra load
```

## Design Choices

| Pattern | Guarantee | Complexity | Cross-System |
|---|---|---|---|
| Kafka EOS (transactions) | Exactly-once | Medium | No |
| Outbox Pattern | Exactly-once | Medium | Yes |
| Idempotent consumer | At-least-once + dedup | Low | Yes |
| 2PC | Exactly-once | High | Yes (but fragile) |
| Saga | Eventually consistent | High | Yes |
| TCC (Try-Confirm-Cancel) | Exactly-once | High | Yes |

## Follow-up Questions

1. How does Debezium implement the Outbox Pattern via Change Data Capture?
2. How does the TCC (Try-Confirm-Cancel) pattern differ from Saga?
3. How do you implement idempotency in a REST API?
4. How does Kafka Streams achieve exactly-once with state stores?
5. What is the role of epoch numbers in Kafka producer fencing?

## Python Implementation

```python
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Set
import uuid
import time
import random

@dataclass
class TransactionRecord:
    txn_id: str
    producer_id: int
    epoch: int
    state: str  # "ongoing", "committed", "aborted"
    records: List[dict] = field(default_factory=list)
    committed_at: Optional[float] = None

class TransactionCoordinator:
    def __init__(self):
        self._transactions: Dict[str, TransactionRecord] = {}
        self._producer_epochs: Dict[str, tuple] = {}  # transactional_id -> (pid, epoch)

    def init_transactions(self, transactional_id: str) -> tuple[int, int]:
        if transactional_id in self._producer_epochs:
            old_pid, old_epoch = self._producer_epochs[transactional_id]
            epoch = old_epoch + 1
            pid = old_pid
            print(f"  [TxnCoord] Fencing old epoch {old_epoch} for {transactional_id}")
        else:
            pid = random.randint(1000, 9999)
            epoch = 0
        self._producer_epochs[transactional_id] = (pid, epoch)
        return pid, epoch

    def begin(self, producer_id: int, epoch: int) -> str:
        txn_id = str(uuid.uuid4())
        self._transactions[txn_id] = TransactionRecord(txn_id, producer_id, epoch, "ongoing")
        return txn_id

    def add_record(self, txn_id: str, record: dict):
        if txn_id in self._transactions:
            self._transactions[txn_id].records.append(record)

    def commit(self, txn_id: str) -> bool:
        txn = self._transactions.get(txn_id)
        if not txn or txn.state != "ongoing":
            return False
        txn.state = "committed"
        txn.committed_at = time.time()
        return True

    def abort(self, txn_id: str):
        txn = self._transactions.get(txn_id)
        if txn:
            txn.state = "aborted"

    def get_committed_records(self, up_to_txn: Optional[str] = None) -> List[dict]:
        committed = []
        for txn in self._transactions.values():
            if txn.state == "committed":
                committed.extend(txn.records)
        return committed

class TransactionalProducer:
    def __init__(self, transactional_id: str, coordinator: TransactionCoordinator):
        self.transactional_id = transactional_id
        self._coordinator = coordinator
        self._pid, self._epoch = coordinator.init_transactions(transactional_id)
        self._current_txn: Optional[str] = None
        self._seq: Dict[str, int] = {}
        print(f"[Producer] Initialized: pid={self._pid}, epoch={self._epoch}")

    def begin_transaction(self):
        if self._current_txn:
            raise RuntimeError("Transaction already active")
        self._current_txn = self._coordinator.begin(self._pid, self._epoch)

    def send(self, topic: str, key: str, value: Any) -> dict:
        if not self._current_txn:
            raise RuntimeError("No active transaction")
        partition_key = f"{topic}-0"
        seq = self._seq.get(partition_key, 0)
        self._seq[partition_key] = seq + 1
        record = {
            "topic": topic, "key": key, "value": value,
            "pid": self._pid, "epoch": self._epoch, "seq": seq,
        }
        self._coordinator.add_record(self._current_txn, record)
        return record

    def commit_transaction(self):
        if not self._current_txn:
            raise RuntimeError("No active transaction")
        success = self._coordinator.commit(self._current_txn)
        if success:
            print(f"[Producer] Transaction {self._current_txn[:8]}... committed")
        self._current_txn = None
        return success

    def abort_transaction(self):
        if self._current_txn:
            self._coordinator.abort(self._current_txn)
            print(f"[Producer] Transaction {self._current_txn[:8]}... aborted")
            self._current_txn = None

class OutboxProcessor:
    def __init__(self):
        self._outbox: List[dict] = []
        self._published: Set[str] = set()
        self._domain_state: Dict[str, Any] = {}

    def write_with_outbox(self, entity_id: str, new_state: Any, event_type: str, event_payload: dict):
        event_id = str(uuid.uuid4())
        # Simulate atomic DB transaction
        self._domain_state[entity_id] = new_state
        self._outbox.append({
            "id": event_id,
            "event_type": event_type,
            "payload": event_payload,
            "published": False,
            "created_at": time.time(),
        })
        print(f"[Outbox] Wrote {event_type} for {entity_id} (event_id={event_id[:8]}...)")

    def relay(self, publish_fn: Callable[[dict], None]):
        for item in self._outbox:
            if not item["published"]:
                publish_fn(item)
                item["published"] = True
                self._published.add(item["id"])
                print(f"[Relay] Published {item['event_type']} (id={item['id'][:8]}...)")

class IdempotentConsumer:
    def __init__(self):
        self._processed_ids: Set[str] = set()
        self._results: List[Any] = []

    def process(self, event: dict, handler: Callable[[dict], Any]) -> bool:
        event_id = event.get("id")
        if event_id in self._processed_ids:
            print(f"  [Consumer] Duplicate event {event_id[:8]}..., skipping")
            return False
        result = handler(event)
        self._processed_ids.add(event_id)
        self._results.append(result)
        return True

# Demo
coordinator = TransactionCoordinator()

print("=== Transactional Producer ===")
producer = TransactionalProducer("order-service-0", coordinator)
producer.begin_transaction()
producer.send("orders", "order-1", {"amount": 100})
producer.send("inventory", "item-A", {"delta": -1})
producer.commit_transaction()

print("\n=== Simulate producer restart (epoch bump) ===")
producer2 = TransactionalProducer("order-service-0", coordinator)  # Same transactional_id
producer2.begin_transaction()
producer2.send("orders", "order-2", {"amount": 200})
producer2.commit_transaction()

print("\n=== Committed records (read_committed) ===")
for r in coordinator.get_committed_records():
    print(f"  {r['topic']}/{r['key']}: {r['value']}")

print("\n=== Outbox Pattern ===")
outbox = OutboxProcessor()
outbox.write_with_outbox("user-1", {"email": "alice@ex.com", "verified": True},
                          "UserCreated", {"user_id": "user-1"})

published = []
outbox.relay(lambda e: published.append(e))

print("\n=== Idempotent Consumer ===")
consumer = IdempotentConsumer()
for event in published:
    consumer.process(event, lambda e: f"Handled {e['event_type']}")
# Simulate retry
for event in published:
    consumer.process(event, lambda e: f"Handled {e['event_type']}")
```

## Java Implementation

```java
import java.util.*;

public class ExactlyOnceDemo {
    record Event(String id, String type, Map<String, Object> payload) {}

    static class IdempotentProcessor {
        private final Set<String> processed = new HashSet<>();
        private int duplicates = 0;

        boolean process(Event e, Runnable handler) {
            if (processed.contains(e.id())) { duplicates++; return false; }
            handler.run();
            processed.add(e.id());
            return true;
        }

        int getDuplicates() { return duplicates; }
    }

    static class OutboxSimulator {
        Map<String, Object> state = new HashMap<>();
        List<Event> outbox = new ArrayList<>();

        void writeWithOutbox(String id, Object newState, String eventType) {
            state.put(id, newState);
            outbox.add(new Event(UUID.randomUUID().toString(), eventType, Map.of("id", id)));
        }

        List<Event> relay() {
            List<Event> published = new ArrayList<>(outbox);
            outbox.clear();
            return published;
        }
    }

    public static void main(String[] args) {
        OutboxSimulator outbox = new OutboxSimulator();
        outbox.writeWithOutbox("order-1", Map.of("status", "created"), "OrderCreated");
        List<Event> events = outbox.relay();

        IdempotentProcessor processor = new IdempotentProcessor();
        // First delivery
        events.forEach(e -> processor.process(e, () -> System.out.println("Processed: " + e.type())));
        // Retry (duplicate)
        events.forEach(e -> processor.process(e, () -> System.out.println("Should not print")));
        System.out.println("Duplicates: " + processor.getDuplicates());
    }
}
```

## Complexity

| Operation | Time |
|---|---|
| Idempotency check (hash set) | O(1) |
| Transaction commit (Kafka) | O(1) + 2 RTT |
| Outbox relay poll | O(unpublished events) |
| Saga compensation | O(steps) |
| Producer epoch fence | O(1) |

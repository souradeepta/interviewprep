# Message Queues & Event Streaming — Asynchronous Communication at Scale

**Level:** L4-L5
**Time to read:** ~10 min

Building decoupled, resilient systems.

---

## 📨 Message Queues vs. Event Streams

### Message Queues (RabbitMQ, AWS SQS)

```
Sender → Queue → Receiver (consumes & deletes)

Properties:
- Point-to-point messaging
- Message deleted after consumption
- Good for job queues, notifications

Use case: Send email, process order
```

### Event Streams (Kafka, AWS Kinesis)

```
Producer → Topic → Multiple Subscribers
Events retained (replayed)

Properties:
- Pub-sub, multiple consumers
- Events stored, can be replayed
- Good for event sourcing, analytics

Use case: User activity stream, monitoring
```

---

## 🏗️ Architecture Patterns

### Event-Driven Architecture

```
Request → Service → Publish Event → Other Services React

Benefits:
- Decoupling: Services don't call each other
- Scalability: Easy to add subscribers
- Auditability: Event log

Challenges:
- Eventual consistency
- Complexity (distributed systems)
```

### Saga Pattern (Distributed Transactions)

```
Transaction split across services:
1. Service A: Reserve inventory (publish event)
2. Service B: Process payment (subscribe, respond)
3. Service A: Confirm order or rollback

Choreography: Services listen and respond
Orchestration: Central coordinator
```

---

## 📊 Ordering Guarantees

```
At-most-once: May lose messages (fast)
At-least-once: Messages delivered, may duplicate (reliable)
Exactly-once: Complex, expensive guarantee
```

### Idempotency

```
Receiving same message twice = same result
Idempotency key: Unique ID per message
Database: Check if already processed
```

---

## 💾 Retention & Replay

```
Message Queue: Delete after consumption
Event Stream: Retain for days/months

Replay: Re-process events from beginning
Use: Bug fixes, new subscriber, audit
```

---

## ❓ Interview Q&A

**Q: When to use message queues vs. streams?**
A: Queues for jobs (email, notifications). Streams for events (audit log, analytics).

**Q: How to ensure exactly-once delivery?**
A: Idempotent operations + idempotency keys. Difficult, often at-least-once sufficient.

**Q: Design order processing system.**
A: Order service publishes event. Payment service subscribes, processes. Saga pattern for rollback.

---

**Last updated:** 2026-05-22

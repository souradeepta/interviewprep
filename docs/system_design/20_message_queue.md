# Message Queue System

## Problem Statement
Design a publish-subscribe message queue for asynchronous processing.

**Operations:**
- `publish(topic, message)` — Publish message
- `subscribe(topic, callback)` — Subscribe to topic
- `consume(queue, n)` — Consume n messages
- `acknowledge(message_id)` — ACK processed message

## Design

### Queue Structure

```
Topics: Channels for messages
Partitions: Within topic for parallelism
Consumer groups: Multiple consumers per topic
Offset: Position in partition
```

### Delivery Guarantees

```
At-most-once: Fire and forget
At-least-once: Resend until ACK
Exactly-once: Deduplication + ordering
```

### Dead Letter Queue

```
Failed messages → DLQ
Manual inspection
Retry with backoff
```

## Complexity

| Operation | Time |
|-----------|------|
| Publish | O(1) |
| Consume | O(k) where k=batch |
| ACK | O(1) |

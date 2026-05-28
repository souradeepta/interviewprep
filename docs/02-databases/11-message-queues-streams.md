# Message Queues & Event Streaming — Kafka, RabbitMQ, and Beyond

**Level:** L4-L5
**Time to read:** ~20 min

Asynchronous communication for distributed systems with message ordering and durability.

---

## ⚖️ Message Queue vs. Event Stream Comparison

```
Feature              | Message Queue      | Event Stream
─────────────────────|────────────────────|──────────────
Delivery            | At-most-once       | Exactly-once possible
Message History     | Deleted on read    | Permanent (days/months)
Consumer Scale      | Single consumer    | Multiple consumers
Replayability       | No                 | Yes (replay from offset)
Throughput          | 10K-100K msgs/sec  | 100K-1M msgs/sec
Latency             | <100ms             | <10ms
Use Case            | Task queue         | Audit log, event source
Ordering            | Per queue          | Per partition

When Message Queue (RabbitMQ, AWS SQS):
├─ Task-based (send email, process order)
├─ One-time processing
├─ Different consumer types
└─ Simple acknowledgment model

When Event Stream (Kafka, Pulsar):
├─ Event-driven architecture
├─ Multiple consumers of same events
├─ Replay/audit trail needed
└─ High throughput required
```

---

## 🏗️ Architecture Patterns

### Pub/Sub Pattern

```
Publisher → Topic/Channel → Subscribers
            (RabbitMQ, Kafka)

Subscribers receive copy of message
Multiple independent consumers possible
Each processes at own pace
```

### Event Sourcing Pattern

```
Event Store: Append-only log of all events
├─ User signed up
├─ User updated profile
├─ User placed order
├─ Order shipped
└─ ...

Current state = Replay all events
Audit trail = Built-in
Recovery = Replay from event store
```

---

## 📊 Throughput & Scale Comparison

```
System          | Throughput | Latency | Scale    | Persistence
─────────────────|──────────|──────────|──────────|────────────
RabbitMQ        | 100K/sec | 50ms    | Millions | Optional
Apache Kafka    | 1M/sec   | <10ms   | Billions | Days
AWS Kinesis     | 1M/sec   | <100ms  | Billions | 24h default
AWS SQS         | 10K/sec  | 1s      | Millions | 14d default
Google Pub/Sub  | 1M/sec   | <100ms  | Billions | 7d default
Apache Pulsar   | 2M/sec   | <10ms   | Billions | Configurable
```

---

## 🧪 Practical Exercises

### Exercise 1: Design Order Processing Queue (Easy)

**Problem:**
E-commerce: Process 1000 orders/sec, send emails, update inventory, charge payment

**Solution:**

```python
import pika

# RabbitMQ for task queue (order processing)
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Durable queue (survives restarts)
channel.queue_declare(queue='orders', durable=True)

def process_order(ch, method, properties, body):
    order_data = json.loads(body)
    
    # Step 1: Charge payment
    payment_result = charge_payment(order_data)
    if not payment_result:
        # Reject message (requeue)
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        return
    
    # Step 2: Update inventory
    update_inventory(order_data['items'])
    
    # Step 3: Send email
    send_email(order_data['email'], f"Order {order_data['id']} confirmed")
    
    # Acknowledge (remove from queue)
    ch.basic_ack(delivery_tag=method.delivery_tag)

# Consumer (worker)
channel.basic_consume(
    queue='orders',
    on_message_callback=process_order,
    auto_ack=False
)

# Scale: Run multiple workers in parallel
# RabbitMQ distributes messages round-robin
channel.basic_qos(prefetch_count=1)  # Process 1 at a time
channel.start_consuming()

# Publisher
def publish_order(order_data):
    channel.basic_publish(
        exchange='',
        routing_key='orders',
        body=json.dumps(order_data),
        properties=pika.BasicProperties(delivery_mode=2)  # Persistent
    )
```

**Trade-offs:**
- ✓ Simple, reliable task processing
- ✗ No message history (lost after processing)
- ✗ No replay capability
- Best for: Transient tasks

---

### Exercise 2: Design Event Stream for Analytics (Medium)

**Problem:**
Track 1B user events/day (page views, clicks, purchases), replay for analysis

**Solution:**

```python
from kafka import KafkaProducer, KafkaConsumer
import json
from datetime import datetime

# Kafka for event streaming
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Publish events
def track_event(user_id, event_type, properties):
    event = {
        'user_id': user_id,
        'event_type': event_type,
        'timestamp': datetime.now().isoformat(),
        'properties': properties
    }
    
    # Partition by user_id (ensures order per user)
    producer.send('user_events', value=event, key=str(user_id).encode())

# Examples
track_event(123, 'page_view', {'page': '/products'})
track_event(123, 'click', {'product_id': 456})
track_event(123, 'purchase', {'items': [456], 'total': 99.99})

# Consumer 1: Real-time analytics
consumer1 = KafkaConsumer(
    'user_events',
    bootstrap_servers=['localhost:9092'],
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    group_id='analytics_group',
    auto_offset_reset='earliest'
)

for message in consumer1:
    event = message.value
    # Update dashboards, metrics
    track_in_analytics(event)

# Consumer 2: Data warehouse (same data, different processing)
consumer2 = KafkaConsumer(
    'user_events',
    bootstrap_servers=['localhost:9092'],
    group_id='warehouse_group'
)

for message in consumer2:
    # Store in S3/Hadoop for batch analysis
    store_in_data_lake(message.value)

# Consumer 3: Fraud detection (can start anytime)
# Kafka stores messages for 7 days by default
# New consumer replays from beginning
```

**Trade-offs:**
- ✓ Multiple consumers independently
- ✓ Replay capability (audit trail)
- ✓ High throughput (1M events/sec)
- ✗ More complex (partitions, offsets, groups)
- Best for: Event-driven architectures

---

### Exercise 3: Handle Message Ordering & Failures (Hard)

**Problem:**
Process financial transactions in order (user A sends $100 to B, then $50 back)
Handle consumer crashes mid-processing

**Solution:**

```python
from kafka import KafkaProducer, KafkaConsumer
import json

# Key insight: Partition by user_id to maintain order per user
producer = KafkaProducer(bootstrap_servers=['localhost:9092'])

# Transaction 1: A → B ($100)
transaction1 = {
    'from_user': 'user_a',
    'to_user': 'user_b',
    'amount': 100,
    'id': 'tx_001'
}
producer.send('transactions', 
              value=json.dumps(transaction1).encode(),
              key=b'user_a')  # Partition by source user

# Transaction 2: B → A ($50)
transaction2 = {
    'from_user': 'user_b',
    'to_user': 'user_a',
    'amount': 50,
    'id': 'tx_002'
}
producer.send('transactions',
              value=json.dumps(transaction2).encode(),
              key=b'user_a')  # Same partition (preserves order)

# Consumer with idempotent processing
class TransactionProcessor:
    def __init__(self):
        self.processed = set()  # Track processed IDs
        self.db = Database()    # Persistent storage
    
    def process_transaction(self, tx):
        # Check if already processed (idempotency)
        if self.db.transaction_exists(tx['id']):
            return True
        
        try:
            # Process
            self.db.transfer_money(tx['from_user'], tx['to_user'], tx['amount'])
            self.processed.add(tx['id'])
            
            # Commit offset only after processing
            self.consumer.commit()
            
        except Exception as e:
            # Failed transaction
            # Consumer will reprocess from last committed offset on restart
            print(f"Failed: {e}")
            raise

consumer = KafkaConsumer(
    'transactions',
    bootstrap_servers=['localhost:9092'],
    group_id='transaction_processor',
    enable_auto_commit=False,  # Manual commit
    auto_offset_reset='earliest'
)

for message in consumer:
    tx = json.loads(message.value)
    processor.process_transaction(tx)

# Guarantees:
# 1. Order: Partitioned by user_id, processed sequentially
# 2. No duplicates: Idempotent processing + unique IDs
# 3. Exactly-once: Only commit after successful processing
# 4. Crash-safe: Restart replays unprocessed messages
```

---

## ❓ Interview Q&A

**Q: When would you use Kafka vs. RabbitMQ?**

A:
```
Kafka when:
✓ Need message history/replay
✓ High throughput (1M+/sec)
✓ Multiple independent consumers
✓ Event sourcing pattern
✓ Analytics/data pipeline

RabbitMQ when:
✓ Task queue (one-time processing)
✓ Different consumer types
✓ Don't need replay
✓ Simpler setup
✓ Medium throughput (100K/sec)
```

**Q: Design system for processing 1B events/day with replay capability**

A: Use Kafka with 10 partitions, 3-day retention, multiple consumer groups for different purposes (analytics, warehouse, fraud detection).

---

## 💡 Interview Tips

- Trade-offs: Kafka is powerful but more complex
- Ordering: Partition by entity ID for sequential processing
- Exactly-once: Combine idempotent processing + offset management
- Failures: Plan for consumer crashes and message replay

---

**Last updated:** 2026-05-22

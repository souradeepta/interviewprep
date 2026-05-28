# Message Queue Patterns: Async Communication and Event Streaming

**Level:** L4-L5
**Time to read:** ~20 min

Master message queue patterns for decoupling services and handling async workloads.

---

## Message Queue Fundamentals

**Purpose:** Decouple producer from consumer, ensure delivery, handle bursts.

```
Producer → [Queue] → Consumer
           (async, durable)
```

---

## Queue Patterns

### Point-to-Point (Task Queue)

```
Producer sends task
    ↓
Task goes to queue
    ↓
One consumer picks up task
    ↓
Task processed once

Example: Order processing queue
- Producer: OrderService publishes "ProcessOrder"
- Consumer: PaymentService processes payment
```

```python
# Using Celery/RabbitMQ
@app.task
def process_payment(order_id):
    order = db.get_order(order_id)
    payment_service.charge(order.user_id, order.amount)

# Producer
process_payment.delay(order_id=123)
```

### Pub-Sub (Event Stream)

```
Producer publishes event
    ↓
Event goes to topic
    ↓
Multiple subscribers get event

Example: User registered event
- Producer: UserService publishes "UserRegistered"
- Subscribers: 
  - WelcomeEmail sends email
  - AnalyticsService logs event
  - RecommendationService initializes recommendations
```

```python
# Using Kafka
producer = KafkaProducer(bootstrap_servers=['localhost:9092'])
producer.send('user-events', value={'type': 'user_registered', 'user_id': 123})

# Consumer 1: Email service
consumer1.subscribe(['user-events'])
for msg in consumer1:
    if msg.value['type'] == 'user_registered':
        send_welcome_email(msg.value['user_id'])

# Consumer 2: Analytics
consumer2.subscribe(['user-events'])
for msg in consumer2:
    if msg.value['type'] == 'user_registered':
        log_analytics(msg.value)
```

---

## Queue Technologies

| Tool | Type | Durability | Use Case |
|------|------|-----------|----------|
| **RabbitMQ** | Broker | Durable | Reliable task queues |
| **Kafka** | Event stream | Persistent | Event streaming, log aggregation |
| **SQS** | Managed queue | Durable | AWS ecosystem |
| **Redis** | In-memory | Non-durable | Real-time, caching |
| **Celery** | Task queue | Depends on backend | Python async tasks |

---

## Message Delivery Guarantees

### At-Most-Once
```
Producer sends message
↓
If crash: message might be lost
↓
Consumer: Exactly 0 or 1 delivery

Pros: Fast, simple
Cons: Data loss possible
Use: Analytics, logs where loss is acceptable
```

### At-Least-Once
```
Producer sends message
↓
Broker: Durably stored
↓
Consumer processes, acknowledges
↓
If crash before ack: retransmitted

Pros: No data loss
Cons: Duplicates possible
Use: Most applications (payments, orders)
```

### Exactly-Once (Hardest)
```
Producer sends with unique ID
↓
Consumer: Check if seen before
↓
If duplicate: Skip processing
↓
Guarantee: Exactly 1 processing

Pros: No loss, no duplicates
Cons: Complex, slower
Use: Financial transactions
```

---

## Dead Letter Queues

```
Message fails multiple times
    ↓
Moved to Dead Letter Queue
    ↓
Manual inspection/retry

Prevents: Queue getting stuck on bad message
```

```python
class RetryableConsumer:
    def process(self, message):
        try:
            return self.handle(message)
        except Exception as e:
            if message.retry_count < 3:
                message.retry_count += 1
                self.queue.requeue(message)  # Retry
            else:
                self.dead_letter_queue.send(message)  # Give up
```

---

## Async Patterns

### Fan-Out (One Producer, Multiple Consumers)

```
OrderService publishes "OrderCreated"
    ↓
├─ PaymentService consumes
├─ ShippingService consumes
├─ NotificationService consumes
└─ AnalyticsService consumes
```

### Fan-In (Multiple Producers, One Consumer)

```
├─ UserService publishes "UserEvent"
├─ OrderService publishes "OrderEvent"
└─ ProductService publishes "ProductEvent"
    ↓
AnalyticsService consumes all and aggregates
```

---

## Message Queue Checklist

- ✓ Identified producer/consumer roles
- ✓ Chose queue type (task or event stream)
- ✓ Chose technology (RabbitMQ, Kafka, SQS, etc.)
- ✓ Set delivery guarantee (at-least-once typical)
- ✓ Implemented idempotency for duplicates
- ✓ Dead letter queue for failed messages
- ✓ Monitoring: queue depth, consumer lag
- ✓ Retention policy (how long to keep messages)
- ✓ Scaling: auto-scale consumers with queue depth
- ✓ Tested message loss scenarios


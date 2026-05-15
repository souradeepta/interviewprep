# Pub-Sub System

## Problem Statement

Implement a publish-subscribe messaging system where publishers send messages to topics and subscribers receive them asynchronously.

**Requirements:**
- Topics (channels for messages)
- Publish messages to topics
- Subscribe to topics
- Async message delivery
- Multiple subscribers per topic

## Design

### Architecture

```
Publisher ---→ Topic ---→ Subscriber1
                  │    ---→ Subscriber2
                  └-------→ Subscriber3
```

### Key Components

```
Topic: Channel holding subscribers and message queue
Publisher: Publishes messages to topics
Subscriber: Receives messages from subscribed topics
Message: Data being published
```

### Data Structure

```
topics: {topic_name -> [subscribers, message_queue]}
subscribers: {subscriber_id -> subscribed_topics[]}
```

### Operations

```
subscribe(subscriber, topic):
  topics[topic].subscribers.add(subscriber)

publish(topic, message):
  for each subscriber in topics[topic].subscribers:
    subscriber.receive(message)

receive(subscriber, message):
  subscriber.onMessage(message)
```


## Scenario

Pub-Sub System is a critical component in modern distributed systems. In real-world applications, handling complex business logic at scale with high reliability. For example, major tech companies like Netflix, Uber, and Airbnb rely on similar solutions to handle millions of concurrent users and requests. The challenge is achieving this while maintaining sub-100ms latency, 99.99% availability, and gracefully handling 10x traffic spikes during peak demand. This component provides the foundational capability to solve these challenges reliably and efficiently at global scale.

## Users

- **Backend Engineers**: Responsible for implementing and maintaining this system component in production environments. They need to understand the architecture, trade-offs, failure modes, and operational considerations.
- **DevOps/SRE Teams**: Monitor system health, manage scaling policies, handle incidents, and ensure reliability SLAs are met. They need insights into performance characteristics, bottlenecks, and failure recovery mechanisms.
- **Data Engineers**: Design data pipelines and analytics around this system, requiring deep understanding of data flow, consistency guarantees, and throughput characteristics.
- **System Architects**: Make high-level architectural decisions that impact company infrastructure, requiring comprehensive understanding of capabilities, limitations, and scalability boundaries.
- **Security Teams**: Understand security implications, potential vulnerabilities, and compliance requirements for this component.

## PRD

**Functional Requirements:**
- Correct behavior under all specified operating conditions
- Reliable operation with explicit failure modes
- Data consistency or eventual consistency guarantees as specified
- Clear mechanisms for error handling and recovery
- Monitoring and observability hooks

**Non-Functional Requirements:**
- **Performance**: Sub-100ms P99 latency for standard operations; measure and track tail latencies
- **Availability**: 99.99%+ uptime with automatic failover and graceful degradation
- **Scalability**: Support 10-100x current load with minimal architectural modifications
- **Consistency**: Specify whether strong, eventual, or causal consistency is required
- **Cost Efficiency**: Minimize operational cost per unit of throughput; consider compute, memory, and network costs
- **Operational Simplicity**: Reduce complexity to minimize human error and operational toil

**Constraints:**
- Resource limits (memory for caches, disk for databases, network bandwidth)
- Deployment constraints (cloud provider limits, regulatory requirements)
- Latency budgets (maximum acceptable delay for operations)

## Flow

The typical operational flow for this system involves these key phases:

1. **Request Arrival**: Client/upstream system sends request with required parameters and context
2. **Validation & Routing**: System validates request format, authentication, and routes to correct handler/shard/instance
3. **Core Processing**: Execute the main algorithm, database query, or business logic on the data/state
4. **State Management**: Update internal state (caches, indexes, counters, logs) with proper atomicity and locking
5. **Response Generation**: Format results and return to requester with relevant metadata (timing, version info)
6. **Observability**: Record metrics (latency, throughput, errors), logs (for debugging), and traces (for performance analysis)

This flow repeats thousands or millions of times per second in production. Each operation's efficiency compounds across the entire system, making careful optimization essential. Bottlenecks at any phase can cascade to impact overall system performance.

## Code Explanation

The provided implementations demonstrate key architectural concepts and design patterns:

**Python Implementation**: Uses built-in Python structures and standard library features to express the core logic clearly. Python emphasizes readability and conciseness—each operation's purpose should be obvious without extensive comments. You'll see different implementation approaches (e.g., using OrderedDict vs. manual linked lists) that represent trade-offs between convenience and fine-grained control.

**Java Implementation**: Shows how to implement the same logic with explicit memory management and type safety. Java's strong typing forces clear interface design; you'll see how generics, null safety, mutable state, and thread safety are handled. This implementation style is closer to production systems at scale.

**Key Implementation Patterns**:
- **Initialization**: Setting up core data structures, thread pools, or connection pools with specified capacity and configuration
- **Read Operations**: Fetching data while maintaining O(1) or O(log n) access, updating metadata (access times, hit counts, etc.)
- **Write Operations**: Inserting/updating data while handling eviction policies, balancing tree structures, or replicating state
- **Edge Cases**: Handling capacity limits, concurrent access, data consistency, and error conditions
- **Performance Optimization**: Using techniques like batch operations, lazy evaluation, or caching to reduce latency

Each line of code represents a deliberate choice about performance characteristics, memory usage, safety guarantees, and implementation complexity. Understanding these trade-offs is essential for using this component effectively in production systems.

## Architecture Diagram

```
┌──────────────────────────────────────────┐
│      Pub-Sub Broker (Central Hub)        │
│  ┌──────────────────────────────────────┐│
│  │  Topics: {topic → [sub1, sub2, ...]}  ││
│  │  Message Queue: [msg1, msg2, ...]    ││
│  │  Subscriptions: {subscriber → topics} ││
│  └──────────────────────────────────────┘│
└──────────────────────────────────────────┘
        ↑ publish       ↓ subscribe/notify
┌───────┴──────┐      ┌──────┴────────┐
│              │      │               │
▼              ▼      ▼               ▼
Pub1    Pub2   Sub1   Sub2   Sub3   Sub4
(writes)       (reads)
```

## Back-of-Envelope Calculations

For typical pub-sub (10 topics, 100 publishers, 1000 subscribers, 100K msg/sec):
- Storage: 1000 topics × 100 subscribers = 100K subscriptions × 16 bytes = 1.6MB registry
- Message queue: 100K msg/sec × 100 bytes = 10MB/sec, need 10-100GB buffer for 10s-100s latency
- Throughput: 100K msg/sec per broker, scale via sharding by topic
- Latency: Push ~1-10ms, Pull ~100ms (polling interval)

Network: ~10Gbps for 100K msg/sec × 100 bytes. Need clustering/sharding.

## Design Choice Comparison

| Approach | Pros | Cons |
|----------|------|------|
| In-Memory Hash | Simple, fast O(1) | All data in RAM, no persistence |
| Message Queue (Redis) | Persistent, scalable | Adds external dependency, latency |
| Kafka/Event Bus | Massively scalable, replay | Complex, high operational overhead |

## Follow-up Interview Questions

1. How would you persist messages for replay? Use Kafka-like append-only log.
2. What if a subscriber crashes? Track offset, resume from checkpoint.
3. How to monitor topic lag (subscriber behind publisher)?
4. What's the bottleneck at 10x scale (1M msg/sec)? Broker I/O; need Kafka cluster.
5. How to implement ordering guarantees (messages in order per topic)?

## Example Scenario Walkthrough

Scenario: Real-time stock price updates

Initial state:
- Topics: {"stocks.AAPL", "stocks.GOOG"}
- Publishers: StockDataProvider
- Subscribers: PortfolioManager, Trader, Logger

Step 1: Portfolio Manager subscribes
- pubsub.subscribe("stocks.AAPL", portfolioMgr)
- topic = "stocks.AAPL"
- subscribers = [portfolioMgr]

Step 2: Trader subscribes to same topic
- pubsub.subscribe("stocks.AAPL", trader)
- topic = "stocks.AAPL"
- subscribers = [portfolioMgr, trader]

Step 3: Logger subscribes to all stocks
- pubsub.subscribe("stocks.*", logger)
- subscribers for "stocks.*" = [logger]

Step 4: Stock price publisher publishes
- pubsub.publish("stocks.AAPL", {price: 150.0})
- Message added to queue

Step 5: Broker notifies all subscribers
- for sub in subscribers["stocks.AAPL"]:
-     sub.onMessage({price: 150.0})
- Calls: portfolioMgr.onMessage(), trader.onMessage()

Step 6: Subscribers process independently
- PortfolioManager: recalculate portfolio value
- Trader: check if price triggers trade rule
- Logger: log price to analytics DB

Step 7: Subscriber unsubscribes (cleanup)
- pubsub.unsubscribe("stocks.AAPL", portfolioMgr)
- subscribers = [trader]
- Future prices only notify trader

## Trade-offs

| Async | Sync |
|-------|------|
| Non-blocking, scalable | Simpler, immediate |
| Ordering challenges | Blocking calls |
| Decoupled publishers/subs | Tight coupling |

### Architecture Diagram

```mermaid
graph TB
    Publisher["Publisher"]
    Broker["Message Broker<br/>Topic/Queue"]
    Consumer1["Consumer 1"]
    Consumer2["Consumer 2"]
    Consumer3["Consumer 3"]

    Publisher -->|Publish| Broker
    Broker -->|Deliver| Consumer1
    Broker -->|Deliver| Consumer2
    Broker -->|Deliver| Consumer3
```

### Flow Diagram

```mermaid
sequenceDiagram
    participant Pub as Publisher
    participant B as Broker
    participant C1 as Consumer 1
    participant C2 as Consumer 2

    Pub->>B: Send Message
    B->>B: Store in Topic
    B->>C1: Deliver
    B->>C2: Deliver
    C1->>C1: Process
    C2->>C2: Process
    C1-->>B: ACK
    C2-->>B: ACK
```

## Complexity

| Operation | Time |
|-----------|------|
| subscribe | O(1) |
| unsubscribe | O(1) |
| publish | O(n) where n=subscribers |
| Space | O(t+s+m) where t=topics, s=subscribers, m=messages |

## Python Implementation

```python
from collections import defaultdict
from typing import Callable, Any

class EventBroker:
    def __init__(self):
        self._subscribers: dict[str, list[Callable]] = defaultdict(list)

    def subscribe(self, topic: str, handler: Callable[[Any], None]):
        self._subscribers[topic].append(handler)

    def unsubscribe(self, topic: str, handler: Callable):
        self._subscribers[topic].remove(handler)

    def publish(self, topic: str, message: Any):
        for handler in self._subscribers[topic]:
            handler(message)

# Usage
broker = EventBroker()

def email_handler(msg): print(f"Email: {msg}")
def sms_handler(msg): print(f"SMS: {msg}")

broker.subscribe("order.placed", email_handler)
broker.subscribe("order.placed", sms_handler)
broker.publish("order.placed", {"order_id": 42, "total": 99.99})
```

## Java Implementation

```java
import java.util.*;
import java.util.function.Consumer;

public class EventBroker {
    private Map<String, List<Consumer<Object>>> subscribers = new HashMap<>();

    public void subscribe(String topic, Consumer<Object> handler) {
        subscribers.computeIfAbsent(topic, k -> new ArrayList<>()).add(handler);
    }

    public void publish(String topic, Object message) {
        subscribers.getOrDefault(topic, Collections.emptyList())
                   .forEach(h -> h.accept(message));
    }

    public static void main(String[] args) {
        EventBroker broker = new EventBroker();
        broker.subscribe("user.signup", msg -> System.out.println("Email: " + msg));
        broker.subscribe("user.signup", msg -> System.out.println("SMS: " + msg));
        broker.publish("user.signup", "New user joined");
    }
}
```

## Common Questions & Answers

**Q: What is caching and why do we need it?**

A: Caching stores frequently accessed data in fast storage (memory) to reduce latency and load on slower backends (database). Trade space (cache) for speed (latency). Critical for systems serving millions of requests per second.

**Q: What are the main cache eviction policies?**

A: LRU (least recently used), LFU (least frequently used), FIFO (first in first out), TTL (time-based), Random, and ARC (adaptive replacement). Choose based on access patterns: LRU for temporal, LFU for frequency, TTL for time-sensitive data.

**Q: What is cache hit rate and cache miss rate?**

A: Hit rate = successful_finds / total_accesses. Miss rate = 1 - hit rate. P(hit) = hits / (hits + misses). Target 80%+ hit rates for effective caching. Too-small cache gives low hit rate (wasted resources). Too-large cache uses more memory than needed.

**Q: How do you handle cache invalidation when backend data changes?**

A: Use TTL (time-based expiration), active invalidation (notify cache on write), cache-aside pattern (client checks backend), or write-through (update both). Active invalidation is fastest but complex. TTL is simplest but has stale data window.

**Q: What is the cache-aside pattern?**

A: Application checks cache first. On miss, fetch from backend, update cache, then return. Simple to implement. Risk: race condition where multiple threads fetch same miss simultaneously (thundering herd problem).

**Q: What is write-through caching?**

A: Writes go to both cache and backend simultaneously (synchronously). Ensures consistency: read always gets latest. Cost: write latency includes backend write. Safer than write-back but slower.

**Q: What is write-back (write-behind) caching?**

A: Writes go to cache only; backend updated asynchronously later (batch or periodic). Fast writes. Risk: data loss if cache fails before flushing. Need durability guarantees (persistence, replication).

**Q: How do you choose cache size?**

A: Estimate working set (frequently accessed data volume). Add 20-30% buffer for margin. Monitor hit rate: if < 80%, increase size. If > 95%, might be oversized (waste). Use tools like cachegrind to profile.

**Q: What's the difference between client-side and server-side caching?**

A: Client cache (browser): reduces network round-trips, entirely controlled by client. Server cache (memory, Redis): shared across clients, controlled by server. Multi-level caching often best.

**Q: How do you measure cache effectiveness?**

A: Hit rate (primary metric), latency reduction (P99 latency with vs. without cache), backend load reduction, and memory cost per cache entry. Calculate ROI: cost of cache vs. benefit (reduced latency, backend load).

## Follow-up Questions & Answers

**Q: How do you prevent the thundering herd problem in caches?**

A: When popular key expires, many threads fetch from backend simultaneously causing spike. Solutions: probabilistic early expiration (refresh before TTL), request coalescing (single thread rebuilds, others wait), or bloom filters (detect non-existent keys fast).

**Q: How would you implement multi-level cache hierarchy?**

A: Use L1 (fast, small, in-process), L2 (medium, local machine), L3 (large, remote, Redis). Check L1, miss→L2, miss→L3, miss→backend. On write: update all levels. Trade space for speed across levels.

**Q: Can you implement read-through caching (automatic population)?**

A: Yes, cache loader/resolver called on miss. Transparent to application. Backend automatically uses cache layer. More complex than cache-aside but cleaner separation.

**Q: How do you handle hot keys in distributed caches?**

A: Hot key = key accessed by many threads/clients. Replicate hot keys on multiple cache nodes. Use local in-process caches for very hot keys. Monitor and detect hot keys automatically.

**Q: What's the difference between warm and cold cache startup?**

A: Cold cache: empty at start, misses until populated (slow ramp-up). Warm cache: pre-loaded from previous state (RDB/snapshot). Warm startup is critical for production (instant performance).

**Q: How would you measure cache effectiveness for business metrics?**

A: Track hit rate, P99 latency (with/without cache), backend QPS reduction, revenue impact. Calculate cache size vs. cost savings. A/B test to prove business value.

**Q: What happens when cache size is insufficient for working set?**

A: Constant evictions = high miss rate = ineffective cache. Solution: increase cache size, improve eviction policy, reduce working set, or use better hardware (faster storage).

**Q: How do you debug cache issues in production?**

A: Monitor hit rate continuously. Profile cache keys (which keys are accessed). Check for cache stampedes (sudden miss spike). Use distributed tracing to see cache path.

**Q: How would you implement a persistent cache?**

A: Combine memory cache (fast) with persistent backend (database, RocksDB, LevelDB). Write-back pattern: batch updates to persistent store. Trade latency for durability.

**Q: Can you use caching for write-heavy workloads?**

A: Write caching is risky (consistency issues). Use carefully: write-through for safety, write-back for speed. Good for batch writes (aggregate before writing). Monitor durability guarantees.


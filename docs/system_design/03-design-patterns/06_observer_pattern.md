# Observer Pattern

## Problem Statement

Define a one-to-many dependency between objects so that when one object changes state, all its dependents are notified automatically.

**Use Cases:**
- Event systems (button clicks, form changes)
- MVC frameworks (model changes notify views)
- Real-time data updates (stock price changes)
- Publish-subscribe systems


## Code Explanation (Detailed)

### Implementation Approach
The code demonstrates core patterns and trade-offs.

### Key Operations
Each operation shows algorithm and performance characteristics.

### Concurrency and Atomicity
Locking strategies, race condition prevention.

### Edge Cases
Boundary conditions and error handling.

### Performance Optimization
Techniques for reducing latency and throughput.

## Design

### Class Diagram

```
        Subject (Observable)
        ├── attach(Observer)
        ├── detach(Observer)
        └── notify()
             │
             ├─→ Observer.update()
             ├─→ Observer.update()
             └─→ Observer.update()
```

### Key Components

```
Subject: Maintains list of observers, notifies on state change
Observer: Interface with update() method
ConcreteObserver: Implements Observer, performs action on update
ConcreteSubject: Concrete Subject that holds state
```

### Interaction

```
1. Observer registers with Subject (attach)
2. Subject state changes
3. Subject calls notify() -> calls update() on all observers
4. Each observer reacts to the change independently
```


## Scenario

Observer Pattern is a critical component in modern distributed systems. In real-world applications, handling complex business logic at scale with high reliability. For example, major tech companies like Netflix, Uber, and Airbnb rely on similar solutions to handle millions of concurrent users and requests. The challenge is achieving this while maintaining sub-100ms latency, 99.99% availability, and gracefully handling 10x traffic spikes during peak demand. This component provides the foundational capability to solve these challenges reliably and efficiently at global scale.

## Users

- **Backend Engineers**: Responsible for implementing and maintaining this system component in production environments. They need to understand the architecture, trade-offs, failure modes, and operational considerations.
- **DevOps/SRE Teams**: Monitor system health, manage scaling policies, handle incidents, and ensure reliability SLAs are met. They need insights into performance characteristics, bottlenecks, and failure recovery mechanisms.
- **Data Engineers**: Design data pipelines and analytics around this system, requiring deep understanding of data flow, consistency guarantees, and throughput characteristics.
- **System Architects**: Make high-level architectural decisions that impact company infrastructure, requiring comprehensive understanding of capabilities, limitations, and scalability boundaries.
- **Security Teams**: Understand security implications, potential vulnerabilities, and compliance requirements for this component.

## PRD

### Functional Requirements
- Core operations work correctly
- Explicit error handling
- Consistency guarantees defined
- Monitoring and observability

### Non-Functional Requirements
- Performance targets met
- Availability SLA achieved
- Scalability headroom
- Cost efficient

### Success Metrics
- Benchmarks met
- Uptime targets met
- Resource budgets
- No data loss


## Flow

The typical operational flow for this system involves these key phases:

1. **Request Arrival**: Client/upstream system sends request with required parameters and context
2. **Validation & Routing**: System validates request format, authentication, and routes to correct handler/shard/instance
3. **Core Processing**: Execute the main algorithm, database query, or business logic on the data/state
4. **State Management**: Update internal state (caches, indexes, counters, logs) with proper atomicity and locking
5. **Response Generation**: Format results and return to requester with relevant metadata (timing, version info)
6. **Observability**: Record metrics (latency, throughput, errors), logs (for debugging), and traces (for performance analysis)

This flow repeats thousands or millions of times per second in production. Each operation's efficiency compounds across the entire system, making careful optimization essential. Bottlenecks at any phase can cascade to impact overall system performance.

## Architecture Diagram

```
┌─────────────────────────────────────────────┐
│      Subject (Stock Price)                  │
│  ┌──────────────────────────────────────┐   │
│  │  - price: float                      │   │
│  │  - observers: List<Observer>         │   │
│  │                                      │   │
│  │  + attach(observer)                  │   │
│  │  + detach(observer)                  │   │
│  │  + notify()                          │   │
│  │  + setPrice(newPrice)                │   │
│  └──────────────────────────────────────┘   │
│              ↓ notify()                      │
│  ┌──────────────────┬──────────────────┐    │
│  │                  │                  │    │
│  ▼                  ▼                  ▼    │
│ Observer1      Observer2           Observer3│
│ (PortfolioMgr) (AlertService)      (Logger)│
│ + update()     + update()           + update()
└─────────────────────────────────────────────┘
```

## Back-of-Envelope Calculations

For typical UI event system with 1000 observers:
- Storage: 1000 observers × 8 bytes/reference = 8KB per subject
- Throughput: Notify 1000 observers sequentially: 1000 × 1ms = 1s per change (slow)
- Latency: Single observer update = 100-500μs, 1000 total = 100-500ms p99
- Bandwidth: Each notification ~100 bytes × 1000 = 100KB per state change

Optimization: Batch notifications, use weak references, async task queue for heavy observers.

## Design Choice Comparison

| Approach | Pros | Cons |
|----------|------|------|
| Direct Observer List | Simple, clear | O(n) notifications, tight coupling |
| Event Bus / Message Queue | Async, decoupled, scalable | Extra infrastructure, eventual consistency |
| Weakly-Referenced List | Prevents memory leaks | Observers can disappear silently |

## Follow-up Interview Questions

1. How would you handle observer priority (some observers must execute before others)?
2. What if an observer should only be notified of certain state changes? Implement filters/topics.
3. How to debug observer notification chains with 100+ observers? Add instrumentation/tracing.
4. What's the bottleneck at 10x scale (10K observers)? Notification time O(n). Use event bus/sharding.
5. How would you implement observer unsubscribe safely during iteration?

## Example Scenario Walkthrough

Scenario: Stock price changes, notify portfolio manager and logging service

Initial state:
- Subject: Stock(symbol="AAPL", price=150.0)
- Observer1: PortfolioManager
- Observer2: PriceLogger
- Both attached to Stock

Step 1: Portfolio manager attaches
- Stock.attach(portfolioMgr)
- observers list = [portfolioMgr]

Step 2: Logger attaches
- Stock.attach(logger)
- observers list = [portfolioMgr, logger]

Step 3: Stock price changes
- Stock.setPrice(152.5)
- Old price = 150.0, new price = 152.5
- Call notify()

Step 4: Notify all observers (push model)
- for each observer in observers:
  - observer.update(oldPrice=150.0, newPrice=152.5)

Step 5: PortfolioManager.update() executes
- Recalculate portfolio value
- Rebalance if needed
- Update dashboard: +$2.5 per share

Step 6: PriceLogger.update() executes
- Log: "AAPL: 150.0 → 152.5 at 2026-05-14 14:32:10"
- Send to analytics DB

Step 7: Observer detaches (cleanup)
- Stock.detach(logger)
- observers list = [portfolioMgr]
- Next price change only notifies portfolio manager

## Trade-offs

| Pro | Con |
|-----|-----|
| Loose coupling | Order of notifications unpredictable |
| Dynamic subscriptions | Memory overhead (observer lists) |
| Supports broadcast | Debugging can be harder |
| Open/Closed principle | Observer must check what changed |

### Observer Pattern - Python

```python
class Subject:
    def __init__(self):
        self.observers = []
    
    def attach(self, observer):
        self.observers.append(observer)
    
    def notify(self, **kwargs):
        for observer in self.observers:
            observer.update(**kwargs)

class Observer:
    def update(self, **kwargs):
        raise NotImplementedError

class StockPrice(Subject):
    def __init__(self):
        super().__init__()
        self._price = 0
    
    def set_price(self, price):
        self._price = price
        self.notify(price=price)

class Trader(Observer):
    def update(self, **kwargs):
        price = kwargs['price']
        print(f'Trader notified: price={price}')
        if price > 150:
            print('Sell signal!')
```

### Architecture Diagram

```mermaid
graph TB
    Subject["Subject<br/>notifyObservers()"]
    Observer1["Observer 1<br/>update()"]
    Observer2["Observer 2<br/>update()"]
    Observer3["Observer 3<br/>update()"]

    Subject -->|notify| Observer1
    Subject -->|notify| Observer2
    Subject -->|notify| Observer3
```

### Flow Diagram

```mermaid
sequenceDiagram
    participant E as Event
    participant S as Subject
    participant O1 as Observer 1
    participant O2 as Observer 2

    E->>S: Change State
    S->>O1: notifyObservers()
    S->>O2: notifyObservers()
    O1->>O1: update()
    O2->>O2: update()
```

## Complexity

| Operation | Time |
|-----------|------|
| attach | O(1) |
| detach | O(n) where n=observers |
| notify | O(n) |

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


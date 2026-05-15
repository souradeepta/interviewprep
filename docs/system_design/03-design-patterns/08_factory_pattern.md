# Factory Pattern

## Problem Statement

Define an interface for creating an object, but let subclasses decide which class to instantiate. Factory pattern lets a class defer instantiation.

**Use Cases:**
- Creating objects without specifying exact classes
- Database abstraction (MySQL, PostgreSQL factories)
- UI frameworks (button, dialog creation)
- Shape creation (circle, square, rectangle)

## Design

### Class Diagram

```
        Creator (Factory)
        └── create(): Product
             │
    ┌────────┴────────┐
    │                 │
ConcreteCreatorA    ConcreteCreatorB
  └── create()      └── create()
       ↓                 ↓
ProductA            ProductB
```

### Key Components

```
Product: Interface for objects created
ConcreteProduct: Concrete implementations
Creator: Interface declaring factory method
ConcreteCreator: Implements factory method returning specific product
```

### Factory Method

```
public Product create(String type) {
  if (type == "A") return new ConcreteProductA();
  if (type == "B") return new ConcreteProductB();
  return null;
}
```


## Scenario

Factory Pattern is a critical component in modern distributed systems. In real-world applications, handling complex business logic at scale with high reliability. For example, major tech companies like Netflix, Uber, and Airbnb rely on similar solutions to handle millions of concurrent users and requests. The challenge is achieving this while maintaining sub-100ms latency, 99.99% availability, and gracefully handling 10x traffic spikes during peak demand. This component provides the foundational capability to solve these challenges reliably and efficiently at global scale.

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

```mermaid
graph TB
    Client["Client"]
    Factory["Factory<br/>createProduct()"]
    Product["Product"]
    ProductA["ConcreteA"]
    ProductB["ConcreteB"]

    Client -->|uses| Factory
    Factory -->|creates| Product
    Product <|--| ProductA
    Product <|--| ProductB
```

## Back-of-Envelope Calculations

For typical scenario (shape factory with 5 product types):
- Storage: 5 shape classes × 1KB code = 5KB, shape instances vary (Circle=100 bytes, Square=100 bytes)
- Throughput: Factory creation O(1), 1M objects/sec easily achievable
- Latency: Factory.create() = 1-5μs (just instantiation), negligible vs application logic
- Bandwidth: Negligible (only object creation metadata)

Scaling: Factory pattern doesn't bottleneck; use caching/pooling for expensive products.

## Design Choice Comparison

| Approach | Pros | Cons |
|----------|------|------|
| Simple Factory | Straightforward, one point of creation | Violates OCP, all logic in one factory |
| Factory Method | OCP compliant, subclasses decide | More classes, inheritance overhead |
| Abstract Factory | Families of products | Complex, overkill for simple cases |

## Follow-up Interview Questions

1. How would you implement factory caching (reuse products instead of creating new)?
2. What if product creation is expensive (database queries, network calls)? Implement lazy initialization.
3. How to monitor which products are created and how often?
4. What's the bottleneck at 10x scale? Creation itself is O(1); bottleneck is product usage.
5. How would you implement versioning (create ProductV1 or ProductV2)?

## Example Scenario Walkthrough

Scenario: Shape drawing application using factory

Initial state:
- ShapeFactory with methods: create(type) -> Shape

Step 1: Create circle
- factory.create("circle")
- Factory checks: type == "circle"
- Instantiate: new Circle(radius=5)
- Return Circle object

Step 2: Create square
- factory.create("square")
- Factory checks: type == "square"
- Instantiate: new Square(side=10)
- Return Square object

Step 3: Create rectangle
- factory.create("rectangle")
- Factory checks: type == "rectangle"
- Instantiate: new Rectangle(width=20, height=10)
- Return Rectangle object

Step 4: Client code (decoupled from concrete classes)
- Shape shape1 = factory.create("circle")
- Shape shape2 = factory.create("square")
- shape1.draw()  // Calls Circle.draw()
- shape2.draw()  // Calls Square.draw()

Step 5: Add new shape (Triangle) - factory modification
- ShapeFactory.create("triangle") -> new Triangle(...)
- No client code changes needed
- Maintains encapsulation

## Trade-offs

| Pro | Con |
|-----|-----|
| Decouples creation | Extra classes |
| Centralizes logic | Conditionals in factory |
| Easy to extend | More complex |
| Follows OCP | Overhead for simple cases |

### Factory Pattern - Python

```python
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self):
        pass

class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius
    
    def area(self):
        return 3.14 * self.radius ** 2

class Square(Shape):
    def __init__(self, side):
        self.side = side
    
    def area(self):
        return self.side ** 2

class ShapeFactory:
    @staticmethod
    def create_shape(shape_type, **kwargs):
        if shape_type == 'circle':
            return Circle(kwargs['radius'])
        elif shape_type == 'square':
            return Square(kwargs['side'])
        else:
            raise ValueError(f'Unknown shape: {shape_type}')

# Usage
factory = ShapeFactory()
shape1 = factory.create_shape('circle', radius=5)
print(f'Circle area: {shape1.area()}')  # 78.5

shape2 = factory.create_shape('square', side=10)
print(f'Square area: {shape2.area()}')  # 100
```

## Complexity

| Operation | Time |
|-----------|------|
| create | O(1) |

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


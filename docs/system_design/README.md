# System Design Problems

Comprehensive collection of real-world system design problems solved with detailed walkthroughs, architectural diagrams, and implementations in Python and Java.

## Problems Covered

### Caching Systems
1. **LRU Cache** — Least Recently Used eviction, O(1) all operations
2. **LFU Cache** — Least Frequently Used eviction, track access frequency

### Real-World Systems
3. **Rate Limiter** — Token bucket and sliding window algorithms
4. **URL Shortener** — Encoding, collision handling, distributed generation
5. **Parking Lot System** — OOP design, spot allocation, payment tracking

### Design Patterns (Gang of Four)
6. **Observer Pattern** — Event publishing, loose coupling
7. **Strategy Pattern** — Runtime algorithm switching
8. **Factory Pattern** — Object creation abstraction
9. **Decorator Pattern** — Dynamic behavior extension
10. **Adapter Pattern** — Interface compatibility layer

### Distributed Systems
11. **Pub-Sub System** — Publish-subscribe messaging, topic management
12. **Thread Pool** — Task scheduling, worker threads, queue management
13. **Load Balancer** — Request distribution, health checks, multiple strategies

## How to Use

1. **Read the design doc** (`docs/system_design/NN_*.md`) — understand problem, constraints, trade-offs
2. **Study Python implementation** (`python/system_design/`) — cleaner syntax, easier to follow
3. **Study Java implementation** (`java/system_design/`) — production patterns, type safety
4. **Run the demo** — each implementation has executable `main` block
5. **Run tests** — verify behavior under different scenarios

## Study Path

**Week 1: Caching & Storage**
- Day 1-2: LRU Cache (eviction policy, linked list + hash map)
- Day 3: LFU Cache (frequency tracking, tie-breaking)
- Day 4-5: Rate Limiter (token bucket, time windows)
- Day 6-7: URL Shortener (encoding, uniqueness)

**Week 2: System Design**
- Day 1: Parking Lot (state management, OOP)
- Day 2-4: Design Patterns (Observer, Strategy, Factory, Decorator, Adapter)
- Day 5: Pub-Sub (event distribution)
- Day 6-7: Thread Pool (concurrency, work queues)

**Week 3: Advanced Systems**
- Day 1-2: Load Balancer (multiple algorithms)
- Day 3-5: Combined problems (rate limiting + caching, etc.)
- Day 6-7: Mock system design interviews

## Common Patterns Across Problems

| Problem | Key Data Structure | Time Complexity | Space Complexity |
|---------|-------------------|-----------------|------------------|
| LRU Cache | Doubly Linked List + HashMap | O(1) | O(capacity) |
| LFU Cache | HashMap + Min-Heap + Frequency Map | O(1) | O(capacity) |
| Rate Limiter (Token Bucket) | Deque | O(1) | O(capacity) |
| URL Shortener | HashMap | O(1) | O(n) |
| Parking Lot | HashMap | O(1) | O(spots) |
| Thread Pool | Queue | O(1) | O(tasks) |
| Load Balancer | Array + Index | O(1) | O(servers) |

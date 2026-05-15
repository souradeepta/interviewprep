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

### Tier 3: Real-World Applications (26 Problems)

#### Real-World Apps (6)
14. **News Feed** — Timeline generation, fanout strategies, follower cache
15. **E-Commerce** — Product catalog, shopping cart, order processing, inventory
16. **Ride-Sharing** — Driver/rider matching, ETA, real-time tracking, payment
17. **Chat System** — Message storage, group chat, notifications, delivery guarantees
18. **Video Streaming** — Adaptive bitrate, CDN delivery, transcoding pipeline
19. **Database Sharding** — Consistent hashing, distributed data, cross-shard queries

#### Data & Infrastructure (7)
20. **Message Queue** — Pub-sub, FIFO, consumer groups, dead letter queue
21. **Search Engine** — Inverted index, ranking, distributed search, autocomplete
22. **Recommendation Engine** — Collaborative filtering, content-based, cold start
23. **Leaderboard** — Sorted sets, real-time rankings, pagination
24. **Payment System** — Transaction processing, idempotency, fraud detection
25. **Wallet System** — Balance tracking, double-entry bookkeeping, currency exchange
26. **Followers System** — Social graph, timeline generation, mutual follows

#### Advanced Patterns & APIs (6)
27. **Notifications** — Multi-channel delivery (email, SMS, push, in-app)
28. **API Gateway** — Routing, authentication, rate limiting, transformation
29. **WebSocket Server** — Bidirectional communication, rooms, broadcast
30. **Distributed Transactions** — 2-Phase Commit, Saga Pattern, eventual consistency
31. **Circuit Breaker** — Failure detection, state transitions, cascading failures
32. **Saga Pattern** — Long-running transactions, compensation, choreography

#### Storage & Analytics (4)
33. **Photo Sharing** — Upload pipeline, thumbnail generation, CDN delivery
34. **Time Series DB** — Compression, retention policies, time-range queries
35. **Log Aggregation** — Collection, parsing, storage, searching, alerting
36. **Like/Comment System** — Atomic counters, caching, real-time updates

#### Specialized Systems (3)
37. **Auction System** — Bidding, winner determination, settlement, time management
38. **Transaction Ledger** — Immutable log, audit trail, reconciliation
39. **Consensus Algorithm** — Raft/Paxos, leader election, fault tolerance

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

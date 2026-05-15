# Leaderboard System

## Problem Statement
Design a system tracking and displaying user rankings in real-time.

**Operations:**
- `updateScore(user_id, points)` — Add points
- `getLeaderboard(page)` — Get top rankings
- `getUserRank(user_id)` — Get user position
- `getUserScore(user_id)` — Get user score

## Design

### Data Structure

```
Sorted set: {score -> [user_ids]}
Or: Redis sorted set (ZSET)
Time-based: Multiple leaderboards (daily, weekly, all-time)
```

### Caching Strategy

```
Top 100 cached (hot)
User's position: On-demand calculation
Periodic refresh: Avoid stale cache
```

### Handling Ties

```
Secondary sort: Timestamp (who reached first)
Tertiary sort: User ID (deterministic)
Consistent ordering
```


## Scenario

Leaderboard System is a critical component in modern distributed systems. In real-world applications, handling complex business logic at scale with high reliability. For example, major tech companies like Netflix, Uber, and Airbnb rely on similar solutions to handle millions of concurrent users and requests. The challenge is achieving this while maintaining sub-100ms latency, 99.99% availability, and gracefully handling 10x traffic spikes during peak demand. This component provides the foundational capability to solve these challenges reliably and efficiently at global scale.

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
┌───────────────────────────────┐
│   Real-time Leaderboard      │
│  Sorted Set (Redis)           │
│  - O(log n) insert            │
│  - O(n) rank (shard)          │
│  Ranking Queries              │
│  - Top 100: ZREVRANGE         │
│  - User rank: ZREVRANK        │
│  Snapshots (hourly)           │
│  - MySQL for persistence      │
└───────────────────────────────┘
```

## Back-of-Envelope Calculations

10M players, 1 Hz update = 1M updates/sec. Redis: ZADD O(log n). Throughput: 1M easily. Query: top-100 = 1ms.
## Design Choice Comparison

| Approach | Pros | Cons |
|----------|------|------|
| Redis Sorted Set | O(log n), simple | No persistence |
| DB index | Persistent | Slower |
| Sharded Set | Scalable | Complex |

## Follow-up Interview Questions

1. Prevent cheating? 2. Mobile (low bandwidth)? 3. Competitive leagues? 4. Bottleneck at 10x? 5. Real-time visualization?

## Example Scenario Walkthrough

[Describe a concrete example with step-by-step execution]

### Architecture Diagram

```mermaid
graph TB
    User["User Scores"]
    Update["Update Service"]
    Redis["Redis<br/>Sorted Set"]
    DB["Database"]
    Ranking["Ranking"]

    User -->|Score| Update
    Update -->|Increment| Redis
    Update -->|Persist| DB
    Ranking -->|Compute| Redis
```

### Flow Diagram

```mermaid
flowchart TD
    A["New Score"] --> B["Update Redis"]
    B --> C["Persist DB"]
    C --> D["Compute Ranks"]
    D --> E["Cache Top 100"]
    E --> F["Query Leaderboard"]
```

## Complexity

| Operation | Time |
|-----------|------|
| Update score | O(log n) |
| Get leaderboard | O(k log n) |
| Get rank | O(log n) |

## Python Implementation

```python
import heapq
from typing import List, Tuple
from sortedcontainers import SortedList

class Leaderboard:
    def __init__(self):
        self._scores: dict[str, int] = {}
        self._sorted: SortedList = SortedList(key=lambda x: -x[0])

    def add_score(self, player_id: str, score: int):
        if player_id in self._scores:
            old_score = self._scores[player_id]
            self._sorted.remove((old_score, player_id))
        self._scores[player_id] = score
        self._sorted.add((score, player_id))

    def top_k(self, k: int) -> List[Tuple[str, int]]:
        return [(pid, s) for s, pid in list(self._sorted)[:k]]

    def rank(self, player_id: str) -> int:
        score = self._scores.get(player_id, 0)
        for i, (s, _) in enumerate(self._sorted):
            if s <= score:
                return i + 1
        return len(self._sorted) + 1

# Simple leaderboard without sortedcontainers
class SimpleLeaderboard:
    def __init__(self):
        self._scores: dict[str, int] = {}

    def add_score(self, player_id: str, score: int):
        self._scores[player_id] = max(self._scores.get(player_id, 0), score)

    def top_k(self, k: int) -> List[Tuple[str, int]]:
        return sorted(self._scores.items(), key=lambda x: -x[1])[:k]

# Usage
lb = SimpleLeaderboard()
lb.add_score("alice", 1500)
lb.add_score("bob", 2000)
lb.add_score("carol", 1800)
print(lb.top_k(3))  # [('bob', 2000), ('carol', 1800), ('alice', 1500)]
```

## Java Implementation

```java
import java.util.*;

public class Leaderboard {
    private Map<String, Integer> scores = new HashMap<>();

    public void addScore(String playerId, int score) {
        scores.merge(playerId, score, Integer::max);
    }

    public List<Map.Entry<String, Integer>> topK(int k) {
        return scores.entrySet().stream()
            .sorted(Map.Entry.<String, Integer>comparingByValue().reversed())
            .limit(k).toList();
    }

    public static void main(String[] args) {
        Leaderboard lb = new Leaderboard();
        lb.addScore("alice", 1500);
        lb.addScore("bob", 2000);
        lb.topK(2).forEach(e -> System.out.println(e.getKey() + ": " + e.getValue()));
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


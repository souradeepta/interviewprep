# Like/Comment System

## Problem Statement
Design a system for social interactions (likes, comments) at scale.

**Operations:**
- `like(user_id, post_id)` — Like post
- `unlike(user_id, post_id)` — Unlike post
- `comment(user_id, post_id, text)` — Add comment
- `deleteComment(comment_id)` — Delete comment
- `getLikeCount(post_id)` — Get like count


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

### Like Counter

```
Atomic increment: Redis INCR
Batch write: Eventually consistent
Denormalized: Cache in post doc
Eventual consistency: Async update to DB
```

### Comment Storage

```
Ordered by timestamp
Indexed by post_id
Pagination: Get top K comments
Sorting: Top comments (likes)
```

### Real-time Updates

```
WebSocket push: New likes/comments
Counter update: Client + server
Caching: Popular posts cached
```


## Scenario

Like/Comment System is a critical component in modern distributed systems. In real-world applications, handling complex business logic at scale with high reliability. For example, major tech companies like Netflix, Uber, and Airbnb rely on similar solutions to handle millions of concurrent users and requests. The challenge is achieving this while maintaining sub-100ms latency, 99.99% availability, and gracefully handling 10x traffic spikes during peak demand. This component provides the foundational capability to solve these challenges reliably and efficiently at global scale.

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
┌──────────────────────────────────────┐
│   Like/Comment Engine                │
│  ┌──────────────────────────────────┐  │
│  │ Like Counter                     │  │
│  │ - Redis atomic increment         │  │
│  │ - Persist to DB (async)          │  │
│  │ Comments                         │  │
│  │ - Threaded (parent_id)           │  │
│  │ - Sorted by time/score           │  │
│  │ Notification on engagement       │  │
│  │ - Publish event (Kafka)          │  │
│  └──────────────────────────────────┘  │
└──────────────────────────────────────────┘
```

## Back-of-Envelope Calculations

1B items, 1K likes avg = 1T likes. Like updates: 10 req/sec per item = 100K global. Cache 1B items × 4B = 4GB Redis.

## Design Choice Comparison

| Approach | Pros | Cons |
|----------|------|------|
| Count-only | Simple, fast | No like history |
| Set-based (track users) | De-duplicate, per-user prefs | Higher memory |
| Sorted set (scored) | Complex ranking | More storage |

## Follow-up Interview Questions

1. Spam like detection? 2. Sort comments optimally? 3. Like propagation (friend feed update)? 4. Sensitivity (hide counts)? 5. Verification (real accounts)?

## Example Scenario Walkthrough

[Describe a concrete example with step-by-step execution]

### Architecture Diagram

```mermaid
graph TB
    User["User"]
    LikeService["Like Service"]
    CommentService["Comment Service"]
    Cache["Cache"]
    DB["Database"]

    User -->|Like| LikeService
    User -->|Comment| CommentService
    LikeService -->|Store| Cache
    CommentService -->|Store| Cache
    Cache -->|Persist| DB
```

### Flow Diagram

```mermaid
flowchart TD
    A["User Action"] --> B{"Type?"}
    B -->|Like| C["Increment Count"]
    B -->|Comment| D["Create Comment"]
    C --> E["Update Cache"]
    D --> E
    E --> F["Persist"]
    F --> G["Notify"]
```

## Complexity

| Operation | Time |
|-----------|------|
| Like | O(1) |
| Comment | O(1) |
| Get count | O(1) cached |
| Get comments | O(k) |

## Python Implementation

```python
from dataclasses import dataclass, field
from typing import Dict, Set, List, Optional
from datetime import datetime

@dataclass
class Comment:
    comment_id: str
    user_id: str
    content_id: str
    text: str
    created_at: datetime = field(default_factory=datetime.now)
    parent_id: Optional[str] = None  # For replies

class LikeCommentService:
    def __init__(self):
        self._likes: Dict[str, Set[str]] = {}          # content_id -> set of user_ids
        self._comments: Dict[str, Comment] = {}         # comment_id -> comment
        self._content_comments: Dict[str, List[str]] = {}  # content_id -> comment_ids
        self._counter = 0

    def like(self, user_id: str, content_id: str) -> int:
        self._likes.setdefault(content_id, set()).add(user_id)
        return len(self._likes[content_id])

    def unlike(self, user_id: str, content_id: str) -> int:
        self._likes.get(content_id, set()).discard(user_id)
        return len(self._likes.get(content_id, set()))

    def like_count(self, content_id: str) -> int:
        return len(self._likes.get(content_id, set()))

    def has_liked(self, user_id: str, content_id: str) -> bool:
        return user_id in self._likes.get(content_id, set())

    def comment(self, user_id: str, content_id: str, text: str,
                parent_id: Optional[str] = None) -> Comment:
        self._counter += 1
        c = Comment(f"C-{self._counter}", user_id, content_id, text, parent_id=parent_id)
        self._comments[c.comment_id] = c
        self._content_comments.setdefault(content_id, []).append(c.comment_id)
        return c

    def get_comments(self, content_id: str) -> List[Comment]:
        ids = self._content_comments.get(content_id, [])
        return [self._comments[i] for i in ids]

# Usage
svc = LikeCommentService()
svc.like("alice", "post1")
svc.like("bob", "post1")
print(svc.like_count("post1"))  # 2
c = svc.comment("alice", "post1", "Great post!")
print(c.text, svc.get_comments("post1")[0].text)  # Great post! Great post!
```

## Java Implementation

```java
import java.util.*;

public class LikeCommentService {
    record Comment(String id, String userId, String contentId, String text) {}

    private Map<String, Set<String>> likes = new HashMap<>();
    private Map<String, List<Comment>> comments = new HashMap<>();
    private int counter = 0;

    public int like(String userId, String contentId) {
        return likes.computeIfAbsent(contentId, k -> new HashSet<>()).size();
    }

    public void unlike(String userId, String contentId) {
        likes.getOrDefault(contentId, Set.of()).remove(userId);
    }

    public int likeCount(String contentId) {
        return likes.getOrDefault(contentId, Set.of()).size();
    }

    public Comment comment(String userId, String contentId, String text) {
        Comment c = new Comment("C-" + (++counter), userId, contentId, text);
        comments.computeIfAbsent(contentId, k -> new ArrayList<>()).add(c);
        return c;
    }

    public List<Comment> getComments(String contentId) {
        return comments.getOrDefault(contentId, List.of());
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


# Chat System

## Problem Statement
Design a real-time messaging system supporting one-to-one and group chat.

**Operations:**
- `sendMessage(from, to, text)` — Send message
- `getMessages(user_id, thread_id)` — Get conversation
- `createGroup(members)` — Create group
- `updateGroupMembers(group_id, members)` — Modify group


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

### Message Storage

```
One-to-one: Bilateral storage (both users get copy)
Group: Centralized, sync to members
Indexing: (user_id, timestamp) for fast retrieval
```

### Delivery Guarantees

```
At-least-once: Message queued until ACK
Message status: Sent, Delivered, Read
Retry on failure: Exponential backoff
```

### Notifications

```
Online: WebSocket push
Offline: Store and push when online
Badges: Unread count per user
```


## Scenario

Chat System is a critical component in modern distributed systems. In real-world applications, handling complex business logic at scale with high reliability. For example, major tech companies like Netflix, Uber, and Airbnb rely on similar solutions to handle millions of concurrent users and requests. The challenge is achieving this while maintaining sub-100ms latency, 99.99% availability, and gracefully handling 10x traffic spikes during peak demand. This component provides the foundational capability to solve these challenges reliably and efficiently at global scale.

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
┌───────────────────────────────┐
│   Chat Application            │
│  WebSocket Server             │
│  - User connection mgmt       │
│  - Message broadcast          │
│  Message Persistence          │
│  - MongoDB (flexible)         │
│  - Sharded by conversation_id │
│  Delivery Tracking            │
│  - Sent, Delivered, Read      │
└───────────────────────────────┘
```

## Back-of-Envelope Calculations

100M users, 1M concurrent, 10K msg/sec. WebSocket: 1M × 10KB = 10GB. Throughput: 10K/sec × 200B = 2MB/sec storage.
## Design Choice Comparison

| Approach | Pros | Cons |
|----------|------|------|
| Polling | Simple | High latency |
| Long-polling | Better | Connection overhead |
| WebSocket | Real-time | Firewall |

## Follow-up Interview Questions

1. Message search across convos? 2. E2E encryption? 3. Spam detection? 4. WebSocket bottleneck? 5. Message migration?

## Example Scenario Walkthrough

[Describe a concrete example with step-by-step execution]

### Architecture Diagram

```mermaid
graph TB
    User1["User 1"]
    User2["User 2"]
    WebSocket["WebSocket Server"]
    MessageQueue["Message Queue"]
    Storage["Storage"]

    User1 -->|Send| WebSocket
    WebSocket -->|Enqueue| MessageQueue
    MessageQueue -->|Deliver| User2
    MessageQueue -->|Store| Storage
```

### Flow Diagram

```mermaid
sequenceDiagram
    participant U1 as User 1
    participant WS as WebSocket
    participant Q as Queue
    participant U2 as User 2

    U1->>WS: Send Message
    WS->>Q: Enqueue
    Q->>U2: Deliver (if online)
    alt Offline
        Q->>Storage: Mark unread
    end
```

## Complexity

| Operation | Time |
|-----------|------|
| Send message | O(1) |
| Get messages | O(k) where k=messages |
| Group update | O(n) where n=members |

## Python Implementation

```python
from dataclasses import dataclass, field
from typing import List, Dict
from datetime import datetime

@dataclass
class Message:
    sender_id: str
    content: str
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class ChatRoom:
    room_id: str
    members: List[str] = field(default_factory=list)
    messages: List[Message] = field(default_factory=list)

class ChatService:
    def __init__(self):
        self._rooms: Dict[str, ChatRoom] = {}
        self._user_rooms: Dict[str, List[str]] = {}

    def create_room(self, room_id: str) -> ChatRoom:
        room = ChatRoom(room_id)
        self._rooms[room_id] = room
        return room

    def join_room(self, user_id: str, room_id: str):
        self._rooms[room_id].members.append(user_id)
        self._user_rooms.setdefault(user_id, []).append(room_id)

    def send_message(self, room_id: str, sender_id: str, content: str) -> Message:
        msg = Message(sender_id, content)
        self._rooms[room_id].messages.append(msg)
        return msg

    def get_history(self, room_id: str, limit: int = 50) -> List[Message]:
        return self._rooms[room_id].messages[-limit:]

# Usage
chat = ChatService()
chat.create_room("room1")
chat.join_room("alice", "room1")
chat.join_room("bob", "room1")
chat.send_message("room1", "alice", "Hello!")
msgs = chat.get_history("room1")
print(msgs[0].content)  # Hello!
```

## Java Implementation

```java
import java.util.*;
import java.time.Instant;

public class ChatService {
    record Message(String senderId, String content, Instant ts) {}
    record Room(String id, List<String> members, List<Message> messages) {}

    private Map<String, Room> rooms = new HashMap<>();

    public Room createRoom(String id) {
        Room room = new Room(id, new ArrayList<>(), new ArrayList<>());
        rooms.put(id, room);
        return room;
    }

    public void joinRoom(String userId, String roomId) {
        rooms.get(roomId).members().add(userId);
    }

    public Message sendMessage(String roomId, String senderId, String content) {
        Message msg = new Message(senderId, content, Instant.now());
        rooms.get(roomId).messages().add(msg);
        return msg;
    }

    public List<Message> getHistory(String roomId, int limit) {
        List<Message> msgs = rooms.get(roomId).messages();
        return msgs.subList(Math.max(0, msgs.size() - limit), msgs.size());
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


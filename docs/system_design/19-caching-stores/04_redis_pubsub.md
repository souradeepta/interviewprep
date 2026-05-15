# Redis Pub/Sub and Keyspace Notifications

## Problem Statement

Design real-time messaging systems using Redis Pub/Sub for broadcast messaging and keyspace notifications — enabling chat systems, live dashboards, and event-driven cache invalidation.

## Scenario

Redis Pub/Sub and Keyspace Notifications is a critical component in modern distributed systems. In real-world applications, providing fast in-memory data access with persistence options. For example, major tech companies like Netflix, Uber, and Airbnb rely on similar solutions to handle millions of concurrent users and requests. The challenge is achieving this while maintaining sub-100ms latency, 99.99% availability, and gracefully handling 10x traffic spikes during peak demand. This component provides the foundational capability to solve these challenges reliably and efficiently at global scale.

## Users

- **Backend Engineers**: Responsible for implementing and maintaining this system component in production environments. They need to understand the architecture, trade-offs, failure modes, and operational considerations.
- **DevOps/SRE Teams**: Monitor system health, manage scaling policies, handle incidents, and ensure reliability SLAs are met. They need insights into performance characteristics, bottlenecks, and failure recovery mechanisms.
- **Data Engineers**: Design data pipelines and analytics around this system, requiring deep understanding of data flow, consistency guarantees, and throughput characteristics.
- **System Architects**: Make high-level architectural decisions that impact company infrastructure, requiring comprehensive understanding of capabilities, limitations, and scalability boundaries.
- **Security Teams**: Understand security implications, potential vulnerabilities, and compliance requirements for this component.

## PRD

### Functional Requirements
- Store key-value with optional TTL
- Support strings, lists, sets, hashes, sorted sets
- Atomic INCR, APPEND, ZADD operations
- Optional persistence (RDB, AOF)
- Master-slave replication

### Non-Functional Requirements
- Latency: < 1ms for get/set
- Throughput: 100K-1M ops/sec
- Memory: all in-memory (set maxmemory policy)
- Availability: sentinel or cluster HA
- Durability: optional (can lose data without persistence)

### Success Metrics
- Hit rate > 95% for caching
- Latency p99 < 10ms
- Memory utilization < 80%
- Replication lag < 1s


## Flow

The typical operational flow for this system involves these key phases:

1. **Request Arrival**: Client/upstream system sends request with required parameters and context
2. **Validation & Routing**: System validates request format, authentication, and routes to correct handler/shard/instance
3. **Core Processing**: Execute the main algorithm, database query, or business logic on the data/state
4. **State Management**: Update internal state (caches, indexes, counters, logs) with proper atomicity and locking
5. **Response Generation**: Format results and return to requester with relevant metadata (timing, version info)
6. **Observability**: Record metrics (latency, throughput, errors), logs (for debugging), and traces (for performance analysis)

This flow repeats thousands or millions of times per second in production. Each operation's efficiency compounds across the entire system, making careful optimization essential. Bottlenecks at any phase can cascade to impact overall system performance.


## Code Explanation (Detailed)

### Data Structures
- String: Atomic increment, append (cache values, counters)
- List: FIFO queue (rpush/lpop)
- Hash: Object-like (hset/hget)
- Set: Unique values, fast membership (sadd/smembers)
- Sorted Set: Ranked data (zadd/zrevrange for leaderboards)

### Caching Pattern (Cache-Aside)
1. Check cache (fast path, O(1))
2. If miss: fetch from DB (slow)
3. Update cache with TTL (setex)
4. Risk: thundering herd on popular key

### Atomic Operations
- Lua scripts: Complex operations, server-side atomicity
- WATCH/MULTI/EXEC: Optimistic locking
- INCR/ZADD: Inherently atomic

## Architecture Diagram

```mermaid
graph LR
    subgraph Publishers
        P1["Web Server 1"]
        P2["Web Server 2"]
    end

    subgraph Redis["Redis Pub/Sub"]
        CH1["Channel: chat:room1"]
        CH2["Channel: notifications:user123"]
        PAT["Pattern: news.*"]
    end

    subgraph Subscribers
        S1["WebSocket\nGateway 1"]
        S2["WebSocket\nGateway 2"]
        S3["Mobile Push\nService"]
    end

    P1 -->|PUBLISH chat:room1 msg| CH1
    P2 -->|PUBLISH news.sports| PAT
    CH1 --> S1
    CH1 --> S2
    PAT --> S3
    CH2 --> S3
```

## Flow Diagram

```mermaid
sequenceDiagram
    participant S1 as Subscriber 1
    participant R as Redis
    participant S2 as Subscriber 2
    participant P as Publisher

    S1->>R: SUBSCRIBE chat:room1
    R-->>S1: ["subscribe", "chat:room1", 1]
    S2->>R: SUBSCRIBE chat:room1
    R-->>S2: ["subscribe", "chat:room1", 2]

    P->>R: PUBLISH chat:room1 "Hello!"
    R-->>S1: ["message", "chat:room1", "Hello!"]
    R-->>S2: ["message", "chat:room1", "Hello!"]
    R-->>P: 2 (subscribers reached)

    S1->>R: PSUBSCRIBE news.*
    P->>R: PUBLISH news.sports "Goal!"
    R-->>S1: ["pmessage", "news.*", "news.sports", "Goal!"]
```

## Design

### Pub/Sub Commands

```
SUBSCRIBE channel [channel ...]: Subscribe to channels
UNSUBSCRIBE [channel ...]: Unsubscribe
PSUBSCRIBE pattern [pattern ...]: Pattern subscribe (glob)
PUNSUBSCRIBE [pattern ...]: Pattern unsubscribe
PUBLISH channel message: Publish to channel -> returns subscriber count

Patterns:
  news.*        matches: news.sports, news.weather
  chat:room:?   matches: chat:room:1 (single char wildcard)
  h?llo         matches: hello, hallo
  h*llo         matches: hllo, heeello

SUBSCRIBE puts connection into subscribe mode:
  Only SUBSCRIBE/UNSUBSCRIBE/PING allowed
  Cannot SET/GET while subscribed
  Use separate connection for pub/sub
```

### Keyspace Notifications

```
Redis can emit events when keys are modified:
  notify-keyspace-events "KEA"  (in redis.conf or CONFIG SET)
  K = Keyspace (key-based events)
  E = Keyevent (event-based subscriptions)
  A = All events (g$lzxedt)

Channels:
  __keyspace@0__:mykey -> events for specific key
  __keyevent@0__:expired -> all expired events

Use cases:
  Cache invalidation: subscribe to expired/del events
  Distributed locks: notify when lock key expires
  Job scheduling: set key with TTL, trigger on expiry

Example:
  PSUBSCRIBE __keyevent@0__:expired
  -> receive all key expiry events
  -> trigger cache refresh logic
```

### Scaling Pub/Sub

```
Problem: Pub/Sub doesn't work across Redis Cluster shards
  PUBLISH goes to one node; subscribers on other nodes miss it

Solutions:
  1. Dedicated Redis instance (not cluster) for pub/sub
  2. Redis Streams (preferred for reliability)
  3. Client-side fan-out: app layer publishes to all nodes
  4. Redis Cluster pub/sub (Redis 7.0+): shard pub/sub

Redis Streams vs Pub/Sub:
  Pub/Sub: fire-and-forget, no persistence, missed if offline
  Streams: persistent, consumer groups, replay, ACKs
  Use Streams for: reliable messaging, offline consumers
  Use Pub/Sub for: real-time broadcast, ephemeral events
```

## Back-of-Envelope Calculations

```
Pub/Sub throughput:
  Single channel, 1000 subscribers, 100 msg/s:
  100 * 1000 = 100K message deliveries/sec
  Each message ~100 bytes: 10MB/s network
  Redis can handle this easily

Message size limit:
  Max message: 512MB (same as String)
  Recommended: < 1KB for real-time use

Connection overhead:
  Each subscriber = 1 TCP connection
  Redis: ~50K connections default (maxclients)
  Memory: ~20KB per connection = 50K * 20KB = 1GB

Keyspace notification overhead:
  Enabled: adds ~5-10% CPU per Redis op (notify all subscribers)
  Disabled (default): zero overhead
  Only enable if needed; use targeted events (not "all")

Fan-out architecture:
  10 WebSocket servers x 100K connections each = 1M users
  Each WS server: 1 Redis connection for pub/sub
  Redis sees 10 subscribers per channel
  Efficient!
```

## Design Choices

| Approach | Reliability | Scalability | Complexity |
|---|---|---|---|
| Redis Pub/Sub | Fire-and-forget | 50K connections | Low |
| Redis Streams | Persistent + ACK | Consumer groups | Medium |
| Kafka + WS gateway | Durable | Millions | High |
| SSE + Pub/Sub | Browser-native | Stateless scaling | Medium |
| WebSocket + Redis | Real-time | Horizontal | Medium |

## Python Implementation

```python
import asyncio
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Set
import time
import fnmatch
from collections import defaultdict

@dataclass
class PubSubMessage:
    msg_type: str  # "message", "pmessage", "subscribe", "unsubscribe"
    channel: str
    data: Any
    pattern: Optional[str] = None
    timestamp: float = field(default_factory=time.time)

class RedisPubSub:
    def __init__(self):
        self._channels: Dict[str, Set[str]] = defaultdict(set)  # channel -> subscriber_ids
        self._patterns: Dict[str, Set[str]] = defaultdict(set)  # pattern -> subscriber_ids
        self._subscriber_queues: Dict[str, List[PubSubMessage]] = defaultdict(list)

    def subscribe(self, subscriber_id: str, *channels: str) -> List[PubSubMessage]:
        responses = []
        for channel in channels:
            self._channels[channel].add(subscriber_id)
            count = len(self._channels[channel])
            responses.append(PubSubMessage("subscribe", channel, count))
            print(f"[PubSub] {subscriber_id} subscribed to '{channel}' (total={count})")
        return responses

    def unsubscribe(self, subscriber_id: str, *channels: str) -> List[PubSubMessage]:
        responses = []
        for channel in (channels or list(self._channels.keys())):
            self._channels[channel].discard(subscriber_id)
            if not self._channels[channel]:
                del self._channels[channel]
            count = len(self._channels.get(channel, set()))
            responses.append(PubSubMessage("unsubscribe", channel, count))
        return responses

    def psubscribe(self, subscriber_id: str, *patterns: str):
        for pattern in patterns:
            self._patterns[pattern].add(subscriber_id)
            print(f"[PubSub] {subscriber_id} psubscribed to pattern '{pattern}'")

    def publish(self, channel: str, message: Any) -> int:
        delivered = 0
        # Exact subscribers
        for sub_id in self._channels.get(channel, set()):
            msg = PubSubMessage("message", channel, message)
            self._subscriber_queues[sub_id].append(msg)
            delivered += 1
        # Pattern subscribers
        for pattern, sub_ids in self._patterns.items():
            if fnmatch.fnmatch(channel, pattern):
                for sub_id in sub_ids:
                    msg = PubSubMessage("pmessage", channel, message, pattern=pattern)
                    self._subscriber_queues[sub_id].append(msg)
                    delivered += 1
        print(f"[PubSub] Published to '{channel}': {delivered} subscribers")
        return delivered

    def receive(self, subscriber_id: str) -> List[PubSubMessage]:
        msgs = self._subscriber_queues.pop(subscriber_id, [])
        return msgs

class KeyspaceNotifications:
    def __init__(self, pubsub: RedisPubSub):
        self.pubsub = pubsub
        self.enabled_events = set()

    def enable(self, events: str = "KEA"):
        if "K" in events:
            self.enabled_events.add("keyspace")
        if "E" in events:
            self.enabled_events.add("keyevent")
        if "x" in events or "A" in events:
            self.enabled_events.add("expired")
        if "g" in events or "A" in events:
            self.enabled_events.add("generic")

    def emit(self, db: int, key: str, event: str):
        if "keyspace" in self.enabled_events:
            channel = f"__keyspace@{db}__:{key}"
            self.pubsub.publish(channel, event)
        if "keyevent" in self.enabled_events:
            channel = f"__keyevent@{db}__:{event}"
            self.pubsub.publish(channel, key)

class CacheInvalidator:
    def __init__(self, pubsub: RedisPubSub, local_cache: Dict[str, Any]):
        self.sub_id = "cache-invalidator"
        self._cache = local_cache
        pubsub.psubscribe(self.sub_id, "__keyevent@0__:expired", "__keyevent@0__:del")
        self._pubsub = pubsub

    def process_events(self):
        messages = self._pubsub.receive(self.sub_id)
        for msg in messages:
            key = msg.data  # keyevent: data = key name
            if key in self._cache:
                del self._cache[key]
                print(f"[CacheInvalidator] Invalidated local cache for '{key}'")

# Demo
pubsub = RedisPubSub()

# Chat room subscribers
pubsub.subscribe("gateway-1", "chat:room1")
pubsub.subscribe("gateway-2", "chat:room1")
pubsub.psubscribe("push-service", "notifications.*")

print("\n=== Publishing Messages ===")
pubsub.publish("chat:room1", "Hello, world!")
pubsub.publish("notifications.user123", "You have a new follower!")
pubsub.publish("news.sports", "Goal scored!")  # No subscribers

print("\n=== Receiving Messages ===")
for sub_id in ["gateway-1", "gateway-2", "push-service"]:
    msgs = pubsub.receive(sub_id)
    for msg in msgs:
        print(f"  [{sub_id}] {msg.msg_type} on '{msg.channel}': {msg.data}")

print("\n=== Keyspace Notifications ===")
kn = KeyspaceNotifications(pubsub)
kn.enable("KE")

local_cache = {"session:abc": "user-1", "session:xyz": "user-2"}
invalidator = CacheInvalidator(pubsub, local_cache)

kn.emit(0, "session:abc", "expired")
invalidator.process_events()
print(f"Local cache after expiry: {local_cache}")
```

## Java Implementation

```java
import java.util.*;
import java.util.function.*;

public class RedisPubSubSimulator {
    Map<String, List<Consumer<String>>> subs = new HashMap<>();
    Map<String, List<Consumer<String>>> patternSubs = new HashMap<>();

    void subscribe(String channel, Consumer<String> handler) {
        subs.computeIfAbsent(channel, k -> new ArrayList<>()).add(handler);
    }

    void psubscribe(String pattern, Consumer<String> handler) {
        patternSubs.computeIfAbsent(pattern, k -> new ArrayList<>()).add(handler);
    }

    int publish(String channel, String msg) {
        int count = 0;
        for (Consumer<String> h : subs.getOrDefault(channel, List.of())) { h.accept(msg); count++; }
        for (var entry : patternSubs.entrySet()) {
            if (channel.matches(entry.getKey().replace(".", "\\.").replace("*", ".*"))) {
                entry.getValue().forEach(h -> h.accept(msg)); count += entry.getValue().size();
            }
        }
        return count;
    }

    public static void main(String[] args) {
        RedisPubSubSimulator ps = new RedisPubSubSimulator();
        ps.subscribe("chat:room1", m -> System.out.println("Gateway1: " + m));
        ps.subscribe("chat:room1", m -> System.out.println("Gateway2: " + m));
        ps.psubscribe("notifications.*", m -> System.out.println("Push: " + m));
        System.out.println("Delivered: " + ps.publish("chat:room1", "Hello!"));
        ps.publish("notifications.user1", "New follower!");
    }
}
```

## Complexity

| Operation | Time |
|---|---|
| SUBSCRIBE | O(1) |
| PUBLISH (N subscribers) | O(N) |
| PSUBSCRIBE matching | O(patterns) |
| Keyspace notification | O(matching subscribers) |

## Common Questions & Answers

**Q: What is Redis and when do you use it?**

A: In-memory key-value data store with sub-millisecond latency. Used for caching (reduce DB load), sessions (user state), queues, real-time counters, leaderboards. Very fast but volatile (data loss on crash without persistence).

**Q: What data structures does Redis support?**

A: Strings (simple values), Lists (FIFO queues), Sets (unique values), Hashes (objects), Sorted Sets (leaderboards), Streams (Kafka-like), HyperLogLog (cardinality), Bitmaps (bitwise ops). Rich beyond simple cache.

**Q: How does Redis persistence work?**

A: RDB (snapshot): periodic point-in-time backup (fast, compact). AOF (append-only file): log all writes (durable, slower). BGSAVE/BGREWRITEAOF: background operations. Choose: speed vs. durability trade-off. Most use both.

**Q: What is Redis replication?**

A: Master-slave architecture: master accepts writes, slaves replicate. Read from master (strong consistency) or slaves (eventual, faster). Slaves can be read-only replicas or chain-replicate to others.

**Q: What is Redis Sentinel?**

A: High availability solution: monitors Redis instances, detects failures, promotes replica to master automatically. Requires 3+ Sentinel instances (majority quorum). Client connects via Sentinel instead of Redis directly.

**Q: What is Redis Cluster?**

A: Distributed Redis: data sharded across multiple nodes (hash slots). Auto-sharding, automatic failover, rebalancing. More complex than Sentinel. Required for massive scale (TB+ data).

**Q: How do you choose between Sentinel and Cluster?**

A: Sentinel: single master, high availability. Cluster: distributed, massive scale. Sentinel for most (simpler), Cluster only if need horizontal scaling. Data > memory = use Cluster.

**Q: How do you handle eviction when Redis runs out of memory?**

A: Set maxmemory policy: LRU, LFU, TTL, random, or no-eviction. LRU/LFU common for caching. TTL for session data. No-eviction blocks writes (safe but risky). Monitor memory usage constantly.

**Q: What is key expiration in Redis?**

A: Keys have optional TTL (time-to-live). After expiration, key automatically deleted. Lazy deletion (on access) + periodic cleanup. Use for session data, cache, or temporary counters. Check expiration policy for accuracy.

**Q: How do you secure Redis?**

A: Use password authentication (requirepass). ACLs (Redis 6+): per-user permissions. Run inside VPC (no internet access). Disable dangerous commands (FLUSHDB, CONFIG). TLS for remote connections.

## Follow-up Questions & Answers

**Q: How would you implement distributed locking with Redis?**

A: SET key value EX ttl NX (atomic: set if not exists with TTL). Acquire lock, execute critical section, delete key. Risk: crash loses lock (data consistency issue). Redlock solves this with multiple instances.

**Q: What is Redlock and what problem does it solve?**

A: Distributed lock across 5 Redis instances. Acquire lock on majority (quorum). Survives single instance failure. Overkill for most, but necessary for safety-critical sections. Trade: performance for correctness.

**Q: How would you implement rate limiting with Redis?**

A: Use sorted set with timestamps or hash with counters. Increment on each request, check against limit. Fast (O(log n)). Alternative: token bucket in Lua script. Faster than database.

**Q: How do you handle Redis memory limits and eviction policy?**

A: Set maxmemory (bytes), maxmemory-policy (LRU/LFU/TTL/random). Monitor hit rate (eviction = misses). Can also manually delete old keys or use cache-aside with database.

**Q: Can you use Redis for reliable message queues?**

A: Partially. Lists (basic) or Streams (better). Lists: FIFO, no persistence without RDB. Streams: replicas, consumer groups, reliable delivery (Kafka-like). For critical: use Kafka instead.

**Q: How would you implement Pub/Sub in Redis?**

A: Publisher sends to channel, subscribers receive. Fire-and-forget (no persistence). Good for notifications. Bad for reliable messaging (missed if subscriber offline). Better: Streams for reliable pub/sub.

**Q: How do you scale Redis beyond single node?**

A: Use Cluster (distributed), replicate read-heavy workload (slaves), or shard in application code. Cluster best for massive scale. Replication for read scaling. App sharding for distributed control.

**Q: Can you implement transactions in Redis?**

A: MULTI/EXEC: atomic batch of commands. Optimistic locking with WATCH. No rollback (all-or-nothing at command level). Use Lua scripts for complex atomic operations.

**Q: How would you debug Redis performance issues?**

A: SLOWLOG: find slow commands. MONITOR: see all commands in real-time. Memory analysis: MEMORY DOCTOR, key usage patterns. Network: latency between app and Redis. Profiling tools.

**Q: How do you backup and restore Redis?**

A: Backup: RDB snapshots, AOF files, or replication. Restore: copy files, or use Redis replication + replicaof. Backup strategy: periodic snapshots + AOF for durability. Test recovery regularly.


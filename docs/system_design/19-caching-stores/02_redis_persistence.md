# Redis Persistence

## Problem Statement

Design Redis persistence strategies to balance data durability against performance — understanding RDB snapshots, AOF append-only files, and hybrid RDB+AOF persistence.

## Scenario

Redis Persistence is a critical component in modern distributed systems. In real-world applications, providing fast in-memory data access with persistence options. For example, major tech companies like Netflix, Uber, and Airbnb rely on similar solutions to handle millions of concurrent users and requests. The challenge is achieving this while maintaining sub-100ms latency, 99.99% availability, and gracefully handling 10x traffic spikes during peak demand. This component provides the foundational capability to solve these challenges reliably and efficiently at global scale.

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
graph TB
    subgraph Redis["Redis Process"]
        MEM["In-Memory Data\n(current state)"]
        RDB["RDB Snapshot\ndump.rdb\n(periodic fork)"]
        AOF["AOF Log\nappendonly.aof\n(every command)"]
    end

    subgraph Disk["Disk"]
        RDBF["dump.rdb\n~100MB compressed"]
        AOFF["appendonly.aof\n~500MB growing"]
    end

    MEM -->|BGSAVE fork| RDB
    RDB -->|write| RDBF
    MEM -->|after each write command| AOF
    AOF -->|fsync| AOFF
    AOFF -->|AOF rewrite| AOFF
    RDBF -->|reload on startup| MEM
    AOFF -->|replay on startup| MEM
```

## Flow Diagram

```mermaid
sequenceDiagram
    participant C as Client
    participant R as Redis
    participant F as Forked Child
    participant D as Disk

    C->>R: SET key1 value1
    R->>R: Write to memory (instant)
    R->>R: Append to AOF buffer: "SET key1 value1"
    R->>D: fsync AOF (if appendfsync=everysec: async)
    R-->>C: OK

    Note over R: Every 300s or 10 writes
    R->>F: fork() - copy-on-write
    F->>D: Write dump.rdb (in background)
    R->>R: Continue serving requests

    Note over D: Redis restart
    R->>D: Load dump.rdb (fast, bulk restore)
    R->>D: Replay AOF from checkpoint (delta since snapshot)
```

## Design

### RDB (Redis Database)

```
How it works:
  1. BGSAVE triggers fork() (copy-on-write)
  2. Child process serializes all data to temp file
  3. Atomic rename: temp file -> dump.rdb
  4. Parent continues serving requests

Configuration:
  save 900 1      # Save if 1 write in 900s (15min)
  save 300 10     # Save if 10 writes in 300s
  save 60 10000   # Save if 10000 writes in 60s
  dbfilename dump.rdb
  dir /var/lib/redis

Pros:
  - Fast recovery (single file load, no replay)
  - Compact, compressed binary format
  - Fork overhead minimal with copy-on-write

Cons:
  - Data loss up to last snapshot (minutes)
  - Fork can pause Redis on copy for large datasets (COW pages)
  - Large dataset + lots of writes = high memory pressure
```

### AOF (Append-Only File)

```
How it works:
  1. Every write command appended to buffer
  2. Buffer flushed to disk based on policy
  3. On restart: replay all commands in order

appendfsync options:
  always:   fsync after every command (safest, slowest: 1000 IOPS)
  everysec: fsync once per second (1s max data loss, recommended)
  no:       OS handles fsync (fastest, unpredictable data loss)

AOF Rewrite:
  aof-rewrite-min-size 64mb
  auto-aof-rewrite-percentage 100
  Background process rewrites AOF to current state (no dups/expired keys)
  Reduces AOF size from GB to current-state size

Pros:
  - Much lower data loss (1s with everysec)
  - Human-readable commands
  - Replayable history

Cons:
  - Larger file than RDB
  - Slower startup (replay all commands)
  - Potential for partial writes on crash
```

### Hybrid (RDB + AOF)

```
aof-use-rdb-preamble yes (default Redis 7+)

How it works:
  AOF file starts with RDB snapshot (preamble)
  Then AOF commands for changes since snapshot

Startup:
  1. Load RDB preamble (fast bulk restore)
  2. Replay AOF delta (small)
  = Fast startup + small data loss

Best of both worlds:
  - Near-AOF durability (1s loss max)
  - Near-RDB startup performance
  - Recommended for production
```

## Back-of-Envelope Calculations

```
RDB snapshot size:
  1M keys, 100 bytes avg = 100MB raw
  RDB compression (LZF): ~50MB on disk
  
RDB fork time (COW):
  16GB Redis, 10% write rate during snapshot
  16GB * 10% = 1.6GB copied on write
  At 1GB/s disk: ~1.6s fork overhead
  
AOF file growth:
  100K writes/sec, 30 bytes/command avg = 3MB/s
  After 1 hour: 10.8GB AOF
  After rewrite (10:1 compression): ~1GB
  
AOF rewrite trigger (100% growth):
  Base size 512MB -> rewrite at 1GB
  At 3MB/s growth: triggers every 170 seconds
  
Recovery time:
  RDB: 50MB/s disk read + deserialization
  16GB RDB: ~320 seconds = 5+ minutes
  Hybrid: smaller AOF delta, faster
  
  Solution: Redis Sentinel/Cluster with replicas
  Replica always ready to serve (no cold restart)
```

## Design Choices

| Mode | Data Loss | Startup Speed | Disk Space | Use Case |
|---|---|---|---|---|
| No persistence | All data | Instant | None | Pure cache |
| RDB only | Up to 1-15 min | Fast | Small | Snapshots, dev |
| AOF (everysec) | ~1 second | Slow (replay) | Large | Durable store |
| RDB + AOF (hybrid) | ~1 second | Fast | Medium | Production |
| AOF (always) | Zero | Slow | Large | Financial, audit |

## Python Implementation

```python
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import time
import json
import pickle
import io
import os

@dataclass
class AOFEntry:
    command: str
    args: List[Any]
    timestamp: float = field(default_factory=time.time)

    def serialize(self) -> str:
        return json.dumps({"cmd": self.command, "args": self.args, "ts": self.timestamp})

class AOFPersistence:
    def __init__(self, filename: str = "appendonly.aof", fsync_mode: str = "everysec"):
        self.filename = filename
        self.fsync_mode = fsync_mode  # always, everysec, no
        self._buffer: List[str] = []
        self._last_fsync = time.time()
        self._total_commands = 0
        self._file_size = 0

    def record(self, command: str, *args):
        entry = AOFEntry(command=command, args=list(args))
        line = entry.serialize() + "\n"
        self._buffer.append(line)
        self._total_commands += 1
        self._file_size += len(line)

        if self.fsync_mode == "always":
            self._flush()
        elif self.fsync_mode == "everysec":
            if time.time() - self._last_fsync >= 1.0:
                self._flush()

    def _flush(self):
        if not self._buffer:
            return
        print(f"[AOF] Flushing {len(self._buffer)} commands to {self.filename}")
        # In real Redis: write to file + fsync
        self._buffer.clear()
        self._last_fsync = time.time()

    def replay(self, store: Dict[str, Any], commands: List[AOFEntry]):
        for entry in commands:
            self._apply(store, entry)
        print(f"[AOF] Replayed {len(commands)} commands")

    def _apply(self, store: Dict, entry: AOFEntry):
        cmd = entry.command.upper()
        args = entry.args
        if cmd == "SET":
            store[args[0]] = args[1]
        elif cmd == "DEL":
            store.pop(args[0], None)
        elif cmd == "INCR":
            store[args[0]] = int(store.get(args[0], 0)) + 1

    def stats(self) -> dict:
        return {
            "total_commands": self._total_commands,
            "file_size_kb": round(self._file_size / 1024, 2),
            "buffer_pending": len(self._buffer),
            "fsync_mode": self.fsync_mode,
        }

class RDBPersistence:
    def __init__(self, filename: str = "dump.rdb"):
        self.filename = filename
        self._last_save = time.time()
        self._changes_since_save = 0
        self._save_rules = [
            (900, 1),    # 1 change in 900s
            (300, 10),   # 10 changes in 300s
            (60, 10000), # 10000 changes in 60s
        ]

    def on_write(self, store: Dict):
        self._changes_since_save += 1
        elapsed = time.time() - self._last_save
        for seconds, changes in self._save_rules:
            if elapsed >= seconds and self._changes_since_save >= changes:
                self._bgsave(store)
                break

    def _bgsave(self, store: Dict):
        print(f"[RDB] BGSAVE triggered (fork + serialize {len(store)} keys)")
        # In real Redis: fork(), child serializes to temp file, rename
        data = json.dumps(store)
        print(f"[RDB] Saved {len(data)} bytes to {self.filename}")
        self._last_save = time.time()
        self._changes_since_save = 0

    def load(self, filename: str) -> Optional[Dict]:
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            print(f"[RDB] Loaded {len(data)} keys from {filename}")
            return data
        except (FileNotFoundError, json.JSONDecodeError):
            return None

class HybridPersistence:
    def __init__(self):
        self._rdb = RDBPersistence()
        self._aof = AOFPersistence(fsync_mode="everysec")
        self._store: Dict[str, Any] = {}

    def execute(self, command: str, *args) -> Any:
        self._aof.record(command, *args)
        result = self._execute_command(command, *args)
        self._rdb.on_write(self._store)
        return result

    def _execute_command(self, command: str, *args) -> Any:
        cmd = command.upper()
        if cmd == "SET":
            self._store[args[0]] = args[1]
            return "OK"
        elif cmd == "GET":
            return self._store.get(args[0])
        elif cmd == "DEL":
            return self._store.pop(args[0], None) is not None
        elif cmd == "INCR":
            self._store[args[0]] = int(self._store.get(args[0], 0)) + 1
            return self._store[args[0]]
        return None

    def get_store_copy(self) -> Dict:
        return dict(self._store)

# Demo
print("=== AOF Persistence ===")
aof = AOFPersistence(fsync_mode="everysec")
aof.record("SET", "user:1", "alice")
aof.record("SET", "user:2", "bob")
aof.record("INCR", "counter")
aof.record("DEL", "user:2")
print(f"AOF stats: {aof.stats()}")

print("\n=== Hybrid Persistence Demo ===")
redis = HybridPersistence()
redis.execute("SET", "session:abc", "user-1")
redis.execute("INCR", "page_views")
redis.execute("INCR", "page_views")
redis.execute("SET", "config:theme", "dark")

print(f"Current store: {redis.get_store_copy()}")
print(f"AOF stats: {aof.stats()}")

print("\n=== AOF Replay Simulation ===")
replay_commands = [
    AOFEntry("SET", ["key1", "value1"]),
    AOFEntry("INCR", ["counter"]),
    AOFEntry("SET", ["key2", "value2"]),
    AOFEntry("DEL", ["key1"]),
]
recovered_store: Dict = {}
aof.replay(recovered_store, replay_commands)
print(f"Recovered store: {recovered_store}")
```

## Java Implementation

```java
import java.util.*;
import java.util.concurrent.*;

public class RedisPersistence {
    static class AOF {
        List<String> log = new ArrayList<>();
        String fsyncMode = "everysec";
        long lastFsync = System.currentTimeMillis();

        void record(String cmd, Object... args) {
            log.add(cmd + " " + Arrays.toString(args));
            if ("always".equals(fsyncMode) || 
                ("everysec".equals(fsyncMode) && System.currentTimeMillis() - lastFsync >= 1000)) {
                flush();
            }
        }

        void flush() {
            System.out.printf("[AOF] Flushing %d commands%n", log.size());
            lastFsync = System.currentTimeMillis();
        }

        void replay(Map<String, Object> store) {
            for (String entry : log) {
                String[] parts = entry.split(" ", 2);
                if ("SET".equals(parts[0])) {
                    String[] keyVal = parts[1].replace("[", "").replace("]", "").split(", ");
                    store.put(keyVal[0], keyVal[1]);
                } else if ("DEL".equals(parts[0])) {
                    store.remove(parts[1].replace("[", "").replace("]", ""));
                }
            }
            System.out.println("Replayed " + log.size() + " commands. Store: " + store);
        }
    }

    public static void main(String[] args) {
        AOF aof = new AOF();
        aof.record("SET", "user:1", "alice");
        aof.record("SET", "user:2", "bob");
        aof.record("DEL", "user:2");
        aof.flush();

        Map<String, Object> recovered = new HashMap<>();
        aof.replay(recovered);
    }
}
```

## Complexity

| Operation | RDB | AOF (everysec) |
|---|---|---|
| Write latency | O(1) + async snapshot | O(1) + 1s async fsync |
| Startup time | O(keys) linear scan | O(commands) replay |
| Disk space | Small (compressed) | Large (all commands) |
| Data loss risk | Minutes | ~1 second |
| Fork memory pressure | O(write rate) | None |

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


## System Overview

**Scale Metrics:**
- Throughput: Millions of operations per second
- Latency: Sub-millisecond to sub-second response times
- Data volume: Gigabytes to Petabytes
- Concurrent users: Millions to billions
- Availability: 99.99% to 99.999% uptime SLA

**Key Components:**
- Request handling and routing
- Data processing and storage
- Replication and consistency
- Failure detection and recovery
- Monitoring and alerting

## Architecture Diagrams

### System Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        C1["Client"]
        LB["Load Balancer"]
    end

    subgraph "Service Layer"
        S1["Service 1"]
        S2["Service 2"]
        S3["Service N"]
    end

    subgraph "Cache"
        CACHE["Redis/Memcached"]
    end

    subgraph "Storage"
        DB["Primary DB"]
        REP["Replicas"]
    end

    C1 --> LB
    LB --> S1
    LB --> S2
    LB --> S3
    S1 --> CACHE
    S2 --> CACHE
    S3 --> CACHE
    CACHE --> DB
    DB --> REP

    style C1 fill:#e1f5ff
    style S1 fill:#f3e5f5
    style CACHE fill:#fff3e0
    style DB fill:#e8f5e9
```

### Data Flow

```mermaid
graph LR
    A["Request"] --> B["Parse"]
    B --> C["Validate"]
    C --> D["Process"]
    D --> E["Cache"]
    E --> F["Store"]
    F --> G["Response"]

    style A fill:#c8e6c9
    style B fill:#ffccbc
    style C fill:#bbdefb
    style D fill:#f8bbd0
    style E fill:#ffe0b2
    style F fill:#d1c4e9
    style G fill:#c8e6c9
```

### Failover Mechanism

```mermaid
graph TB
    A["Primary Node"] -->|heartbeat| B["Health Checker"]
    C["Replica 1"] -->|heartbeat| B
    D["Replica 2"] -->|heartbeat| B
    B -->|failure detected| E["Coordinator"]
    E -->|elect new primary| F["New Primary"]
    F -->|start accepting| G["Clients"]

    style A fill:#ffcdd2
    style F fill:#c8e6c9
    style G fill:#fff9c4
```

### Consistency Models

```mermaid
graph TB
    subgraph "Strong Consistency"
        A1["Quorum Write"] --> A2["Read Latest"]
    end

    subgraph "Eventual Consistency"
        B1["Write Async"] --> B2["Replicate"]
        B2 --> B3["Read May Stale"]
    end

    subgraph "Causal Consistency"
        C1["Track Causality"] --> C2["Enforce Order"]
    end

    style A1 fill:#c8e6c9
    style B1 fill:#ffccbc
    style C1 fill:#bbdefb
```

### Scaling Strategy

```mermaid
graph TB
    subgraph "Vertical Scaling"
        V1["Bigger CPU"] --> V2["More RAM"]
        V2 --> V3["Faster Disk"]
    end

    subgraph "Horizontal Scaling"
        H1["Add Replicas"] --> H2["Shard Data"]
        H2 --> H3["Distributed Cache"]
    end

    subgraph "Result"
        R["Increased Capacity"]
    end

    V3 --> R
    H3 --> R

    style V1 fill:#bbdefb
    style H1 fill:#f8bbd0
    style R fill:#c8e6c9
```

## Implementation Examples

### Python Implementation

```python
# Python Implementation

from typing import Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)

@dataclass
class Config:
    """Configuration for the system."""
    timeout_ms: int = 5000
    retry_count: int = 3
    batch_size: int = 100
    max_connections: int = 1000

class Handler:
    """Main handler class for operations."""

    def __init__(self, config: Config):
        self.config = config
        self.metrics = {"success": 0, "failure": 0, "latency_ms": []}

    async def process(self, data: Any) -> Any:
        """Process request with error handling."""
        try:
            # Validate input
            self._validate(data)

            # Execute operation
            result = await self._execute(data)

            # Track metrics
            self.metrics["success"] += 1
            return result

        except Exception as e:
            logger.error(f"Processing failed: {e}")
            self.metrics["failure"] += 1
            raise

    def _validate(self, data: Any) -> None:
        """Validate input data."""
        if data is None:
            raise ValueError("Data cannot be None")

    async def _execute(self, data: Any) -> Any:
        """Execute core logic."""
        # Implement actual logic here
        return {"status": "success", "timestamp": datetime.now().isoformat()}

    def get_metrics(self) -> dict:
        """Return collected metrics."""
        return self.metrics

# Usage example
async def main():
    config = Config(timeout_ms=5000, batch_size=100)
    handler = Handler(config)
    result = await handler.process({"key": "value"})
    print(f"Result: {result}")
    print(f"Metrics: {handler.get_metrics()}")
```

### Java Implementation

```java
// Java Implementation

import java.util.*;
import java.util.concurrent.*;
import java.time.Instant;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SystemHandler {
    private static final Logger logger = LoggerFactory.getLogger(SystemHandler.class);

    private final Config config;
    private final Map<String, Long> metrics = new ConcurrentHashMap<>();
    private final ExecutorService executor;

    public static class Config {
        public int timeoutMs = 5000;
        public int retryCount = 3;
        public int batchSize = 100;
        public int maxConnections = 1000;

        public Config withTimeoutMs(int timeout) {
            this.timeoutMs = timeout;
            return this;
        }
    }

    public SystemHandler(Config config) {
        this.config = config;
        this.executor = Executors.newFixedThreadPool(
            Math.min(config.maxConnections, 10)
        );
        metrics.put("success", 0L);
        metrics.put("failure", 0L);
    }

    public <T> T process(Object data) throws Exception {
        try {
            // Validate input
            validate(data);

            // Execute operation
            Object result = execute(data);

            // Track metrics
            metrics.put("success", metrics.get("success") + 1);
            return (T) result;

        } catch (Exception e) {
            logger.error("Processing failed: {}", e.getMessage());
            metrics.put("failure", metrics.get("failure") + 1);
            throw e;
        }
    }

    private void validate(Object data) throws IllegalArgumentException {
        if (data == null) {
            throw new IllegalArgumentException("Data cannot be null");
        }
    }

    private Object execute(Object data) throws Exception {
        // Implement core logic
        return Map.of(
            "status", "success",
            "timestamp", Instant.now().toString()
        );
    }

    public Map<String, Long> getMetrics() {
        return new HashMap<>(metrics);
    }

    public void shutdown() {
        executor.shutdown();
    }

    public static void main(String[] args) throws Exception {
        Config config = new Config()
            .withTimeoutMs(5000);

        SystemHandler handler = new SystemHandler(config);
        Object result = handler.process(Map.of("key", "value"));
        System.out.println("Result: " + result);
        System.out.println("Metrics: " + handler.getMetrics());
        handler.shutdown();
    }
}
```

## Back-of-Envelope Calculations

### Traffic & Throughput
**Assumptions:**
- Daily active users: 100 million (100M)
- Requests per user per day: 50
- Peak hour traffic: 10% of daily (concentrated)
- Request distribution: 70% read, 30% write

**Calculations:**
```
Total daily requests = 100M users × 50 requests = 5 billion requests/day
Average RPS = 5B requests / 86400 seconds ≈ 57,870 RPS
Peak hour RPS = (5B / 86400) × (100 / 10) ≈ 578,700 RPS
Peak minute RPS = 578,700 / 60 ≈ 9,645 RPS

Read operations = 57,870 × 0.7 ≈ 40,509 RPS (average)
Write operations = 57,870 × 0.3 ≈ 17,361 RPS (average)
```

### Storage Requirements
**Assumptions:**
- Data per user: 1 KB (profile, settings)
- Data per transaction: 500 bytes
- Data retention: 3 years

**Calculations:**
```
User profile storage = 100M × 1 KB = 100 GB
Transaction data = 5B requests/day × 500 bytes × 365 × 3 = 2.74 PB
Total storage ≈ 2.75 PB
Replication factor: 3× → 8.25 PB raw storage

Backup storage (weekly snapshots): 8.25 PB × 52 weeks = 429 PB
```

### Network Bandwidth
**Assumptions:**
- Average request size: 2 KB
- Average response size: 5 KB
- Replication overhead: 2× (write to replicas)

**Calculations:**
```
Inbound bandwidth = 57,870 RPS × 2 KB = 115.74 MB/s
Outbound bandwidth = 57,870 RPS × 5 KB = 289.35 MB/s
Replication bandwidth = 17,361 RPS × 2 KB × 2 = 69.44 MB/s
Total peak bandwidth ≈ 474 MB/s ≈ 3.8 Tbps (peak hour)
```

### Compute Requirements
**Assumptions:**
- Processing time per request: 10 ms
- CPU efficiency: 1 core handles 50 RPS

**Calculations:**
```
CPUs needed for average traffic = 57,870 RPS / 50 = 1,158 cores
CPUs needed for peak traffic = 578,700 RPS / 50 = 11,574 cores
Overprovisioning factor: 1.5× → 17,361 cores total

Using 16 cores per server = 17,361 / 16 ≈ 1,085 servers
With 3:1 replication = 3,255 servers needed
Regional redundancy (3 regions) = 9,765 servers
```

### Latency Analysis (p99)
**Components:**
- Network latency: 5 ms
- Processing: 10 ms
- Storage access: 50 ms (disk), 1 ms (cache)
- Replication write: 20 ms

**Path Analysis:**
```
Cache hit path: 5 + 1 + 5 = 11 ms
Database read path: 5 + 10 + 50 + 5 = 70 ms
Write path: 5 + 10 + 20 + 5 = 40 ms
```

### Cost Estimation
**Monthly costs (approximate):**
```
Compute: 9,765 servers × $1,000/month = $9.765M
Storage: 8.25 PB × $10/GB/month = $82.5M
Bandwidth: 3.8 Tbps × $0.12/GB = $456M
Personnel: 100 engineers × $200K = $20M
Total: ~$568M/month
Cost per user: $5.68/month
```


## Interview Questions & Answers

### Q1: Design the System from Scratch

**Question:** Design a system that can handle 1 billion requests per day with sub-100ms latency.

**Answer Structure:**
1. **Clarify requirements**: DAU, request types, geographic distribution, consistency needs
2. **Back-of-envelope**: Calculate RPS (11.5K avg, 115K peak), storage, bandwidth
3. **High-level design**: Load balancing → services → cache → storage
4. **Deep dive**:
   - Horizontal scaling with sharding
   - Multi-region active-active with eventual consistency
   - Caching strategy (write-through for critical data)
   - Monitoring: metrics, logging, tracing
5. **Bottlenecks**: Identify and address each
6. **Trade-offs**: Consistency vs. availability, latency vs. cost

### Q2: Scaling Challenges

**Question:** You're growing from 10M to 1B users (100x). What breaks and how do you fix it?

**Answer:**
- **Database bottleneck**: Sharding by user ID, consistent hashing, shard rebalancing
- **Cache hit rate drops**: Larger working set, tiered caching (L1: local, L2: distributed)
- **Replication lag**: Write-through for consistency-critical data, eventual consistency elsewhere
- **Operational complexity**: Infrastructure-as-code, auto-scaling, chaos engineering
- **Cost**: Optimize resource utilization, use reserved instances, spot instances for batch

### Q3: Failure Scenarios

**Question:** Your primary database goes down. What happens? How do you recover?

**Answer:**
- **Detection**: Health check timeout (3-5 seconds)
- **Failover**: Automatic promotion of replica using Raft consensus
- **Impact**: Write requests fail for ~10 seconds, reads use replicas
- **Recovery**: Background sync of failed node, re-add to cluster
- **Lessons**: Circuit breakers prevent cascade, bulkhead limits blast radius

### Q4: Consistency Requirements

**Question:** Do you need strong or eventual consistency? Why?

**Answer:**
- **Strong consistency**: Critical for financial transactions, inventory, user auth
  - Implementation: Quorum writes, read-after-write
  - Cost: Higher latency (p99 100ms+), lower throughput

- **Eventual consistency**: Fine for user feeds, recommendations, analytics
  - Implementation: Async replication, read-repair
  - Benefit: Lower latency (p99 <10ms), higher throughput

- **Hybrid approach**: Consistency per operation type, not global

### Q5: Performance Optimization

**Question:** How would you reduce p99 latency from 100ms to 20ms?

**Answer:**
1. **Profile** (measure first): Identify bottleneck (storage, network, compute)
2. **Caching**: Multi-tier (L1 local, L2 distributed), bloom filters for misses
3. **Batching**: Group operations, reduce RPC overhead
4. **Connection pooling**: Reuse TCP connections, reduce handshake latency
5. **Async I/O**: Non-blocking operations, increase parallelism
6. **Database optimization**: Indexing, query optimization, read replicas
7. **Code optimization**: Reduce allocations, use faster algorithms
8. **Hardware**: SSD for storage, faster network interconnects

### Q6: Operational Concerns

**Question:** How do you deploy a new version with zero downtime?

**Answer:**
1. **Canary deployment**: Roll out to 1% of servers, monitor metrics
2. **Gradual rollout**: 1% → 10% → 50% → 100% as confidence increases
3. **Health checks**: Automated rollback if error rate exceeds threshold
4. **Database migration**: Schema changes with backward compatibility
5. **Feature flags**: Toggle features independently of deployment
6. **Monitoring**: Enhanced alerting during rollout, easy incident response


## Technology Stack Recommendations

| Layer | Technology | Why |
|-------|-----------|-----|
| Load Balancing | Nginx, HAProxy, AWS ALB | Distribute traffic, health checks |
| Service Framework | FastAPI (Python), Spring Boot (Java) | Async, built-in monitoring |
| Caching | Redis, Memcached | Sub-millisecond latency, distributed |
| Primary Storage | PostgreSQL, MySQL | ACID, complex queries, reliability |
| Analytics | Elasticsearch, Data Warehouse | Full-text search, time-series analysis |
| Streaming | Kafka, AWS Kinesis | Event processing, real-time |
| Observability | Prometheus, ELK Stack, Jaeger | Metrics, logs, traces |

## Lessons Learned

1. **Premature optimization kills projects**: Start simple, measure, then optimize
2. **Consistency is hard**: Eventually consistent systems are tricky to reason about
3. **Monitoring is non-negotiable**: You can't fix what you can't see
4. **Failure is not rare**: Plan for it, test it, automate recovery
5. **Cost grows with complexity**: Each component adds operational overhead

## Related Topics

- Database design and optimization
- Distributed consensus algorithms
- Load balancing strategies
- Caching mechanisms and patterns
- Monitoring and alerting systems
- Security and compliance


## Back-of-the-Envelope Calculations

**System Load Estimation:**
- 1M daily active users × 10 requests/day = 10M requests/day
- Peak QPS = 10M / 86400 × 3 (peak factor) ≈ 350 QPS
- API server capacity: 1000 QPS/server → 1 server sufficient at peak
- With 2x redundancy: 2 servers minimum

**Storage Estimation:**
- 1M users × 10KB average data = 10GB structured data
- Annual growth: 10GB × 365 = 3.65TB/year
- With 3x replication: 11TB/year
- SSD cost ($0.10/GB): $1,100/year

**Bandwidth:**
- 350 QPS × 10KB response = 3.5MB/sec outbound
- Monthly egress: 3.5MB × 86400 × 30 = 9TB/month

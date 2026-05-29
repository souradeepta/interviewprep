# Database Sharding

**Level:** L3-L5+
**Time to read:** ~30 min

## Problem Statement

A single relational database node can typically handle 10K-50K QPS with ~1TB of hot data before
hitting CPU, memory, or I/O ceilings. As the user base grows to hundreds of millions, a monolithic
database becomes a single point of failure and a performance bottleneck that no vertical scaling can
fix. Database sharding distributes both data and query load across multiple independent database
nodes, enabling horizontal scalability without redesigning the application from scratch.

The challenge is not merely splitting data—it is doing so in a way that keeps most queries
single-shard (no cross-shard joins), allows the cluster to grow without full data migration, and
maintains operational simplicity when individual shards fail.

## Functional Requirements

- Store and retrieve user/entity records by primary key (point lookups)
- Support range queries within a single shard
- Add new shards without downtime (online resharding)
- Route queries to the correct shard transparently
- Handle shard failure with automatic failover

## Non-Functional Requirements

- **Scale:** 10B rows total, 50K writes/sec, 500K reads/sec across all shards
- **Latency:** P99 < 10 ms for point lookups, P99 < 50 ms for range queries
- **Availability:** 99.99% (52 min downtime/year); each shard has replicas
- **Consistency:** Strong within a shard (ACID); eventual across shards for aggregates

---

## Tier 1: L3-L4 Design (the basic interview answer)

### Back-of-Envelope

```
Users:            1B registered, 100M DAU
Write QPS:        100M DAU * 5 writes/day / 86400 sec  ≈  5,800 writes/sec   → round to 10K
Read QPS:         100M DAU * 50 reads/day / 86400 sec  ≈  58K reads/sec      → round to 100K
Row size:         ~1 KB (user record with metadata)
Storage/day:      10K writes/sec * 86400 * 1 KB         ≈  864 GB/day
Total storage:    3-year retention → 864 * 365 * 3      ≈  950 TB

Single DB node:   handles ~10K QPS, ~5 TB hot data
Shards needed:    100K reads / 10K per node             = 10 read shards (round to 16 for headroom)
Replication:      1 primary + 2 replicas per shard      = 48 nodes total
```

### Architecture Diagram

```
         Client / Application Layer
                    |
         +----------+----------+
         |    Shard Router     |   ← reads shard map, hashes key
         |   (stateless app)   |
         +----+----+----+------+
              |    |    |
     +--------+  +-+--+  +--------+
     | Shard 0 |  |Shard N|  |Shard15|
     | Primary |  |Primary|  |Primary|
     +----+----+  +-------+  +---+----+
          |                      |
     +----+----+            +----+----+
     |Replica 1|            |Replica 1|
     |Replica 2|            |Replica 2|
     +---------+            +---------+

Shard Map (stored in ZooKeeper / etcd):
  shard_id → [host:port primary, host:port replica1, ...]
  key_range or hash_range → shard_id
```

### Data Model

```sql
-- Shard map table (stored centrally, rarely changes)
CREATE TABLE shard_map (
    shard_id      INT PRIMARY KEY,
    range_start   BIGINT NOT NULL,   -- inclusive (hash or range key)
    range_end     BIGINT NOT NULL,   -- exclusive
    primary_host  VARCHAR(255) NOT NULL,
    replica_hosts TEXT NOT NULL,     -- JSON array
    status        ENUM('active','draining','offline') DEFAULT 'active',
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Virtual node table (consistent hashing with vnodes)
CREATE TABLE vnode_map (
    vnode_id      BIGINT PRIMARY KEY,  -- position on hash ring (0..2^32)
    shard_id      INT NOT NULL,
    FOREIGN KEY (shard_id) REFERENCES shard_map(shard_id)
);

-- Example: users table (replicated on each shard — only owns its partition)
CREATE TABLE users (
    user_id       BIGINT PRIMARY KEY,
    username      VARCHAR(128) NOT NULL UNIQUE,
    email         VARCHAR(255) NOT NULL,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata      JSON
);
CREATE INDEX idx_users_created ON users(created_at);
```

### API Design

```
# Shard-aware client API (internal SDK)

GET  /data/users/{user_id}
  → routes to shard = hash(user_id) % N
  Response: 200 { user_id, username, email, created_at }

POST /data/users
  Body: { username, email }
  → picks shard via consistent hash of generated user_id
  Response: 201 { user_id }

PUT  /data/users/{user_id}
  Body: { field: value, ... }
  → routes to owning shard
  Response: 200 { updated: true }

DELETE /data/users/{user_id}
  → routes to owning shard
  Response: 204

# Admin / Resharding API
POST /admin/shards
  Body: { new_shard_id, range_start, range_end, primary_host, replica_hosts }
  → adds shard and begins data migration

GET  /admin/shards/{shard_id}/status
  Response: { rows_migrated, rows_total, lag_seconds }
```

### Basic Scaling

- **Hash sharding:** `shard_id = hash(primary_key) % N` — even distribution, prevents hot ranges
- **Read replicas per shard:** 2 replicas per primary; route reads to replicas, writes to primary
- **Connection pooling:** PgBouncer/ProxySQL per shard to limit DB connections (≤200 per node)
- **Shard key selection:** Choose the highest-cardinality field that appears in all queries;
  avoid sharding on low-cardinality fields (e.g., country_code → guaranteed hot shards)

---

## Tier 2: L5+ Design (the staff interview answer)

### Capacity Planning (Real Numbers)

```
Per shard node (Primary):
  CPU:    32 vCPUs; at 50K read QPS / 16 shards = 3,125 reads/sec/shard  → 30% CPU
  RAM:    256 GB; hot working set per shard = 950TB / 16 ≈ 59 TB total
          Buffer pool: 60 GB (caches ~1M most-accessed rows) + 64 GB OS
  Disk:   4 TB NVMe SSD (3× data for WAL + indexes + working space)
  Net:    25 Gbps; 10K writes/sec * 16KB avg tx = 160 MB/sec well within limit

Replica lag budget:
  Target: < 50 ms replication lag
  Achieved via: semi-sync replication (1 ack before commit) on replica 1
                async replication on replica 2 (read-scale, stale reads OK)

Shard map cache:
  All app nodes cache shard map in memory; TTL = 5 min
  ZooKeeper watch pushes invalidation on shard topology change
  Cold start: app fetches full map (< 1 MB) at startup
```

### Failure Modes

```
FAILURE: Primary shard goes down
  Detection:  Health check every 2 sec; 3 missed = declare failure
  Mitigation: Replica 1 promoted via Orchestrator/Patroni within 10-30 sec
  Client:     Retries with exponential backoff (3 attempts, 100ms/200ms/400ms)
  Data risk:  Semi-sync ensures 0 committed-but-lost writes on async replica

FAILURE: Shard map becomes stale (app routes to wrong shard)
  Symptom:    DB returns "key not found" or wrong data
  Mitigation: Shard returns 301-style redirect hint ("owner is shard 7")
              App refreshes shard map and retries once
  Prevention: Version-stamp on shard map; reject queries if version too old

FAILURE: Hot shard (uneven load)
  Detection:  QPS per shard monitored; alert at 2× average
  Mitigation: Split hot shard: migrate top 50% of hash range to new shard
              Use virtual nodes (vnodes) to make splits non-disruptive
  Short-term: Route hot-key reads to replicas (read-scaling)

FAILURE: Cross-shard operation partially fails (saga step fails)
  Mitigation: Compensating transaction logged before step execution
              Saga coordinator retries with idempotency key
              If unrecoverable: mark saga as failed, alert, manual resolution
```

### Consistency Boundaries

```
STRONG consistency (within shard):
  All writes go to primary; reads from primary or semi-sync replica
  Ensures read-your-writes for single-entity operations

EVENTUAL consistency (cross-shard aggregates):
  Global COUNT(*), SUM() queries run on replicas with accepted staleness
  Reported with timestamp: "count as of T-30s"

CONFLICT RESOLUTION (split-brain after network partition):
  Fencing token (monotonic epoch) issued at promotion time
  Old primary's writes rejected by replicas if epoch < current
  Quorum-based: write succeeds only if primary + at least 1 replica acknowledge

CROSS-SHARD TRANSACTIONS:
  Option A: 2PC (Two-Phase Commit)
    - Coordinator locks rows on all shards (prepare phase)
    - Commits if all ACK, aborts if any NACK
    - Problem: coordinator failure leaves shards locked (use timeout + rollback)
  Option B: Saga pattern (preferred at scale)
    - Each shard operation is local ACID
    - On failure: execute compensating transactions in reverse order
    - No distributed lock; better availability, eventual consistency
```

### Cost Model

```
Infrastructure (AWS us-east-1 approximate):
  Per shard: r6g.8xlarge primary ($1.60/hr) + 2× r6g.4xlarge replicas ($0.80/hr each)
  16 shards: 16 * ($1.60 + 2 * $0.80) * 8760 hr/yr  = $449K/yr compute
  Storage:   950 TB / 16 shards = 60 TB/shard → io2 SSD $0.125/GB/month
             16 * 60 TB * 12 months * $125          = $1.44M/yr storage
  Network:   ~50 TB/month cross-AZ replication * $0.01/GB * 12 = $6K/yr

Total:      ~$1.9M/yr for 1B users
Per user:   $0.0019/user/month  ($1.90/1000 users/month)

Optimization levers:
  1. Tiered storage: move cold rows (>90 days) to S3 via Aurora S3 export → 70% storage cost cut
  2. Reserved instances: 1-yr commit cuts compute by 40%  → saves $180K/yr
  3. Read replica auto-scaling: scale replicas down during off-peak (18:00-08:00 UTC)
```

---

## Trade-off Comparison

| Approach | Pros | Cons | Best For |
|----------|------|------|----------|
| Hash sharding | Even distribution, no hot ranges | Cross-range queries span all shards; resharding rehashes | Point lookups, uniform key distribution |
| Range sharding | Range queries stay on 1 shard; easy to reason | Sequential inserts → hot shard at range boundary | Time-series, ordered data, range scans |
| Directory-based sharding | Fully flexible mapping; easy to move any key | Lookup table becomes bottleneck; single point of failure if not replicated | Migrating existing data; irregular distributions |
| Consistent hashing + vnodes | Minimal data movement on add/remove; no full rehash | Slightly more complex routing; vnode count tuning needed | Elastic clusters, frequent shard add/remove |

## Follow-up Questions (escalating difficulty)

1. **(L3)** What is the difference between horizontal and vertical sharding?
   → Vertical splits by column (put rarely-used columns in separate table/DB). Horizontal splits by
   row (each shard holds a subset of rows). Horizontal sharding is what most people mean by
   "sharding."

2. **(L3)** Why not just shard on user_id modulo N?
   → Modulo sharding requires a full data migration every time N changes. Consistent hashing only
   moves 1/N of data when adding one shard.

3. **(L4)** How do you handle a query that needs data from multiple shards (e.g., "find all users
   created in the last 24 hours")?
   → Scatter-gather: send the query to all shards in parallel, merge results in the application
   layer, then sort/paginate. Accept higher latency for these queries or maintain a separate
   secondary index (e.g., Elasticsearch) for cross-shard search patterns.

4. **(L4)** How do you rebalance when one shard becomes a hot spot?
   → With vnodes: move some virtual nodes from the hot shard to a new shard. Data migration
   happens in the background while the shard still serves traffic. The shard map is updated
   atomically once migration completes.

5. **(L5)** Describe the 2PC protocol for a cross-shard transfer and its failure modes.
   → Phase 1 (Prepare): coordinator asks each shard to lock resources and vote yes/no. Phase 2
   (Commit/Abort): if all vote yes, coordinator sends commit; any no → abort. Failure: if
   coordinator crashes between phases, shards are locked indefinitely. Mitigation: coordinator
   writes decision to durable log before phase 2; replayed on restart.

6. **(L5)** How would you implement exactly-once semantics for writes across shards?
   → Idempotency key stored with each write. Before executing, check if idempotency_key already
   exists in the target shard. If yes, return cached result. Key expires after dedup window
   (typically 24 hours). For cross-shard, use saga with idempotency keys at each step.

7. **(L5+)** How does a Saga differ from 2PC and when do you choose each?
   → 2PC provides strong atomicity but holds locks during the protocol — bad for high-latency or
   unreliable participants. Saga chains local ACID transactions with compensating rollbacks; no
   locks held across steps, so it scales better. Choose 2PC when you need strict atomicity and all
   participants are fast and reliable (same datacenter). Choose Saga when participants are external
   services or when availability > strict consistency.

## Anti-patterns / Things NOT to Say

- **"Just use a UUID as the shard key"** — Random UUIDs distribute well but make range queries
  impossible and can cause cache thrashing because adjacent keys map to random shards. Use a
  time-sortable ID (ULID, Snowflake) or a domain-meaningful key.
- **"Shard on a low-cardinality field like country_code"** — With 50 countries, you get 50 shards
  max, and the US shard will get 40%+ of traffic—a permanent hot shard with no easy fix.
- **"We'll add cross-shard foreign keys"** — Foreign keys only work within a single DB engine.
  Cross-shard referential integrity must be enforced in application logic; relying on DB-level
  constraints will break silently when keys span shards.
- **"Let's shard when we need it"** — Retrofitting sharding onto an existing schema is one of the
  hardest migrations. Plan the shard key in the initial data model; adding it later requires
  backfilling all records and changing every query.
- **"We don't need to handle hot shards; consistent hashing prevents them"** — Consistent hashing
  prevents structural hot spots, but viral content (a celebrity's record, a trending item_id) still
  creates logical hot spots. Mitigate with application-level caching (Redis) in front of hot keys.

## Python Implementation (sketch)

```python
import hashlib
import bisect
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class ShardNode:
    shard_id: int
    host: str
    port: int = 5432

class ConsistentHashRouter:
    """Consistent hash ring with virtual nodes for shard routing."""

    def __init__(self, vnodes_per_shard: int = 150):
        self.vnodes_per_shard = vnodes_per_shard
        self._ring: list[int] = []                 # sorted hash positions
        self._shard_map: dict[int, ShardNode] = {}  # hash_pos -> shard

    def add_shard(self, node: ShardNode) -> None:
        for i in range(self.vnodes_per_shard):
            key = f"{node.host}:{node.port}#{i}".encode()
            pos = int(hashlib.md5(key).hexdigest(), 16)
            bisect.insort(self._ring, pos)
            self._shard_map[pos] = node

    def remove_shard(self, node: ShardNode) -> None:
        for i in range(self.vnodes_per_shard):
            key = f"{node.host}:{node.port}#{i}".encode()
            pos = int(hashlib.md5(key).hexdigest(), 16)
            self._ring.remove(pos)
            del self._shard_map[pos]

    def get_shard(self, entity_key: str) -> Optional[ShardNode]:
        if not self._ring:
            return None
        h = int(hashlib.md5(entity_key.encode()).hexdigest(), 16)
        idx = bisect.bisect(self._ring, h) % len(self._ring)
        return self._shard_map[self._ring[idx]]

    def distribution_stats(self) -> dict[int, int]:
        """Count vnodes per shard (should be roughly equal)."""
        counts: dict[int, int] = {}
        for node in self._shard_map.values():
            counts[node.shard_id] = counts.get(node.shard_id, 0) + 1
        return counts


# Usage
router = ConsistentHashRouter(vnodes_per_shard=150)
for i, host in enumerate(["db-shard-0", "db-shard-1", "db-shard-2", "db-shard-3"]):
    router.add_shard(ShardNode(shard_id=i, host=host))

user_id = "user_98765432"
shard = router.get_shard(user_id)
print(f"Route {user_id} → shard {shard.shard_id} @ {shard.host}")
# Route user_98765432 → shard 2 @ db-shard-2

print(router.distribution_stats())
# {0: 150, 1: 150, 2: 150, 3: 150} — ideal
```

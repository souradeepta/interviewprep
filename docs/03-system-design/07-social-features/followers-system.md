# Followers System

**Level:** L3-L5+
**Time to read:** ~30 min

## Problem Statement

Social platforms need a follow/unfollow mechanism that tracks directed relationships between users:
Alice follows Bob, but Bob may or may not follow Alice (asymmetric graph). The system must answer
queries like "who does Alice follow?", "who follows Bob?", "does Alice follow Bob?", and "what is
Bob's follower count?" for 1 billion users where celebrities can have 100 million followers.

The challenge is that the follower graph is highly skewed: 99% of users have < 1,000 followers
(easy), but 0.001% have millions (a write amplification and hot-key nightmare). The data model and
serving strategy must handle both tails efficiently.

## Functional Requirements

- Follow a user (create a directed follow relationship)
- Unfollow a user (remove the relationship)
- List followers of a user (paginated, sorted by most-recently-followed)
- List users that a user follows (following list, paginated)
- Check if user A follows user B (is_following? query)
- Get follower count for a user

## Non-Functional Requirements

- **Scale:** 1B users; avg 500 followers/user; top celebrities: 100M followers;
  1B follow events/day (11,574/sec); 10B follow-check queries/day (115K/sec)
- **Latency:** P99 < 20 ms for is_following? check; P99 < 50 ms for paginated follower list
- **Availability:** 99.9%; eventual consistency for count approximation acceptable
- **Consistency:** Strong for is_following? check; eventual (±5%) for follower counts

---

## Tier 1: L3-L4 Design (the basic interview answer)

### Back-of-Envelope

```
Users:           1B
Avg followers:   500 per user
Total edges:     1B users * 500 avg = 500B follow relationships
Edge row size:   16 bytes (follower_id int64 + followee_id int64) + 8 bytes created_at = 24 bytes
Total raw:       500B * 24 bytes = 12 TB (before indexes and overhead)
With indexes:    ~40 TB total (forward index + reverse index)

Sharding:        40 TB / 4 TB per node = 10+ nodes; use 20 nodes for headroom
Follow QPS:      11,574 writes/sec (inserts into follows table)
Is-following QPS: 115,000 reads/sec (point lookup by follower_id + followee_id)

Cache size for hot follows:
  Top 1M most-followed accounts * 100 byte Redis SET entry each ≈ 100 MB (trivial)
  Hot followers lists (top 10K accounts): 10K * 10K followers * 24 bytes = 2.4 GB in Redis
```

### Architecture Diagram

```
  Client: "Does user_42 follow user_99?"  /  "Get followers of user_99"
        |
  +-----v-----------+
  | Follow API      |  ← stateless, handles auth
  +-----+-----------+
        |                     Cache Layer
        |            +--------+----------+
        |            | Redis  |  Cache   |
        |            | hot follower sets |
        |            | HLL for counts    |
        |            +--------+----------+
        |                     |
  +-----v-------------------v-+
  | Follows DB (Cassandra /   |
  |  Postgres sharded)        |
  |                           |
  | Table: follows            |
  |   (follower_id, followee_id, created_at)
  |                           |
  | Index: by followee_id     |  ← "who follows me?"
  | Index: by follower_id     |  ← "who do I follow?"
  +---------------------------+

Fan-out on Write (for feed generation — separate concern):
  Follow event → Kafka → Feed Service → pre-populate follower feeds
  (Not needed for followers system itself, but common follow-up)
```

### Data Model

```sql
-- Follows table (core relationship store)
-- Sharded by follower_id (primary access pattern: "who do I follow?")
CREATE TABLE follows (
    follower_id   BIGINT NOT NULL,
    followee_id   BIGINT NOT NULL,
    created_at    TIMESTAMP NOT NULL DEFAULT NOW(),
    PRIMARY KEY (follower_id, followee_id),
    INDEX idx_followee (followee_id, follower_id, created_at)  -- "who follows me?"
);
-- Note: For Cassandra, this would be TWO separate tables (one for each query direction)

-- Follower counts (materialized, eventually consistent)
CREATE TABLE follower_counts (
    user_id           BIGINT PRIMARY KEY,
    follower_count    BIGINT NOT NULL DEFAULT 0,
    following_count   BIGINT NOT NULL DEFAULT 0,
    updated_at        TIMESTAMP NOT NULL DEFAULT NOW()
);

-- For celebrity accounts: Redis SET (hot follower list)
-- Key: followers:{user_id}       → Redis ZSET scored by follow timestamp
-- Key: following:{user_id}       → Redis ZSET scored by follow timestamp
-- Key: follower_count:{user_id}  → Redis string (HLL or exact count)
```

### API Design

```
# Follow a user
POST /follows
  Body: { follower_id: 42, followee_id: 99 }
  Response: 201 { followed: true, followee_follower_count: 1_234_567 }

# Unfollow a user
DELETE /follows
  Body: { follower_id: 42, followee_id: 99 }
  Response: 200 { unfollowed: true }

# Check if following (is_following?)
GET /follows/check?follower_id=42&followee_id=99
  Response: 200 { is_following: true, followed_at: "2024-01-15T12:00:00Z" }

# Get followers of a user (paginated)
GET /users/{user_id}/followers?limit=50&before_cursor=<cursor>
  Response: 200 {
    followers: [{ user_id, display_name, followed_at }, ...],
    total_count: 1_234_567,
    next_cursor: "base64_encoded_follow_timestamp_and_id",
    has_more: true
  }

# Get users that a user follows
GET /users/{user_id}/following?limit=50&before_cursor=<cursor>
  Response: 200 { following: [...], total_count: 892, next_cursor: "..." }

# Get follower/following counts
GET /users/{user_id}/counts
  Response: 200 { follower_count: 1_234_567, following_count: 892 }
```

### Basic Scaling

- **Dual-index:** Two separate lookup paths: (follower_id, followee_id) for "do I follow X?" and
  (followee_id, follower_id) for "who follows me?" — in SQL, two indexes; in Cassandra, two tables
- **Pagination cursor:** Use (created_at, followee_id) as composite cursor; avoid OFFSET (slow for
  large pages); encode cursor as opaque base64 token
- **Count cache:** Follower counts in Redis (INCR/DECR on follow/unfollow); async sync to DB every
  minute; HyperLogLog for approximate counts if exact count performance becomes a bottleneck
- **Partial results for celebrities:** For accounts with 100M followers, don't materialize full
  list in memory; paginate directly from DB/Cassandra with cursor

---

## Tier 2: L5+ Design (the staff interview answer)

### Capacity Planning (Real Numbers)

```
Cassandra cluster sizing (follows table):
  Total data: 40 TB (500B edges, with indexes)
  Replication: 3× across 3 DCs (for geo-distribution) = 120 TB total raw disk
  Node disk: 4 TB SSD per node → 30 Cassandra nodes
  Reads: 115K is_following checks/sec → primary key lookup = 1 Cassandra read
         30 nodes → 3,833 reads/sec/node → well within Cassandra capacity (>50K/sec/node)
  Writes: 11,574 follow events/sec * 2 (dual-index) = 23,148 rows/sec
         30 nodes → 771 writes/sec/node → trivial for Cassandra

Celebrity follower problem:
  Katy Perry (100M followers) → followee_id=KP row has 100M entries in Cassandra partition
  Cassandra wide rows handle this: single partition key can have billions of clustering keys
  BUT: "get all followers of KP" = read 100M rows = never done; always paginated
  Hot-key on is_following? → 115K checks/sec all for popular accounts → cache mandatory

Redis cache for celebrity checks:
  Top 10K celebrities * 100K most-recent-followers cached in Redis ZSET (scored by follow time)
  10K * 100K * 40 bytes per entry = 40 GB → fits in 3 Redis cluster nodes (32 GB each)
  Cache hit: < 1 ms; Cache miss: Cassandra read < 5 ms; total P99 < 10 ms
```

### Failure Modes

```
FAILURE: Cassandra node goes down (holds some partition data)
  Cassandra with RF=3: reads/writes can proceed with 2/3 nodes (quorum = 2)
  Data rerouted to remaining nodes in < 1 sec (Cassandra gossip protocol)
  Hinted handoff: writes destined for failed node temporarily stored on healthy node
                  delivered when failed node comes back (hint window = 3 hours)

FAILURE: Follow count inconsistency (Redis says 1M, DB says 999K)
  Cause: Redis crash between INCR and DB update; or concurrent follow/unfollow
  Detection: Nightly reconciliation: compare Redis count vs DB COUNT(*)
  Resolution: Overwrite Redis from DB count; accept brief inconsistency
  Alternative: Remove Redis count cache; use HyperLogLog (±0.8% error, never drifts)

FAILURE: Duplicate follow (race: two concurrent follow requests for same pair)
  Prevention: PRIMARY KEY (follower_id, followee_id) unique constraint in DB
              INSERT IF NOT EXISTS in Cassandra (lightweight transaction) for idempotency
  Result: one insert succeeds; other gets "already exists" → return 200 (already following)

FAILURE: Mutual unfollow storm (mass unfollow event — celebrity scandal)
  Symptom: 1M unfollow events/sec hitting Cassandra and Redis simultaneously
  Mitigation: Rate limit: max 10 unfollows/sec per user (client + server)
              Queue unfollow events; process asynchronously; show "unfollow pending" state
              Redis DECR for immediate count update; Cassandra delete async
```

### Consistency Boundaries

```
IS-FOLLOWING CHECK (strong consistency required):
  Write: INSERT into Cassandra with LOCAL_QUORUM (2/3 nodes ACK before returning)
  Read:  SELECT with LOCAL_QUORUM → reads from 2/3 nodes, takes latest value
  Result: read-your-writes guaranteed for same DC; cross-DC: 1-5 sec eventual

FOLLOWER COUNTS (eventual consistency acceptable):
  Exact count: SELECT COUNT(*) from Cassandra = table scan for 100M rows = minutes → unusable
  Approximate: Redis INCR/DECR on follow/unfollow; sync to DB asynchronously
  HyperLogLog: PFADD follower_ids → PFCOUNT gives ±0.8% error in O(1) space (12 KB per user)
  Display: "1.2M followers" (rounded to 2 sig figs) — users don't care about exact count

GRAPH PARTITIONING CONSISTENCY:
  Follow relationship stored twice (by follower, by followee) for two access patterns
  If write to table-1 succeeds but table-2 fails: inconsistent state
  Prevention: use Cassandra batch (LOGGED BATCH) to write both rows atomically within a partition
  OR: accept brief inconsistency; async worker reconciles failed writes from Kafka event log
```

### Cost Model

```
Cassandra (30 nodes, i3en.3xlarge, 7.5 TB NVMe each):
  30 * $1.08/hr * 8760 = $283,824/yr

Redis cluster (3 nodes, r6g.2xlarge for 64 GB RAM):
  3 * $0.485/hr * 8760 = $12,741/yr

Kafka (follow events → feed service, analytics):
  3-broker MSK: ~$15,000/yr

App servers (ECS, 20× c6g.xlarge):
  20 * $0.136/hr * 8760 = $23,827/yr

Total: ~$335K/yr for 1B users
Per-user: $0.000335/user/year = $0.000028/user/month (essentially free per user)

At 100M users (earlier stage):
  Cassandra: 3 nodes (enough for 4 TB data): $32K/yr
  Total: ~$75K/yr
  Per user: $0.00075/user/year
```

---

## Trade-off Comparison

| Approach | Pros | Cons | Best For |
|----------|------|------|----------|
| SQL with two indexes (Postgres) | Simple; ACID; familiar tooling; easy to query | Doesn't scale past ~100M edges per node; index size; slow range scans on large follower lists | Early-stage platforms, < 100M total follow relationships |
| Cassandra wide rows (two tables) | Scales to trillions of edges; excellent range scan; tunable consistency | Eventual consistency; complex data model (two tables); no joins | Twitter/Instagram scale; 500B+ edges; geo-distributed |
| Redis ZSET (follower set in memory) | Sub-millisecond reads; sorted by time; easy ZREVRANGE pagination | Memory-limited; 100M followers × 40 bytes = 4 GB per celebrity (expensive); no persistence | Caching hot follower lists for celebrities; real-time counts |
| Graph database (Neo4j, Amazon Neptune) | Native graph queries; mutual friends, recommendations easy | Doesn't scale to billions of edges on single instance; operational complexity | Small graphs; social analytics; recommendation traversals |

## Follow-up Questions (escalating difficulty)

1. **(L3)** How do you store a directed follow relationship in a database?
   → A row in a `follows` table with `(follower_id, followee_id, created_at)`. The primary key
   is the composite `(follower_id, followee_id)` to prevent duplicates and enable fast lookup.
   Add a secondary index on `(followee_id, follower_id)` to answer "who follows me?" efficiently.

2. **(L3)** How do you check if user A follows user B efficiently?
   → Point lookup: `SELECT 1 FROM follows WHERE follower_id = A AND followee_id = B LIMIT 1`.
   With the composite primary key, this is an O(1) B-tree lookup — microseconds. Cache frequent
   pairs in Redis (e.g., `GET follows:{A}:{B}` → "1" or "0", TTL 5 min).

3. **(L4)** How do you paginate through 100M followers efficiently without using OFFSET?
   → Cursor-based pagination: the cursor encodes the last-seen `(created_at, follower_id)`. Next
   page query: `WHERE followee_id = ? AND (created_at, follower_id) < (cursor_ts, cursor_id)
   ORDER BY created_at DESC LIMIT 50`. This is a seek predicate — constant time regardless of
   page number, unlike OFFSET which gets slower with each page.

4. **(L4)** How do you handle the follower count for a celebrity with 100M followers without doing
   a COUNT(*) on every request?
   → Materialized counter: maintain a `follower_counts` row per user, incremented on follow and
   decremented on unfollow. Store in Redis with INCR/DECR for sub-millisecond reads. Async
   sync to DB every minute. Periodically reconcile Redis count vs DB COUNT(*) for drift detection.

5. **(L5)** Why does Twitter use two Cassandra tables instead of one table with two indexes?
   → Cassandra's data model requires the partition key to be known for efficient reads. A single
   table partitioned by follower_id is fast for "who do I follow?" but requires a full cluster
   scan for "who follows me?" (unknown partition). Two separate tables: one partitioned by
   follower_id, one by followee_id — each query uses its native partition key. Write amplification
   (2× writes) is the trade-off for 2× read efficiency.

6. **(L5)** How would you compute "mutual follows" (does A follow B AND does B follow A)?
   → Two parallel reads: `is_following(A, B)` and `is_following(B, A)`. Both are O(1) point
   lookups. If both return true → mutual. At scale, cache mutual status in Redis
   `GET mutual:{min(A,B)}:{max(A,B)}`, invalidate on follow/unfollow for either user.

7. **(L5+)** How do you partition the follower graph for geo-distribution across 3 datacenters?
   → Cassandra's native multi-DC replication (NetworkTopologyStrategy): each DC gets RF=1 or RF=3.
   Writes use LOCAL_QUORUM (2 local nodes ACK → return success; async replication to other DCs).
   Reads use LOCAL_QUORUM (served from local DC, < 5 ms). Cross-DC replication lag: 50-200 ms.
   Trade-off: if DC-A is partitioned, DC-B and DC-C can still serve reads but with potentially
   stale follower data until the partition heals.

## Anti-patterns / Things NOT to Say

- **"Store followers as a JSON array column in the users table"** — A JSON array of 100M follower
  IDs in one column is 800 MB per celebrity row, can't be indexed or paginated efficiently, and
  requires reading/writing the entire array on every follow/unfollow. Use a proper relationship
  table.
- **"Use OFFSET for pagination (OFFSET 1000000 LIMIT 50)"** — OFFSET N scans and discards N rows
  before returning results; at page 20,000 (1M offset) it reads 1M rows to return 50. Always use
  cursor-based pagination (WHERE created_at < cursor).
- **"SELECT COUNT(*) FROM follows WHERE followee_id = ?  for real-time count"** — For a celebrity
  with 100M followers, this is a 100M-row scan on every profile view. Use a materialized counter
  (INCR in Redis + async DB sync).
- **"Cassandra handles celebrity hot keys automatically"** — Cassandra distributes data by
  partition key. The celebrity's partition (all 100M followers on one logical partition) can still
  overwhelm a single Cassandra coordinator node for writes. Mitigate with write rate limiting and
  batching for follow events against celebrity accounts.
- **"Fanout on write for celebrities is fine"** — If you write a new post to all 100M followers'
  feeds synchronously, that's 100M writes per post. Fanout on write works for normal users; use
  fanout on read (pull model) for celebrities above a follower threshold (Twitter's hybrid model).

## Python Implementation (sketch)

```python
import time
from dataclasses import dataclass, field
from collections import defaultdict

@dataclass
class FollowEdge:
    follower_id: int
    followee_id: int
    created_at: float = field(default_factory=time.time)

class FollowerGraph:
    """In-memory follower graph with dual-index and cursor pagination."""

    def __init__(self):
        # followee_id → list of (created_at, follower_id) — sorted descending
        self._followers: dict[int, list[tuple[float, int]]] = defaultdict(list)
        # follower_id → set of followee_ids (for fast is_following check)
        self._following: dict[int, set[int]] = defaultdict(set)
        # follower counts
        self._follower_count: dict[int, int] = defaultdict(int)

    def follow(self, follower_id: int, followee_id: int) -> bool:
        if follower_id == followee_id:
            return False
        if followee_id in self._following[follower_id]:
            return False  # already following (idempotent)

        ts = time.time()
        self._following[follower_id].add(followee_id)
        self._followers[followee_id].append((ts, follower_id))
        self._followers[followee_id].sort(reverse=True)  # sorted by recency
        self._follower_count[followee_id] += 1
        return True

    def unfollow(self, follower_id: int, followee_id: int) -> bool:
        if followee_id not in self._following[follower_id]:
            return False
        self._following[follower_id].discard(followee_id)
        self._followers[followee_id] = [
            (ts, fid) for ts, fid in self._followers[followee_id]
            if fid != follower_id
        ]
        self._follower_count[followee_id] = max(0, self._follower_count[followee_id] - 1)
        return True

    def is_following(self, follower_id: int, followee_id: int) -> bool:
        return followee_id in self._following[follower_id]

    def get_followers(
        self, user_id: int, limit: int = 50, cursor: float = float("inf")
    ) -> tuple[list[tuple[float, int]], float | None]:
        """Returns (entries, next_cursor) using cursor-based pagination."""
        all_entries = self._followers[user_id]
        page = [(ts, fid) for ts, fid in all_entries if ts < cursor][:limit]
        next_cursor = page[-1][0] if len(page) == limit else None
        return page, next_cursor

    def get_follower_count(self, user_id: int) -> int:
        return self._follower_count[user_id]

    def get_mutual_follows(self, user_a: int, user_b: int) -> bool:
        return self.is_following(user_a, user_b) and self.is_following(user_b, user_a)


# Usage
graph = FollowerGraph()
graph.follow(follower_id=1, followee_id=42)
graph.follow(follower_id=2, followee_id=42)
graph.follow(follower_id=42, followee_id=1)

print(f"User 1 follows 42: {graph.is_following(1, 42)}")   # True
print(f"Mutual 1↔42: {graph.get_mutual_follows(1, 42)}")   # True
print(f"Mutual 2↔42: {graph.get_mutual_follows(2, 42)}")   # False

followers, cursor = graph.get_followers(42, limit=10)
print(f"Followers of 42: {[fid for _, fid in followers]}")  # [2, 1] (most recent first)
print(f"Follower count: {graph.get_follower_count(42)}")    # 2
```

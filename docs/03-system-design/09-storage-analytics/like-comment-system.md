# Like and Comment System

**Level:** L3-L5+
**Time to read:** ~30 min

## Problem Statement

Social platforms process 100M+ likes and millions of comments per day. A like/unlike operation must be idempotent — double-clicking "like" should not double-count. Comment threads can be flat (all top-level) or deeply nested (Reddit-style), and each design has different storage and query trade-offs. Like counts are shown everywhere (feed, detail view, notifications) and must be fast to read, but exact precision matters less than availability.

The core design challenges are: atomic counter updates under high concurrent write load, efficient comment tree traversal, and preventing read-path bottlenecks on viral content with millions of likes.

## Functional Requirements

- Users can like and unlike any content item (post, photo, video, comment)
- Like/unlike is idempotent: liking twice results in one like, unliking unset only if previously liked
- Users can see who liked an item (paginated)
- Users can post top-level comments and reply to existing comments (threaded)
- Comment threads paginated with cursor-based navigation
- Users can flag comments for moderation; moderators can hide or delete flagged comments

## Non-Functional Requirements

- **Scale:** 100M likes/day = 1,157 likes/sec; 10M comments/day = 116 comments/sec
- **Latency:** Like P99 < 100ms; like count read P99 < 20ms; comment load P99 < 200ms
- **Availability:** 99.99% for reads; 99.9% for writes
- **Consistency:** Eventual for like counts (±100 tolerance OK); strong for like existence (did I like this?)

---

## Tier 1: L3-L4 Design (the basic interview answer)

### Back-of-Envelope

```
Likes: 100M/day = 1,157/sec; peak 5x = 5,785/sec
Unlike rate: ~20% of like actions → net new likes: ~927/sec
Comment creation: 116/sec; reply rate: 50% → ~58 replies/sec

Storage (likes table):
  - Each like: content_id (8B) + user_id (8B) + created_at (8B) = 24 bytes
  - 100M likes/day → 2.4 GB/day
  - Annual: 876 GB (manageable in a sharded relational DB)

Comment storage:
  - Each comment: ~500 bytes (content + metadata)
  - 10M/day * 500B = 5 GB/day → 1.8 TB/year

Redis counters:
  - 1B content items * 8 bytes per counter = 8 GB RAM
  - Affordable on r5.xlarge (32 GB RAM); 1 Redis primary + 2 replicas

Virality problem:
  - A viral post receives 1M likes in 1 hour = 277 likes/sec on single key
  - Redis INCR is O(1) and can handle 100K+ ops/sec per shard → no bottleneck
  - DB write: 277 rows/sec per content_id → partition likes table by content_id hash
```

### Architecture Diagram

```
Like/Unlike Flow:
Client
  |
  | POST /likes  or  DELETE /likes
  v
+------------------+
| Like Service     |
+------------------+
  |          |
  | 1. Write  | 2. Update counter
  | to DB     |    in Redis
  v          v
+--------+  +--------+
| Likes  |  | Redis  |
| DB     |  | INCR / |
|(Cassandra)| DECR   |
| or PG  |  | key: like:{content_id}
+--------+  +--------+
  |               |
  | Async         | Async reconciliation
  v               | (every 5 min: Redis vs DB)
+----------------+
| Like Events    |  -> Notification Service
| (Kafka)        |  -> Activity Feed
+----------------+

Comment Thread Flow (flat storage, hierarchy via parent_id):
Client
  |
  | GET /content/{id}/comments
  v
+------------------+
| Comment Service  |
+------------------+
  |
  | SELECT * FROM comments WHERE content_id = X ORDER BY created_at
  | (flat list, client renders tree using parent_id)
  v
+------------------+
| Comments DB      |
| (PostgreSQL,     |
|  sharded by      |
|  content_id)     |
+------------------+
```

### Data Model

```sql
-- Likes: one row per (user, content) pair
CREATE TABLE likes (
    content_id  BIGINT NOT NULL,
    user_id     BIGINT NOT NULL,
    content_type VARCHAR(20) NOT NULL,  -- 'post', 'photo', 'comment'
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (content_id, user_id)
);
-- For "did I like this?" lookup: O(1) by (content_id, user_id)
-- For "who liked this?" query: paginate by (content_id ORDER BY created_at)

-- Like counts cache (Redis): like:{content_id} -> integer
-- DB denormalized counter (for persistence):
CREATE TABLE content_stats (
    content_id    BIGINT PRIMARY KEY,
    content_type  VARCHAR(20),
    like_count    BIGINT DEFAULT 0,
    comment_count BIGINT DEFAULT 0,
    updated_at    TIMESTAMPTZ DEFAULT NOW()
);

-- Comments: flat storage with parent_id for threading
CREATE TABLE comments (
    comment_id  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content_id  BIGINT NOT NULL,
    user_id     BIGINT NOT NULL,
    parent_id   UUID REFERENCES comments(comment_id),  -- NULL = top-level
    body        TEXT NOT NULL,
    status      VARCHAR(20) DEFAULT 'ACTIVE',  -- ACTIVE, HIDDEN, DELETED
    depth       INT DEFAULT 0,   -- 0=top-level, 1=reply, 2=reply-to-reply
    like_count  INT DEFAULT 0,
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    INDEX (content_id, created_at DESC),
    INDEX (parent_id, created_at)
);

-- Moderation flags
CREATE TABLE comment_flags (
    flag_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    comment_id  UUID REFERENCES comments(comment_id),
    flagger_id  BIGINT,
    reason      VARCHAR(50),   -- 'spam', 'harassment', 'misinformation'
    created_at  TIMESTAMPTZ DEFAULT NOW()
);
```

### API Design

```
# Likes

POST /v1/likes
  Body: { content_id: "123", content_type: "post" }
  Response: { liked: true, like_count: 48291 }
  Idempotent: returns 200 if already liked (not 4xx)

DELETE /v1/likes/{content_id}
  Response: { liked: false, like_count: 48290 }
  Idempotent: returns 200 if not previously liked

GET /v1/content/{content_id}/likes?cursor=<...>&limit=20
  Response: { users: [{ user_id, username, avatar_url }], next_cursor: "..." }

GET /v1/content/{content_id}/liked?user_id={user_id}
  Response: { liked: true }  (fast: Redis set member check)

# Comments

POST /v1/content/{content_id}/comments
  Body: { body: "Great photo!", parent_id?: "..." }
  Response: { comment_id, body, user_id, parent_id, created_at }

GET /v1/content/{content_id}/comments?sort=top|new&cursor=<...>&limit=20
  Response: { comments: [...], next_cursor: "..." }
  # Returns flat list; client builds tree from parent_id

DELETE /v1/comments/{comment_id}
  Response: 204 (soft delete: status=DELETED; body replaced with "[deleted]")

POST /v1/comments/{comment_id}/flag
  Body: { reason: "spam" }
  Response: { flag_id, status: "PENDING_REVIEW" }
```

### Basic Scaling

- Keep `likes` table as a pure lookup (content_id, user_id); never store the count there — count comes from Redis or content_stats
- Use Redis INCR/DECR for like counters with lazy write-back to DB every 5 minutes
- Shard likes table by content_id hash to distribute viral content across shards
- Use cursor-based pagination for "who liked this" — avoid OFFSET on large tables (O(n) scan)
- For comments: load top-level comments first; lazy-load replies on expand

---

## Tier 2: L5+ Design (the staff interview answer)

### Capacity Planning (Real Numbers)

```
Redis (like counters + liked-by sets):
  - Counter per content item: 8 bytes * 1B items = 8 GB
  - Liked-by set (compact bloom filter for "did I like?"): avoid storing full sets at scale
    Alternative: store only in DB; Redis used only for counter, not membership check
    For "did I like?": single-row DB lookup with primary key (content_id, user_id) < 5ms
  - Redis cluster: 3 primary nodes r6g.large (16 GB each):
    16 GB * 3 = 48 GB Redis RAM → covers 6B content items at 8 bytes each
    Cost: 3 * $0.166/hr = $0.50/hr = $360/month

Likes DB (Cassandra for like events, PostgreSQL for content_stats):
  - Cassandra: 3-node cluster (RF=3), r5.xlarge (32 GB, 2 TB SSD)
    876 GB/year * 3 RF = 2.6 TB → fits on 2 TB SSD per node (plus compaction headroom)
    Write throughput: 5,785/sec peak → trivial for Cassandra
  - PostgreSQL (content_stats): 2-node (primary + replica)
    Writes: 5,785 rows update/sec → use bulk update via Redis flush every 5 min = 1 write/min per content_id
    Cost: 2 * r5.large $0.126/hr = $181/month

Comments DB (PostgreSQL, sharded by content_id % 4):
  - 10M comments/day * 500 bytes = 5 GB/day; 4 shards = 1.25 GB/shard/day
  - 1-year retention: 4 * 456 GB = 1.8 TB total (4 x db.r5.xlarge with 2 TB storage)
  - Write: 116 comments/sec → trivial
  - Read: viral post with 100K comments → paginate 20 at a time → max 20 rows per query
  - Cost: 4 * $0.248/hr = $716/month
```

### Failure Modes

```
Failure: Redis counter diverges from DB (Redis restart loses recent increments)
  Impact: Like count shows 47,000 but DB has 48,000 actual likes
  Mitigation:
    - Redis counter persistence: AOF (append-only file) with fsync=everysec
      Max data loss: 1 second of INCR operations (~1,157 likes)
    - Reconciliation job: every 5 minutes, COUNT(*) from Cassandra → write to Redis
      Reconciliation overwrites Redis with DB count, correcting drift
    - Acceptable: ±1% count error during Redis outage → show DB count until Redis recovers

Failure: Concurrent like + unlike race condition
  Impact: User A likes (in-flight) and user A unlikes (arrives first) → double-like state
  Mitigation:
    - Idempotency via DB primary key: (content_id, user_id)
    - Like: INSERT INTO likes ... ON CONFLICT DO NOTHING → INCR Redis
    - Unlike: DELETE WHERE content_id=X AND user_id=Y → DECR Redis IF exists
    - Both operations in separate transactions; counter may briefly be off by 1 during race
    - Eventual reconciliation corrects any counter drift

Failure: Viral content creates hot shard in likes DB
  Impact: All 5,785 likes/sec for one piece of content hit one Cassandra partition
  Mitigation:
    - Cassandra partitions by (content_id) → 5,785 writes/sec to one partition → within Cassandra's
      15K writes/sec/partition capacity, but approaches limit at 3x peak
    - Add write buffer: batch like events in Redis list, flush to Cassandra every 100ms in batch
    - Counter sharding (advanced): split counter across N Redis keys:
      like:{content_id}:{random(0,10)} → sum all 10 keys for total
      Eliminates single Redis key hotspot; 10 INCR ops distributed

Failure: Comment flood on viral post (100K comments in 1 hour)
  Impact: Paginated query on comment table returns stale/slow results
  Mitigation:
    - Always use cursor-based pagination: WHERE content_id=X AND created_at < cursor ORDER BY created_at DESC LIMIT 20
      Index on (content_id, created_at) makes this O(log N) regardless of total comments
    - Top comments (sort=top): precompute top-N by like_count in Redis sorted set
      ZADD top_comments:{content_id} score comment_id → ZRANGE for top comments
    - Do NOT use OFFSET: SELECT ... LIMIT 20 OFFSET 100000 scans 100,020 rows → O(N)
```

### Consistency Boundaries

```
Like count: eventual consistency (Redis + DB reconciliation)
  - Between Redis flush and DB update: up to 5 minutes of drift possible
  - Maximum drift: 5 min * 1,157 likes/sec = 347,100 likes
  - For viral posts: displayed count may be significantly behind actual
  - Solution: use Redis as the source of truth for counts (reconcile DB from Redis, not vice versa)
  - Display "47.2K likes" not "47,234 likes" — imprecision is visually acceptable

"Did I like this?": strong consistency required
  - Must be correct to show the correct heart icon state to the user
  - Read from DB primary (content_id, user_id) lookup: <5ms P99
  - Cannot use Redis SET membership — if Redis is down, must fall back to DB
  - Alternatively: read-your-own-writes via sticky session to DB primary for
    1 minute after a like/unlike operation

Comment visibility after moderation:
  - Moderator hides comment (status=HIDDEN) → DB write is immediate
  - Comment still cached in client's session for up to 5 minutes
  - No global cache invalidation needed: comments are not aggressively CDN-cached
  - TTL on comment API response: Cache-Control: max-age=60 (1 minute max staleness)

Comment count accuracy:
  - Same Redis counter pattern as likes
  - Comments are created less frequently (116/sec vs 1,157/sec) → drift is smaller
  - Count displayed: approximate (e.g., "1.2K comments") → imprecision acceptable
```

### Cost Model

```
Redis cluster: $360/month
Cassandra (likes): ~$450/month (3 x r5.xlarge)
PostgreSQL (content_stats): ~$181/month
PostgreSQL (comments, 4 shards): ~$716/month
Compute (Like Service, Comment Service, 10 pods each): ~$200/month

Total: ~$1,907/month

Per 100M likes/day at $1,907/month:
  - Cost per 1M likes: $1,907 / (100 * 30) = $0.64/million likes
  - Cost per comment: $1,907 / (10M * 30) = $0.0064/comment

At Instagram scale (4B likes/day):
  - Scale factor: 40x
  - Estimated cost: 40 * $1,907 = $76K/month
  - Revenue per user: $0.50 ARPU * 1B users = $500M/month
  - Infrastructure as % revenue: 0.015%
```

---

## Trade-off Comparison

| Approach                       | Pros                                                  | Cons                                                   | Best For                              |
|--------------------------------|-------------------------------------------------------|--------------------------------------------------------|---------------------------------------|
| Redis counter + DB reconcile   | Fast reads (<1ms), tolerates DB downtime for counts   | Eventual consistency; drift up to 5 min                | Most platforms (default)              |
| DB-only counter (atomic INCR)  | Always accurate, simpler architecture                 | DB becomes bottleneck at 5K+ like/sec on one item      | Low-scale platforms (<1K likes/sec)   |
| Approximate counter (HLL)      | Constant memory regardless of scale                   | Cannot enumerate likers (who liked?); imprecise        | View counts; not suitable for likes   |
| Flat comment storage           | Simple queries, easy cursor pagination                | Client must build tree; no depth constraint enforcement| Most social platforms (Instagram)     |
| Nested set model (MPTT)        | Fast subtree queries without recursion                | Complex inserts/deletes (rewrite left/right values)    | Rarely changed deep hierarchies       |
| Adjacency list + WITH RECURSIVE| Flexible depth, standard SQL                          | Recursive query expensive for deep trees               | Small comment volumes (<100K per post)|
| Redis sorted set (top comments) | O(log N) top-N retrieval                             | Must keep sorted set in sync with like_count updates   | "Top comments" sort on viral content  |

## Follow-up Questions (escalating difficulty, 7 minimum)

1. **(L3)** Why must like/unlike be idempotent?
   → Double-clicking "like" or mobile network retries should not result in a double-count. Idempotency means: liking when already liked is a no-op (returns current state), and unliking when not liked is a no-op. This is implemented via `INSERT ... ON CONFLICT DO NOTHING` and `DELETE WHERE user_id = X AND content_id = Y` — both are safe to retry.

2. **(L3)** Why use Redis for like counts instead of reading from the database?
   → The like count is read on every feed item render, notifications, and detail views. At 580K views/sec (Instagram scale), reading the count from a DB query per page load would require millions of DB queries per second — far beyond any RDBMS capacity. Redis INCR/GET is O(1) and handles 100K+ ops/sec per shard, serving like counts in <1ms with no DB involvement.

3. **(L4)** Explain the race condition in like/unlike and how to prevent it.
   → If User A rapidly clicks like then unlike, both requests may be in-flight simultaneously. The unlike may arrive at the DB before the like, deleting a row that doesn't exist yet (no-op), and then the like inserts — leaving the user in a "liked" state with an incorrect counter increment. Prevention: (1) Use DB primary key `(content_id, user_id)` — only one row can exist per user/content pair. (2) `INSERT ... ON CONFLICT DO NOTHING` for like ensures no double-insert. (3) Accept ±1 counter drift and rely on reconciliation to correct it. For exact consistency, serialize like/unlike operations per user per content item using a Redis distributed lock (hold lock for <10ms).

4. **(L4)** Compare flat vs. nested comment storage. Which do you recommend and why?
   → Flat storage: all comments in one table with `parent_id` reference. Simple inserts, easy cursor pagination by `created_at`. Client receives the flat list and builds the tree in-memory using `parent_id`. Limitation: unlimited nesting depth is hard to control (user can reply to reply to reply 50 times). Nested Set Model (MPTT): stores left/right tree traversal positions per node. Fast subtree queries (`WHERE left > X AND right < Y`) but every insert requires rewriting many rows' left/right values. Recommendation: flat storage is correct for social platforms. Most platforms limit depth to 2-3 levels (top → reply → reply-to-reply), which flat storage handles trivially with a `depth` column constraint. Reserve MPTT for rarely-changed hierarchies (category trees, org charts).

5. **(L5)** How would you implement the "top comments" sort that shows the most-liked comments first?
   → Use a Redis Sorted Set per content item: `ZADD top_comments:{content_id} score comment_id`. The score is the comment's like_count. When a comment is liked: `ZINCRBY top_comments:{content_id} 1 {comment_id}`. When loading "top" sort: `ZREVRANGE top_comments:{content_id} 0 19` returns the top 20 by score in O(log N). For a viral post with 100K comments, this is far faster than `SELECT ... ORDER BY like_count DESC LIMIT 20` on the DB (which requires a filesort). The sorted set must be populated on first load (cold cache) from the DB: `SELECT comment_id, like_count FROM comments WHERE content_id=X ORDER BY like_count DESC LIMIT 1000`.

6. **(L5)** How do you handle the moderator hide workflow without showing deleted content to users?
   → Use a soft-delete pattern with `status` column: ACTIVE, HIDDEN, DELETED. HIDDEN = visible to moderators and the author but not other users. DELETED = replaced with "[comment deleted]" body for context (replies still make sense). All comment queries add `WHERE status = 'ACTIVE'` filter in the default view. Moderator-authenticated requests use a separate query endpoint without the status filter. API Gateway or service-level auth checks: if the requester is a moderator, add `include_hidden=true` to the backend call. Cascade: if a top-level comment is HIDDEN, its replies are still shown unless individually flagged. Implement a soft-delete instead of hard delete so that moderators can reverse their decision and reinstate a comment.

7. **(L5+)** At 4 billion likes/day (Instagram scale), the likes table grows by 4B rows/day. How do you manage this?
   → Data retention policy: keep only the last 90 days of individual like records (who liked). After 90 days, aggregate: store only the total count in `content_stats`. The "who liked" feature naturally becomes unavailable for old posts (acceptable UX trade-off). This keeps the likes table at 4B * 90 days = 360B rows — 360 billion rows requires Cassandra or BigTable (not PostgreSQL). Shard by `content_id % 1000` across 1000 virtual nodes. For Cassandra: each row is 24 bytes → 360B * 24B = 8.6 TB (within a 10-node cluster's capacity). Additionally: cold-tier archival — move likes older than 30 days to S3 Parquet (used only for analytics, not live "who liked" queries). Hot Cassandra holds only 30 days; cold S3 holds the rest.

## Anti-patterns / Things NOT to Say

- **"Store like count as a column in the content/posts table with an UPDATE counter"** — A single content item receiving 1,000 likes/sec would serialize on the `UPDATE posts SET like_count = like_count + 1` operation, creating a hotspot row that causes lock contention. Use Redis INCR for counters, with periodic DB flush.
- **"Use OFFSET for comment pagination"** — `SELECT ... LIMIT 20 OFFSET 50000` scans and discards 50,000 rows. On a post with 100K comments, loading page 2,500 takes seconds. Always use cursor-based pagination: `WHERE created_at < $cursor AND content_id = X ORDER BY created_at DESC LIMIT 20`. The cursor is the `created_at` timestamp of the last seen comment, making each page load O(log N) via the index.
- **"Count likes with SELECT COUNT(*) FROM likes WHERE content_id = X"** — This full-table scan (or even index scan on a 4B-row table) takes tens of milliseconds and puts read load on the likes DB. At 580K read requests/sec, this would destroy the database. Cache counts in Redis; read counts from cache, not the raw likes table.
- **"Allow unlimited comment nesting depth"** — Unlimited nesting creates UI/UX problems (thread collapses to 1-pixel wide), query problems (recursive CTEs on 50-level deep trees are expensive), and abuse vectors (bots creating deeply nested spam to avoid detection). Always enforce a maximum depth (2-3 levels). Store `depth` column and reject inserts that would exceed `max_depth=3`.

## Python Implementation (sketch)

```python
import uuid
import time
import redis
from typing import Optional, List
from dataclasses import dataclass

r = redis.Redis(host="redis", port=6379, decode_responses=True)

@dataclass
class LikeResult:
    liked: bool
    like_count: int

class LikeService:
    """Handles like/unlike with Redis counter + DB persistence."""

    def __init__(self, db, redis_client: redis.Redis):
        self.db = db
        self.redis = redis_client

    def like(self, user_id: int, content_id: int, content_type: str) -> LikeResult:
        """Idempotent like. Returns current state after operation."""
        # Try to insert; ON CONFLICT DO NOTHING if already liked
        inserted = self._db_insert_like(user_id, content_id, content_type)
        if inserted:
            count = self.redis.incr(f"like:{content_id}")
        else:
            count = int(self.redis.get(f"like:{content_id}") or 0)
        return LikeResult(liked=True, like_count=count)

    def unlike(self, user_id: int, content_id: int) -> LikeResult:
        """Idempotent unlike. Returns current state after operation."""
        deleted = self._db_delete_like(user_id, content_id)
        if deleted:
            count = self.redis.decr(f"like:{content_id}")
            count = max(0, count)  # Never go negative
        else:
            count = int(self.redis.get(f"like:{content_id}") or 0)
        return LikeResult(liked=False, like_count=count)

    def get_count(self, content_id: int) -> int:
        """Fast counter read from Redis."""
        val = self.redis.get(f"like:{content_id}")
        if val is not None:
            return int(val)
        # Cache miss: load from DB and populate Redis
        count = self._db_count_likes(content_id)
        self.redis.set(f"like:{content_id}", count, ex=3600)
        return count

    def did_user_like(self, user_id: int, content_id: int) -> bool:
        """Strong consistency: always read from DB primary."""
        return self._db_check_like(user_id, content_id)

    def get_likers(self, content_id: int, cursor: Optional[str], limit: int = 20) -> dict:
        """Paginated list of users who liked this content."""
        rows = self._db_get_likers(content_id, cursor, limit + 1)
        has_more = len(rows) > limit
        rows = rows[:limit]
        next_cursor = str(rows[-1]["created_at"]) if has_more else None
        return {"users": rows, "next_cursor": next_cursor}

    # DB stub methods (real impl uses psycopg2/asyncpg)
    def _db_insert_like(self, user_id, content_id, content_type) -> bool: return True
    def _db_delete_like(self, user_id, content_id) -> bool: return True
    def _db_count_likes(self, content_id) -> int: return 0
    def _db_check_like(self, user_id, content_id) -> bool: return False
    def _db_get_likers(self, content_id, cursor, limit) -> List[dict]: return []


class CommentService:
    """Handles comment creation and cursor-based pagination."""

    def __init__(self, db):
        self.db = db

    def create_comment(self, user_id: int, content_id: int,
                       body: str, parent_id: Optional[str] = None,
                       max_depth: int = 3) -> dict:
        if parent_id:
            parent = self._get_comment(parent_id)
            if parent["depth"] >= max_depth:
                raise ValueError(f"Maximum comment depth {max_depth} exceeded")
            depth = parent["depth"] + 1
        else:
            depth = 0

        comment_id = str(uuid.uuid4())
        comment = {
            "comment_id": comment_id, "content_id": content_id,
            "user_id": user_id, "parent_id": parent_id,
            "body": body, "depth": depth, "status": "ACTIVE",
            "created_at": time.time()
        }
        self._db_insert(comment)
        return comment

    def get_comments(self, content_id: int, cursor: Optional[float],
                     limit: int = 20, sort: str = "new") -> dict:
        """Cursor-based pagination. cursor = created_at timestamp of last seen comment."""
        if sort == "new":
            rows = self._db_get_by_time(content_id, cursor, limit + 1)
        else:  # top
            rows = self._redis_get_top(content_id, cursor, limit + 1)

        has_more = len(rows) > limit
        rows = rows[:limit]
        next_cursor = rows[-1]["created_at"] if has_more and rows else None
        return {"comments": rows, "next_cursor": next_cursor}

    def _get_comment(self, comment_id): return {"depth": 0}
    def _db_insert(self, comment): pass
    def _db_get_by_time(self, content_id, cursor, limit) -> List[dict]: return []
    def _redis_get_top(self, content_id, cursor, limit) -> List[dict]: return []
```

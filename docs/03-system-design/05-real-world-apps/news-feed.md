# News Feed

**Level:** L3-L5+
**Time to read:** ~30 min

## Problem Statement

A news feed aggregates posts from people and entities a user follows and presents them in ranked
order. This is the core feature of Facebook, Twitter/X, Instagram, and LinkedIn. The engineering
challenge is twofold: at write time, a user's post must reach all their followers' feeds quickly;
at read time, hundreds of millions of simultaneous users must see a personalized, ranked feed with
sub-100ms latency.

The feed problem is a canonical "write amplification vs read amplification" trade-off that comes up
in almost every senior+ interview loop at major tech companies. Knowing when fan-out-on-write breaks
down (celebrity problem) and when fan-out-on-read is too slow — and how the hybrid model solves
both — is the key L5 differentiator.

## Functional Requirements

- Users can create posts (text, images, links)
- Users can follow/unfollow other users
- Each user sees a personalized feed: posts from accounts they follow, ranked by relevance/recency
- Feed loads the latest 20 posts; supports cursor-based pagination for older posts
- Feed updates in near-real-time (new posts appear within seconds)
- Users can like and comment on posts

## Non-Functional Requirements

- **Scale:** 500M DAU; average 200 follows; 5M celebrity accounts (>1M followers); 100M posts/day
- **Latency:** Feed load P99 < 100ms; post publish P99 < 500ms
- **Availability:** 99.99%; feed degradation (stale cache) preferred over downtime
- **Consistency:** Eventual — a new post appearing in followers' feeds within 30s is acceptable

---

## Tier 1: L3-L4 Design (the basic interview answer)

### Back-of-Envelope

```
Post volume:
  100M posts/day ÷ 86400 s/day ≈ 1,157 posts/sec average
  Peak (10× average): 11,570 posts/sec

Fan-out (fan-out-on-write baseline):
  Average user: 200 followers → 1,157 posts/sec × 200 = 231,400 feed writes/sec
  Celebrity (1M followers): 1 post → 1M feed writes in burst

Feed read volume:
  500M DAU opens feed 10×/day = 5B feed reads/day = 57,870 reads/sec average
  Peak: ~500K reads/sec (morning commute spike)

Storage (feed table):
  Each feed entry: 100 bytes (user_id, post_id, author_id, timestamp, score)
  Each user's feed: 1,000 entries (kept in feed, older evicted) = 100KB/user
  500M users × 100KB = 50TB → too large for RAM; tier by hot/cold

Post storage:
  1KB per post average × 100M posts/day = 100 GB/day text
  5 years retention: 100 GB × 365 × 5 = 182 TB
```

### Architecture Diagram

```
[User] → POST /posts ──────────────────────────────────┐
                                                        ▼
                                              ┌──────────────────┐
                                              │   Post Service   │
                                              │  - write to DB   │
                                              │  - enqueue event │
                                              └────────┬─────────┘
                                                       │ publish(post_event)
                                                       ▼
                                             ┌─────────────────┐
                                             │   Message Queue  │
                                             │   (Kafka topic:  │
                                             │   new_posts)     │
                                             └────────┬────────┘
                                                      │
                                          ┌───────────┴───────────┐
                                          ▼                       ▼
                               ┌──────────────────┐  ┌───────────────────────┐
                               │  Fan-out Service │  │  Notification Service │
                               │  - lookup follows│  │  - push to mobile     │
                               │  - write to feed │  └───────────────────────┘
                               │    cache (Redis) │
                               └──────────────────┘

[User] → GET /feed ──────────────────────────────────┐
                                                      ▼
                                          ┌───────────────────────┐
                                          │     Feed Service      │
                                          │  1. Read feed from    │
                                          │     Redis (hot cache) │
                                          │  2. Hydrate post data │
                                          │     (Post Service)    │
                                          │  3. Rank & paginate   │
                                          └───────────────────────┘

Data stores:
  Redis:     feed list per user (ZSET scored by timestamp/rank; top 1000 entries)
  Cassandra: feed archive (older entries beyond Redis window)
  PostgreSQL: users, follows, posts (source of truth)
  S3:         media (images, videos)
```

### Data Model

```sql
-- Users table
CREATE TABLE users (
    user_id     BIGINT PRIMARY KEY,
    username    VARCHAR(64) UNIQUE,
    follower_count INT DEFAULT 0,
    created_at  TIMESTAMP
);

-- Follows graph
CREATE TABLE follows (
    follower_id BIGINT,
    followee_id BIGINT,
    created_at  TIMESTAMP,
    PRIMARY KEY (follower_id, followee_id)
);
CREATE INDEX idx_followee ON follows(followee_id); -- "who follows user X?"

-- Posts table
CREATE TABLE posts (
    post_id     BIGINT PRIMARY KEY,      -- Snowflake ID (timestamp + machine + seq)
    author_id   BIGINT NOT NULL,
    content     TEXT,
    media_urls  TEXT[],
    like_count  INT DEFAULT 0,
    comment_count INT DEFAULT 0,
    created_at  TIMESTAMP NOT NULL
);

-- Feed table (materialized; fan-out-on-write populates this)
CREATE TABLE feed_items (
    user_id     BIGINT,
    post_id     BIGINT,
    author_id   BIGINT,
    score       FLOAT,      -- ranking score (recency + engagement)
    created_at  TIMESTAMP,
    PRIMARY KEY (user_id, score DESC, post_id)
);

-- Redis feed (hot tier — top 1000 per user):
-- Key: "feed:{user_id}"
-- Type: ZSET (score = rank score; member = post_id)
-- ZADD feed:123 1716900000 post_456  -- add post
-- ZREVRANGE feed:123 0 19            -- get top 20
```

### API Design

```
# Post creation
POST /v1/posts
  Body: { "content": "Hello world!", "media_urls": ["s3://..."] }
  Response: { "post_id": "7892043", "author_id": "123", "created_at": "..." }

# Feed retrieval (cursor-based pagination)
GET /v1/feed?limit=20&cursor=<opaque_cursor>
  Response: {
    "posts": [
      { "post_id": "...", "author_id": "...", "content": "...", "created_at": "...",
        "like_count": 42, "author_username": "alice", "author_avatar": "s3://..." },
      ...
    ],
    "next_cursor": "<opaque_cursor>",
    "has_more": true
  }

# Follow/unfollow
POST   /v1/follows   -- Body: { "followee_id": "456" }
DELETE /v1/follows/{followee_id}
```

### Basic Scaling

- **Redis feed cache:** Top 1,000 posts per user stored in a Redis ZSET; feed reads hit cache directly (sub-1ms). Evict oldest entries when count exceeds 1,000.
- **Fan-out worker pool:** Kafka consumer group reads post events; workers look up follower list and batch-write to Redis. Scale horizontally by adding Kafka partitions and worker instances.
- **Pagination via cursor:** Cursor encodes (last_score, last_post_id); avoids OFFSET scans on large feeds. Feed items fetched from Redis (hot) or Cassandra (warm/cold archive).
- **CDN for media:** All images/videos served from S3 + CloudFront; post service stores only S3 URLs.

---

## Tier 2: L5+ Design (the staff interview answer)

### Capacity Planning (Real Numbers)

```
Fan-out write budget:
  Normal users (< 1K followers): fan-out-on-write
    1,157 posts/sec × 200 avg followers = 231,400 Redis ZADD/sec
    Redis: 500K ops/sec per node → 1 Redis cluster handles this easily
  Celebrity problem (>1M followers):
    1 celebrity post → 1M ZADD operations needed in < 30s
    At 500K ops/sec: 2 seconds of Redis capacity just for 1 celebrity
    With 100 active celebrities posting simultaneously: IMPOSSIBLE with fan-out-on-write

  Solution: Fan-out-on-write threshold
    If author.follower_count < 100,000 → fan-out-on-write (pre-compute feed)
    If author.follower_count >= 100,000 → fan-out-on-read (read at request time)

Fan-out-on-read (celebrity posts):
  At feed read time: fetch top-20 posts from each celebrity the user follows
    Typical user follows 3 celebrities: 3 × Cassandra reads → merge + rank
    Latency: 3 parallel reads × 5ms each = 5ms added (parallel)
    Merge celebrity posts with pre-computed feed: in-memory merge in < 1ms

Redis memory budget:
  1,000 feed items/user × 16 bytes (post_id + score) = 16KB/user
  Active users (10% DAU with active Redis entry): 50M × 16KB = 800GB RAM
  Redis cluster: 10 nodes × 128GB = 1.28TB capacity (60% utilized)

Cassandra warm tier:
  Posts older than 48h moved from Redis to Cassandra
  500M users × 1,000 entries × 100 bytes = 50TB Cassandra storage
  Cassandra reads: < 5ms for single-partition lookup
```

### Failure Modes

```
Scenario 1: Fan-out worker lag spikes (queue backs up)
  - Kafka consumer lag grows → new posts appear in feeds minutes later
  - Monitoring: alert on fan-out topic lag > 10,000 events per partition
  - Mitigation: pre-scale fan-out workers during scheduled celebrity events (sports games,
    product launches) using predictive scaling
  - Fallback: if lag > 5min, temporarily switch to fan-out-on-read for all users

Scenario 2: Redis cache eviction storm
  - Memory pressure causes Redis to evict feed entries (LRU)
  - Next read: cache miss → fan-out-on-read from Cassandra (slower path)
  - Mitigation: Redis maxmemory-policy = allkeys-lru; Cassandra as fallback is automatic
  - Limit Redis feed TTL to 48h; evict stale feeds proactively before memory pressure

Scenario 3: Hot follows spike (celebrity with 10M followers announces something)
  - 10M followers all open the app simultaneously (thundering herd)
  - Fan-out-on-read for celebrity: 10M concurrent reads for celebrity's latest post
  - Fix: cache celebrity's feed (top-100 posts) separately in a shared cache
    Key: "celebrity_feed:{author_id}" → shared by all followers
    TTL: 60s (acceptable staleness for celebrity content)
  - Celebrity cache: 5M celebrities × 100 posts × 16 bytes = 8GB (tiny)

Scenario 4: Follow relationship DB overload
  - Feed generation requires follower lookup: SELECT followee_id FROM follows WHERE follower_id = ?
  - At 11,500 posts/sec, 11,500 follower list lookups/sec on PostgreSQL
  - Fix: cache follower lists in Redis with TTL = 5min
    Key: "followers:{user_id}" → List of follower user_ids (serialized)
  - For celebrities: follower list is 1M+ entries; don't cache entire list
    Instead: stream from Cassandra in batches during fan-out worker processing
```

### Consistency Boundaries

```
Feed consistency guarantees:
  Post appears in own feed: immediate (author sees own post via direct DB read)
  Post appears in followers' feeds: eventual (30s SLA under normal load)
  Like/comment count: eventually consistent (counter in Redis, synced to DB every 60s)
  Unfollow effect: fan-out worker skips unfollowed users; stale posts may appear briefly
    Solution: filter out posts from unfollowed users at read time (blacklist in Redis)

Feed ranking:
  Simple: reverse-chronological (sort by post.created_at)
  ML-ranked: score = engagement_model(user_id, post_id, context_features)
    Inference: precomputed offline scores for top-K candidates, re-ranked at serve time
    Latency budget: ranking adds 5-10ms (in-process with pre-fetched features)
  Candidate generation: top-1000 posts from follows (from feed cache) → ML re-rank → top-20

Storage tiering:
  Hot  (< 48h): Redis ZSET — sub-ms read latency; 16KB/user
  Warm (< 30d): Cassandra — 5ms read; 100 bytes/entry × 1000 entries = 100KB/user
  Cold (> 30d): S3 + Athena query — minutes to query; for analytics only, not real-time feed
```

### Cost Model

```
Redis cluster (feed hot tier):
  10 × r6g.4xlarge (128GB RAM, 16 vCPU): $0.702/hr × 10 = $5,054/month

Cassandra cluster (feed warm tier):
  20 × i4i.4xlarge (NVMe, 128GB): $1.196/hr × 20 = $17,222/month
  50TB data + 3× replication = 150TB raw → 20 nodes × 7.5TB = feasible

Kafka (fan-out queue):
  10 brokers × r6i.2xlarge: $0.504/hr × 10 = $3,629/month

Fan-out workers:
  20 × c6i.2xlarge: $0.340/hr × 20 = $4,896/month

PostgreSQL (posts + users source of truth):
  Primary + 2 replicas: db.r6g.4xlarge × 3 = $0.960/hr × 3 = $2,074/month

Total: ~$33K/month for core feed infrastructure at 500M DAU
Per-user cost: $33,000 / 500,000,000 = $0.000066/user/month ≈ $0.001/user/year
Dominant cost: Cassandra (warm tier storage) — optimize with tiered S3 after 7 days
```

---

## Trade-off Comparison

| Approach | Pros | Cons | Best For |
|----------|------|------|----------|
| **Fan-out-on-write** | Feed reads are O(1) from cache; consistent latency | Write amplification; celebrity posts cause fan-out storms | Normal users (< 100K followers) |
| **Fan-out-on-read** | No write amplification; simple write path | Read is expensive (N follows × DB reads); latency spikes | Celebrity accounts (> 100K followers) |
| **Hybrid (threshold-based)** | Balances both; used by Facebook/Twitter | Complex dual-path logic; follower threshold adds code complexity | Large social networks at scale |
| **Reverse-chron only** | Simple; no ML complexity; fast | Low engagement (users miss relevant content); Twitter proved users prefer ranked | Dev/MVP environments |
| **ML-ranked feed** | Higher engagement (+15-30% vs reverse-chron) | ML inference cost; A/B testing complexity; filter bubbles | Production social feeds at scale |

## Follow-up Questions (escalating difficulty)

1. **(L3)** What is the celebrity problem in news feed design?
   → When a user with 1M+ followers posts, fan-out-on-write must write to 1M+ feed caches simultaneously. At 500K Redis ops/sec, that takes 2+ seconds per celebrity post. With 100 celebrities posting in the same minute, the fan-out system saturates. Solution: skip fan-out-on-write for celebrities; merge their posts at read time.

2. **(L3)** Why use a cursor for pagination instead of page number?
   → Page-number pagination (OFFSET N) scans and discards the first N rows on every request. As N grows, performance degrades linearly. Cursor-based pagination encodes the last seen position (e.g., last post_id + score), allowing O(1) index seek regardless of depth.

3. **(L4)** How do you handle a user who unfollows someone? Do their posts disappear from the feed immediately?
   → In fan-out-on-write, posts already written to the feed aren't retroactively removed (that would require scanning and deleting). Solution: at read time, filter out posts from unfollowed authors (maintain an "unfollowed" set per user). This is lazy removal — O(1) per post at read time, avoiding expensive write-time cleanup.

4. **(L4)** How would you add like counts to posts without a hot-key problem?
   → Hot posts receive thousands of likes/sec. A single Redis counter becomes a hot key. Solution: (1) probabilistic counting — don't count every like; sample 1% and multiply by 100 (±10% accuracy, 100× throughput); (2) Redis cluster sharding — use multiple like counter shards and sum at read time; (3) approximate counters — use HyperLogLog for unique liker count.

5. **(L5)** Walk me through the complete lifecycle of a post from a user with 500 followers, including ranking.
   → User creates post → Post Service validates + stores in PostgreSQL (post_id via Snowflake) → publishes post_event to Kafka → Fan-out Service consumes, fetches follower list from cache, batch-writes (post_id, score) to 500 Redis ZSETs. Score = f(recency, author engagement rate, user affinity). At feed read time: Feed Service reads top-1000 from Redis ZSET, fetches post metadata from Post Service (batch), applies lightweight re-ranking (blending celebrity merge + personalization), returns top-20. Total read latency: Redis ~1ms + post hydration ~5ms (batched) + ranking ~2ms = ~8ms.

6. **(L5)** How does Twitter's (X's) ranked timeline work, and what changed when they open-sourced the algorithm?
   → Twitter's ranked feed uses a two-stage pipeline: candidate retrieval (in-network: following graph + social graph; out-of-network: trending + collaborative filtering on 48h engagement) → heavy ranker (neural network scoring engagement probability per (user, tweet) pair) → heuristic filters (de-duplication, diversity, content moderation). The open-sourced code revealed they maintain separate real-time features and precomputed features, merged at serve time.

7. **(L5+)** Design a feed system that handles 500M DAU and can survive a full region failure with < 30 seconds of feed unavailability.
   → Multi-region active-active with Kafka MirrorMaker replicating the post event stream cross-region. Redis feed cache is rebuilt by replaying the last 48h of Kafka events in the DR region. In steady state, DR region keeps its Redis cache warm by consuming events with <5s lag. On primary region failure: Route53 health check detects within 10s → DNS failover to DR region within 15s → DR Redis is already populated → feed reads served normally. RTO: ~25s for new connections; ~0s for users already connected (connections auto-retry).

## Anti-patterns / Things NOT to Say

- **"Use a single SQL table with OFFSET pagination for the feed"** — OFFSET N scans N rows on every page load. At 1,000 items deep (common for active users), every feed page load scans 1,000 rows. At 500M DAU × 10 daily opens = 5B scans/day. This is an O(N) query that gets worse as feeds grow. Always use cursor-based pagination on feeds.
- **"Fan-out-on-write for everyone"** — Fails catastrophically for celebrities. A celebrity with 10M followers posting once triggers 10M cache writes. With any non-trivial celebrity activity (100 posts/day × 100 celebrities), the fan-out system processes 100 billion writes/day — 10× the compute you'd need. Use the hybrid model with a follower threshold.
- **"Store the full post body in the feed table"** — Feed table should store only post_id and ranking metadata. Post content lives in the Posts service. Duplicating content into feed entries means every edit or delete requires updating millions of feed rows. Hydrate post content at read time using the post_id.
- **"Real-time ranking for every feed load"** — Full ML inference per feed load (500K reads/sec × 1,000-candidate ranking = 500M ML inferences/sec) is prohibitively expensive. Pre-compute engagement scores for top-K candidates offline; do lightweight re-ranking (blending weights, diversity filters) at serve time.

## Python Implementation (sketch)

```python
import time
import heapq
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple

CELEBRITY_THRESHOLD = 100_000  # followers; above this → fan-out-on-read

@dataclass
class Post:
    post_id: int
    author_id: int
    content: str
    created_at: float = field(default_factory=time.time)
    like_count: int = 0

@dataclass
class User:
    user_id: int
    follower_count: int = 0

class FeedService:
    """Hybrid fan-out news feed (in-memory simulation)."""

    def __init__(self):
        self._posts: Dict[int, Post] = {}
        self._users: Dict[int, User] = {}
        # follower_id -> set of followee_ids
        self._following: Dict[int, set] = {}
        # followee_id -> list of follower_ids
        self._followers: Dict[int, List[int]] = {}
        # user_id -> [(neg_score, post_id)]  (min-heap → top-K by score)
        self._feed_cache: Dict[int, List[Tuple[float, int]]] = {}
        self._post_counter = 0

    def add_user(self, user_id: int, follower_count: int = 0):
        self._users[user_id] = User(user_id, follower_count)
        self._following[user_id] = set()
        self._followers[user_id] = []
        self._feed_cache[user_id] = []

    def follow(self, follower_id: int, followee_id: int):
        self._following[follower_id].add(followee_id)
        self._followers[followee_id].append(follower_id)
        self._users[followee_id].follower_count += 1

    def _score(self, post: Post, now: float) -> float:
        age_hours = (now - post.created_at) / 3600
        recency_decay = 1.0 / (1.0 + age_hours)  # simple decay
        engagement = 1 + 0.01 * post.like_count
        return recency_decay * engagement

    def publish(self, author_id: int, content: str) -> Post:
        self._post_counter += 1
        post = Post(self._post_counter, author_id, content)
        self._posts[post.post_id] = post
        author = self._users[author_id]

        if author.follower_count < CELEBRITY_THRESHOLD:
            # Fan-out-on-write: push to all followers' caches
            now = time.time()
            score = self._score(post, now)
            for fid in self._followers[author_id]:
                heapq.heappush(self._feed_cache[fid], (-score, post.post_id))
                # Keep top 1000 only
                if len(self._feed_cache[fid]) > 1000:
                    heapq.heappop(self._feed_cache[fid])
        # Celebrities: no fan-out; resolved at read time

        return post

    def get_feed(self, user_id: int, limit: int = 20) -> List[Post]:
        now = time.time()
        candidates: List[Tuple[float, int]] = list(self._feed_cache[user_id])

        # Fan-out-on-read for celebrity followees
        for followee_id in self._following[user_id]:
            if self._users[followee_id].follower_count >= CELEBRITY_THRESHOLD:
                # Read celebrity's recent posts directly
                celebrity_posts = [
                    p for p in self._posts.values()
                    if p.author_id == followee_id
                ][-100:]  # last 100 posts
                for p in celebrity_posts:
                    candidates.append((-self._score(p, now), p.post_id))

        # Sort by score descending; deduplicate
        seen = set()
        result = []
        for neg_score, post_id in sorted(candidates):
            if post_id not in seen and post_id in self._posts:
                seen.add(post_id)
                result.append(self._posts[post_id])
                if len(result) >= limit:
                    break
        return result


# Demo
if __name__ == "__main__":
    svc = FeedService()
    for uid in range(1, 6):
        svc.add_user(uid, follower_count=0)

    # Celebrity with 200K followers
    svc.add_user(99, follower_count=200_000)

    # User 1 follows users 2, 3, and celebrity 99
    svc.follow(1, 2)
    svc.follow(1, 3)
    svc.follow(1, 99)

    # Users 2, 3, and celebrity post
    svc.publish(2, "Post from user 2")
    svc.publish(3, "Post from user 3")
    svc.publish(99, "Celebrity announcement!")

    feed = svc.get_feed(user_id=1, limit=10)
    for post in feed:
        src = "CELEB" if svc._users[post.author_id].follower_count >= CELEBRITY_THRESHOLD else "normal"
        print(f"[{src}] Post {post.post_id} by user {post.author_id}: {post.content}")
```

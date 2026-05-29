# Leaderboard

**Level:** L3-L5+
**Time to read:** ~30 min

## Problem Statement

Online games, fitness apps, and e-commerce platforms reward competitive engagement by showing
users where they rank relative to peers. A leaderboard must display a user's current rank among
millions of players, show the top-N players globally (or in a region/friend group), and update
scores in near-real-time as users complete actions. A naive database query (`SELECT rank() OVER
(ORDER BY score DESC)`) on 10M rows takes hundreds of milliseconds per request and melts the DB
at scale.

The design challenge is achieving sub-millisecond rank lookups for any player, efficient top-N
queries, time-windowed leaderboards (daily/weekly/all-time), and accurate rank updates without
sacrificing write throughput.

## Functional Requirements

- Update a player's score (additive: +points for action)
- Get a player's current rank and score
- Get the global top-K players (paginated)
- Support time-windowed leaderboards: daily, weekly, all-time
- Support regional leaderboards (per country or server shard)

## Non-Functional Requirements

- **Scale:** 10M active players; 50K score updates/sec; 100K rank reads/sec
- **Latency:** P99 < 5 ms for rank lookup; P99 < 10 ms for top-100 query
- **Availability:** 99.9%; leaderboard is a non-critical feature, brief staleness OK
- **Consistency:** Eventual — rank updates visible within 1-2 seconds; not strictly real-time

---

## Tier 1: L3-L4 Design (the basic interview answer)

### Back-of-Envelope

```
Players:          10M active
Score updates:    50K/sec (peak: 200K/sec during events)
Rank reads:       100K/sec
ZSET entry size:  8 bytes score (float64) + 8 bytes member (player_id) = ~40 bytes with overhead
Total ZSET RAM:   10M * 40 bytes = 400 MB  ← fits comfortably in single Redis node
Top-100 query:    ZREVRANGE with WITHSCORES: O(log N + 100) ≈ microseconds
Rank query:       ZREVRANK: O(log N) = log2(10M) ≈ 23 comparisons → < 1 ms
Write throughput: Redis single-threaded: 100K+ ZINCRBY/sec on a single core → sufficient
Persistence:      Daily leaderboard resets → persist to DB nightly; Redis for hot read/write
```

### Architecture Diagram

```
  Player Action: "+100 points for user_id=42"
        |
  +-----v-----------+
  | Score Service   |  ← validates action, applies business rules
  +-----+-----------+
        |  ZINCRBY leaderboard:global 100 "user_42"
  +-----v-----------+         +------------------------+
  | Redis Cluster   |         | Persistent DB (Postgres)|
  |                 |         |                        |
  | ZSET: global   |◄────────| scores table (async    |
  | ZSET: daily     |         | sync, best-effort)     |
  | ZSET: weekly    |         |                        |
  | ZSET: region:US |         +------------------------+
  +-----------------+
        |  ZREVRANGE / ZREVRANK
  +-----v-----------+
  | Leaderboard API |  ← reads from Redis directly
  +-----------------+
        |
     Response: top-100 / player rank

Regional Leaderboards:
  One ZSET per region: leaderboard:region:US, leaderboard:region:EU, etc.
  Player update writes to global ZSET + regional ZSET simultaneously
```

### Data Model

```
# Redis ZSET (Sorted Set) — primary leaderboard store
Key:    leaderboard:global          (all-time)
Key:    leaderboard:daily:20240115  (expires after 48h)
Key:    leaderboard:weekly:2024W02  (expires after 14d)
Key:    leaderboard:region:US       (no expiry)

Each ZSET member:   "user_42"
Each ZSET score:    12345.0   (cumulative score, float64)

# Postgres — persistent record (for audit, recovery, cross-session queries)
CREATE TABLE player_scores (
    player_id       BIGINT NOT NULL,
    window_type     ENUM('alltime', 'daily', 'weekly') NOT NULL,
    window_key      VARCHAR(32) NOT NULL,   -- "20240115", "2024W02", "alltime"
    score           BIGINT NOT NULL DEFAULT 0,
    rank            INT,                    -- materialized nightly, approximate
    last_updated    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (player_id, window_type, window_key),
    INDEX idx_score_desc (window_type, window_key, score DESC)
);

CREATE TABLE score_events (
    event_id        BIGINT PRIMARY KEY AUTO_INCREMENT,
    player_id       BIGINT NOT NULL,
    delta           INT NOT NULL,           -- points earned (can be negative)
    reason          VARCHAR(128),           -- "quest_completed", "pvp_win"
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_player_created (player_id, created_at)
);
```

### API Design

```
# Submit score update
POST /leaderboard/scores
  Body: { player_id: 42, delta: 100, reason: "quest_completed" }
  Response: 200 { new_score: 12345, rank: 1872 }

# Get player rank and score
GET /leaderboard/rank/{player_id}?window=alltime
GET /leaderboard/rank/{player_id}?window=daily
  Response: 200 {
    player_id: 42,
    score: 12345,
    rank: 1872,
    percentile: 81.3,
    window: "alltime"
  }

# Get top-K players
GET /leaderboard/top?window=weekly&limit=100&offset=0
  Response: 200 {
    entries: [
      { rank: 1, player_id: 99, score: 98765, display_name: "ProGamer" },
      ...
    ],
    total_players: 10_000_000,
    window: "weekly",
    generated_at: "2024-01-15T12:00:00Z"
  }

# Get players around a specific player (neighborhood)
GET /leaderboard/around/{player_id}?window=daily&radius=5
  Response: 200 { entries: [ 5 above, player, 5 below ] }
```

### Basic Scaling

- **Redis ZSET:** Core data structure; ZINCRBY for score updates (O(log N)), ZREVRANK for rank
  (O(log N)), ZREVRANGE for top-K (O(log N + K)); all sub-millisecond for 10M players
- **Multiple ZSETs:** One per time window (alltime, daily, weekly); daily keys expire after 48h
  to auto-cleanup; use `EXPIREAT` to set expiry at end-of-day
- **Async DB sync:** Write to Redis synchronously (fast path); async worker drains score events
  to Postgres every 10 seconds (for persistence, analytics, recovery after Redis failure)
- **Read replicas:** Redis read replicas (Redis Sentinel or Cluster) serve rank reads; writes
  go to primary; staleness on replicas < 100 ms (acceptable per SLO)

---

## Tier 2: L5+ Design (the staff interview answer)

### Capacity Planning (Real Numbers)

```
Redis node sizing:
  RAM: 400 MB ZSETs + 10M player metadata (100 bytes each = 1 GB) + overhead = 2 GB needed
       Use r6g.large (16 GB RAM): 8× headroom for multiple windows + temporary data
  CPU: 50K ZINCRBY/sec on 1 core → Redis handles up to 500K ops/sec single-threaded
       At 50K/sec: 10% CPU → plenty of headroom for read traffic
  Net: 50K writes * 100 bytes + 100K reads * 200 bytes = 25 MB/sec → trivial for 1 Gbps NIC

Cluster topology:
  Sharding: NOT needed at 10M players (all fits in 1 Redis node)
  Replication: 1 primary + 2 replicas (read replicas + HA failover)
  Failover: Redis Sentinel or Cluster auto-promotes replica in < 30 sec

At 100M players (future scale):
  400 MB * 10 = 4 GB ZSETs; still fits in 1 large node (256 GB RAM)
  Cluster sharding needed only if players > 500M or multiple games share same cluster

Write amplification:
  Each score update writes to: global ZSET + daily ZSET + weekly ZSET + region ZSET = 4 ZSETs
  At 50K updates/sec: 200K Redis ops/sec → within single-node capacity (500K ops/sec)

Event sourcing (score_events table):
  50K events/sec * 100 bytes = 5 MB/sec → 432 GB/day
  Retain 30 days hot (for disputes, audits): 432 * 30 = 13 TB
  Cold storage to S3 after 30 days at $0.023/GB = $300/month
```

### Failure Modes

```
FAILURE: Redis primary node dies
  Detection:    Redis Sentinel detects failure in 3-5 sec (down-after-milliseconds = 5000)
  Promotion:    Replica elected primary in < 30 sec
  Data risk:    Redis AOF (append-only file) enabled with fsync=everysec
                At-most 1 sec of writes lost (50K * 1 sec = 50K updates)
  Mitigation:   Score updates also queued in Kafka (replay lost updates from last 60 sec)

FAILURE: Score update storm (viral event → 10× spike to 500K updates/sec)
  Detection:    Redis command latency > 1 ms P99 (normally < 0.5 ms)
  Mitigation:   Score aggregation buffer: accumulate updates in app-level counter per player
                Flush to Redis every 100 ms in batches → reduce Redis QPS by 10-50×
                Accept: player sees stale rank during spike (up to 1 sec delay)

FAILURE: Daily leaderboard reset fails (EXPIREAT not set correctly)
  Symptom:      Stale scores from yesterday persist into today's leaderboard
  Prevention:   Dedicated daily reset job: atomic RENAME old key to archive, create new empty ZSET
                Set EXPIREAT on archive key to 48h (for dispute resolution)
  Recovery:     If stale data detected: replay today's score_events from Postgres to rebuild

FAILURE: Rank manipulation (player submits fake score events)
  Prevention:   Score events come from game server (trusted backend), not client
                Rate limit: max 1 score event per player per 100 ms from backend
                Anomaly detection: flag if player score increases > 10× historical max in 1 min
```

### Consistency Boundaries

```
RANK FRESHNESS:
  Score update applied to Redis primary: immediate (< 1 ms)
  Visible on Redis replicas: < 100 ms replication lag
  Visible in top-100 list (cached with 5s TTL): up to 5 sec stale
  Acceptable: leaderboard is "near-real-time", not transactionally exact

SLIDING WINDOW LEADERBOARD:
  True sliding window (e.g., "last 24 hours"): requires expiring individual score events
  Implementation: Redis ZSET scored by event_timestamp; ZADD for each event; ZREMRANGEBYSCORE
    to remove events older than 24h before each rank computation
  Cost: 50K ZADD/sec; ZREMRANGEBYSCORE on each read query → O(log N + M) where M = expired count
  Alternative (approximate): use hourly buckets; current rank = SUM of last 24 hourly ZSET scores
    (24 ZSET lookups per player, then aggregate). Cheaper writes, slightly complex reads.

CROSS-REGION CONSISTENCY:
  Global leaderboard: single source of truth in primary region Redis
  Regional copies: async replication; up to 5 sec stale
  Decision: don't allow writes to regional replica; reads tolerate 5 sec staleness
```

### Cost Model

```
Redis (primary + 2 replicas):
  3× r6g.large ($0.155/hr): 3 * $0.155 * 8760 = $4,073/yr

Postgres (for persistence, audit):
  db.r6g.large RDS ($0.26/hr): $2,278/yr compute
  Storage: 13 TB hot = $1,430/yr (gp3 at $0.11/GB)
  Total Postgres: $3,708/yr

Kafka (for event streaming, recovery):
  3-broker MSK cluster: ~$15K/yr (small cluster, 1 topic, 10 partitions)

Total: ~$23K/yr for 10M players
Per-player: $0.0023/player/year = $0.00019/player/month (extremely cheap)

At 100M players:
  Redis still 1-2 nodes ($8K/yr); Postgres 5× more storage ($25K/yr)
  Total: ~$50K/yr for 100M players = $0.0005/player/year
```

---

## Trade-off Comparison

| Approach | Pros | Cons | Best For |
|----------|------|------|----------|
| Redis ZSET | O(log N) rank + update; sub-ms latency; built-in expiry; no extra infra | Single-threaded (1 CPU core); volatile by default; limited to ~1B members per ZSET | Real-time gaming leaderboards, any use case where speed > strict durability |
| PostgreSQL window function (RANK() OVER) | Exact rank; ACID; no extra infra; complex queries easy | Full scan or expensive index at scale; 100s of ms at 10M rows | Small leaderboards (< 100K players), admin dashboards, batch rank snapshots |
| Approximate rank (percentile buckets) | O(1) rank lookup; trivially scalable; no single hot key | Not exact; bucket width determines precision (± 0.1% rank) | All-time leaderboards with > 100M players where exact rank doesn't matter |
| Tiered sharding (region → global) | Scales to billions; regional low-latency | Aggregation complexity; eventual consistency across regions | Global games with strong regional communities (League of Legends, FIFA) |

## Follow-up Questions (escalating difficulty)

1. **(L3)** Why is Redis ZSET better than a sorted DB table for real-time leaderboards?
   → ZSET provides O(log N) rank lookup natively (ZREVRANK) in sub-millisecond time. A DB
   `SELECT COUNT(*) WHERE score > ?` is O(N) without careful indexing, and even with an index
   it's ~1-10 ms for 10M rows. Redis is in-memory, so it's 100-1000× faster for this access
   pattern.

2. **(L3)** How do you implement a daily leaderboard that resets at midnight?
   → Use a Redis ZSET key named `leaderboard:daily:YYYYMMDD`. Set `EXPIREAT` to midnight + 24h.
   New day: create fresh key; old key auto-expires. During transition, both keys exist briefly —
   queries use today's key. For dispute resolution, archive yesterday's key with a 7-day TTL.

3. **(L4)** How do you show a player their "neighborhood" (5 ranks above and below them)?
   → (1) Get player's rank with ZREVRANK. (2) Compute window: rank-5 to rank+5. (3) Use
   ZREVRANGE with these indices to fetch the 11 players in the window. Three Redis commands,
   all O(log N), completing in < 1 ms total.

4. **(L4)** How do you handle 10× traffic spikes during tournaments without Redis overload?
   → Score aggregation buffer: instead of writing each point update directly to Redis, accumulate
   deltas in a per-player in-memory counter and flush to Redis every 100 ms as a single ZINCRBY.
   Reduces Redis write rate by 10-100×. Trade-off: rank is 100 ms stale during flush window.

5. **(L5)** How would you implement a true sliding-window leaderboard (last 24 hours of activity)?
   → Store each score event as a ZSET entry: `ZADD leaderboard:sliding <timestamp> <event_id>`.
   Separately store event scores in a hash. To compute rank: ZREMRANGEBYSCORE below (now - 24h),
   then aggregate per-player scores from remaining events. This is expensive — better approach:
   hourly ZSET buckets (24 buckets); rank = sum of a player's score across last 24 buckets.
   Expires old bucket keys with TTL.

6. **(L5)** How does consistent hashing help if we need to shard a leaderboard with 1B players?
   → A single ZSET with 1B entries exceeds practical Redis node capacity (~500M entries
   comfortably). Shard by player_id: shard_id = hash(player_id) % N. Each shard holds 1B/N
   players. Top-K query: fetch top-K from each shard, merge with a min-heap → final top-K.
   Rank query: scatter rank computation to all shards (expensive!) → approximate rank using
   binary search on score histograms per shard.

7. **(L5+)** How do you compute approximate global rank for a leaderboard with 100M players
   without querying all 100M ZSET entries?
   → Percentile bucket approach: maintain a score histogram (1000 buckets covering score range).
   Bucket i holds the count of players with scores in [bucket_i_min, bucket_i_max]. To find
   rank: binary search histogram to find bucket containing player's score; rank ≈ SUM of counts
   in all buckets with higher scores. O(1) lookup, O(1000) memory for histogram, ± 0.1%
   rank accuracy. Update histogram with a streaming approximate counter (Count-Min Sketch).

## Anti-patterns / Things NOT to Say

- **"Store rank in the database and update it on every score change"** — With 50K score
  updates/sec, updating ranks in a SQL table requires recomputing ranks for all players above
  the updated player — O(N) per update, O(N²) total. Use Redis ZSET which computes rank
  on-the-fly in O(log N).
- **"Use a single global counter for rank"** — Rank is a derived value (position in sorted
  order), not a stored value. Storing rank means any score update invalidates all ranks below
  it. Store scores only; compute rank on read.
- **"Redis is unreliable for leaderboards (data loss)"** — Redis with AOF persistence (fsync=
  everysec) loses at most 1 second of data. For leaderboards, this is acceptable. For true
  zero-loss, pair Redis with async DB sync (score_events table) for full replay capability.
- **"Use ZRANGE with index 0 to 10M to get all players for rank computation"** — ZRANGE is
  O(log N + M) where M is the number of returned elements. Fetching all 10M is equivalent
  to a full sort — use ZREVRANK instead, which directly returns a player's rank in O(log N).
- **"One ZSET key for all time windows"** — Mixing daily and all-time scores in one ZSET makes
  resets impossible without affecting all-time rankings. Always use separate ZSET keys per
  time window; daily keys can be named with the date and set to auto-expire.

## Python Implementation (sketch)

```python
import time
import redis
from datetime import datetime, timezone
from dataclasses import dataclass

@dataclass
class RankEntry:
    player_id: str
    score: float
    rank: int

class Leaderboard:
    """Multi-window leaderboard using Redis Sorted Sets."""

    def __init__(self, game_id: str, host: str = "localhost", port: int = 6379):
        self.game_id = game_id
        self.r = redis.Redis(host=host, port=port, decode_responses=True)

    def _key(self, window: str) -> str:
        if window == "alltime":
            return f"lb:{self.game_id}:alltime"
        elif window == "daily":
            date = datetime.now(timezone.utc).strftime("%Y%m%d")
            return f"lb:{self.game_id}:daily:{date}"
        elif window == "weekly":
            iso = datetime.now(timezone.utc).isocalendar()
            return f"lb:{self.game_id}:weekly:{iso.year}W{iso.week:02d}"
        raise ValueError(f"Unknown window: {window}")

    def add_score(self, player_id: str, delta: float) -> dict:
        """Add delta to player's score across all windows."""
        pipeline = self.r.pipeline()
        for window in ("alltime", "daily", "weekly"):
            key = self._key(window)
            pipeline.zincrby(key, delta, player_id)
            if window != "alltime":
                # Auto-expire daily key after 48h, weekly after 14 days
                ttl = 172800 if window == "daily" else 1209600
                pipeline.expire(key, ttl)
        results = pipeline.execute()
        new_score = results[0]  # alltime new score
        rank = self.get_rank(player_id, "alltime")
        return {"new_score": new_score, "rank": rank}

    def get_rank(self, player_id: str, window: str = "alltime") -> int:
        """Returns 1-based rank (1 = highest score)."""
        key = self._key(window)
        rank = self.r.zrevrank(key, player_id)
        return (rank + 1) if rank is not None else -1

    def get_score(self, player_id: str, window: str = "alltime") -> float:
        key = self._key(window)
        score = self.r.zscore(key, player_id)
        return score or 0.0

    def get_top_k(self, k: int = 100, window: str = "alltime") -> list[RankEntry]:
        key = self._key(window)
        entries = self.r.zrevrange(key, 0, k - 1, withscores=True)
        return [
            RankEntry(player_id=pid, score=score, rank=i + 1)
            for i, (pid, score) in enumerate(entries)
        ]

    def get_neighborhood(
        self, player_id: str, radius: int = 5, window: str = "alltime"
    ) -> list[RankEntry]:
        rank_0based = self.r.zrevrank(self._key(window), player_id)
        if rank_0based is None:
            return []
        start = max(0, rank_0based - radius)
        end = rank_0based + radius
        entries = self.r.zrevrange(self._key(window), start, end, withscores=True)
        return [
            RankEntry(player_id=pid, score=score, rank=start + i + 1)
            for i, (pid, score) in enumerate(entries)
        ]


# Usage
lb = Leaderboard("my_game")
lb.add_score("player_42", 500)
lb.add_score("player_99", 750)
lb.add_score("player_7",  300)

print(lb.get_top_k(3))
print(lb.get_rank("player_42"))       # → 2
print(lb.get_neighborhood("player_42", radius=1))
```

# URL Shortener

**Level:** L3-L5+
**Time to read:** ~30 min

## Problem Statement
Design a URL shortening service like bit.ly or tinyurl.com. A long URL is mapped to a short 7–8 character alias; visiting the short link redirects to the original. This is a foundational system design problem because it teaches: ID generation at scale (avoiding collisions), read-heavy caching strategies, database sharding, and redirect performance. The hard parts are not the hashing itself, but the collision avoidance, the 100:1 read/write ratio, and generating short IDs at 100K writes/sec without coordination bottlenecks.

## Functional Requirements
- `shorten(long_url, custom_alias?)` — generate and store a short URL (7 chars)
- `redirect(short_code)` — return the original URL (HTTP 301/302)
- `analytics(short_code)` — return click count, geographic distribution, referrers
- `expire(short_code, ttl_days?)` — support optional link expiry
- Custom aliases: allow user to specify `short_code` (e.g., bit.ly/my-brand)

## Non-Functional Requirements
- **Scale:** 100B total URLs, 500M new URLs/day (writes), 50B redirects/day (reads)
- **Latency:** P99 redirect < 10 ms; P99 shorten < 100 ms
- **Availability:** 99.99% (4 nines) — downtime < 53 min/year
- **Consistency:** eventual for analytics; strong for unique short code assignment

---

## Tier 1: L3-L4 Design (the basic interview answer)

### Back-of-Envelope
```
Writes (URL creation):
  - 500M writes/day ÷ 86,400 = ~5,800 writes/sec
  - Peak (3× avg): ~17,500 writes/sec

Reads (redirects):
  - 50B redirects/day ÷ 86,400 = ~578,700 reads/sec
  - Read:Write ratio = 578,700 / 5,800 = 100:1

Storage:
  - Per URL record: short_code (8B) + long_url (200B avg) + created_at (8B) + user_id (8B) = ~224 bytes
  - 100B URLs × 224 bytes = 22.4 TB total
  - Growth rate: 500M/day × 224 bytes = 112 GB/day

Short code space:
  - Base62 chars (a-z, A-Z, 0-9): 62^7 = 3.5 trillion codes
  - At 500M writes/day: 3.5T / 500M = 7,000 days = ~19 years of codes
  - 8 chars: 62^8 = 218 trillion — safe for 100+ years

Cache:
  - 80% reads hit 20% of URLs (hot links)
  - Cache 20% of total: 100B × 0.20 × 8 bytes (code→URL pointer) = 160 GB
  - 2× Redis nodes (100 GB each) covers hot cache
```

### Architecture Diagram
```
                    ┌──────────────┐
Write Path:         │    Client    │
  Client            └──────┬───────┘
    → API Gateway           │ POST /shorten
    → URL Service           │
    → ID Generator          ▼
    → DB write        ┌─────────────┐       ┌──────────────┐
                      │ API Gateway │       │  ID Generator│
                      └──────┬──────┘       │  (Snowflake) │
                             │              └──────────────┘
                    ┌────────┴────────┐
                    │                 │
               ┌────▼────┐      ┌─────▼────┐
               │ Shorten │      │ Redirect │
               │ Service │      │  Service │
               └────┬────┘      └─────┬────┘
                    │                  │ check cache first
                    ▼                  ▼
             ┌──────────┐      ┌───────────────┐
             │  DB Write│      │  Redis Cache  │
             │(Cassandra│      │  (hot URLs)   │
             │ / MySQL) │      └───────┬───────┘
             └──────────┘             │ miss
                                      ▼
                               ┌──────────────┐
                               │  DB Read     │
                               │ (Cassandra   │
                               │  read nodes) │
                               └──────────────┘
```

### Data Model
```sql
-- Primary URL mapping table
CREATE TABLE url_mappings (
    short_code  VARCHAR(8)   PRIMARY KEY,
    long_url    TEXT         NOT NULL,
    user_id     BIGINT,
    created_at  TIMESTAMP    DEFAULT NOW(),
    expires_at  TIMESTAMP,
    is_active   BOOLEAN      DEFAULT TRUE
);

-- Analytics (separate table / stream)
CREATE TABLE url_clicks (
    short_code  VARCHAR(8),
    clicked_at  TIMESTAMP,
    ip_hash     VARCHAR(64),
    country     VARCHAR(2),
    referrer    TEXT,
    PRIMARY KEY (short_code, clicked_at)
);
-- Index: short_code + created_at for time-range analytics

-- Custom aliases
CREATE TABLE custom_aliases (
    alias       VARCHAR(50)  PRIMARY KEY,
    short_code  VARCHAR(8)   NOT NULL,
    user_id     BIGINT,
    FOREIGN KEY (short_code) REFERENCES url_mappings(short_code)
);
```

### API Design
```
POST /shorten
  Request:  { long_url: "https://...", custom_alias?: "my-link", ttl_days?: 365 }
  Response: { short_url: "https://sho.rt/aB3xY7z", short_code: "aB3xY7z", expires_at?: "..." }
  Status: 201 Created | 409 Conflict (alias taken) | 400 Bad Request

GET /{short_code}
  Response: HTTP 302 Location: https://original-long-url.com/...
  Headers: Cache-Control: max-age=3600
  Status: 302 Found | 404 Not Found | 410 Gone (expired)

GET /analytics/{short_code}
  Response: { clicks: 42891, top_countries: [...], referrers: [...], daily_clicks: [...] }
  Status: 200 OK | 403 Forbidden (not owner)

DELETE /{short_code}
  Status: 204 No Content | 403 Forbidden
```

### Basic Scaling
- **Read path:** Redis cache in front of DB; cache hit rate > 99% for hot links
- **Write path:** async analytics write to Kafka; synchronous only for core mapping
- **DB:** MySQL with read replicas for < 10B URLs; Cassandra for 100B+ (wide-column, partition by short_code)
- **HTTP 301 vs 302:** 301 (permanent) — browser caches redirect, reduces server load; 302 (temporary) — every click hits server, accurate analytics. Choose based on analytics needs.

---

## Tier 2: L5+ Design (the staff interview answer)

### ID Generation: 3 Approaches

```
Option A: MD5 Hash of long_url + base62 encode
  - Take first 7 chars of base62(MD5(long_url))
  - Collision probability: 1 - e^(-n²/2m) where n=100B, m=62^7=3.5T
  - ~1.4% collision chance at 100B URLs → need collision handling
  - Collision handling: append counter or random suffix, retry
  - Advantage: same URL always produces same short code (dedup)
  - Disadvantage: collision retry adds latency

Option B: Auto-increment ID → base62 encode
  - DB auto-increment: ID=1 → "0000001", ID=238,328 → "aB3"
  - Simple, no collisions, sequential
  - Bottleneck: single DB for ID generation → use ID range pre-allocation
  - Pre-allocation: service fetches block of 10K IDs from DB, serves locally
  - Disadvantage: IDs are predictable (guessable URLs, privacy concern)

Option C: Snowflake-like distributed ID (recommended for L5)
  - 64-bit ID = 41-bit timestamp(ms) + 10-bit machine_id + 12-bit sequence
  - Fits in 8 base62 chars (62^8 > 2^64? No: 62^8 = 2.18×10^14, 2^64 = 1.84×10^19)
  - Use 11 chars for full 64-bit space in base62
  - Practically: truncate to 7-8 chars; accept 0.01% collision rate + retry
  - No coordination needed — each machine generates IDs independently
  - Advantage: time-ordered, unique, no DB round-trip for ID
  - Disadvantage: requires time sync (NTP); clock skew causes gaps
```

### Capacity Planning (Real Numbers)
```
Cache sizing:
  - 50B redirects/day; 80% cache hit rate → 40B redirects served from Redis
  - Redis GET: 0.1 ms; DB read: 1 ms
  - Latency saving: 40B × (1ms - 0.1ms) / 86400 = irrelevant, but cost matters
  - Redis memory: top 1M hot URLs × (8 byte key + 200 byte value) = 208 MB — tiny
  - Top 10M hot URLs = 2 GB → cache 10M in Redis, cover 80%+ of traffic

DB sizing:
  - 22.4 TB across 3 years of growth
  - Cassandra cluster: 3 nodes × 10 TB SSD = 30 TB; RF=3 → 10 TB effective
  - Need 3 more nodes as data grows: plan for 10-node cluster (100 TB effective)
  - Write throughput: 17.5K writes/sec → Cassandra handles 50K+ writes/sec/node

Analytics pipeline:
  - 578K redirects/sec → each click event = ~100 bytes
  - 578K × 100 bytes = 57.8 MB/sec event stream
  - Kafka: 3-broker cluster, 10 MB/s/partition → 10 partitions sufficient
  - Downstream: Flink or Spark Streaming → Cassandra time-series or ClickHouse
```

### Failure Modes
```
Cache stampede on viral link:
  - New link goes viral; cold cache → all 578K req/sec hit DB for 1 link
  - Fix: Cache-warming on write (after shorten(), immediately populate Redis)
  - Fix: Redis SETNX + background fetch (one request fetches, others wait)
  - Fix: Serve stale cache value while refreshing async

Duplicate URL dedup:
  - With hash-based IDs: same long_url → same short_code (automatic dedup)
  - With Snowflake IDs: same long_url gets multiple short codes (no dedup)
  - Add reverse index: long_url_hash → short_code for dedup check before insert

Short code collision (hash approach):
  - Collision rate: ~1.4% at 100B URLs with 7-char base62
  - Retry strategy: append 1-char suffix, re-hash, retry up to 3 times
  - Monitoring: alert if collision rate > 5% (indicates hash space exhaustion)

Expired URL handling:
  - Don't delete immediately — lazy expiry: check expires_at on read, return 410
  - Batch cleanup job: daily scan, delete expired entries older than 30 days
  - Benefit: no cascading deletes, simple TTL logic

Analytics data loss:
  - Kafka consumer lag → clicks counted late but eventually consistent
  - If Kafka fails: buffer clicks in Redis LIST, flush when Kafka recovers
  - Accept eventual consistency: click counts may be off by seconds
```

### Consistency Boundaries
```
URL assignment (strong consistency required):
  - Two concurrent requests for same custom_alias must not both succeed
  - Use DB unique constraint on short_code/alias as serialization point
  - Snowflake approach: unique by construction, no DB check needed

Redirect (eventual consistency acceptable):
  - Read from Redis cache; may serve stale if URL was updated/deleted
  - TTL on cache entries: 1 hour (balance freshness vs performance)
  - On delete: invalidate Redis key synchronously before returning 204

Analytics (eventual consistency):
  - Click counts can lag by seconds to minutes
  - Batch aggregation: count clicks per hour, not per request
  - User expectation: analytics dashboard shows data with 5-minute delay
```

### Cost Model
```
At 500M writes/day, 50B reads/day (mid-size service):

Redis cluster:
  - 2x r6g.large (13 GB): 2 × $0.15/hr = $216/mo
  - Covers top 10M hot links with 99% hit rate

Cassandra cluster (self-hosted):
  - 10× i3.2xlarge (1.9 TB NVMe): 10 × $0.624/hr = $4,493/mo
  - Or DynamoDB: 22 TB storage + 578K read units/sec = ~$50K/mo (DynamoDB much pricier)

Kafka (analytics):
  - 3× kafka.m5.xlarge (MSK): ~$800/mo

API servers:
  - 578K req/sec ÷ 50K req/sec/server = 12 servers
  - 12× c5.2xlarge: 12 × $0.34/hr = $2,952/mo

Total: ~$8,500/mo = $0.000000170/redirect ($0.17/million redirects)
CDN (optional): cache top 1M links at edge → reduce origin by 70%, save $2K/mo
```

---

## Trade-off Comparison

| ID Strategy | Collision Risk | Guessable | Dedup | Distributed | Use When |
|-------------|---------------|-----------|-------|-------------|----------|
| MD5 + base62 | ~1.4% at 100B | No | Yes (same URL = same code) | Yes | When dedup is important |
| Auto-increment | None | Yes (sequential) | No | No (single DB) | Small scale, simple |
| UUID | None | No | No | Yes | Privacy-sensitive |
| Snowflake + base62 | Negligible | No | No | Yes (no coord) | Large scale, recommended |
| Nano ID | None | No | No | Yes | Modern, URL-safe |

**301 vs 302 redirect:**

| | 301 Permanent | 302 Temporary |
|--|--------------|---------------|
| Browser caching | Yes (no server hit on repeat) | No (every click hits server) |
| Analytics accuracy | Poor (miss repeat visitors) | Perfect |
| Server load | Low | High |
| Use when | Static links, reduce cost | Need accurate click tracking |

---

## Follow-up Questions (5-10, escalating)

1. **(L3)** What's the minimum short code length needed for 100B URLs?
   > base62^n >= 100B → n >= log_62(100B) = log(10^11)/log(62) ≈ 6.2 → 7 characters.

2. **(L3)** When would you use HTTP 301 vs 302 for the redirect?
   > 301: permanent redirect, browser caches it (saves server load, but analytics miss repeats). 302: temporary, every click goes through server (accurate analytics, higher load). Choose 302 if analytics matter; 301 if cost reduction matters.

3. **(L4)** How do you handle hash collisions with MD5-based short codes?
   > On insert, check if short_code already exists in DB. If collision: append a 1-char suffix to the long_url and re-hash, retry up to 3 times. If still colliding, fall back to random suffix. Monitor collision rate; switch to Snowflake IDs if > 1%.

4. **(L4)** How would you scale to 100K writes/sec without a single ID generator bottleneck?
   > Option A: Pre-allocate ID ranges — each server fetches 10K IDs from DB, serves locally. Option B: Snowflake — each server generates unique IDs with machine_id prefix, no coordination. Option C: Hash-based — MD5 is stateless, no coordination needed.

5. **(L4)** How would you implement custom short codes (vanity URLs)?
   > Check custom_alias availability in `custom_aliases` table. If available: insert with unique constraint (DB handles race). If taken: return 409. Store mapping alias → short_code. On redirect: check custom_aliases first, then url_mappings.

6. **(L5)** Design the analytics pipeline for 50B clicks/day with real-time dashboard.
   > Write path: on redirect, emit click event (short_code, ts, ip, country, referrer) to Kafka. Flink job: tumbling 1-minute windows, aggregate click counts per short_code, write to ClickHouse. Dashboard reads from ClickHouse via pre-aggregated hourly/daily tables. Real-time: Redis INCR for approximate live count, reconcile with ClickHouse hourly.

7. **(L5)** How would you implement URL expiry at 100B URL scale?
   > Store expires_at in DB. On redirect, check expires_at; if expired, return 410. Lazy expiry: don't delete immediately, just reject on read. Background job: daily Cassandra scan using TTL feature (Cassandra natively supports row TTL) — set TTL = expires_at - created_at on insert. Redis cache: set Redis key TTL = min(cache_ttl, url_expires_at - now).

8. **(L5+)** A malicious user creates 10M short codes all pointing to phishing sites. How do you detect and handle this?
   > Detection: rate limit by user_id (100 creates/day default), anomaly detection on bulk creates (Z-score on 5-min rolling window). Safe browsing: integrate Google Safe Browsing API — async scan all new URLs, flag dangerous ones. On redirect: check flagged status before serving redirect; return 451 (Legal Reasons) or 403. Abuse scoring: ML model on URL patterns (homoglyph domains, redirect chains). Automated suspension + human review queue for flagged accounts.

---

## Anti-patterns / Things NOT to Say

- **"I'll use UUID as the short code"** — UUIDs are 32 hex chars; completely defeats the purpose of URL shortening.
- **"MD5 guarantees no collisions"** — MD5 absolutely has collisions; the truncated 7-char version even more so (~1.4% at 100B URLs). Must mention collision handling.
- **"HTTP 301 is always better"** — 301 bypasses analytics for repeat visitors; wrong choice if you're monetizing on clicks.
- **"I'll store analytics in the same DB as URL mappings"** — analytics is write-heavy time-series; pollutes your read-heavy URL table; use separate Kafka/ClickHouse pipeline.
- **"I'll delete expired URLs immediately"** — cascading deletes at 500M/day scale will crush your DB; lazy expiry + TTL is correct.
- **"Auto-increment IDs are fine at any scale"** — single-point bottleneck at 100K writes/sec; must mention range pre-allocation or Snowflake.

---

## Python Implementation

```python
import hashlib
import time
import string
import random
from dataclasses import dataclass, field
from typing import Optional


# ── Base62 encoding ────────────────────────────────────────────────────────

ALPHABET = string.ascii_lowercase + string.ascii_uppercase + string.digits  # 62 chars

def encode_base62(n: int) -> str:
    if n == 0:
        return ALPHABET[0]
    result = []
    while n:
        result.append(ALPHABET[n % 62])
        n //= 62
    return "".join(reversed(result))

def decode_base62(s: str) -> int:
    return sum(ALPHABET.index(c) * (62 ** i) for i, c in enumerate(reversed(s)))


# ── Snowflake-like ID generator ────────────────────────────────────────────

class SnowflakeIDGenerator:
    """
    64-bit ID: 41-bit ms timestamp + 10-bit machine ID + 12-bit sequence.
    Generates ~4096 unique IDs/ms per machine = 4.1B IDs/sec.
    """
    EPOCH = 1_700_000_000_000   # custom epoch (Nov 2023) to extend timestamp range

    def __init__(self, machine_id: int = 1):
        assert 0 <= machine_id < 1024
        self.machine_id = machine_id
        self._seq = 0
        self._last_ms = -1

    def next_id(self) -> int:
        ms = int(time.time() * 1000) - self.EPOCH
        if ms == self._last_ms:
            self._seq = (self._seq + 1) & 0xFFF      # 12-bit max = 4095
            if self._seq == 0:
                # Sequence exhausted this millisecond; busy-wait
                while ms <= self._last_ms:
                    ms = int(time.time() * 1000) - self.EPOCH
        else:
            self._seq = 0
        self._last_ms = ms
        return (ms << 22) | (self.machine_id << 12) | self._seq

    def next_short_code(self, length: int = 8) -> str:
        return encode_base62(self.next_id()).zfill(length)[:length]


# ── Hash-based short code generator ───────────────────────────────────────

def hash_url(long_url: str, salt: str = "") -> str:
    """Generate 7-char base62 short code from MD5 of URL."""
    digest = hashlib.md5((long_url + salt).encode()).hexdigest()
    # Convert hex string to integer
    n = int(digest, 16)
    return encode_base62(n)[:7]


# ── URL Shortener service (in-memory for demo) ─────────────────────────────

@dataclass
class URLRecord:
    short_code: str
    long_url: str
    created_at: float = field(default_factory=time.time)
    expires_at: Optional[float] = None
    clicks: int = 0


class URLShortener:
    def __init__(self, base_url: str = "https://sho.rt"):
        self.base_url = base_url
        self._db: dict[str, URLRecord] = {}           # short_code → URLRecord
        self._reverse: dict[str, str] = {}            # long_url_hash → short_code
        self._id_gen = SnowflakeIDGenerator(machine_id=1)

    def shorten(
        self,
        long_url: str,
        custom_alias: Optional[str] = None,
        ttl_days: Optional[int] = None,
    ) -> dict:
        # Dedup: same long_url → return existing short code
        url_hash = hashlib.sha256(long_url.encode()).hexdigest()[:16]
        if not custom_alias and url_hash in self._reverse:
            existing_code = self._reverse[url_hash]
            if existing_code in self._db:
                rec = self._db[existing_code]
                if not rec.expires_at or rec.expires_at > time.time():
                    return {"short_url": f"{self.base_url}/{existing_code}", "deduplicated": True}

        # Determine short code
        if custom_alias:
            if custom_alias in self._db:
                raise ValueError(f"Alias '{custom_alias}' already taken")
            short_code = custom_alias
        else:
            # Snowflake ID → base62
            short_code = self._id_gen.next_short_code(length=7)
            # Collision retry (rare with Snowflake, but handle)
            retries = 0
            while short_code in self._db and retries < 3:
                short_code = hash_url(long_url, salt=str(retries))
                retries += 1

        expires_at = (time.time() + ttl_days * 86400) if ttl_days else None
        record = URLRecord(short_code=short_code, long_url=long_url, expires_at=expires_at)
        self._db[short_code] = record
        self._reverse[url_hash] = short_code

        return {
            "short_url": f"{self.base_url}/{short_code}",
            "short_code": short_code,
            "expires_at": expires_at,
        }

    def redirect(self, short_code: str) -> str:
        if short_code not in self._db:
            raise KeyError("404 Not Found")
        rec = self._db[short_code]
        if rec.expires_at and rec.expires_at < time.time():
            raise ValueError("410 Gone — link expired")
        rec.clicks += 1
        return rec.long_url

    def analytics(self, short_code: str) -> dict:
        if short_code not in self._db:
            raise KeyError("404 Not Found")
        rec = self._db[short_code]
        return {
            "short_code": short_code,
            "long_url": rec.long_url,
            "clicks": rec.clicks,
            "created_at": rec.created_at,
            "expires_at": rec.expires_at,
        }


# ── Demo ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    svc = URLShortener()

    r1 = svc.shorten("https://www.example.com/very/long/path?param=value")
    print("Shortened:", r1["short_url"])

    r2 = svc.shorten("https://www.example.com/very/long/path?param=value")
    print("Dedup:", r2)   # same short code returned

    r3 = svc.shorten("https://openai.com", custom_alias="openai", ttl_days=30)
    print("Custom alias:", r3["short_url"])

    url = svc.redirect(r1["short_code"])
    print("Redirected to:", url)
    print("Analytics:", svc.analytics(r1["short_code"]))

    print("\nSnowflake IDs:")
    gen = SnowflakeIDGenerator(machine_id=5)
    for _ in range(5):
        print(f"  {gen.next_id()} → {gen.next_short_code()}")
```

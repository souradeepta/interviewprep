# Mock System Design Interview — Senior Engineer (L5)

**Problem:** Design a URL Shortener (like bit.ly)
**Level:** L5 (senior, 4-7 years experience)
**Duration:** ~45 minutes

---

## Transcript

**Interviewer:** Design a URL shortener. Users submit a long URL and get back a short link. When someone visits the short link, they're redirected to the original URL. Go ahead.

**Candidate:** Before I sketch anything, I want to make sure I'm designing the right system. A few questions: Is this public-facing or internal tooling? That changes the abuse surface. What's the expected scale — roughly how many new URLs per day, and what's the read-to-write ratio? Do we need analytics on how many times each link is clicked? And do we need custom aliases, like `bit.ly/my-brand`, or is random generation fine?

> **[Annotation: Clarifying Requirements]:** These four questions map directly to four architectural decisions: public-facing → abuse controls; scale → capacity planning; analytics → write path complexity; custom aliases → ID generation strategy. Strong L5 candidates don't treat requirements as fixed — they treat the prompt as a starting point and shape the scope deliberately.

**Interviewer:** Public-facing. Assume 100M URLs stored total, 1M new URLs per day, 100:1 read-to-write ratio. No custom aliases for now. Analytics are a stretch goal.

**Candidate:** Great. Let me do a quick back-of-envelope estimate. 1M writes per day is roughly 12 writes per second — low write load. At 100:1 read ratio, that's 1,200 reads per second, or about 1.2K RPS. That's easy for a single DB node. Storage: 100M rows, each URL at maybe 500 bytes average → 50GB total, comfortably fits on one machine or a small cluster. Bandwidth: 1.2K redirects per second, each response ~100 bytes → ~120 KB/s, trivial. The bottleneck here will be read latency for popular links, not raw throughput.

> **[Annotation: Back-of-Envelope Before Architecture]:** Capacity planning before drawing boxes is essential at L5. The numbers here immediately reveal that this is not a scale-at-all-costs problem — it's a latency problem for hot links. That insight should drive the architecture toward caching, not sharding. Candidates who skip this step often over-engineer the write path and under-engineer the read path.

**Candidate:** Okay, now the data model. Core table:

```sql
CREATE TABLE urls (
    short_code   CHAR(7)      PRIMARY KEY,
    long_url     TEXT         NOT NULL,
    user_id      BIGINT,
    created_at   TIMESTAMP    DEFAULT NOW(),
    expires_at   TIMESTAMP,
    click_count  BIGINT       DEFAULT 0
);
```

`short_code` is the lookup key. `expires_at` is NULL for permanent links. `click_count` for basic analytics without a separate service.

> **[Annotation: Data Model First]:** Naming the schema before discussing services or infrastructure is a senior-level signal. The schema reveals what the system stores, which drives everything else: index strategy, cache key, sharding key. Candidates who draw a "URL Service" box without defining what it reads/writes are reasoning at the wrong level of abstraction.

**Interviewer:** How do you generate the short code?

**Candidate:** Two main options. Option 1: auto-increment the primary key in the DB, then base62-encode it. An 8-digit base62 number gives 62^8 ≈ 218 trillion unique codes — more than enough. The advantage is zero collision risk and global uniqueness via the DB sequence. The downside is the DB is in the critical write path for ID generation.

Option 2: generate a hash of the long URL, take the first 7 characters of the base62 representation. Advantage: ID generation is stateless, works without a DB round-trip. Disadvantage: collisions, which require retry logic. For 100M URLs, birthday-problem collision probability with 7-char base62 (≈ 3.5 trillion space) is well under 0.1%, manageable with a simple retry.

I'd go with option 1 for simplicity: auto-increment + base62 encode. We can move to distributed ID generation (Snowflake-style) if we shard later.

> **[Annotation: Trade-off Analysis on Core Mechanism]:** Presenting two options and choosing one with explicit reasoning is textbook L5 behavior. The candidate didn't just pick one — they quantified the collision risk for option 2 (birthday problem) and explained why option 1's DB dependency is acceptable at this scale. This is the difference between a decision and a guess.

**Candidate:** For the read path — the redirect — I want to minimize latency. Most redirects are for recently-created or popular links, which is a classic Zipf distribution. I'll put a Redis cache in front of the DB. Key: `short_code`, value: `long_url`. TTL: 24 hours. Expected cache hit rate for popular links: 90%+. This turns most redirects into a single Redis lookup at sub-millisecond latency instead of a DB query.

> **[Annotation: Cache for Read-Heavy Path]:** Identifying the Zipf distribution pattern — that a small fraction of links get the vast majority of clicks — and connecting that directly to the caching decision is an L5-level insight. It's not just "add a cache"; it's explaining *why* a cache works especially well here.

**Candidate:** The high-level architecture:

```
Client
  |
  v
Load Balancer (e.g., ALB)
  |         |
  v         v
Write API   Read API (redirect service)
  |              |
  v              v
  DB (Postgres) <-- Redis cache (hot short codes)
  (primary)         (TTL = 24h)
      |
      v
  DB Replica (read fallback on cache miss)
```

Write API: accepts POST with long URL, generates short code, writes to DB, returns short URL.
Read API: accepts GET on short code, checks Redis, falls back to DB replica on miss, returns 301/302 redirect.

> **[Annotation: Separation of Read and Write Paths]:** Splitting into two logical services (write and redirect) is an important design choice — they have fundamentally different load profiles and scaling needs. The redirect service is read-heavy and latency-sensitive; the write service is low-QPS and correctness-sensitive. Keeping them separate means we can scale and deploy them independently.

**Interviewer:** What about the single-point-of-failure concern?

**Candidate:** The load balancer should have a standby (AWS ALB handles this natively). For the redirect service, we run multiple stateless instances behind the LB — if one dies, traffic routes to others. Redis: use a Redis Sentinel or Redis Cluster for high availability; primary-replica with automatic failover. Postgres: primary with a synchronous replica. On primary failure, promote the replica — Recovery Time Objective should be under 30 seconds with automatic failover tooling like Patroni.

The one place I'd flag as genuinely risky is Redis failover during high traffic — if the cache is cold during failover, we get a thundering herd on the DB. Mitigation: circuit breaker in the redirect service that rate-limits DB fallback during cache recovery, plus pre-warming the new primary from the replica before cutover.

> **[Annotation: Failure Mode Analysis]:** Naming specific failure modes — and specifically identifying thundering herd on cache failover as the most dangerous one — is an L5 signal. The candidate also pairs each failure mode with a concrete mitigation (circuit breaker, pre-warming), not just a vague "add redundancy."

**Interviewer:** What about the analytics stretch goal?

**Candidate:** I wouldn't add `click_count` to the URLs table for high-traffic links — it creates a hot row problem where every redirect is a write contention on the same row. Instead, I'd emit a click event to a message queue (Kafka or SQS) from the redirect service, and a separate analytics consumer aggregates asynchronously. This decouples redirect latency from analytics writes. The redirect stays fast; analytics can tolerate seconds of lag.

> **[Annotation: Async Analytics Pattern]:** Recognizing the hot row problem and solving it with async event streaming rather than synchronous counter increments is exactly the kind of production-aware thinking that distinguishes L5 from L4. An L4 might suggest updating the counter on every click; an L5 knows that's a write bottleneck at scale and proposes event sourcing without being prompted.

---

## Summary of Strong L5 Signals

- Opened with targeted requirement-shaping questions before touching the whiteboard
- Completed a back-of-envelope estimate before proposing architecture, and used the estimate to identify the right bottleneck (read latency, not throughput)
- Defined the database schema before services, revealing clear understanding of what the system stores
- Presented two ID generation strategies with quantified trade-offs and made an explicit choice with reasoning
- Identified the Zipf distribution pattern and connected it to cache design
- Separated read and write paths as independent services with different scaling characteristics
- Identified thundering herd as the primary failure risk during Redis failover and proposed specific mitigations
- Proactively addressed the analytics stretch goal and identified the hot row anti-pattern

## What This Answer Would Score

- L3 bar: ✅ Passes (clear architecture, handles basic scale)
- L4 bar: ✅ Passes (capacity planning, trade-off analysis, failure modes)
- L5 bar: ✅ Passes (schema-first thinking, hot row analysis, thundering herd mitigation)
- L6 bar: ⚠️ Does not pass (missing multi-region design, cost modeling, org/team concerns, operational runbooks)

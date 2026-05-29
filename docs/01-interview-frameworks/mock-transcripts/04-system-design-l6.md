# Mock System Design Interview — Staff Engineer (L6)

**Problem:** Design a URL Shortener (like bit.ly)
**Level:** L6 (staff, 8+ years, cross-org scope)
**Duration:** ~50 minutes

---

## Transcript

**Interviewer:** Design a URL shortener. Users submit a long URL and get back a short link. When someone visits the short link, they're redirected to the original URL. Go ahead.

**Candidate:** I'll get there — but let me push back on the requirements framing first, because that changes the design by an order of magnitude. A few questions: What's the failure tolerance for the redirect service? If it goes down for 60 seconds, is that a P0 incident? Is this critical path for the product — meaning, does revenue depend directly on redirects completing? And what's our SLA: 99.9% uptime (8.7 hours downtime/year) or 99.99% (52 minutes/year)?

> **[Annotation: Challenging the Problem Frame]:** An L6 candidate doesn't accept requirements passively — they interrogate the business context. Failure tolerance, SLA tier, and revenue criticality are not scope questions; they are architectural constraints that determine whether you need active-active multi-region (99.99%) or a simpler primary-region-with-DR setup (99.9%). Asking this before touching the whiteboard signals that the candidate thinks in organizational risk, not just technical components.

**Interviewer:** Assume 99.99% SLA, public-facing, revenue-adjacent (marketing campaigns route through this). 100M URLs, 100:1 read-to-write, 1B redirects per day.

**Candidate:** 99.99% SLA with revenue-adjacent criticality means multi-region active-active — a single-region failover won't meet that bar. Let me do the capacity math with the actual numbers. 1B redirects per day is 11,600 RPS average. Assume 3× peak factor for campaign spikes → 35K RPS peak. At 100 bytes per redirect response, that's 3.5 MB/s peak bandwidth, trivial. But at 35K RPS with 99.99% availability, we cannot afford cold-start or region failover lag. That means the redirect path must be served from every region simultaneously, not failed over to.

> **[Annotation: SLA-Driven Architecture Decision]:** Connecting "99.99% SLA" directly to "active-active, not active-passive" is the key L6 insight here. An L5 would design for redundancy; an L6 starts from the SLA number, derives the allowable downtime (52 minutes/year), and reasons that manual or even automated regional failover — which typically takes minutes — cannot satisfy that budget. The architecture choice follows from the math, not from preference.

**Candidate:** Storage math: 100M URLs × 500 bytes average = 50GB. Tiny. Even with replication to 3 regions × 3 replicas each, we're under 500GB total. That easily fits on a handful of database nodes per region. Caching is where the interesting decision is: at 35K RPS reads, a single Redis r6g.large handles ~100K ops/sec, giving us 2.8× headroom before we need to shard. But for 99.99% SLA, I'd run Redis Cluster with at least 3 primary shards per region for fault isolation. Cache hit rate for a Zipf distribution of popular campaign links will be north of 95%, so DB RPS is under 2K even at peak.

> **[Annotation: Granular Capacity Planning]:** The L5 candidate said "Redis handles this." The L6 candidate cites the specific instance type, its ops/sec ceiling, derives the headroom multiple, and then sizes the cluster for fault isolation — not just performance. This level of precision signals that the candidate has operated production systems at scale and knows the difference between "technically works" and "safely operates."

**Interviewer:** How do you handle short code generation across multiple regions?

**Candidate:** This is where active-active gets interesting. If we use auto-increment IDs, we have a coordination problem: two regions generating IDs independently will collide. Options:

Option 1: Single global ID generator (e.g., a Snowflake service or a dedicated Postgres sequence in one region). Writes always go to a single authoritative region for ID allocation, then replicate. This is simple and collision-free but adds cross-region write latency — 50-100ms for a US write to go to EU and back if the ID service lives there.

Option 2: Pre-allocate ID ranges per region. Region 1 owns IDs 0-999M, Region 2 owns 1B-1.999B. Each region generates IDs independently within its range. No coordination needed, no collision risk. Downside: range exhaustion requires coordination, and ranges look asymmetric if we ever shard.

Option 3: Include the region ID in the short code's base62 encoding. First character encodes the origin region. This is a CRDT-style approach — each region is authoritative for its own codes. Collision-free by construction, fully decentralized. The trade-off is that short codes are slightly longer (8 chars instead of 7) and reveal the origin region.

I'd go with option 2 for simplicity at the stated scale — range exhaustion is a problem for a future day, and the architecture stays clean.

> **[Annotation: Multi-Region Conflict Resolution]:** Presenting three options for distributed ID generation — with their trade-offs framed as coordination cost vs. complexity vs. observable properties — is a staff-level discussion. The candidate uses the term "CRDT-style" accurately and explains why option 2 beats option 3 for this specific use case without over-generalizing. L5s often stop at "use a UUID" or "use a hash"; L6s reason through the correctness model.

**Candidate:** On the redirect path, I'd push as much as possible to the CDN edge. Cloudflare Workers or Lambda@Edge can serve the redirect directly from the edge node's cache — no origin hit needed for hot links. For a marketing campaign link that's fired 10M times in an hour, 95%+ of those redirects never touch our origin infrastructure at all.

> **[Annotation: Edge-First Redirect Architecture]:** Proposing CDN-layer redirects is an L6 insight that most L5 candidates miss. It fundamentally changes the scaling model: instead of planning for 35K RPS on our origin Redis, we plan for ~1.75K RPS (the cache-miss traffic). The implications cascade into cost modeling and failure domain isolation.

**Candidate:** Speaking of cost — let me model this quickly. Cloudflare Workers: $0.0000003 per request × 1B/day = $300/day = $9,000/month at full load. Self-hosted origin infra: 3 regions × 3 redirect service pods × r6g.large ($0.20/hr) = 9 × $0.20 × 730 hrs/month ≈ $1,314/month for compute, plus DB and Redis costs. Break-even: at what traffic level does self-hosting beat Cloudflare Workers cost? Roughly at 4.5B redirects/month, assuming linear pricing. At our stated 30B redirects/month (1B/day), self-hosting wins on cost but loses on simplicity and global PoP coverage.

> **[Annotation: Cost Modeling at Staff Level]:** Doing a cost break-even analysis during a system design interview is a rare and powerful signal. L6 engineers are accountable for engineering efficiency, not just technical correctness. Bringing cost numbers into the trade-off (and deriving a break-even point) demonstrates that the candidate thinks about the total cost of ownership, not just the architecture diagram.

**Interviewer:** What about malicious links? If a URL becomes associated with spam or phishing after it's been shortened?

**Candidate:** This is an operational correctness problem that most architecture diagrams ignore. We need a revocation mechanism in the hot redirect path. My approach: maintain a revocation list — a Redis set of banned short codes, updated by a trust-and-safety service. The redirect service checks this list before serving. Because the revocation list is small (maybe 100K entries), it fits in a single Redis key and can be replicated to every region in under a second. We can also push revocations to the CDN edge via Cache-Control: no-store + a purge API call.

For proactive detection: scan long URLs against Google Safe Browsing API at write time. Flag suspicious domains. Add a quarantine status to the URL schema (`status ENUM: active, quarantined, revoked`). Quarantined links show an interstitial warning page instead of a silent redirect.

> **[Annotation: Trust and Safety in the Hot Path]:** Raising trust-and-safety unprompted is a staff-level signal. It shows the candidate is thinking about the full product lifecycle, not just the happy path. The specific design — a Redis revocation set checked in the redirect path, with CDN purge for edge nodes — is operationally concrete, not hand-wavy "we'd handle abuse separately."

**Interviewer:** This system touches multiple teams. How would you think about the organizational side?

**Candidate:** Good question. I see at least three teams with stakes: Platform (owns the redirect infra and SLA), Product (owns analytics and the shortened URL creation UX), and Security/Trust-and-Safety (owns abuse detection and revocation). A few concerns I'd raise before we finalize the design.

First, API versioning. The redirect endpoint can't change its contract — it's embedded in millions of existing links. That means `/r/{code}` must remain stable indefinitely, which constrains the Platform team's ability to evolve the schema or add headers. We should document this as a frozen API contract on day one.

Second, the analytics write path crosses the Platform/Product boundary. Who owns the Kafka topic? Who owns the consumer and the downstream data warehouse? We need an agreed schema and an SLA on analytics freshness (real-time vs. T+1 hours).

Third, the revocation path crosses Platform/Security. We need a clear incident response playbook: if a phishing campaign uses our service, what's the escalation path? What's the SLA for revocation — minutes or seconds? That SLA determines whether we need push-based invalidation (CDN purge API) or if polling every 30 seconds is acceptable.

> **[Annotation: Org/Team Ownership as Design Input]:** Raising API contract freezing, cross-team Kafka ownership, and incident SLA as design constraints is the defining characteristic of L6. These are not technical concerns — they're organizational concerns that feed back into technical decisions (do we need real-time CDN purge? Yes, if the security SLA is "minutes"). An L5 stays within a single service boundary. An L6 reasons about the system across team boundaries.

**Interviewer:** Anything you'd do differently if this needed to scale to 100× traffic — 100B redirects per day?

**Candidate:** At 100B redirects per day (≈1.16M RPS average, 3.5M RPS peak), the architecture shifts fundamentally. CDN-edge redirects become non-negotiable — you cannot serve 3.5M RPS from a centralized origin. Cache miss rate matters more than anything: even a 0.1% miss rate is 3,500 RPS hitting origin. That means aggressive pre-warming, higher TTLs for campaign links, and possibly a dedicated "campaign URL" tier that gets pre-loaded to all edge PoPs before a campaign launches.

DB sharding: at 100M URLs × 100× = 10B URLs, 5TB of storage. We'd shard by `short_code % N` across N Postgres clusters. ID generation with regional ranges still works but ranges need to be larger (or we switch to Snowflake-style IDs with embedded shard keys).

Redirect infrastructure at Cloudflare alone: $0.0000003 × 100B/day = $30,000/day = $900K/month. That's when you seriously evaluate building your own edge CDN or negotiating enterprise pricing.

> **[Annotation: Scaling Inflection Points]:** The candidate doesn't just say "shard the database" — they model the cost at 100× ($900K/month CDN spend), identify the new bottleneck (cache miss rate at sub-0.1%), and reason through what changes at each layer. Identifying the break-even point where the architecture needs to fundamentally change is an L6 capability: knowing when incremental scaling stops working.

---

## Summary of Strong L6 Signals

- Challenged the requirements framing by asking about SLA tier and business criticality before touching the design
- Derived active-active multi-region directly from the 99.99% SLA and allowable downtime budget
- Cited specific instance types and ops/sec limits in capacity planning, not just "add more Redis"
- Presented three distributed ID generation strategies with correctness models and operational trade-offs
- Proposed CDN-edge redirects as the primary scaling lever, reducing origin load by 95%+
- Built a cost model with a break-even analysis between Cloudflare Workers and self-hosted origin
- Raised the trust-and-safety revocation path unprompted and designed it concretely
- Identified three team ownership boundaries (Platform, Product, Security) and the cross-cutting concerns each creates
- Modeled the 100× scaling scenario with cost projections and identified the new architectural constraints

## What This Answer Would Score

- L3 bar: ✅ Passes
- L4 bar: ✅ Passes
- L5 bar: ✅ Passes
- L6 bar: ✅ Passes (cost modeling, org ownership, SLA-driven architecture, multi-region correctness, 100× scaling analysis)

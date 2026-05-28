# Staff System Design Playbook

**Level:** L5+  
**Time:** 45-60 min to read + exercises  
**Interview weight:** Highest — almost every L5+ loop includes at least one system design session

---

## Quick Summary

The L5+ system design interview is not a harder version of the L4 interview. It is a different interview. L4 evaluates whether you can *design* a system. L5+ evaluates whether you can *own* a system — including scope definition, capacity planning, failure modeling, org coordination, and migration strategy. This guide gives you the frameworks to do all of that under interview pressure.

---

## The L4 vs L5+ Framing Matrix

| Interview Phase | L4 Expectation | L5+ Expectation |
|-----------------|----------------|-----------------|
| **Clarifying questions** | Ask 2-3 basic questions about scale and requirements | Drive a full requirements conversation; surface unstated constraints (budget, team size, operational burden) |
| **Scope definition** | Accept the scope as given | Propose what is in/out of scope and defend the choice |
| **High-level design** | Draw boxes and arrows | Explain the ownership model — which team owns each box, what the API contracts are |
| **Deep dive** | Go deep on the data model or one component | Propose which component to deep dive and justify why it is the most critical |
| **Capacity planning** | "We need a database and a cache" | Produce a back-of-envelope calculation with real numbers; size the components; state assumptions |
| **Reliability** | "Add retries and a load balancer" | Specify SLAs, failure budget, what degrades gracefully and what fails hard |
| **Migration** | Not asked | How do you get from the current state to this design without taking down prod? |
| **Trade-offs** | "Option A is faster, Option B is cheaper" | Assign costs to each trade-off; recommend an option with explicit reasoning about org context |
| **Failure modes** | Asked if it comes up | Proactively enumerate failure modes; show which are mitigated and which are accepted risks |

The single biggest mistake L5+ candidates make is running the L4 playbook in an L5+ interview. They answer questions well but never drive. An interviewer evaluating for Staff will see this as a signal that you are not ready.

---

## Capacity Planning Deep-Dive: Twitter Feed Fanout

This is the canonical staff-level system design because the interesting problem is not the data model — it is the *write amplification* problem and the trade-offs around solving it.

### The Problem Statement

Design the Twitter home timeline. Users follow other users. When a user opens Twitter, they see tweets from the people they follow, in reverse-chronological order. The system handles 100 million daily active users.

An L4 answer: "Store tweets in a database, query tweets from users you follow, sort by time."

That answer is correct and completely wrong at this scale. Here is why.

### Back-of-Envelope: Write Amplification

```
100M DAU
Average user follows 100 accounts
Average user posts 1 tweet/day (some post 0, some post 100 — use average)

Naive fan-out-on-write:
  100M users × 100 followers = 10 billion timeline writes/day
  10B / 86,400 seconds = ~115,000 writes/second at average load
  Peak (assume 3x): 345,000 writes/second

That is a lot. But is it too much?
A single Redis instance handles ~100K ops/sec.
So you need at minimum a Redis cluster with 3-4 shards just for peak write volume.
Memory: Average tweet = 140 chars + metadata ≈ 500 bytes
  Each user's timeline holds 800 recent tweets = 400 KB/user
  100M users × 400 KB = 40 TB of timeline data in cache
  This is expensive but not impossible — a 40TB Redis cluster costs ~$80K/month on AWS.
```

### Push vs. Pull Fanout Decision

Now you have the math. The actual decision:

**Fan-out-on-write (push):**
- Write tweet to all follower timelines at post time
- Timeline reads are O(1) — just read pre-computed list
- Problem: Celebrity problem. If @elonmusk has 140M followers and posts a tweet, that is 140M writes. At 500 bytes each, that is 70 GB for a single tweet.

**Fan-out-on-read (pull):**
- Store tweets in author's tweet list only
- At read time, fetch tweets from all followed accounts, merge and sort
- Problem: If you follow 1,000 accounts, reading the timeline requires 1,000 cache lookups + a merge sort. Latency spikes.

**Hybrid approach (what Twitter actually uses):**
- Fan-out-on-write for normal users (< 1M followers)
- Fan-out-on-read for celebrities (> 1M followers, configurable threshold)
- At read time, merge pre-computed timelines with live celebrity feeds
- The merge operation is bounded because there are relatively few accounts above the threshold

This is the answer an L5+ interviewer wants: you identified the problem through math, enumerated the options with their failure modes, and arrived at the hybrid with a justification.

### Storage Calculations

```
Tweet storage (persistent):
  100M DAU × 1 tweet/day = 100M tweets/day
  Each tweet: ~500 bytes
  Daily: 50 GB/day
  5-year retention: 50 GB × 1,825 days = ~90 TB
  With 3x replication: ~270 TB
  This fits on a moderately sized Cassandra or DynamoDB cluster.

Timeline cache (Redis):
  Active users: 100M DAU, assume 20M "hot" users online at peak
  Timeline per user: 800 tweets × 500 bytes = 400 KB
  Hot cache: 20M × 400 KB = 8 TB
  This is your minimum Redis cluster size for hot data.
```

### Cache Sizing Rule of Thumb

When sizing a cache in an interview, use this formula:

```
Cache size = (peak concurrent users) × (data per user) × (cache hit ratio target / 100)
```

For Twitter timelines: if you want a 95% cache hit ratio, you need enough memory to hold the timelines of ~95% of your peak concurrent users. Work backwards from cost to find the right hit ratio.

---

## Failure Budget Framework

Every production system degrades or goes down. The question is not "will it fail?" but "how much failure do we budget for?"

### Reliability Math

| SLA | Annual Downtime | Monthly Downtime |
|-----|-----------------|------------------|
| 99.0% | 87.6 hours | 7.3 hours |
| 99.5% | 43.8 hours | 3.65 hours |
| 99.9% | 8.76 hours | 43.8 minutes |
| 99.95% | 4.38 hours | 21.9 minutes |
| 99.99% | 52.6 minutes | 4.38 minutes |
| 99.999% | 5.26 minutes | 26.3 seconds |

### How to Reason About Reliability at Design Time

The failure budget is 100% minus your SLA. A 99.9% SLA gives you 8.76 hours/year to spend on planned and unplanned downtime.

**Step 1: Identify your SLA.** Ask what the business requires. "Users expect Twitter to be available" is not an SLA. "P95 timeline load < 200ms, availability > 99.9%" is an SLA.

**Step 2: Allocate the budget.** Your system is composed of dependencies. Each dependency has its own failure rate. A system with 10 dependencies each at 99.9% availability has a combined availability of 99% — you have already burned your budget.

```
Combined availability = dependency_1 × dependency_2 × ... × dependency_n
10 dependencies at 99.9% = 0.999^10 = 0.99 = 99.0% combined
```

**Step 3: Decide what degrades gracefully.** Not all failures are equal. If the recommendation service is down, show the home timeline without personalization. If the timeline cache is down, fall back to the database at higher latency. If the database is down, show a cached static page. Each graceful degradation path extends your effective availability.

**Step 4: Make failure explicit in your design.** Draw the failure boundaries on your diagram. Label which components are in the critical path (failure = user-visible outage) vs. the non-critical path (failure = degraded experience).

### Multi-Region Design Checklist

When a system requires 99.99%+ availability, single-region is almost never sufficient. Add this checklist to your mental model:

- [ ] **Data replication:** Is data replicated across regions? Synchronous (strong consistency, higher latency) or async (eventual consistency, lower latency)?
- [ ] **Failover mechanism:** Automated or manual? What is the RTO (recovery time objective)?
- [ ] **Active-active vs. active-passive:** Active-active means both regions serve traffic simultaneously. Active-passive means one region is warm standby. Active-active is harder (write conflicts) but has no failover latency.
- [ ] **DNS TTL:** Low TTL allows fast failover. High TTL reduces DNS resolution cost. Standard: 30-60 seconds for critical services.
- [ ] **Data loss tolerance:** RPO (recovery point objective). If a region fails at 2:00 PM and async replication lag is 5 seconds, you lose 5 seconds of data.
- [ ] **Cross-region traffic cost:** Data transfer between regions is expensive. Design to minimize cross-region reads.
- [ ] **Regulatory constraints:** GDPR, CCPA, data residency laws may prohibit replicating certain data across borders.

---

## Tech Debt Trade-off Framework

L5+ interviews often include a scenario like: "You discover that the core service is built on a deprecated framework that nobody maintains. What do you do?"

The answer is never "rewrite it immediately" or "ignore it forever." The answer is a structured trade-off analysis:

| Factor | Address Now | Defer |
|--------|-------------|-------|
| **Security risk** | Active CVEs, compliance requirement | No known vulnerabilities |
| **Velocity impact** | Slowing down every sprint | Occasional friction |
| **Blast radius** | Core path, used by many teams | Peripheral service |
| **Migration cost** | Small, well-understood | Large, risky |
| **Team capacity** | Available now | Fully allocated |
| **Business timing** | Low-traffic period, stable product | Pre-launch, high change rate |

Frame your answer: "I would assess the security exposure first. If there are active CVEs in the dependency, that becomes an immediate priority regardless of cost. If it is just end-of-life, I would evaluate the velocity impact — how much is it slowing the team down per sprint? If the answer is 'it takes an extra 2 hours per month to work around it,' that is probably not worth a 3-month migration. If it is 'every feature requires a 2-day workaround,' that cost compounds and the rewrite pays back quickly."

---

## 5 Staff-Level Follow-Up Questions with Model Answers

### Q1: "Your design relies heavily on caching. What happens when the cache is cold after a restart?"

**Model answer:** "That is the thundering herd problem. When a cache restarts, every request hits the database simultaneously and you can overwhelm it before the cache warms up. I would handle this with three mitigations: first, use a probabilistic cache expiry — instead of all keys expiring at exactly the same time, add a random jitter of ±10% to TTLs. Second, implement a cache-aside warming script that pre-populates the most popular keys before the cache goes live. Third, implement request coalescing at the application layer — if 1,000 requests arrive for the same uncached key simultaneously, only one goes to the database and the others wait for that result."

### Q2: "How would you migrate from the current system to this design with zero downtime?"

**Model answer:** "I would use the strangler fig pattern. First, stand up the new system in parallel. Second, write to both old and new systems (dual-write phase). Third, start reading from the new system for a small percentage of traffic — say 1% — and compare results against the old system. Fourth, gradually shift read traffic to the new system using a feature flag. Fifth, once 100% of reads are on the new system and results are consistent, turn off writes to the old system. The whole migration might take 2-3 months but there is no cutover window and rollback is trivial until step 5."

### Q3: "How would you handle a situation where the PM wants to ship a feature that requires a significant security trade-off?"

**Model answer:** "I would make the trade-off explicit and in writing. I would write a short document — even just an email — that says: 'To hit the deadline, we are skipping X security control. The risk is Y. We are accepting this risk and plan to address it in sprint Z. Sign-off from: [PM name], [security team name].' This does two things: it ensures everyone understands what we are accepting, and it creates an audit trail so that if the risk materializes, we can trace back to the decision and learn from it. I would not block the ship, but I would not proceed without explicit sign-off."

### Q4: "You've designed the system. Which part worries you most, and what would you do differently with more time?"

**Model answer:** "The part I glossed over most is the data migration for the dual-write period. Dual-write sounds simple but the devils are in the edge cases: what happens when the write to the new system succeeds and the write to the old system fails? You have to decide whether to treat that as a transaction (roll back both) or accept inconsistency temporarily. I assumed we'd accept eventual consistency and reconcile with a background job, but in a real design I would spend significantly more time on the consistency model during migration before committing to that approach."

### Q5: "How would you communicate this design to a team that is skeptical of the new approach?"

**Model answer:** "I would start by understanding their objections before trying to persuade them. Skepticism usually comes from one of three places: they tried something similar and it failed, they have legitimate concerns I have not addressed, or they have not seen enough evidence that this approach works. For the first two, the right move is to listen carefully and either incorporate their concerns into the design or explain specifically why this situation is different. For the third, I would bring data — either from industry case studies or from a small proof-of-concept we can run in a low-risk environment. I would also be explicit about what success looks like so we have a shared definition for evaluating the decision."

---

## Interview Execution Checklist

Use this as a mental checklist during an L5+ system design session:

- [ ] Clarified functional and non-functional requirements
- [ ] Proposed scope explicitly (stated what is out of scope)
- [ ] Did capacity planning math on paper (not just "we need a database")
- [ ] Identified the critical path through the system
- [ ] Named failure modes for each critical component
- [ ] Addressed the migration path or explicitly noted it as out of scope
- [ ] Made a clear recommendation with trade-off reasoning
- [ ] Left 5-10 minutes for follow-up questions

---

*Next:* [Writing RFCs](02-writing-rfcs.md) — how to drive technical alignment through written proposals

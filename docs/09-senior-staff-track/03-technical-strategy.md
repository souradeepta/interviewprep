# Technical Strategy

**Level:** L5+-L6+  
**Time:** 50 min to read + 90 min to draft a strategy outline  
**Interview weight:** High at L6+; increasingly evaluated at L5+ as companies shift responsibility down

---

## Quick Summary

Technical strategy is the document that connects your current technical reality to where you need to be in 12-24 months. It is not a product roadmap (that is the PM's job) and it is not a design doc (that is too granular). It is the answer to "how do we get the platform to a state where the product roadmap is achievable?" This guide teaches you how to write one, how to drive consensus around it, and how to answer strategy questions in interviews.

---

## Tech Strategy vs. Other Documents

This table prevents the most common confusion about what document to write:

| Document | Answers | Time Horizon | Owner | Audience |
|----------|---------|--------------|-------|----------|
| **Architecture Decision Record (ADR)** | Why did we decide X? | Past | Tech lead | New team members |
| **Design Doc / RFC** | How will we build Y? | Present (this quarter) | Senior engineer | Team + stakeholders |
| **Technical Strategy** | Where should our platform be in 12-24 months and how do we get there? | 12-24 months | Staff/Principal | Engineering leadership |
| **Product Roadmap** | What features will we ship? | 6-18 months | PM | Whole org |
| **Engineering OKRs** | What does the engineering team commit to this quarter? | 1 quarter | EM + Staff eng | Team + management |

The confusion usually comes from trying to use a design doc to do the job of a strategy. Design docs are tactical — they describe a specific system in enough detail to implement it. Strategy docs are directional — they describe a destination and the high-level path, without necessarily specifying every component.

---

## The 3 Questions Every Tech Strategy Must Answer

A strategy that does not answer all three questions is incomplete.

### Question 1: Where are we now?

This is a current state assessment. It requires honesty about what is broken, not just a list of what the team has shipped.

Good current state assessment:
> "Our data platform processes 2TB/day through a monolithic ETL pipeline written in Python 2.7. The pipeline has a 4-hour end-to-end latency, 99.3% availability (30+ hours of downtime in 2025), and no unit tests. Three engineers understand how it works; two of them are considering leaving. Product is blocked on two features (real-time fraud signals, personalization) because the pipeline cannot support sub-minute latency."

Bad current state assessment:
> "We have a data pipeline that serves the analytics use case. It works but could be faster."

The current state assessment should make the *cost of doing nothing* visible. If there is no cost to staying put, you do not have a strategy — you have a preference.

### Question 2: Where should we be?

This is the target state. It should be specific enough to know when you have arrived, but not so specific that it is a design doc.

Good target state:
> "By Q4 2027: a streaming data platform that processes events in under 60 seconds end-to-end. 99.9% availability. Any engineer on the data team can add a new pipeline without a platform team dependency. Supports both batch (daily/weekly) and streaming (real-time) workloads from a unified codebase."

Bad target state:
> "A modern, scalable data platform."

The target state should include measurable criteria. "Modern" is not measurable. "60 seconds end-to-end" is.

### Question 3: How do we get there?

This is the migration path. It must be credible — broken into phases that each deliver value independently, with explicit risks and dependencies.

---

## Concrete Example: Monolith to Services Migration Strategy

This is one of the most common technical strategy problems at L5+-L6+ companies. Here is a worked example at the depth an interview expects.

### Context

E-commerce company. Single Rails monolith, 8 years old, ~3M lines of code. 150 engineers. Deployment is risky (requires full regression test), new features are slow to ship (any change can affect any other part of the system), team ownership is ambiguous.

### Current State Assessment

```
Deployment frequency:    2x per week (down from daily 2 years ago — too risky)
Lead time for changes:   3-4 weeks (code complete to production)
Change failure rate:     22% (incidents per deploy)
MTTR:                    4 hours
Test suite duration:     90 minutes
Known tech debt:         ~400 filed tickets, ~1,200 engineering-hours estimated
Team ownership:          Unclear — every PR requires input from 3+ teams
Recruitment impact:      Several candidates cited "Rails monolith" as reason for declining
```

### Target State (18 months)

```
Deployment frequency:    On-demand per service (10-20 deploys/day across teams)
Lead time for changes:   < 1 week for standard features
Change failure rate:     < 10%
MTTR:                    < 30 minutes
Test suite duration:     < 10 minutes per service
Team ownership:          Clear — each service has a single team owner
```

### Migration Phases

**Phase 1 (Q1-Q2): Seams and boundaries (no user impact)**
- Identify service boundaries using domain-driven design (payments, identity, catalog, orders, fulfillment)
- Add API contracts between internal modules (enforced via tests) to prevent cross-domain coupling before extraction
- Stand up observability infrastructure: distributed tracing (Jaeger), service mesh (Linkerd), centralized logging
- Deliverable: Documented service map + API contracts for 5 domains

Why start here: You cannot migrate safely if you do not know where one domain ends and another begins. Skipping this step turns a 3-year migration into a 5-year one with multiple failed extraction attempts.

**Phase 2 (Q2-Q3): Extract lowest-risk, highest-isolation service**
- Identity service: clean API, few upstream dependencies, security-sensitive (good reason to isolate)
- Run dual-write (monolith + new service) for 6 weeks
- Validate functional parity with automated comparison tests
- Deliverable: Identity service fully extracted, team owns it end-to-end

Why start with identity: It has the clearest API boundary, the highest security motivation, and extracting it does not require changing the core order flow. Starting with orders or payments would be faster to convince leadership but much higher risk.

**Phase 3 (Q3-Q4): Extract two more services (catalog + payments)**
- Catalog is read-heavy and has clean APIs — good for proving the pattern
- Payments is high-priority because it has compliance (PCI) requirements that are easier to meet in an isolated service
- Apply lessons from identity extraction
- Deliverable: 3 of 5 services extracted, migration playbook documented for remaining teams

**Phase 4 (Year 2): Remaining services + monolith shrinkage**
- Orders and fulfillment are the hardest — complex business logic, most cross-domain dependencies
- By this point, team should have 2-3 experienced service extraction engineers who can pair with each affected team
- Monolith continues to run but gets smaller each quarter
- Deliverable: Monolith reduced to <500K lines (from 3M); all critical paths in services

### Risk Register

| Risk | Impact | Likelihood | Owner | Mitigation |
|------|--------|------------|-------|------------|
| Monolith continues to grow during migration | High | High | Engineering leadership | No new monolith code policy starting Phase 1 |
| Distributed systems complexity increases on-call burden | High | Medium | Platform team | Service mesh + centralized logging before any extraction |
| Extraction takes 3x longer than estimated | Medium | High | Staff engineers | Phase 2 is deliberately small and lower-risk to establish realistic estimates |
| Engineers leave due to migration fatigue | Medium | Medium | EMs | Time-box migration phases; celebrate completions |
| API contracts break during migration | High | Low | Owning teams | Contract testing in CI; no merges that break contracts |

---

## How to Drive Consensus Without Authority

A Staff engineer writing a technical strategy has no authority to compel teams to follow it. The strategy only works if people choose to follow it. Here is how to build that consent.

### Pre-meetings and 1:1s

The all-hands is not where you build consensus. It is where you announce the consensus you have already built. Before any large group meeting:

1. Identify the 3-5 people whose support you most need (usually: senior engineer from each affected team + EM + the most vocal skeptic)
2. Walk each of them through the strategy 1:1 before it is published
3. Ask explicitly: "What is the strongest objection you expect people to raise?" Then address that objection in the strategy document
4. Get each person to agree to be a "champion" for the strategy in their team's context

This is not manipulation — it is respect. You are giving people the chance to influence the strategy before it is final, rather than asking them to react to a fait accompli.

### Written Proposals Win

A written document forces clarity that verbal proposals do not. "We should migrate to microservices" said in a meeting produces 30 minutes of discussion with no outcome. The same idea in a 5-page document produces specific objections that can be addressed.

Write the strategy before any major meeting. Distribute it at least 48 hours in advance. Set the expectation that people will have read it before the meeting.

### Handling "Not Invented Here" Resistance

The most common form of pushback on a technical strategy is not technical — it is territorial. "Team X will never adopt this because they do not want platform to own their dependencies."

Approach this by finding the alignment of interests: what does Team X get from this strategy? If the answer is "nothing, they just have to do work," the strategy has a design problem. Every team that has to change behavior because of your strategy should get something in return — lower operational burden, faster deployments, shared ownership of a problem they were solving alone.

---

## Decision-Making Under Uncertainty

Technical strategies require making decisions before you have full information. Two failure modes:

**Failure mode 1: Analysis paralysis.** Waiting for perfect information before committing to a direction. The problem is that information arrives slowly and the cost of waiting compounds.

**Failure mode 2: Premature commitment.** Picking a direction before understanding the key uncertainties and getting locked in when those uncertainties resolve differently than expected.

### The Reversibility Matrix

Use this framework to calibrate how much time to invest before deciding:

| Decision | Reversibility | Investment Required |
|----------|---------------|---------------------|
| Which cloud provider to use | Low (years of migration to change) | High — run PoCs, get multiple quotes, involve leadership |
| Which deployment framework to standardize on | Medium (painful but possible to migrate) | Medium — evaluate 3 options, run a pilot project |
| Which logging library to use in a new service | High (easy to swap) | Low — pick the most popular, move on |
| How to structure the monolith extraction phases | Medium | Medium — invest in Phase 1 to get data before committing to Phase 2 |

The heuristic: if you can cheaply reverse the decision in 6 months, decide fast and iterate. If it would take 18 months of migration to undo, invest proportionally in the upfront decision.

### When to Commit vs. When to Defer

Defer when: the decision depends on information you will have in 4-8 weeks (another team's API is being designed, a benchmark is in progress, a vendor contract is being negotiated).

Commit when: the cost of waiting exceeds the expected value of additional information. If the team is blocked on 3 features because you have not decided on the data storage format, the right answer is to commit to a reasonable choice with documented assumptions and revisit in 6 months.

---

## Staff Interview Q: "How Do You Influence Teams You Don't Manage?"

This is the most common L6+ behavioral question and it almost always resolves to a strategy story.

**Model answer:**

"The honest answer is that I cannot compel teams to do anything. I have to persuade them. The way I do that is by making the case that the thing I am proposing solves their problem better than what they would come up with independently.

Concretely: when I drove the data platform migration strategy at [company], the hardest part was not writing the strategy — it was getting three teams who each had their own roadmaps to agree to prioritize it. I started by understanding each team's actual pain points: Team A was frustrated by the 4-hour pipeline latency blocking their ML team; Team B was worried about the 22% deploy failure rate; Team C had a compliance deadline that the current system could not meet.

I redesigned the strategy phases to address each team's specific pain first. Team C's compliance deadline became Phase 2 instead of Phase 4. Team A got early access to the streaming pipeline in the pilot. Team B's deploy reliability improved as a side effect of Phase 1 because we added the contract testing.

By the time I presented the strategy to leadership, I already had verbal buy-in from the tech leads of all three teams. The leadership meeting was about resources and timeline, not about whether to do it.

What I learned: the content of the strategy matters, but the social process of building it matters more. A technically optimal strategy that nobody adopts is worse than a slightly suboptimal strategy that the whole org commits to."

---

*Next:* [Ambiguity and Scoping](04-ambiguity-and-scoping.md) — how to define the problem before solving it
